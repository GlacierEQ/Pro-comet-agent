/**
 * CometProvider — connects to the already-running Comet browser via Chrome DevTools Protocol (CDP)
 *
 * Instead of spawning a new Chromium, this attaches to Comet's built-in browser
 * which exposes a CDP endpoint on localhost:9222 by default.
 *
 * Requirements:
 *   - Comet must be running with remote debugging enabled
 *   - Set COMET_CDP_URL=http://localhost:9222 in your .env (or leave default)
 *
 * Usage: set BROWSER_PROVIDER=comet in your .env
 */

import { chromium, Browser, BrowserContext, Page, CDPSession } from 'playwright';
import { v4 as uuidv4 } from 'uuid';
import { logger } from '../../utils/logger';
import {
  BrowserProvider,
  BrowserSession,
  NavigateOptions,
  ActOptions,
  ExtractOptions,
  ScreenshotOptions,
} from '../../browser/BrowserProvider';

interface SessionState {
  session: BrowserSession;
  context: BrowserContext;
  page: Page;
  lastAccessedAt: Date;
}

export class CometProvider implements BrowserProvider {
  private browser: Browser | null = null;
  private sessions: Map<string, SessionState> = new Map();
  private cdpUrl: string;
  private cleanupInterval: NodeJS.Timeout | null = null;

  constructor() {
    this.cdpUrl = process.env.COMET_CDP_URL ?? 'http://localhost:9222';

    const checkIntervalMs = Number(process.env.SESSION_CHECK_INTERVAL_MS) || 30_000;
    this.cleanupInterval = setInterval(() => {
      this.cleanupInactiveSessions().catch(err =>
        logger.error('[CometProvider] error in session cleanup:', err)
      );
    }, checkIntervalMs);
  }

  private async ensureBrowser(): Promise<Browser> {
    if (this.browser) return this.browser;

    logger.info(`[CometProvider] connecting to Comet CDP at ${this.cdpUrl}`);

    // Verify Comet is reachable before attempting connection
    try {
      const res = await fetch(`${this.cdpUrl}/json/version`);
      if (!res.ok) throw new Error(`CDP /json/version returned ${res.status}`);
      const info = await res.json() as Record<string, string>;
      logger.info(`[CometProvider] connected to: ${info['Browser'] ?? 'unknown'} (${info['Protocol-Version'] ?? '?'})`);
    } catch (err: any) {
      throw new Error(
        `[CometProvider] Cannot reach Comet at ${this.cdpUrl}.\n` +
        `Make sure Comet is running with remote debugging enabled.\n` +
        `Error: ${err?.message ?? err}`
      );
    }

    this.browser = await chromium.connectOverCDP(this.cdpUrl);
    logger.info('[CometProvider] successfully attached to Comet browser via CDP.');
    return this.browser;
  }

  async launch(sessionId?: string): Promise<BrowserSession> {
    const browser = await this.ensureBrowser();

    // Use existing context if available (Comet's active window)
    const contexts = browser.contexts();
    let context: BrowserContext;
    let page: Page;

    if (contexts.length > 0) {
      context = contexts[0];
      const pages = context.pages();
      page = pages.length > 0 ? pages[0] : await context.newPage();
      logger.info('[CometProvider] reusing existing Comet browser context.');
    } else {
      context = await browser.newContext({
        viewport: { width: 1440, height: 900 },
      });
      page = await context.newPage();
      logger.info('[CometProvider] created new context in Comet browser.');
    }

    const id = sessionId ?? uuidv4();
    const session: BrowserSession = { id, url: page.url() || 'about:blank', createdAt: new Date() };
    this.sessions.set(id, { session, context, page, lastAccessedAt: new Date() });
    return session;
  }

  private getState(sessionId: string): SessionState {
    const state = this.sessions.get(sessionId);
    if (!state) throw new Error(`No CometProvider session: ${sessionId}`);
    state.lastAccessedAt = new Date();
    return state;
  }

  async navigate(sessionId: string, url: string, options?: NavigateOptions): Promise<void> {
    const { page, session } = this.getState(sessionId);
    await page.goto(url, {
      waitUntil: options?.waitUntil ?? 'domcontentloaded',
      timeout: options?.timeout ?? 30_000,
    });
    session.url = url;
  }

  async act(sessionId: string, options: ActOptions): Promise<void> {
    const { page } = this.getState(sessionId);
    const timeout = options.timeout ?? 10_000;
    if (options.selector && options.value !== undefined) {
      await page.fill(options.selector, options.value, { timeout });
    } else if (options.selector) {
      await page.click(options.selector, { timeout });
    } else if (options.instruction) {
      logger.warn('[CometProvider] instruction-based act not supported; set BROWSER_PROVIDER=stagehand for NL actions.');
    }
  }

  async extract<T = unknown>(sessionId: string, options: ExtractOptions): Promise<T> {
    const { page } = this.getState(sessionId);
    if (options.selector) {
      const text = await page.$$eval(options.selector, (els) =>
        els.map((el) => el.textContent?.trim()).filter(Boolean)
      );
      return text as unknown as T;
    }
    return (await page.content()) as unknown as T;
  }

  async screenshot(sessionId: string, options?: ScreenshotOptions): Promise<Buffer> {
    const { page } = this.getState(sessionId);
    return page.screenshot({ fullPage: options?.fullPage ?? false, path: options?.path }) as Promise<Buffer>;
  }

  async currentUrl(sessionId: string): Promise<string> {
    const { page } = this.getState(sessionId);
    return page.url();
  }

  async listSessions(): Promise<BrowserSession[]> {
    return Array.from(this.sessions.values()).map((s) => s.session);
  }

  async close(sessionId: string): Promise<void> {
    const state = this.sessions.get(sessionId);
    if (state) {
      // Don't close Comet's context — just detach our session tracking
      this.sessions.delete(sessionId);
      logger.info(`[CometProvider] detached session: ${sessionId}`);
    }
  }

  private async cleanupInactiveSessions(): Promise<void> {
    const timeoutMs = Number(process.env.SESSION_TIMEOUT_MS) || 15 * 60 * 1000;
    const now = Date.now();
    for (const [id, state] of this.sessions.entries()) {
      if (now - state.lastAccessedAt.getTime() > timeoutMs) {
        logger.warn(`[CometProvider] Session ${id} exceeded idle timeout. Detaching.`);
        await this.close(id);
      }
    }
  }

  async closeAll(): Promise<void> {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
      this.cleanupInterval = null;
    }
    for (const [id] of this.sessions) await this.close(id);
    // Disconnect from Comet CDP without closing the browser itself
    if (this.browser) {
      await this.browser.close().catch(() => {});
      this.browser = null;
    }
    logger.info('[CometProvider] disconnected from Comet.');
  }
}
