/**
 * MyMap Workflow Module
 * First-class automation support for MyMap AI canvas
 *
 * Golden paths:
 *   1. createMapFromPrompt — open blank map, submit idea, wait for generation
 *   2. insertMermaid       — add a Mermaid diagram block to existing map
 *   3. getShareLink        — extract the public share URL from a map
 */

import { getProvider } from '../../browser/providerFactory';

const MYMAP_BASE = process.env.MYMAP_BASE_URL ?? 'https://www.mymap.ai';

export interface CreateMapOptions {
  prompt: string;
  sessionId?: string;
  waitMs?: number;
}

export interface InsertMermaidOptions {
  mapUrl: string;
  mermaidCode: string;
  sessionId: string;
}

export interface MapResult {
  sessionId: string;
  mapUrl: string;
  shareLink?: string;
  screenshotBuffer?: Buffer;
}

/**
 * Step 1 — Log into MyMap (call once per session)
 */
export async function loginToMyMap(sessionId: string): Promise<void> {
  const provider = await getProvider();
  const email = process.env.MYMAP_EMAIL;
  const password = process.env.MYMAP_PASSWORD;
  if (!email || !password) throw new Error('MYMAP_EMAIL and MYMAP_PASSWORD must be set in .env');

  await provider.navigate(sessionId, `${MYMAP_BASE}/login`, { waitUntil: 'networkidle' });

  // Fill credentials — selectors may need adjustment if MyMap updates their UI
  await provider.act(sessionId, { selector: 'input[type="email"]', value: email });
  await provider.act(sessionId, { selector: 'input[type="password"]', value: password });
  await provider.act(sessionId, { selector: 'button[type="submit"]' });

  // Wait for redirect to dashboard
  await new Promise((r) => setTimeout(r, 3000));
}

/**
 * Step 2 — Create a new map from a prompt on a blank canvas
 */
export async function createMapFromPrompt(options: CreateMapOptions): Promise<MapResult> {
  const provider = await getProvider();
  const sessionId = options.sessionId ?? 'mymap-default';
  const waitMs = options.waitMs ?? 8000;

  // Launch session if new
  const session = await provider.launch(sessionId);
  await loginToMyMap(session.id);

  // Navigate to new map
  await provider.navigate(session.id, `${MYMAP_BASE}/map/new`, { waitUntil: 'networkidle' });

  // Submit the idea/prompt
  // MyMap exposes a "Describe your idea..." textarea on blank canvases
  await provider.act(session.id, {
    instruction: 'Find the idea description textarea and type the prompt',
    selector: 'textarea[placeholder*="idea"], textarea[placeholder*="Describe"], .prompt-input',
    value: options.prompt,
  });

  // Submit
  await provider.act(session.id, {
    instruction: 'Click the submit or generate button',
    selector: 'button[type="submit"], .generate-btn, button:has-text("Generate")',
  });

  // Wait for canvas to render
  await new Promise((r) => setTimeout(r, waitMs));

  const mapUrl = await provider.currentUrl(session.id);
  const screenshot = await provider.screenshot(session.id, { fullPage: false });

  return {
    sessionId: session.id,
    mapUrl,
    screenshotBuffer: screenshot,
  };
}

/**
 * Step 3 — Get the share link from an open map
 */
export async function getShareLink(sessionId: string, mapUrl: string): Promise<string | null> {
  const provider = await getProvider();
  await provider.navigate(sessionId, mapUrl, { waitUntil: 'networkidle' });

  const result = await provider.extract<string[]>(sessionId, {
    instruction: 'Find the public share URL for this map',
    selector: 'input[value*="mymap.ai/share"]',
  });

  return Array.isArray(result) && result.length > 0 ? result[0] : null;
}
