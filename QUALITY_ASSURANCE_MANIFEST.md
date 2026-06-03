# Quality Assurance Manifest — comet-agent

## Test coverage targets

| Layer | Target | Method |
|---|---|---|
| Contracts (Zod schemas) | 100% | Unit tests — invalid and valid inputs |
| BrowserProvider interface | 100% | Mock provider in Jest |
| PlaywrightProvider | 80% | Integration tests with real browser |
| MyMap workflow | 70% | E2E against live MyMap (requires creds) |
| REST API routes | 90% | supertest |

---

## Critical paths to test

- [ ] `createMapFromPrompt` happy path end to end
- [ ] `loginToMyMap` with valid and invalid credentials
- [ ] `getShareLink` returns a valid share URL
- [ ] Provider factory returns correct engine from env var
- [ ] Zod schema validation rejects malformed requests
- [ ] Session not found throws correctly
- [ ] Docker container starts and responds on port 8787

---

## Pre-commit checklist

- [ ] `npm run lint` passes with zero errors
- [ ] `npm run test` passes
- [ ] `npm run build` compiles without errors
- [ ] No secrets in committed files (env vars only in `.env`, never committed)
- [ ] `.env.example` updated if new vars added

---

## Known issues tracker

| # | Issue | Priority | Status |
|---|---|---|---|
| 1 | src/ directory not committed — source missing from main | HIGH | Fixed |
| 2 | Joi still in dependencies — replace with Zod only | MEDIUM | Fixed |
| 3 | Puppeteer still in dependencies — replace with Playwright | HIGH | Fixed |
| 4 | README was empty 132 bytes | HIGH | Fixed |
| 5 | No .env.example existed | HIGH | Fixed |
