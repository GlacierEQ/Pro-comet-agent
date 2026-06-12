# 📱 Pro-comet-agent — Browser Automation Server
> **[pro-tier] browser-automation** — Node/TypeScript browser automation server and Stagehand adapter | GlacierEQ APEX

[![Node](https://img.shields.io/badge/node-%3E%3D18-brightgreen)](https://nodejs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2-blue)](https://www.typescriptlang.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🧠 Description
`Pro-comet-agent` exposes a structured, typed REST API for programmatically controlling web browser instances. It serves as the core automation controller for GlacierEQ APEX, providing natural-language agent execution and canvas-based workflows.

---

## ⚡ Core Capabilities
*   **Dynamic Actions:** Open, navigate, click, and input actions across pages via JSON payloads.
*   **Stagehand Integration:** Run deterministic Playwright calls or use Stagehand's LLM engine for resilient, natural-language actions.
*   **Workflow Adapters:** Built-in workflow modules for Notion database extraction, GitHub repository management, and MyMap canvas navigation.
*   **Job Lifecycles:** Asynchronous job execution and queue management backed by Prisma (PostgreSQL) and Redis.

---

## 📂 Project Structure
```
src/
├── index.ts                  # Server entry point
├── server/                   # Express application, routes, and middleware
├── browser/                  # Browser launch lifecycle and SessionManager
├── providers/
│   ├── playwright/           # Deterministic Playwright driver
│   └── stagehand/            # Natural-language Stagehand driver
├── workflows/
│   ├── mymap/                # MyMap automated canvas actions
│   ├── github/               # GitHub browser automation
│   └── notion/               # Notion data capture scripts
├── tools/                    # Reusable page actions (screenshots, raw extraction)
├── contracts/                # Zod request/response validation schemas
├── jobs/                     # Background job queue and state
└── utils/                    # Structured logging and configurations
```

---

## 🚀 Quick Start
To launch the server locally:
```bash
git clone https://github.com/GlacierEQ/Pro-comet-agent.git
cd Pro-comet-agent
cp .env.example .env
npm install
npx playwright install chromium
npm run dev
```
The Express API runs at `http://localhost:8787` by default.

---

## ⚙️ Standard Scripts
*   `npm run dev` — Launch tsx-monitored hot-reload server.
*   `npm run build` — Compile TypeScript source to `dist/`.
*   `npm run start` — Run compiled production build.
*   `npm run test` — Execute Jest unit tests.
*   `npm run lint` — Audit syntax and style via ESLint.

---

### Verification & Custody
> **Status:** `[VERIFIED]`  
> *GlacierEQ APEX | Operator: Casey Barton | Honolulu, HI*
