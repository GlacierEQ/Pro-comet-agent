/**
 * Vercel Edge Config client
 * Used for: feature flags, live provider switching, kill switches, rate limits
 *
 * Edge Config reads are ~1ms — faster than any DB or env var reload.
 * Update flags in Vercel dashboard → live in <1s, zero redeploy.
 *
 * EDGE_CONFIG env var is set automatically when you link an Edge Config
 * store to your project in the Vercel dashboard.
 *
 * Degrades gracefully — if Edge Config is not configured, all flags
 * return their provided defaultValue. Nothing breaks.
 */

let _client: any = null;

async function getClient() {
  if (_client) return _client;
  try {
    const { createClient } = await import('@vercel/edge-config');
    _client = createClient(process.env.EDGE_CONFIG!);
    return _client;
  } catch {
    return null; // optional dependency — degrade gracefully
  }
}

/** Read one flag. Returns defaultValue if Edge Config is unavailable. */
export async function getFlag<T>(key: string, defaultValue: T): Promise<T> {
  const client = await getClient();
  if (!client) return defaultValue;
  try {
    const value = await client.get<T>(key);
    return value ?? defaultValue;
  } catch {
    return defaultValue;
  }
}

/** Read all flags at once — cheaper than multiple getFlag calls. */
export async function getAllFlags(): Promise<Record<string, unknown>> {
  const client = await getClient();
  if (!client) return {};
  try {
    return (await client.getAll()) ?? {};
  } catch {
    return {};
  }
}

/** Typed flag keys for comet-agent */
export const FLAGS = {
  BROWSER_PROVIDER:    'browserProvider',    // 'playwright' | 'stagehand'
  MAX_SESSIONS:        'maxSessions',         // number
  ENABLE_SCREENSHOTS:  'enableScreenshots',   // boolean
  RATE_LIMIT_RPM:      'rateLimitRpm',        // number
  MAINTENANCE_MODE:    'maintenanceMode',     // boolean
} as const;
