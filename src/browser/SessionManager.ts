/**
 * SessionManager — manages lifecycle of browser sessions
 * Maps sessionId → active session state
 */

import { BrowserSession } from './BrowserProvider';

export class SessionManager {
  private sessions: Map<string, BrowserSession> = new Map();

  register(session: BrowserSession): void {
    this.sessions.set(session.id, session);
  }

  get(sessionId: string): BrowserSession | undefined {
    return this.sessions.get(sessionId);
  }

  require(sessionId: string): BrowserSession {
    const session = this.sessions.get(sessionId);
    if (!session) throw new Error(`Session not found: ${sessionId}`);
    return session;
  }

  remove(sessionId: string): void {
    this.sessions.delete(sessionId);
  }

  list(): BrowserSession[] {
    return Array.from(this.sessions.values());
  }

  count(): number {
    return this.sessions.size;
  }
}
