import dotenv from 'dotenv';
dotenv.config();

import { createApp } from './server/app';
import { getProvider } from './browser/providerFactory';
import { logger } from './utils/logger';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);
const PORT = parseInt(process.env.PORT ?? '8787', 10);

/**
 * Only clean up orphaned Playwright/Chromium processes when NOT using CometProvider.
 * When BROWSER_PROVIDER=comet, Comet is already running — we must never kill it.
 */
async function cleanupOrphanedProcesses(): Promise<void> {
  const provider = (process.env.BROWSER_PROVIDER ?? 'playwright').toLowerCase().trim();
  if (provider === 'comet') {
    logger.info('[Startup] CometProvider mode — skipping orphan browser cleanup to preserve running Comet instance.');
    return;
  }

  try {
    logger.info('Performing startup process scan to clean up orphaned browsers...');
    await execAsync('pkill -9 -f "chrome|chromium|playwright"');
    logger.info('Orphaned browser cleanup completed.');
  } catch (err: any) {
    if (err.code === 127 || (err.message && (err.message.includes('not found') || err.message.includes('ENOENT')))) {
      logger.warn('[Resilience Warning] "pkill" utility not found in system PATH. Reaping is disabled. Install "procps" (Debian/Crostini/Nix) or "busybox" (Termux) to enable.');
    } else {
      logger.info('No orphaned browser processes found.');
    }
  }
}

async function main(): Promise<void> {
  await cleanupOrphanedProcesses();

  const provider = await getProvider();
  const providerName = (process.env.BROWSER_PROVIDER ?? 'playwright').toLowerCase().trim();
  logger.info(`Browser provider ready: ${providerName}`);

  const app = createApp();

  const server = app.listen(PORT, () => {
    logger.info(`comet-agent running on http://localhost:${PORT}`);
    logger.info(`Environment: ${process.env.NODE_ENV ?? 'development'}`);
  });

  const shutdown = async (signal: string): Promise<void> => {
    logger.info(`${signal} received — shutting down`);
    server.close(async () => {
      await provider.closeAll();
      logger.info('All browser sessions closed. Goodbye.');
      process.exit(0);
    });
  };

  process.on('SIGTERM', () => shutdown('SIGTERM'));
  process.on('SIGINT', () => shutdown('SIGINT'));
}

main().catch((err) => {
  console.error('Fatal startup error:', err);
  process.exit(1);
});
