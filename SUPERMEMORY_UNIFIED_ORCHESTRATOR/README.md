# Legacy CATACLYSM Supermemory Orchestrator — Retired

**Status:** fail-closed compatibility entry point  
**Canonical implementation:** `GlacierEQ/SUPERLUMINAL_CASE_MATRIX/CASEBRAIN_V3`  
**Case:** `1FDV-23-0001009`

## Retirement decision

The prior design is not deployment-ready and must not be activated. It embedded a live credential, exposed connector identifiers, described unsupported custody countdowns and actor-risk labels, auto-calculated legal deadlines without governing authority, and represented unverified integrations as operational.

`orchestrator.py` now performs no network requests, credential reads, memory writes, deadline calculations, monitoring, recommendations, notifications, filings, or other external actions. `status` and `health` return a truthful `RETIRED_FAIL_CLOSED` record; historical action commands exit nonzero without acting.

## Canonical CaseBrain V3 architecture

The unified system is implemented as an evidence-first control plane:

```text
Authorized connector record
    -> deterministic source envelope
    -> original preservation + provenance
    -> truth and sensitivity classification
    -> CaseBrain graph
    -> source-backed timeline and procedural-risk analysis
    -> human review queue
    -> compact continuity memory
```

### Timeline

Allowed timeline records include verified JEFS/docket timestamps, service events, official hearing/calendar changes, source acquisition, and deadlines supported by both a reviewed trigger and governing authority.

Predicted custody-restoration dates, victory dates, automatic sanction dates, speculative cascade phases, and estimated agency or judicial outcomes are not case events.

### Procedural Risk Monitor

Allowed conditions include missing originals, inconsistent docket/minutes/order/service records, hash mismatch, chain-of-custody gaps, stale connector state, reviewed deadlines, and workflow failures.

Private person-location monitoring and unsupported fraud, retaliation, conspiracy, corruption, criminal, or threat scores are prohibited. A source timing pattern alone does not prove intent or tampering.

### Decision engine

The engine may classify records, identify source gaps and contradictions, propose preservation/research/review, and prepare internal drafts. It may not automatically file, serve, publish, accuse, contact an agency, number an operative exhibit, send a demand, or release restricted material.

Each recommendation requires source IDs, rationale, blockers, risk flags, assumptions, approval state, and an audit requirement. External action remains disabled until Casey approves an exact artifact and action.

## Supermemory continuity

Canonical project/container: `sm_project_unified_case_brain`.

Store only compact reviewed continuity such as architecture decisions, validated case identity, source-backed event summaries, contradiction IDs/status, and workflow state. Keep raw evidence and authoritative documents in their source systems.

Never store credentials, token-bearing URLs, protected child/medical/financial records, private addresses, unreviewed bulk documents, unsupported accusations stated as fact, or predicted outcomes.

## Credential incident

The credential formerly committed here must be treated as compromised. Redacting current files does not erase Git history, deleted-line diffs, caches, logs, notifications, or third-party indexes.

Required containment:

1. revoke and rotate the exposed Supermemory credential;
2. review provider access logs from the exposure time forward;
3. search branches, tags, releases, pull requests, issues, Actions logs, and artifacts;
4. rotate any reused or derivative credential;
5. store replacements only in a secret manager or protected environment;
6. never copy a replacement into source, documentation, memory, notifications, or court materials.

## Current operational boundary

The canonical V3 implementation remains in review. Current verified live state includes JEFS notice metadata for Dkts. 217, 219, 221, and 223. Underlying documents remain necessary for content-level legal conclusions. Current calculated legal deadlines: **none**. Current authorized external actions: **none**.
