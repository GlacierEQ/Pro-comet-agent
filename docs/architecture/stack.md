# comet-agent — Stack Architecture

## Layer Map

```
┌──────────────────────────────────────────────────────────────────┐
│  VERCEL EDGE CONFIG    Feature flags — live updates, zero        │
│  ~1ms reads            redeploy. browserProvider, maxSessions,   │
│                        maintenanceMode, rateLimitRpm             │
└──────────────────────────────────────────────────────────────────┘
                  ↓ read on every request
┌──────────────────────────────────────────────────────────────────┐
│  RAILWAY (Docker)      Express server + Playwright engine        │
│  comet-agent:8787      Persistent container — Chromium cached    │
│                        in Docker layer, never reinstalled        │
└──────────────────────────────────────────────────────────────────┘
                  ↓ persist / stream
┌──────────────────────────────────────────────────────────────────┐
│  SUPABASE              PostgreSQL: jobs, sessions, artifacts     │
│  Postgres + Storage    Storage bucket: screenshots + exports     │
│  + Realtime            Realtime: live job status → clients       │
└──────────────────────────────────────────────────────────────────┘
```

## Why This Split

| Layer | Tool | Why |
|---|---|---|
| App server | Railway | Persistent Docker, Chromium cached, always-on |
| Database | Supabase Postgres | Free tier, Prisma-compatible, built-in Realtime |
| File storage | Supabase Storage | Screenshots, map exports, evidence files |
| Feature flags | Vercel Edge Config | ~1ms reads, live toggle, zero redeploy |
| CI | GitHub Actions (lite) | Lint + typecheck only, ~45s, no browser cost |

## Data Flow: MyMap Create Job

```
POST /workflows/mymap/create
  → getFlag('browserProvider') from Vercel Edge Config  (~1ms)
  → INSERT Job (status: PENDING) into Supabase
  → launch Playwright session (Chromium warm in container)
  → navigate mymap.ai → enter prompt → wait for render
  → screenshot() → uploadScreenshot() → Supabase Storage
  → UPDATE Job (status: SUCCESS, result: { mapUrl, shareLink, screenshotUrl })
  → Supabase Realtime pushes update to subscribed clients
  → return 200 { success: true, jobId, mapUrl, shareLink }
```

## Required Environment Variables (Railway)

| Variable | Source | Purpose |
|---|---|---|
| `DATABASE_URL` | Supabase pooler (port 6543) | Prisma runtime queries |
| `DIRECT_URL` | Supabase direct (port 5432) | Prisma migrations |
| `SUPABASE_URL` | Supabase project settings | Supabase JS client |
| `SUPABASE_ANON_KEY` | Supabase project settings | Public reads |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase project settings | Storage uploads (admin) |
| `EDGE_CONFIG` | Vercel dashboard | Feature flag connection string |
| `MYMAP_EMAIL` | Your credentials | MyMap login |
| `MYMAP_PASSWORD` | Your credentials | MyMap login |
| `JWT_SECRET` | Generate random | API auth |

## Setup Checklist

- [ ] Create Supabase project → copy `DATABASE_URL` (pooler) + `DIRECT_URL`
- [ ] Create storage bucket `comet-artifacts` (public read)
- [ ] Run `npx prisma migrate dev` to create tables
- [ ] Connect Railway to GitHub repo → add env vars
- [ ] Create Vercel project → add Edge Config store → link → copy `EDGE_CONFIG` string to Railway
- [ ] Push to `main` → Railway auto-deploys
