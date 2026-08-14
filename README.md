# Pro-Comet Agent

**Browser-automation server plus a fail-closed connector-adapter runtime.**

Pro-Comet Agent is a public diligence project that demonstrates two bounded systems:

1. a TypeScript browser-automation service with explicit provider interfaces; and
2. a Python connector orchestration layer that requires adapters to be registered explicitly instead of pretending external services are connected.

## Implemented surfaces

### TypeScript browser runtime

The TypeScript application includes:

- request contracts in `src/contracts/browser.schema.ts`;
- provider selection in `src/browser/providerFactory.ts`;
- provider implementations for Playwright, Comet/CDP, and Stagehand under `src/providers/`;
- Express routes and server composition under `src/server/`;
- a Prisma schema for structured persistence in `prisma/schema.prisma`.

Hosted CI installs the locked Node dependency graph, runs the repository's Jest suite, and compiles the TypeScript server with `tsc`.

### Explicit connector-adapter runtime

`modules/universal_tools_framework.py` provides an asynchronous adapter contract, lazy connection reuse, fail-closed handling for unavailable connectors, per-tool health metrics, source-preserving result merging, and JSON/CSV/XML parsing.

The generic runtime **does not bundle or claim live access** to Google Drive, Dropbox, Gmail, GitHub, OneDrive, or any other SaaS provider. A concrete adapter must be registered by the caller before an external operation can occur. Missing connectors and unsupported operations fail explicitly.

The Python behavior suite verifies connector registration boundaries, reuse, cleanup, source preservation, unsupported-operation handling, parsing, and deduplication.

## What this repository does not establish

- No live MCP, APEX, Mastermind, or provider-mesh integration is claimed.
- No bundled credentials, proprietary provider access, or universal SaaS connectivity is claimed.
- A successful TypeScript build does not prove a production browser deployment, external CDP endpoint, Browserbase account, or live Stagehand session.
- The Prisma schema does not by itself establish a migrated or production database.
- No production reliability, throughput, latency, security certification, or autonomous operational authority is claimed.

## Verification

The repository-owned CI runs Python behavior proof and the TypeScript test/build path. The same bounded checks can be reproduced locally:

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/verify_public_truth.py
npm ci
npm test -- --runInBand
npm run build
```

Browser-provider execution that depends on external services or a local browser is intentionally outside this deterministic proof unless the required runtime is explicitly supplied.

## Repository identity

This repository is `GlacierEQ/Pro-comet-agent`. Its package metadata, public documentation, and machine-readable capability surface are expected to describe that repository only. The governing license is the GlacierEQ Proprietary License in [`LICENSE`](./LICENSE); public visibility is for inspection and diligence, not an open-source grant.
