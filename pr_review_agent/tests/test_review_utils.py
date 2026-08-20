import unittest

from pr_review_agent.models import Finding
from pr_review_agent.review_utils import deduplicate_findings


class ReviewUtilsTests(unittest.TestCase):
    def test_deduplicate_findings(self):
        findings = [
            Finding(
                agent="logic-agent",
                category="logic",
                severity="medium",
                title="Guard clause risk",
                description="Missing guard clause",
                evidence="if not user",
                recommendation="Add validation",
            ),
            Finding(
                agent="security-agent",
                category="security",
                severity="high",
                title="Guard clause risk",
                description="Missing guard clause",
                evidence="if not user",
                recommendation="Add validation",
            ),
            Finding(
                agent="test-agent",
                category="tests",
                severity="low",
                title="Different issue",
                description="Need more tests",
                evidence="missing branch",
                recommendation="Add tests",
            ),
        ]

        unique = deduplicate_findings(findings)
        self.assertEqual(len(unique), 2)
        self.assertEqual(unique[0].severity, "high")


if __name__ == "__main__":
    unittest.main()
