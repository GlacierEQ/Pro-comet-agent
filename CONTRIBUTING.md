# Contributing to Pro-comet-agent

Thank you for your interest in contributing. This project uses an **open-core model** — the framework is open, the sovereign config layer is proprietary.

---

## What You Can Contribute

✅ **Welcome contributions:**
- Bug fixes to framework logic (browser engines, API routes, job queue)
- Documentation improvements
- New workflow module integrations (not requiring private credentials)
- Test coverage improvements
- Performance improvements to the orchestration layer

❌ **Not accepted:**
- Changes to the core methodology defined in `MASTERMIND.md`
- Modifications to the memory architecture contracts
- Changes that require access to private operator configs

---

## Development Setup

```bash
git clone https://github.com/GlacierEQ/Pro-comet-agent
cd Pro-comet-agent
cp .env.example .env
# Fill in your own credentials — never commit real values
npm install
npx playwright install chromium
npm run dev
```

---

## Pre-Commit Requirements

All contributions must pass the full QA manifest before merge. See `QUALITY_ASSURANCE_MANIFEST.md`.

```bash
npm run lint    # zero errors required
npm run test    # all tests must pass
npm run build   # must compile clean
```

---

## Code Style

This project follows the **Super Pro Humanized Code Engineering** methodology. See `MASTERMIND.md` for the full doctrine.

**Quick rules:**
- Functions named as `verb + noun`
- Error messages written for humans, not log parsers
- Every external call has a timeout and retry
- No silent failures — ever

---

## Commercial Use

This project is licensed under the **Business Source License 1.1**. Free for non-commercial use and study. Commercial deployment requires a license from GlacierEQ.

Contact: GLACIER.EQUILIBRIUM@GMAIL.COM

---

## Authorship

Core methodology and architecture by Casey (GlacierEQ). See `PRIOR-ART.md` for the formal IP disclosure.
