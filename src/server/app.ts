import express, { Express, Request, Response, NextFunction } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import { browserRouter } from './routes/browser.routes';
import { workflowRouter } from './routes/workflow.routes';
import { jobRouter } from './routes/job.routes';
import { logger } from '../utils/logger';

export function createApp(): Express {
  const app = express();

  // Security & logging middleware
  app.use(helmet());
  app.use(cors());
  app.use(morgan('combined', { stream: { write: (msg) => logger.http(msg.trim()) } }));
  app.use(express.json({ limit: '10mb' }));
  app.use(express.urlencoded({ extended: true }));

  // Health check
  app.get('/health', (_req: Request, res: Response) => {
    res.json({
      status: 'ok',
      version: process.env.npm_package_version ?? '2.0.0',
      provider: process.env.BROWSER_PROVIDER ?? 'playwright',
      uptime: process.uptime(),
      timestamp: new Date().toISOString(),
    });
  });

  // Routes
  app.use('/browser', browserRouter);
  app.use('/workflows', workflowRouter);
  app.use('/jobs', jobRouter);

  // 404 handler
  app.use((_req: Request, res: Response) => {
    res.status(404).json({ error: 'Not found' });
  });

  // Global error handler
  app.use((err: Error, _req: Request, res: Response, _next: NextFunction) => {
    logger.error('Unhandled error:', err);
    res.status(500).json({
      error: 'Internal server error',
      message: process.env.NODE_ENV === 'development' ? err.message : undefined,
    });
  });

  return app;
}
