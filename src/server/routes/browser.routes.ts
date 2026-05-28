import { Router, Request, Response } from 'express';
import { getProvider } from '../../browser/providerFactory';
import {
  NavigateRequestSchema,
  ActRequestSchema,
  ExtractRequestSchema,
  LaunchSessionRequestSchema,
} from '../../contracts/browser.schema';
import { logger } from '../../utils/logger';

export const browserRouter = Router();

// POST /browser/session — launch a new browser session
browserRouter.post('/session', async (req: Request, res: Response) => {
  try {
    const body = LaunchSessionRequestSchema.parse(req.body);
    const provider = await getProvider();
    const session = await provider.launch(body.sessionId);
    res.json({ success: true, session });
  } catch (err: any) {
    logger.error('launch session error', err);
    res.status(400).json({ error: err.message });
  }
});

// POST /browser/navigate
browserRouter.post('/navigate', async (req: Request, res: Response) => {
  try {
    const body = NavigateRequestSchema.parse(req.body);
    const provider = await getProvider();
    await provider.navigate(body.sessionId, body.url, {
      waitUntil: body.waitUntil,
      timeout: body.timeout,
    });
    const url = await provider.currentUrl(body.sessionId);
    res.json({ success: true, url });
  } catch (err: any) {
    logger.error('navigate error', err);
    res.status(400).json({ error: err.message });
  }
});

// POST /browser/act
browserRouter.post('/act', async (req: Request, res: Response) => {
  try {
    const body = ActRequestSchema.parse(req.body);
    const provider = await getProvider();
    await provider.act(body.sessionId, {
      selector: body.selector,
      instruction: body.instruction,
      value: body.value,
      timeout: body.timeout,
    });
    res.json({ success: true });
  } catch (err: any) {
    logger.error('act error', err);
    res.status(400).json({ error: err.message });
  }
});

// POST /browser/extract
browserRouter.post('/extract', async (req: Request, res: Response) => {
  try {
    const body = ExtractRequestSchema.parse(req.body);
    const provider = await getProvider();
    const data = await provider.extract(body.sessionId, {
      selector: body.selector,
      instruction: body.instruction,
      schema: body.schema,
    });
    res.json({ success: true, data });
  } catch (err: any) {
    logger.error('extract error', err);
    res.status(400).json({ error: err.message });
  }
});

// POST /browser/screenshot
browserRouter.post('/screenshot', async (req: Request, res: Response) => {
  try {
    const { sessionId, fullPage } = req.body;
    if (!sessionId) return res.status(400).json({ error: 'sessionId required' });
    const provider = await getProvider();
    const buffer = await provider.screenshot(sessionId, { fullPage: fullPage ?? false });
    res.set('Content-Type', 'image/png');
    res.send(buffer);
  } catch (err: any) {
    logger.error('screenshot error', err);
    res.status(400).json({ error: err.message });
  }
});

// DELETE /browser/session/:sessionId
browserRouter.delete('/session/:sessionId', async (req: Request, res: Response) => {
  try {
    const provider = await getProvider();
    await provider.close(req.params.sessionId);
    res.json({ success: true, closed: req.params.sessionId });
  } catch (err: any) {
    logger.error('close session error', err);
    res.status(400).json({ error: err.message });
  }
});
