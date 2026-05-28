# comet-agent

> **Node/TypeScript browser automation server** — Express API + Playwright engine + optional Stagehand adapter + MyMap workflow module

[![Node](https://img.shields.io/badge/node-%3E%3D18-brightgreen)](https://nodejs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2-blue)](https://www.typescriptlang.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## What it is

Comet Agent is a browser automation service that exposes a typed REST API for controlling web browsers programmatically. It is the automation backbone for the GlacierEQ APEX ecosystem, with first-class support for MyMap canvas workflows.

**Core capabilities:**
- Open, navigate, interact with any web page via REST calls
- Submit prompts and interact with AI canvas tools (e.g. MyMap)
- Extract structured data from dynamic pages
- Run Playwright deterministically or Stagehand with natural-language resilience
- Persist sessions, jobs, and results via Prisma + Redis

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Express REST API                   │
│          /browser  /workflows  /tools  /jobs         │
├─────────────────────────────────────────────────────┤
│              BrowserProvider Interface               │
│        (swap engines without changing API)           │
├───────────────────┬─────────────────────────────────┤
│  Playwright Engine│     Stagehand Adapter (NL)       │
│  (deterministic)  │     (resilient / agent-style)    │
├───────────────────┴─────────────────────────────────┤
│              Workflow Modules                        │
│   mymap/  │  github/  │  notion/  │  browser-utils/ │
├─────────────────────────────────────────────────────┤
│         Prisma (Postgres) + Redis + Winston          │
└─────────────────────────────────────────────────────┘
```

---

## Quick start

```bash
git clone https://github.com/GlacierEQ/comet-agent
cd comet-agent
cp .env.example .env
# fill in .env values
npm install
npx playwright install chromium
npm run dev
```

Server starts on **port 8787** by default.

---

## Environment

See [`.env.example`](.env.example) for all required variables.

Key vars:
| Variable | Description |
|---|---|
| `PORT` | Server port (default 8787) |
| `NODE_ENV` | `development` or `production` |
| `JWT_SECRET` | Secret for JWT signing |
| `DATABASE_URL` | Postgres connection string |
| `REDIS_URL` | Redis connection string |
| `BROWSER_PROVIDER` | `playwright` (default) or `stagehand` |
| `OPENAI_API_KEY` | Required only for Stagehand NL mode |
| `MYMAP_EMAIL` | MyMap login email |
| `MYMAP_PASSWORD` | MyMap login password |

---

## API endpoints

```
POST /workflows/mymap/create   — Create a new MyMap from a prompt
POST /workflows/mymap/insert   — Insert Mermaid/content into existing map
GET  /workflows/mymap/share    — Get share link for a map

POST /browser/navigate         — Navigate to URL
POST /browser/act              — Perform an action on the page
POST /browser/extract          — Extract structured data
POST /browser/screenshot       — Take a screenshot

GET  /jobs                     — List all jobs
GET  /jobs/:id                 — Get job status and result
```

---

## Scripts

```bash
npm run dev            # tsx watch mode
npm run build          # compile TypeScript
npm run start          # run compiled dist/
npm run test           # jest
npm run lint           # eslint
npm run format         # prettier
npm run docker:build   # build Docker image
npm run docker:run     # run on port 8787
```

---

## Project structure

```
src/
├── index.ts                  # Entry point
├── server/                   # Express app, middleware, routes
├── browser/
│   ├── BrowserProvider.ts    # Interface — swap engines without changing app code
│   └── SessionManager.ts     # Lifecycle: launch, reuse, close
├── providers/
│   ├── playwright/           # Deterministic Playwright engine
│   └── stagehand/            # NL-driven Stagehand adapter
├── workflows/
│   ├── mymap/                # MyMap automation tasks
│   ├── github/               # GitHub browser tasks
│   └── notion/               # Notion browser tasks
├── tools/                    # Reusable tool modules (screenshot, extract, etc.)
├── contracts/                # Zod schemas and typed request/response models
├── jobs/                     # Job queue, status tracking
└── utils/                    # Logger, config, helpers
docs/
└── architecture/             # System diagrams and specs
```

---

## License

MIT — GlacierEQ
