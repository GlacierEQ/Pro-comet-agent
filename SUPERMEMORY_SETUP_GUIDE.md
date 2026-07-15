# CaseBrain V3 — Supermemory Deployment Contract

**Canonical implementation:** `GlacierEQ/SUPERLUMINAL_CASE_MATRIX/CASEBRAIN_V3`  
**Canonical continuity project/container:** `sm_project_unified_case_brain`  
**Default mode:** dry-run, no memory writes, no external actions

## Security prerequisite

A Supermemory credential was previously committed in this repository and must be treated as compromised. Do not use any value recovered from Git history, a pull-request diff, documentation, chat, logs, or an older deployment.

Before enabling memory writes:

1. revoke and rotate the exposed credential at the provider;
2. review provider access logs from the exposure time forward;
3. search all branches, tags, releases, issues, pull requests, workflow logs, and artifacts;
4. store the replacement only in a protected environment or secret manager;
5. use a project-scoped credential where available;
6. keep credential values out of source, documentation, memory content, notifications, and court materials.

## Supported Supermemory contract

The current CaseBrain adapter uses:

- `POST /v3/documents` for reviewed compact continuity;
- `POST /v4/search` for scoped hybrid retrieval;
- singular `containerTag` for project isolation;
- deterministic `customId` derived from the source idempotency key.

Do not revive the former memory-space or `/memories` examples. They are retired.

## Runtime posture

Use protected environment variables. Never paste values into this guide.

```text
CASEBRAIN_API_TOKEN=<protected internal API token>
SUPERMEMORY_API_KEY=<rotated project-scoped credential>
SUPERMEMORY_API_BASE_URL=https://api.supermemory.ai
CASEBRAIN_DRY_RUN=true
CASEBRAIN_MEMORY_WRITES=false
CASEBRAIN_EXTERNAL_ACTIONS=false
```

Memory writes may be enabled only after credential rotation, schema validation, fixed-source staging replay, and review of the exact continuity payload.

`CASEBRAIN_EXTERNAL_ACTIONS` must remain `false` in the compatibility service.

## What may enter continuity memory

Eligible records must be:

- explicitly reviewed;
- source-backed;
- labeled with a truth class;
- `PUBLIC` or `CASE_INTERNAL` sensitivity;
- linked to a stable source locator and source-record ID;
- compact enough to preserve continuity without duplicating the evidence archive.

Examples:

- architecture decisions;
- validated case identity;
- JEFS notice metadata within its stated scope;
- reviewed timeline event summaries;
- contradiction IDs and resolution status;
- internal task/recommendation state.

## What must not enter continuity memory

- API keys, webhook tokens, passwords, session cookies, or secret-bearing URLs;
- full child, medical, school, financial, device, or credential records;
- raw evidence archives or unreviewed document bodies;
- private addresses or personal-location monitoring;
- unsupported fraud, retaliation, conspiracy, corruption, criminal, or threat labels stated as fact;
- predicted custody-restoration, victory, sanction, agency, or judicial outcomes;
- deadlines without a verified trigger and governing authority;
- AI, task-system, Notion, or memory summaries represented as evidence.

## Timeline and deadline activation

A legal deadline is eligible only when the record includes:

1. verified triggering source and timestamp;
2. service method where material;
3. governing rule, order, or statute;
4. authority source locator;
5. timezone and counting convention;
6. weekend and holiday treatment;
7. computed date;
8. reviewer and review timestamp;
9. uncertainty or dispute flags.

Until then, the system must output `UNVERIFIED_DEADLINE` and create a source/rule review task. It must not generate a calendar event from an estimate.

## Procedural-risk monitoring

Allowed:

- official JEFS and docket changes;
- official hearing/calendar changes;
- notice/service gaps;
- record conflicts;
- missing originals;
- hash mismatch and chain-of-custody gaps;
- connector, notification, CI, and memory-sync failures.

Prohibited:

- private judge or person movement tracking;
- automatic accusation generation;
- treating timestamp patterns as proof of tampering or intent;
- actor threat scores;
- automatic filing, service, publication, agency contact, or demand delivery.

## Fixed-source staging replay

Initial replay set:

- JEFS notice metadata for Dkts. 217, 219, 221, and 223.

Expected results:

- accepted source envelopes: 4;
- unique source-record IDs: 4;
- duplicate records on a second replay: 0;
- reviewable recommendations: 2;
- calculated legal deadlines: 0;
- external actions: 0;
- restricted notification payloads: 0.

## Current status

The former “ready to activate” and “fully autonomous” statements were not supported by deployment logs, health checks, source-backed output, or reviewed authority. Current status is **implementation and security review in progress**. The V3 pull request, schemas, live-state records, and audit outputs are the source of truth.
