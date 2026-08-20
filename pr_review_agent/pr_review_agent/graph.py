from __future__ import annotations

from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from pr_review_agent.agents.logic_agent import LogicAgent
from pr_review_agent.agents.security_agent import SecurityAgent
from pr_review_agent.agents.test_agent import TestAgent
from pr_review_agent.github_client import GitHubClient
from pr_review_agent.models import Finding, PRContext, ReviewResult


class ReviewState(TypedDict):
    pr_url: str
    pr_context: PRContext
    logic_findings: list[Finding]
    security_findings: list[Finding]
    test_findings: list[Finding]
    review: ReviewResult
    markdown: str


def _fetch_pr_context(state: ReviewState, github_client: GitHubClient) -> dict:
    return {"pr_context": github_client.fetch_pr_context(state["pr_url"]) }


def _collect_logic(state: ReviewState) -> dict:
    return {"logic_findings": LogicAgent().analyze(state["pr_context"]) }


def _collect_security(state: ReviewState) -> dict:
    return {"security_findings": SecurityAgent().analyze(state["pr_context"]) }


def _collect_tests(state: ReviewState) -> dict:
    return {"test_findings": TestAgent().analyze(state["pr_context"]) }


def _aggregate_results(state: ReviewState) -> dict:
    findings = state["logic_findings"] + state["security_findings"] + state["test_findings"]
    summary = (
        f"{state['pr_context'].full_name} PR#{state['pr_context'].pull_number} için otomatik inceleme tamamlandı. "
        f"Toplam {len(findings)} bulgu üretildi."
    )
    recommendation = "İncelemeyi manuel olarak doğrulayıp, güvenlik sorunlarını öncelikli şekilde çözün."
    review = ReviewResult(summary=summary, findings=findings, recommendation=recommendation)
    return {"review": review}


def build_review_graph(github_client: GitHubClient):
    workflow = StateGraph(ReviewState)

    workflow.add_node("fetch_pr", lambda s: _fetch_pr_context(s, github_client))
    workflow.add_node("logic_review", _collect_logic)
    workflow.add_node("security_review", _collect_security)
    workflow.add_node("test_review", _collect_tests)
    workflow.add_node("aggregate", _aggregate_results)

    workflow.add_edge(START, "fetch_pr")
    workflow.add_edge("fetch_pr", "logic_review")
    workflow.add_edge("logic_review", "security_review")
    workflow.add_edge("security_review", "test_review")
    workflow.add_edge("test_review", "aggregate")
    workflow.add_edge("aggregate", END)

    return workflow.compile()
