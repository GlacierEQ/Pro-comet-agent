import 'dotenv/config';
import { createApp } from './server/app';
import { getProvider } from './browser/providerFactory';
import { logger } from './utils/logger';

const PORT = parseInt(process.env.PORT ?? '8787', 10);

async function main() {
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
