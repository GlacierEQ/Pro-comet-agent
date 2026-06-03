/**
 * BrowserProvider — core abstraction interface
 *
 * All browser engines (Playwright, Stagehand) implement this interface.
 * Application code depends ONLY on this interface, never on a specific engine.
 * Swap engines by changing BROWSER_PROVIDER env var.
 */

export interface NavigateOptions {
  waitUntil?: 'load' | 'domcontentloaded' | 'networkidle';
  timeout?: number;
}

export interface ActOptions {
  /** Natural language instruction (Stagehand) or CSS selector (Playwright) */
  selector?: string;
  instruction?: string;
  value?: string;
  timeout?: number;
}

export interface ExtractOptions {
  /** JSON schema describing the shape of data to extract */
  schema?: Record<string, unknown>;
  instruction?: string;
  selector?: string;
}

export interface ScreenshotOptions {
  fullPage?: boolean;
  path?: string;
}

export interface BrowserSession {
  id: string;
  url: string;
  createdAt: Date;
}

export interface BrowserProvider {
  /** Launch a new browser session */
  launch(sessionId?: string): Promise<BrowserSession>;

  /** Navigate to a URL in an existing session */
  navigate(sessionId: string, url: string, options?: NavigateOptions): Promise<void>;

  /** Perform a page action (click, type, submit, etc.) */
  act(sessionId: string, options: ActOptions): Promise<void>;

  /** Extract structured data from the current page */
  extract<T = unknown>(sessionId: string, options: ExtractOptions): Promise<T>;

  /** Take a screenshot of the current page */
  screenshot(sessionId: string, options?: ScreenshotOptions): Promise<Buffer>;

  /** Get the current page URL */
  currentUrl(sessionId: string): Promise<string>;

  /** Close a specific session */
  close(sessionId: string): Promise<void>;

  /** List all active sessions */
  listSessions(): Promise<BrowserSession[]>;

  /** Close all sessions and browser */
  closeAll(): Promise<void>;
}
