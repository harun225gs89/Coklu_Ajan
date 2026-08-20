from __future__ import annotations

from pr_review_agent.agents.base import BaseAgent
from pr_review_agent.models import Finding, PRContext


class SecurityAgent(BaseAgent):
    name = "security-agent"
    category = "security"

    def analyze(self, pr_context: PRContext) -> list[Finding]:
        prompt = """
You are a cybersecurity reviewer focused on OWASP Top 10 risks.
Review the following PR diff and identify concrete security issues.
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

            if "eval(" in lower_patch or "exec(" in lower_patch:
                findings.append(
                    self.build_finding(
                        severity="critical",
                        title="Code execution risk",
                        description="Dynamic execution patterns can allow command execution or script injection when user-controlled data reaches the expression.",
                        evidence=patch[:220],
                        file_path=file.path,
                        recommendation="Avoid eval/exec with untrusted input. Prefer explicit parsing, allowlists, or dedicated APIs.",
                    )
                )

            if "subprocess" in lower_patch or "os.system" in lower_patch:
                findings.append(
                    self.build_finding(
                        severity="high",
                        title="Command execution surface",
                        description="The patch uses command execution APIs that may be reachable from external input.",
                        evidence=patch[:220],
                        file_path=file.path,
                        recommendation="Use safe subprocess APIs and validate/whitelist inputs before invoking shell commands.",
                    )
                )

            if "select" in lower_patch and "from" in lower_patch and "+" in lower_patch:
                findings.append(
                    self.build_finding(
                        severity="high",
                        title="SQL injection risk",
                        description="The patch appears to concatenate user-controlled values directly into a SQL query string.",
                        evidence=patch[:220],
                        file_path=file.path,
                        recommendation="Use parameterized queries or prepared statements and avoid string concatenation in queries.",
                    )
                )

            if "jwt.decode" in lower_patch and "verify" in lower_patch and "false" in lower_patch:
                findings.append(
                    self.build_finding(
                        severity="high",
                        title="JWT verification disabled",
                        description="The patch appears to disable signature verification, which weakens authentication guarantees.",
                        evidence=patch[:220],
                        file_path=file.path,
                        recommendation="Require signature verification and validate issuer/audience/expiration before trusting JWT claims.",
                    )
                )

            if "requests.get" in lower_patch and "url" in lower_patch and ("+" in lower_patch or "format(" in lower_patch):
                findings.append(
                    self.build_finding(
                        severity="medium",
                        title="SSRF review",
                        description="The patch builds a request URL from user-controlled or dynamic values, which can enable server-side request forgery.",
                        evidence=patch[:220],
                        file_path=file.path,
                        recommendation="Restrict outbound destinations, validate allowlisted domains, and avoid passing untrusted values to external request targets.",
                    )
                )

        return findings
