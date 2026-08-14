#!/usr/bin/env python3
"""Fail-closed public truth checks for the Pro-comet diligence surface."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"PUBLIC_TRUTH_FAIL: {message}")


def main() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    caps = json.loads((ROOT / "machine/capabilities.json").read_text(encoding="utf-8"))
    state = json.loads((ROOT / "machine/excellence-state.json").read_text(encoding="utf-8"))

    forbidden = (
        "MCP Tool: `run_comet_agent()`",
        "Connected to APEX Highway mesh",
        "src/agent.ts",
        '"hyper-scaling"',
    )
    for phrase in forbidden:
        require(phrase not in readme, f"README contains stale claim/path: {phrase}")

    require("does not bundle or claim live access" in readme, "README live-connector nonclaim missing")
    require("No live MCP, APEX, Mastermind" in readme, "README mesh nonclaim missing")

    repo = package.get("repository", {}).get("url", "")
    require(repo == "https://github.com/GlacierEQ/Pro-comet-agent.git", "package repository identity drift")
    require(package.get("homepage") == "https://github.com/GlacierEQ/Pro-comet-agent#readme", "package homepage drift")
    require(package.get("license") == "SEE LICENSE IN LICENSE", "package license conflicts with root license")

    allowed = {
        "explicit-fail-closed-connector-adapter-orchestration",
        "source-preserving-connector-result-merging",
        "connector-health-metrics-and-idle-lifecycle",
        "json-csv-xml-local-data-parsing",
        "typescript-browser-provider-server-build",
    }
    require(set(caps.get("capabilities", [])) == allowed, "machine capability allowlist drift")
    require(caps.get("operational_authority") is False, "operational authority must remain false")
    require(caps.get("live_external_connectors_bundled") is False, "live connector claim must remain false")
    require(caps.get("live_mcp_apex_mastermind_integration") is False, "live mesh claim must remain false")

    require(state.get("principal_state") == "FUNCTIONAL_CANDIDATE", "stale promoted state restored without proof")
    require(state.get("operational_authority") is False, "machine state grants operational authority")
    require(
        state.get("gates", {}).get("DETERMINISTIC_PROOF_GREEN", {}).get("status") == "PENDING_CANONICAL_CI",
        "fresh exact-head CI requirement missing",
    )

    print("PUBLIC_TRUTH_PASS")


if __name__ == "__main__":
    main()
