import { Router, Request, Response } from 'express';
import { jobStore } from '../../jobs/jobStore';

export const jobRouter = Router();

// GET /jobs — list all jobs
jobRouter.get('/', (_req: Request, res: Response) => {
  res.json({ jobs: jobStore.list() });
});

// GET /jobs/:id — get single job
jobRouter.get('/:id', (req: Request, res: Response) => {
  const job = jobStore.get(req.params.id);
  if (!job) return res.status(404).json({ error: 'Job not found' });
  res.json({ job });
});
