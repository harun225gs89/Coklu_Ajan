from __future__ import annotations

from pr_review_agent.github_client import GitHubClient
from pr_review_agent.graph import build_review_graph
from pr_review_agent.markdown_formatter import render_markdown
from pr_review_agent.models import Finding, ReviewResult
from pr_review_agent.review_utils import deduplicate_findings


class ReviewOrchestrator:
    def __init__(self, github_client: GitHubClient, agents: list | None = None):
        self.github_client = github_client
        self.agents = agents or []
        self.graph = build_review_graph(github_client)

    def run(self, pr_url: str, *, post_comment: bool = False) -> ReviewResult:
        pr_context = self.github_client.fetch_pr_context(pr_url)

        if self.agents:
            all_findings: list[Finding] = []
            for agent in self.agents:
                all_findings.extend(agent.analyze(pr_context))
            findings = deduplicate_findings(all_findings)
        else:
            state = self.graph.invoke({"pr_url": pr_url})
            findings = deduplicate_findings(state["review"].findings)

        summary = (
            f"{pr_context.full_name} PR#{pr_context.pull_number} için otomatik inceleme tamamlandı. "
            f"Toplam {len(findings)} bulgu üretildi."
        )
        recommendation = "İncelemeyi manuel olarak doğrulayıp, güvenlik sorunlarını öncelikli şekilde çözün."
        review = ReviewResult(summary=summary, findings=findings, recommendation=recommendation)

        if post_comment:
            markdown_body = render_markdown(review)
            self.github_client.post_review_comment(pr_context.full_name, pr_context.pull_number, markdown_body)

        return review
