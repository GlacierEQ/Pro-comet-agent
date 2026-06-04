/**
 * PlaywrightProvider — deterministic browser automation
 * Implements BrowserProvider using Microsoft Playwright
 *
 * Install browsers: npx playwright install chromium
 */

import { chromium, Browser, BrowserContext, Page } from 'playwright';
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

export class PlaywrightProvider implements BrowserProvider {
  private browser: Browser | null = null;
  private sessions: Map<string, SessionState> = new Map();
  private headless: boolean;
  
  // Warm context pool
  private contextPool: { context: BrowserContext; page: Page }[] = [];
  private poolSize = 2;
  private isReplenishing = false;
  private cleanupInterval: NodeJS.Timeout | null = null;

  constructor(headless = true) {
    this.headless = headless;
    
    // Start idle session cleanup timer (every 30 seconds)
    const checkIntervalMs = Number(process.env.SESSION_CHECK_INTERVAL_MS) || 30000;
    this.cleanupInterval = setInterval(() => {
      this.cleanupInactiveSessions().catch(err => {
        logger.error('[PlaywrightProvider] error in inactive session cleanup:', err);
      });
    }, checkIntervalMs);
  }

  private async ensureBrowser(): Promise<Browser> {
    if (!this.browser) {
      const execPath = process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH || undefined;
      this.browser = await chromium.launch({
        headless: this.headless,
        executablePath: execPath
      });
      // Trigger initial pool replenishment
      this.replenishPool().catch(err => {
        logger.error('[PlaywrightProvider] failed to initialize context pool:', err);
      });
    }
    return this.browser;
  }

  private async replenishPool(): Promise<void> {
    if (!this.browser || this.isReplenishing) return;
    this.isReplenishing = true;

    try {
      while (this.contextPool.length < this.poolSize) {
        logger.info(`[PlaywrightProvider] replenishing warm context pool (${this.contextPool.length + 1}/${this.poolSize})...`);
        const context = await this.browser.newContext({
          viewport: { width: 1440, height: 900 },
          userAgent:
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        });
        const page = await context.newPage();
        this.contextPool.push({ context, page });
      }
    } finally {
      this.isReplenishing = false;
    }
  }

  async launch(sessionId?: string): Promise<BrowserSession> {
    const browser = await this.ensureBrowser();
    
    let context: BrowserContext;
    let page: Page;
    
    // Pop from pool if available
    const pooled = this.contextPool.shift();
    if (pooled) {
      context = pooled.context;
      page = pooled.page;
      logger.info('[PlaywrightProvider] reused warm context from pool.');
    } else {
      logger.info('[PlaywrightProvider] pool empty, launching new context on demand.');
      context = await browser.newContext({
        viewport: { width: 1440, height: 900 },
        userAgent:
          'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
      });
      page = await context.newPage();
    }

    // Asynchronously replenish pool
    this.replenishPool().catch(err => {
      logger.error('[PlaywrightProvider] failed to replenish context pool:', err);
    });

    const id = sessionId || uuidv4();
    const session: BrowserSession = { id, url: 'about:blank', createdAt: new Date() };
    this.sessions.set(id, { session, context, page, lastAccessedAt: new Date() });
    return session;
  }

  private getState(sessionId: string): SessionState {
    const state = this.sessions.get(sessionId);
    if (!state) throw new Error(`No Playwright session: ${sessionId}`);
    // Update last accessed time
    state.lastAccessedAt = new Date();
    return state;
  }

  async navigate(sessionId: string, url: string, options?: NavigateOptions): Promise<void> {
    const { page, session } = this.getState(sessionId);
    await page.goto(url, {
      waitUntil: options?.waitUntil ?? 'domcontentloaded',
      timeout: options?.timeout ?? 30000,
    });
    session.url = url;
  }

  async act(sessionId: string, options: ActOptions): Promise<void> {
    const { page } = this.getState(sessionId);
    const timeout = options.timeout ?? 10000;

    if (options.selector && options.value !== undefined) {
      await page.fill(options.selector, options.value, { timeout });
    } else if (options.selector) {
      await page.click(options.selector, { timeout });
    } else if (options.instruction) {
      console.warn('[PlaywrightProvider] instruction-based act not natively supported; use Stagehand adapter');
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
    const content = await page.content();
    return content as unknown as T;
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
    return Array.from(this.sessions.values()).map(s => s.session);
  }

  async close(sessionId: string): Promise<void> {
    const state = this.sessions.get(sessionId);
    if (state) {
      await state.context.close();
      this.sessions.delete(sessionId);
      logger.info(`[PlaywrightProvider] closed session: ${sessionId}`);
    }
  }

  private async cleanupInactiveSessions(): Promise<void> {
    const timeoutMs = Number(process.env.SESSION_TIMEOUT_MS) || 15 * 60 * 1000; // 15 mins default
    const now = Date.now();
    for (const [id, state] of this.sessions.entries()) {
      const age = now - state.lastAccessedAt.getTime();
      if (age > timeoutMs) {
        logger.warn(`[PlaywrightProvider] Session ${id} exceeded idle timeout. Auto-evicting.`);
        await this.close(id);
      }
    }
  }

  async closeAll(): Promise<void> {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
      this.cleanupInterval = null;
    }
    
    // Clear pool
    for (const pooled of this.contextPool) {
      try {
        await pooled.context.close();
      } catch (err) {
        logger.error('[PlaywrightProvider] error closing pooled context:', err);
      }
    }
    this.contextPool = [];

    // Clear sessions
    for (const [id] of this.sessions) {
      await this.close(id);
    }
    
    if (this.browser) {
      await this.browser.close();
      this.browser = null;
    }
  }
}
