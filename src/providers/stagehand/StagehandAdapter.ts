/**
 * StagehandAdapter — natural-language browser automation
 * Wraps Stagehand (Browserbase) which sits on top of Playwright
 * Use this when UI selectors are brittle or you want agent-style resilience
 *
 * Install: npm install @browserbasehq/stagehand
 * Stagehand docs: https://docs.stagehand.dev
 */

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

export class StagehandAdapter implements BrowserProvider {
  private instances: Map<string, any> = new Map();
  private modelName: string;

  constructor(modelName = 'gpt-4o') {
    this.modelName = modelName;
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
    this.instances.set(id, sh);
    return { id, url: 'about:blank', createdAt: new Date() };
  }

  private get(sessionId: string): any {
    const sh = this.instances.get(sessionId);
    if (!sh) throw new Error(`No Stagehand session: ${sessionId}`);
    return sh;
  }

  async navigate(sessionId: string, url: string, _options?: NavigateOptions): Promise<void> {
    const sh = this.get(sessionId);
    await sh.page.goto(url, { waitUntil: 'domcontentloaded' });
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

  async close(sessionId: string): Promise<void> {
    const sh = this.instances.get(sessionId);
    if (sh) {
      await sh.close();
      this.instances.delete(sessionId);
    }
  }

  async closeAll(): Promise<void> {
    for (const [id] of this.instances) await this.close(id);
  }
}
