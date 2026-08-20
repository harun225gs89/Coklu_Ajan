from __future__ import annotations

from pr_review_agent.config import settings
from pr_review_agent.llm_client import LLMClient
from pr_review_agent.models import Finding, PRContext


class BaseAgent:
    name: str = "base-agent"
    category: str = "general"

    def analyze(self, pr_context: PRContext) -> list[Finding]:
        raise NotImplementedError

    def build_finding(
        self,
        *,
        severity: str,
        title: str,
        description: str,
        evidence: str,
        file_path: str | None = None,
        line_hint: str | None = None,
        recommendation: str,
    ) -> Finding:
        return Finding(
            agent=self.name,
            category=self.category,
            severity=severity,
            title=title,
            description=description,
            evidence=evidence,
            file_path=file_path,
            line_hint=line_hint,
            recommendation=recommendation,
        )

    def _attempt_llm_findings(self, pr_context: PRContext, prompt: str) -> list[Finding]:
        if not settings.OPENAI_API_KEY:
            return []

        llm_client = LLMClient(api_key=settings.OPENAI_API_KEY)
        raw_items = llm_client.call(prompt)
        findings: list[Finding] = []

        for item in raw_items:
            if not isinstance(item, dict):
                continue
            severity = str(item.get("severity", "medium")).lower()
            if severity not in {"info", "low", "medium", "high", "critical"}:
                severity = "medium"
            findings.append(
                Finding(
                    agent=self.name,
                    category=self.category,
                    severity=severity,
                    title=str(item.get("title", "Review finding")),
                    description=str(item.get("description", "No description provided.")),
                    evidence=str(item.get("evidence", "No evidence provided.")),
                    file_path=item.get("file_path"),
                    line_hint=item.get("line_hint"),
                    recommendation=str(item.get("recommendation", "Review the relevant code path manually.")),
                )
            )

        return findings
