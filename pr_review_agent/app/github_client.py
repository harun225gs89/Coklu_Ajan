from __future__ import annotations

import re
from typing import Any

import requests

from app.config import settings
from app.models import ChangedFile, PRContext


class GitHubClient:
    def __init__(self, token: str | None = None, base_url: str | None = None):
        self.token = token or settings.GITHUB_TOKEN
        self.base_url = (base_url or settings.GITHUB_API_BASE).rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/vnd.github+json"})
        if self.token:
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})

    def _request(self, path: str, params: dict[str, Any] | None = None, method: str = "GET") -> Any:
        url = f"{self.base_url}{path}"
        response = self.session.request(method, url, params=params, timeout=30)
        if response.status_code >= 400:
            raise RuntimeError(f"GitHub request failed for {url}: {response.status_code} {response.text}")
        return response.json()

    def _fetch_all_paginated_files(self, path: str) -> list[dict[str, Any]]:
        all_items: list[dict[str, Any]] = []
        page = 1

        while True:
            chunk = self._request(path, params={"per_page": 100, "page": page})
            if not chunk:
                break
            all_items.extend(chunk)
            if len(chunk) < 100:
                break
            page += 1

        return all_items

    def fetch_pr_context(self, pr_url: str) -> PRContext:
        owner, repo, pull_number = parse_pr_url(pr_url)
        pull = self._request(f"/repos/{owner}/{repo}/pulls/{pull_number}")
        files_response = self._fetch_all_paginated_files(f"/repos/{owner}/{repo}/pulls/{pull_number}/files")

        files = [
            ChangedFile(
                path=item.get("filename", "unknown"),
                status=item.get("status", "modified"),
                additions=int(item.get("additions", 0) or 0),
                deletions=int(item.get("deletions", 0) or 0),
                patch=item.get("patch", ""),
            )
            for item in files_response
        ]

        return PRContext(
            owner=owner,
            repo=repo,
            pull_number=int(pull_number),
            title=str(pull.get("title", "Untitled PR")),
            description=str(pull.get("body") or ""),
            files=files,
        )

    def post_review_comment(self, repo: str, pull_number: int, markdown_body: str) -> dict[str, Any]:
        if not self.token:
            raise RuntimeError("GitHub token is required to post comments. Set GITHUB_TOKEN or pass --token.")
        response = self.session.post(
            f"{self.base_url}/repos/{repo}/issues/{pull_number}/comments",
            json={"body": markdown_body},
            timeout=30,
        )
        if response.status_code >= 400:
            raise RuntimeError(f"Comment post failed: {response.status_code} {response.text}")
        return response.json()


def parse_pr_url(pr_url: str) -> tuple[str, str, int]:
    normalized = str(pr_url).strip().rstrip("/")
    match = re.search(r"github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/pull/(?P<number>\d+)", normalized)
    if not match:
        raise ValueError(f"Unsupported GitHub PR URL: {pr_url}")

    owner = match.group("owner")
    repo = match.group("repo")
    pull_number = int(match.group("number"))
    return owner, repo, pull_number
