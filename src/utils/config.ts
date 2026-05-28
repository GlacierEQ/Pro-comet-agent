/**
 * Central config — reads env vars with defaults and type coercion
 * Import from here instead of process.env directly throughout the app
 */

export const config = {
  port: parseInt(process.env.PORT ?? '8787', 10),
  nodeEnv: process.env.NODE_ENV ?? 'development',
  isProduction: process.env.NODE_ENV === 'production',

  auth: {
    jwtSecret: process.env.JWT_SECRET ?? 'change-me-in-production',
    jwtExpiresIn: process.env.JWT_EXPIRES_IN ?? '7d',
    bcryptRounds: parseInt(process.env.BCRYPT_SALT_ROUNDS ?? '12', 10),
  },

  db: {
    url: process.env.DATABASE_URL ?? '',
  },

  redis: {
    url: process.env.REDIS_URL ?? 'redis://localhost:6379',
  },

  browser: {
    provider: (process.env.BROWSER_PROVIDER ?? 'playwright') as 'playwright' | 'stagehand',
    headless: process.env.BROWSER_HEADLESS !== 'false',
    openaiKey: process.env.OPENAI_API_KEY ?? '',
    openaiModel: process.env.OPENAI_MODEL ?? 'gpt-4o',
  },

  mymap: {
    email: process.env.MYMAP_EMAIL ?? '',
    password: process.env.MYMAP_PASSWORD ?? '',
    baseUrl: process.env.MYMAP_BASE_URL ?? 'https://www.mymap.ai',
  },

  logging: {
    level: process.env.LOG_LEVEL ?? 'info',
  },
} as const;
