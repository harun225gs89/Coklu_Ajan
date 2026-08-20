from __future__ import annotations

from app.agents.base import BaseAgent
from app.models import Finding, PRContext


class LogicAgent(BaseAgent):
    name = "logic-agent"
    category = "logic"

    def analyze(self, pr_context: PRContext) -> list[Finding]:
        prompt = """
You are a senior code reviewer focused on logic and maintainability.
Review the following PR diff and identify concrete logic issues.
Return JSON with an array named 'findings'. Each finding must have:
- title
- severity (info/low/medium/high/critical)
- description
- evidence
- file_path
- recommendation

PR title: {title}
PR description: {description}
Files:
{files}
""".format(
            title=pr_context.title,
            description=pr_context.description,
            files="\n\n".join(f"File: {file.path}\nStatus: {file.status}\nPatch:\n{file.patch}" for file in pr_context.files),
        )

        llm_findings = self._attempt_llm_findings(pr_context, prompt)
        if llm_findings:
            return llm_findings

        findings: list[Finding] = []

        for file in pr_context.files:
            patch = file.patch or ""
            lower_patch = patch.lower()
            if not patch:
                continue

            if "if not" in lower_patch and "return" in lower_patch:
                findings.append(
                    self.build_finding(
                        severity="medium",
                        title="Potential guard clause review",
                        description="Patch contains branching on empty or falsey input but the return path should be checked to ensure graceful failure handling.",
                        evidence=patch[:200],
                        file_path=file.path,
                        recommendation="Review whether this condition covers all invalid input variants and whether the function returns a consistent response for each branch.",
                    )
                )

            if lower_patch.count("if ") >= 3 and "else" in lower_patch:
                findings.append(
                    self.build_finding(
                        severity="low",
                        title="Control flow complexity check",
                        description="The patch introduces multiple conditional branches. This can increase maintainability risk if the code path becomes harder to reason about.",
                        evidence=patch[:200],
                        file_path=file.path,
                        recommendation="Consider extracting nested logic into smaller helpers or validator functions to keep the flow easier to validate.",
                    )
                )

            if "try:" in lower_patch and "except" in lower_patch:
                findings.append(
                    self.build_finding(
                        severity="info",
                        title="Exception handling review",
                        description="The patch contains explicit exception handling. Confirm the error messages and fallback behavior are consistent with the service contract.",
                        evidence=patch[:200],
                        file_path=file.path,
                        recommendation="Add tests for the exception path and verify the fallback behavior is deterministic for callers.",
                    )
                )

        return findings
