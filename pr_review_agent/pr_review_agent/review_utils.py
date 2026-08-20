from __future__ import annotations

from pr_review_agent.models import Finding


SEVERITY_ORDER = {"critical": 5, "high": 4, "medium": 3, "low": 2, "info": 1}


def deduplicate_findings(findings: list[Finding]) -> list[Finding]:
    merged: dict[tuple[str, str | None, str], Finding] = {}

    for finding in findings:
        key = (
            finding.title.strip().lower(),
            finding.file_path or "",
            finding.description.strip().lower(),
        )
        if key not in merged:
            merged[key] = finding
            continue

        existing = merged[key]
        if SEVERITY_ORDER.get(finding.severity, 0) > SEVERITY_ORDER.get(existing.severity, 0):
            merged[key] = finding

    unique = list(merged.values())
    return sorted(unique, key=lambda item: SEVERITY_ORDER.get(item.severity, 0), reverse=True)
