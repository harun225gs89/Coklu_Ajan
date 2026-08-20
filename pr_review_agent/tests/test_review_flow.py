import unittest
from unittest.mock import Mock

from pr_review_agent.agents.logic_agent import LogicAgent
from pr_review_agent.agents.security_agent import SecurityAgent
from pr_review_agent.agents.test_agent import TestAgent
from pr_review_agent.github_client import GitHubClient, parse_pr_url
from pr_review_agent.models import ChangedFile, PRContext


class ReviewFlowTests(unittest.TestCase):
    def test_parse_pr_url(self):
        owner, repo, number = parse_pr_url("https://github.com/example/project/pull/42/")
        self.assertEqual(owner, "example")
        self.assertEqual(repo, "project")
        self.assertEqual(number, 42)

    def test_agents_generate_findings(self):
        pr_context = PRContext(
            owner="example",
            repo="project",
            pull_number=42,
            title="feat: add login flow",
            description="Add login flow",
            files=[
                ChangedFile(
                    path="src/auth.py",
                    status="modified",
                    patch="""
if not username:
    return error

query = "SELECT * FROM users WHERE username = '" + username + "'"
jwt.decode(token, options={"verify_signature": False})
""",
                )
            ],
        )

        findings = []
        findings.extend(LogicAgent().analyze(pr_context))
        findings.extend(SecurityAgent().analyze(pr_context))
        findings.extend(TestAgent().analyze(pr_context))

        self.assertTrue(any(f.category == "logic" for f in findings))
        self.assertTrue(any(f.category == "security" for f in findings))
        self.assertTrue(any(f.category == "tests" for f in findings))

    def test_post_review_comment_calls_github_api(self):
        client = GitHubClient(token="secret-token", base_url="https://api.github.com")
        client.session = Mock()
        response = Mock(status_code=201)
        response.json.return_value = {"html_url": "https://github.com/example/project/pull/42#issuecomment-1"}
        client.session.post.return_value = response

        result = client.post_review_comment("example/project", 42, "## Test report")

        client.session.post.assert_called_once_with(
            "https://api.github.com/repos/example/project/issues/42/comments",
            json={"body": "## Test report"},
            timeout=30,
        )
        self.assertEqual(result["html_url"], "https://github.com/example/project/pull/42#issuecomment-1")


if __name__ == "__main__":
    unittest.main()
