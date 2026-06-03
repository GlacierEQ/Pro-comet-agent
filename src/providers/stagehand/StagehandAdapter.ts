/**
 * StagehandAdapter — natural-language browser automation
 * Wraps Stagehand (Browserbase) which sits on top of Playwright
 * Use this when UI selectors are brittle or you want agent-style resilience
 *
 * Install: npm install @browserbasehq/stagehand
 * Stagehand docs: https://docs.stagehand.dev
 */

import { logger } from '../../utils/logger';
import {
  BrowserProvider,
  BrowserSession,
  NavigateOptions,
  ActOptions,
  ExtractOptions,
  ScreenshotOptions,
} from '../../browser/BrowserProvider';

// Lazy import — Stagehand is optional. Only needed if BROWSER_PROVIDER=stagehand
let StagehandClass: any = null;
const loadStagehand = async () => {
  if (!StagehandClass) {
    try {
      // @ts-ignore
      const mod = await import('@browserbasehq/stagehand');
      StagehandClass = mod.Stagehand;
    } catch {
      throw new Error(
        'Stagehand not installed. Run: npm install @browserbasehq/stagehand\nOr set BROWSER_PROVIDER=playwright to use Playwright instead.'
      );
    }
  }
  return StagehandClass;
};

interface StagehandSessionState {
  session: BrowserSession;
  instance: any;
  lastAccessedAt: Date;
}

export class StagehandAdapter implements BrowserProvider {
  private instances: Map<string, StagehandSessionState> = new Map();
  private modelName: string;
  private cleanupInterval: NodeJS.Timeout | null = null;

  constructor(modelName = 'gpt-4o') {
    this.modelName = modelName;
    
    // Start idle session cleanup timer (every 30 seconds)
    const checkIntervalMs = Number(process.env.SESSION_CHECK_INTERVAL_MS) || 30000;
    this.cleanupInterval = setInterval(() => {
      this.cleanupInactiveSessions().catch(err => {
        logger.error('[StagehandAdapter] error in inactive session cleanup:', err);
      });
    }, checkIntervalMs);
  }

  async launch(sessionId?: string): Promise<BrowserSession> {
    const Stagehand = await loadStagehand();
    const sh = new Stagehand({
      env: 'LOCAL',
      modelName: this.modelName,
      headless: process.env.BROWSER_HEADLESS === 'true',
    });
    await sh.init();
    const id = sessionId || `sh-${Date.now()}`;
    const session: BrowserSession = { id, url: 'about:blank', createdAt: new Date() };
    this.instances.set(id, { session, instance: sh, lastAccessedAt: new Date() });
    return session;
  }

  private get(sessionId: string): any {
    const state = this.instances.get(sessionId);
    if (!state) throw new Error(`No Stagehand session: ${sessionId}`);
    state.lastAccessedAt = new Date();
    return state.instance;
  }

  async navigate(sessionId: string, url: string, _options?: NavigateOptions): Promise<void> {
    const sh = this.get(sessionId);
    await sh.page.goto(url, { waitUntil: 'domcontentloaded' });
    const state = this.instances.get(sessionId);
    if (state) state.session.url = url;
  }

  async act(sessionId: string, options: ActOptions): Promise<void> {
    const sh = this.get(sessionId);
    const action = options.instruction || options.selector || '';
    await sh.act({ action });
  }

  async extract<T = unknown>(sessionId: string, options: ExtractOptions): Promise<T> {
    const sh = this.get(sessionId);
    return sh.extract({ instruction: options.instruction || 'Extract all visible text', schema: options.schema });
  }

  async screenshot(sessionId: string, _options?: ScreenshotOptions): Promise<Buffer> {
    const sh = this.get(sessionId);
    return sh.page.screenshot();
  }

  async currentUrl(sessionId: string): Promise<string> {
    const sh = this.get(sessionId);
    return sh.page.url();
  }

  async listSessions(): Promise<BrowserSession[]> {
    return Array.from(this.instances.values()).map(s => s.session);
  }

  async close(sessionId: string): Promise<void> {
    const state = this.instances.get(sessionId);
    if (state) {
      await state.instance.close();
      this.instances.delete(sessionId);
      logger.info(`[StagehandAdapter] closed session: ${sessionId}`);
    }
  }

  private async cleanupInactiveSessions(): Promise<void> {
    const timeoutMs = Number(process.env.SESSION_TIMEOUT_MS) || 15 * 60 * 1000; // 15 mins default
    const now = Date.now();
    for (const [id, state] of this.instances.entries()) {
      const age = now - state.lastAccessedAt.getTime();
      if (age > timeoutMs) {
        logger.warn(`[StagehandAdapter] Session ${id} exceeded idle timeout. Auto-evicting.`);
        await this.close(id);
      }
    }
  }

  async closeAll(): Promise<void> {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
      this.cleanupInterval = null;
    }
    for (const [id] of this.instances) await this.close(id);
  }
}
