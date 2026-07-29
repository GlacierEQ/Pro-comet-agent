# Pro-Comet Agent — Advanced Comet Agent & Prisma Data Stack 💫

> **TypeScript full-stack browser agent with Prisma ORM database models and Python harness.**

[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6)]()
[![Prisma](https://img.shields.io/badge/Prisma-ORM-2D3748)]()
[![Python](https://img.shields.io/badge/Python-3.9+-blue)]()
[![Domain](https://img.shields.io/badge/Domain-Browser%20Agent-blue)]()

---

## 🎯 For Recruiters & Hiring Managers

This repository implements **Pro-Comet Agent** — an advanced web automation agent backed by Prisma ORM for structured action history and session persistence. It demonstrates:

- **Prisma ORM schema modeling** storing web interactions, DOM selectors, and session snapshots
- **TypeScript agent controller** managing browser contexts and CDP message pipelines
- **Shell automation scripts** managing database migration and agent container lifecycle
- **Python simulation test harness** verifying end-to-end agent action flows

**Why this matters**: Enterprise browser agents require relational persistence to audit actions, retry failed steps, and analyze user session histories.

---

## 🔬 For Engineers & Technical Reviewers

### Core Components

| Component | Language | Purpose |
|---|---|---|
| `prisma/schema.prisma` | Prisma | Relational model for agent sessions and action logs |
| `src/agent.ts` | TypeScript | Core agent controller and DOM action dispatcher |
| `tests/` | Python | Test wrapper validating agent execution |

---

## 🤖 ML/AI & Programmatic Mesh Integration

- **MCP Tool**: `run_comet_agent()` — browser automation tool for swarm agents
- **Mastermind Sidecar**: Connected to APEX Highway mesh
- **SHA-256 Integrity**: Tracked in `.integrity/file_hashes.json`

---

## ⚡ Quick Start

```bash
python3 tests/test_comet_agent.py
```
