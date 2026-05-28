/**
 * In-memory job store
 * Tracks async browser automation tasks with status + result
 * For production: back this with Redis or Prisma
 */

import { v4 as uuidv4 } from 'uuid';

export type JobStatus = 'pending' | 'running' | 'success' | 'error';

export interface Job {
  id: string;
  type: string;
  status: JobStatus;
  input: unknown;
  result?: unknown;
  error?: string;
  createdAt: Date;
  updatedAt: Date;
}

class JobStore {
  private jobs: Map<string, Job> = new Map();

  create(type: string, input: unknown): Job {
    const job: Job = {
      id: uuidv4(),
      type,
      status: 'pending',
      input,
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    this.jobs.set(job.id, job);
    return job;
  }

  update(id: string, patch: Partial<Pick<Job, 'status' | 'result' | 'error'>>): void {
    const job = this.jobs.get(id);
    if (!job) return;
    Object.assign(job, patch, { updatedAt: new Date() });
  }

  get(id: string): Job | undefined {
    return this.jobs.get(id);
  }

  list(): Job[] {
    return Array.from(this.jobs.values()).sort(
      (a, b) => b.createdAt.getTime() - a.createdAt.getTime()
    );
  }
}

export const jobStore = new JobStore();
