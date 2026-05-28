/**
 * PlaywrightProvider — deterministic browser automation
 * Implements BrowserProvider using Microsoft Playwright
 *
 * Install browsers: npx playwright install chromium
 */

import { chromium, Browser, BrowserContext, Page } from 'playwright';
import { v4 as uuidv4 } from 'uuid';
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
}

export class PlaywrightProvider implements BrowserProvider {
  private browser: Browser | null = null;
  private sessions: Map<string, SessionState> = new Map();
  private headless: boolean;

  constructor(headless = true) {
    this.headless = headless;
  }

  private async ensureBrowser(): Promise<Browser> {
    if (!this.browser) {
      this.browser = await chromium.launch({ headless: this.headless });
    }
    return this.browser;
  }

  async launch(sessionId?: string): Promise<BrowserSession> {
    const browser = await this.ensureBrowser();
    const context = await browser.newContext({
      viewport: { width: 1440, height: 900 },
      userAgent:
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    });
    const page = await context.newPage();
    const id = sessionId || uuidv4();
    const session: BrowserSession = { id, url: 'about:blank', createdAt: new Date() };
    this.sessions.set(id, { session, context, page });
    return session;
  }

  private getState(sessionId: string): SessionState {
    const state = this.sessions.get(sessionId);
    if (!state) throw new Error(`No Playwright session: ${sessionId}`);
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
      // Fallback: evaluate JS with instruction as comment for traceability
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

  async close(sessionId: string): Promise<void> {
    const state = this.sessions.get(sessionId);
    if (state) {
      await state.context.close();
      this.sessions.delete(sessionId);
    }
  }

  async closeAll(): Promise<void> {
    for (const [id] of this.sessions) await this.close(id);
    if (this.browser) {
      await this.browser.close();
      this.browser = null;
    }
  }
}
