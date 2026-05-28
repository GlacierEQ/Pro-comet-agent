/**
 * Browser API contracts — Zod schemas
 * Single source of truth for request/response validation
 * Note: Joi has been removed in favour of Zod for TypeScript-native inference
 */

import { z } from 'zod';

export const NavigateRequestSchema = z.object({
  sessionId: z.string().min(1),
  url: z.string().url(),
  waitUntil: z.enum(['load', 'domcontentloaded', 'networkidle']).optional(),
  timeout: z.number().int().positive().optional(),
});

export const ActRequestSchema = z.object({
  sessionId: z.string().min(1),
  selector: z.string().optional(),
  instruction: z.string().optional(),
  value: z.string().optional(),
  timeout: z.number().int().positive().optional(),
});

export const ExtractRequestSchema = z.object({
  sessionId: z.string().min(1),
  selector: z.string().optional(),
  instruction: z.string().optional(),
  schema: z.record(z.unknown()).optional(),
});

export const CreateMapRequestSchema = z.object({
  prompt: z.string().min(1).max(4000),
  sessionId: z.string().optional(),
  waitMs: z.number().int().positive().optional(),
});

export const LaunchSessionRequestSchema = z.object({
  sessionId: z.string().optional(),
});

export type NavigateRequest = z.infer<typeof NavigateRequestSchema>;
export type ActRequest = z.infer<typeof ActRequestSchema>;
export type ExtractRequest = z.infer<typeof ExtractRequestSchema>;
export type CreateMapRequest = z.infer<typeof CreateMapRequestSchema>;
export type LaunchSessionRequest = z.infer<typeof LaunchSessionRequestSchema>;
