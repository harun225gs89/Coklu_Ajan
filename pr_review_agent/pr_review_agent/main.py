from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pr_review_agent.config import settings
from pr_review_agent.github_client import GitHubClient
from pr_review_agent.markdown_formatter import render_markdown
from pr_review_agent.orchestrator import ReviewOrchestrator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Multi-agent GitHub PR review tool")
    parser.add_argument("--url", required=True, help="GitHub Pull Request URL")
    parser.add_argument("--token", default=settings.GITHUB_TOKEN, help="GitHub token for authenticated requests or comment posting")
    parser.add_argument("--post-comment", action="store_true", help="Publish the markdown review as a GitHub PR comment")
    parser.add_argument("--output", help="Optional path to write markdown review report to a file")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        client = GitHubClient(token=args.token)
        orchestrator = ReviewOrchestrator(client)
        review = orchestrator.run(args.url, post_comment=args.post_comment)
        report = render_markdown(review)

        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(report, encoding="utf-8")
            print(f"Markdown report written to {output_path}")

        print(report)
        return 0
    except Exception as exc:  # pragma: no cover - CLI error handling
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
