#!/usr/bin/env python3
"""Fail-closed tombstone for the retired CATACLYSM/Supermemory orchestrator.

The former script embedded a live credential, exposed connector identifiers,
claimed unverified deployment readiness, and described autonomous legal and
actor-risk workflows without source or approval controls. It is disabled.

Canonical implementation:
    GlacierEQ/SUPERLUMINAL_CASE_MATRIX/CASEBRAIN_V3

This file makes no network request, reads no credential value, creates no
memory, computes no deadline, monitors no person, and performs no external
legal or notification action.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Final

CASE_ID: Final = "1FDV-23-0001009"
CANONICAL_REPOSITORY: Final = "GlacierEQ/SUPERLUMINAL_CASE_MATRIX"
CANONICAL_PATH: Final = "CASEBRAIN_V3"
CANONICAL_MEMORY_PROJECT: Final = "sm_project_unified_case_brain"

RETIRED_COMMANDS: Final = {
    "activate",
    "deploy",
    "monitor",
    "sync",
    "deadline",
    "threat",
    "recommend",
    "briefing",
}


@dataclass(frozen=True, slots=True)
class RetirementStatus:
    status: str
    service: str
    case_id: str
    canonical_repository: str
    canonical_path: str
    memory_project: str
    network_enabled: bool
    memory_writes_enabled: bool
    external_actions_enabled: bool
    calculated_legal_deadlines: int
    actor_monitoring_enabled: bool
    credential_rotation_required: bool
    reason: str
    generated_at: str


def get_status() -> RetirementStatus:
    """Return a truthful status without touching any connector or secret."""

    return RetirementStatus(
        status="RETIRED_FAIL_CLOSED",
        service="Legacy CATACLYSM Supermemory orchestrator tombstone",
        case_id=CASE_ID,
        canonical_repository=CANONICAL_REPOSITORY,
        canonical_path=CANONICAL_PATH,
        memory_project=CANONICAL_MEMORY_PROJECT,
        network_enabled=False,
        memory_writes_enabled=False,
        external_actions_enabled=False,
        calculated_legal_deadlines=0,
        actor_monitoring_enabled=False,
        credential_rotation_required=True,
        reason=(
            "Duplicate unsafe design retired. Use CaseBrain V3 source envelopes, "
            "truth/sensitivity classification, procedural-risk conditions, and "
            "human approval gates."
        ),
        generated_at=datetime.now(UTC).isoformat(),
    )


def deprecated_environment_warning() -> list[str]:
    """Detect deprecated variable names without reading or printing values."""

    names = (
        "SUPERMEMORY_API_KEY",
        "SUPERMEMORY_KEY",
        "TASKLET_WEBHOOK_URL",
        "WEBHOOK_URL",
        "WEBHOOK_TOKEN",
    )
    if not any(name in os.environ for name in names):
        return []
    return [
        "Deprecated credential variables are configured for this retired entry "
        "point. Their values were not read, logged, or transmitted.",
        "Rotate previously exposed credentials and configure replacements only "
        "inside the canonical CaseBrain V3 deployment environment.",
    ]


def render_status() -> dict[str, object]:
    payload: dict[str, object] = asdict(get_status())
    payload["warnings"] = deprecated_environment_warning()
    return payload


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    command = args[0].lower() if args else "status"
    print(json.dumps(render_status(), indent=2, sort_keys=True))

    if command in {"status", "health", "--status", "--health"}:
        return 0

    if command in RETIRED_COMMANDS:
        print(f"Command {command!r} is retired. No action was performed.", file=sys.stderr)
        return 2

    print(f"Unknown or retired command {command!r}. No action was performed.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
