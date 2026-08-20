from __future__ import annotations

from app.agents.base import BaseAgent
from app.models import Finding, PRContext


class TestAgent(BaseAgent):
    name = "test-agent"
    category = "tests"

    def analyze(self, pr_context: PRContext) -> list[Finding]:
        prompt = """
You are a test generation expert. Review the PR diff and suggest concrete unit tests.
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

            if "if not" in lower_patch or "if not " in lower_patch:
                findings.append(
                    self.build_finding(
                        severity="medium",
                        title="Add null/empty input test",
                        description="The diff contains explicit falsy checks. Unit tests should cover empty, None, and malformed input variants.",
                        evidence=patch[:220],
                        file_path=file.path,
                        recommendation="Add tests for None, empty string, empty list, and invalid payload inputs to validate guard clauses.",
                    )
                )

            if "try:" in lower_patch and "except" in lower_patch:
                findings.append(
                    self.build_finding(
                        severity="medium",
                        title="Add exception-path tests",
                        description="The patch introduces an exception-handling flow, but the error branch should be asserted explicitly in the test suite.",
                        evidence=patch[:220],
                        file_path=file.path,
                        recommendation="Write unit tests that assert the intended exception type, message, and fallback behavior for the error branch.",
                    )
                )

            if "requests." in lower_patch or "httpx." in lower_patch:
                findings.append(
                    self.build_finding(
                        severity="low",
                        title="Mock external dependency in tests",
                        description="The patch interacts with an external service boundary. Tests should isolate the network layer and validate timeout/failure behavior.",
                        evidence=patch[:220],
                        file_path=file.path,
                        recommendation="Use mocks or stubs to test success, timeout, and failure responses for external calls.",
                    )
                )

        if not findings:
            findings.append(
                self.build_finding(
                    severity="info",
                    title="No immediate gap in the visible diff",
                    description="The current patch does not expose obvious test gaps from static analysis alone.",
                    evidence="No matching patterns found in changed files.",
                    file_path=None,
                    recommendation="Still add edge-case and happy-path tests for the modified behavior and document expected outcomes.",
                )
            )

        return findings
