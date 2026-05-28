/**
 * Supabase client — two modes:
 *   supabase      → anon/public key  (safe for reads)
 *   supabaseAdmin → service_role key (server-only, never expose to client)
 *
 * Used for:
 *  - Storage: screenshot + artifact uploads
 *  - Realtime: live job status push to connected clients
 *  - Auth (optional): API key validation
 */

import { createClient } from '@supabase/supabase-js';

const url = process.env.SUPABASE_URL;
const anonKey = process.env.SUPABASE_ANON_KEY;
const serviceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!url || !anonKey) {
  throw new Error('SUPABASE_URL and SUPABASE_ANON_KEY must be set');
}

// Public client — safe for general reads
export const supabase = createClient(url, anonKey, {
  auth: { persistSession: false },
});

// Admin client — server-side only, bypasses RLS
export const supabaseAdmin = serviceKey
  ? createClient(url, serviceKey, {
      auth: { persistSession: false, autoRefreshToken: false },
    })
  : null;

/**
 * Upload a screenshot buffer to Supabase Storage bucket 'comet-artifacts'
 * Returns the public URL, or null if upload fails / admin client unavailable
 */
export async function uploadScreenshot(
  jobId: string,
  buffer: Buffer
): Promise<string | null> {
  if (!supabaseAdmin) return null;

  const path = `screenshots/${jobId}-${Date.now()}.png`;

  const { error } = await supabaseAdmin.storage
    .from('comet-artifacts')
    .upload(path, buffer, { contentType: 'image/png', upsert: false });

  if (error) {
    console.error('Screenshot upload failed:', error.message);
    return null;
  }

  const { data } = supabaseAdmin.storage
    .from('comet-artifacts')
    .getPublicUrl(path);

  return data.publicUrl;
}
