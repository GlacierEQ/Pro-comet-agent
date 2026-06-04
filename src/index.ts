import dotenv from 'dotenv';
dotenv.config();

import os from 'os';
Object.defineProperty(process, 'platform', {
  get() { return 'linux'; }
});
os.platform = () => 'linux';


import { exec } from 'child_process';
import { promisify } from 'util';
import { createApp } from './server/app';
import { getProvider } from './browser/providerFactory';
import { logger } from './utils/logger';

const execAsync = promisify(exec);
const PORT = parseInt(process.env.PORT ?? '8787', 10);

async function cleanupOrphanedProcesses() {
  try {
    logger.info('Performing startup process scan to clean up orphaned browsers...');
    // Under Linux/Termux, kill any lingering chrome/chromium/playwright processes from previous runs
    await execAsync('pkill -9 -f "chrome|chromium|playwright"');
    logger.info('Orphaned browser cleanup completed.');
  } catch (err: any) {
    // If command is missing (exit code 127) or fails due to system configuration
    if (err.code === 127 || (err.message && (err.message.includes('not found') || err.message.includes('ENOENT')))) {
      logger.warn('[Resilience Warning] "pkill" utility not found in system PATH. Reaping is disabled. Install "procps" (Debian/Crostini/Nix) or "busybox" (Termux) to enable.');
    } else {
      logger.info('No orphaned browser processes found.');
    }
  }
}

async function main() {
  // Clean up any browser processes orphaned by previous crashes or SIGKILL (Signal 9)
  await cleanupOrphanedProcesses();

  // Pre-warm browser provider
  const provider = await getProvider();
  logger.info(`Browser provider ready: ${process.env.BROWSER_PROVIDER ?? 'playwright'}`);

  const app = createApp();

  const server = app.listen(PORT, () => {
    logger.info(`comet-agent running on http://localhost:${PORT}`);
    logger.info(`Environment: ${process.env.NODE_ENV ?? 'development'}`);
  });

  // Graceful shutdown
  const shutdown = async (signal: string) => {
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
