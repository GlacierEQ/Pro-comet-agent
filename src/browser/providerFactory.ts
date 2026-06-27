/**
 * providerFactory — selects and returns the active BrowserProvider
 * Controlled by BROWSER_PROVIDER env var:
 *   comet       — connects to running Comet browser via CDP (recommended for Comet agent)
 *   playwright  — spawns its own headless Chromium (default fallback)
 *   stagehand   — NL-driven via Browserbase/Stagehand (requires OpenAI key)
 */

import { BrowserProvider } from './BrowserProvider';

let instance: BrowserProvider | null = null;

export async function getProvider(): Promise<BrowserProvider> {
  if (instance) return instance;

  const provider = (process.env.BROWSER_PROVIDER ?? 'playwright').toLowerCase().trim();
  const headless = process.env.BROWSER_HEADLESS !== 'false';

  if (provider === 'comet') {
    const { CometProvider } = await import('../providers/comet/CometProvider');
    instance = new CometProvider();
  } else if (provider === 'stagehand') {
    const { StagehandAdapter } = await import('../providers/stagehand/StagehandAdapter');
    instance = new StagehandAdapter(process.env.OPENAI_MODEL ?? 'gpt-4o');
  } else {
    const { PlaywrightProvider } = await import('../providers/playwright/PlaywrightProvider');
    instance = new PlaywrightProvider(headless);
  }

  return instance;
}

export function resetProvider(): void {
  instance = null;
}
