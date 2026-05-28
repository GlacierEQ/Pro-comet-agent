/**
 * providerFactory — selects and returns the active BrowserProvider
 * Controlled by BROWSER_PROVIDER env var
 *   playwright (default) — deterministic, stable, recommended
 *   stagehand            — NL-driven, resilient, requires OpenAI key
 */

import { BrowserProvider } from './BrowserProvider';

let instance: BrowserProvider | null = null;

export async function getProvider(): Promise<BrowserProvider> {
  if (instance) return instance;

  const provider = process.env.BROWSER_PROVIDER ?? 'playwright';
  const headless = process.env.BROWSER_HEADLESS !== 'false';

  if (provider === 'stagehand') {
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
