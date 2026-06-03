import { Router, Request, Response } from 'express';
import { CreateMapRequestSchema } from '../../contracts/browser.schema';
import {
  createMapFromPrompt,
  getShareLink,
} from '../../workflows/mymap/mymapWorkflow';
import { logger } from '../../utils/logger';

export const workflowRouter = Router();

/**
 * POST /workflows/mymap/create
 * Body: { prompt: string, sessionId?: string, waitMs?: number }
 * Creates a new MyMap canvas from a prompt
 */
workflowRouter.post('/mymap/create', async (req: Request, res: Response) => {
  try {
    const body = CreateMapRequestSchema.parse(req.body);
    logger.info(`MyMap create workflow started: "${body.prompt.slice(0, 80)}..."`);
    const result = await createMapFromPrompt({
      prompt: body.prompt,
      sessionId: body.sessionId,
      waitMs: body.waitMs,
    });
    res.json({
      success: true,
      sessionId: result.sessionId,
      mapUrl: result.mapUrl,
      shareLink: result.shareLink ?? null,
    });
  } catch (err: any) {
    logger.error('mymap/create error', err);
    res.status(500).json({ error: err.message });
  }
});

/**
 * GET /workflows/mymap/share
 * Query: { sessionId, mapUrl }
 * Returns the public share link for an existing map
 */
workflowRouter.get('/mymap/share', async (req: Request, res: Response) => {
  try {
    const { sessionId, mapUrl } = req.query as { sessionId: string; mapUrl: string };
    if (!sessionId || !mapUrl) {
      res.status(400).json({ error: 'sessionId and mapUrl required' });
      return;
    }
    const shareLink = await getShareLink(sessionId, mapUrl);
    res.json({ success: true, shareLink });
  } catch (err: any) {
    logger.error('mymap/share error', err);
    res.status(500).json({ error: err.message });
  }
});
