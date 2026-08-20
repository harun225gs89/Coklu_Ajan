from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


Severity = Literal["info", "low", "medium", "high", "critical"]


class ChangedFile(BaseModel):
    path: str
    status: str
    additions: int = 0
    deletions: int = 0
    patch: str = ""


class PRContext(BaseModel):
    owner: str
    repo: str
    pull_number: int
    title: str
    description: str = ""
    files: list[ChangedFile] = Field(default_factory=list)

    @property
    def full_name(self) -> str:
        return f"{self.owner}/{self.repo}"


class Finding(BaseModel):
    agent: str
    category: str
    severity: Severity
    title: str
    description: str
    evidence: str
    file_path: str | None = None
    line_hint: str | None = None
    recommendation: str


class ReviewResult(BaseModel):
    summary: str
    findings: list[Finding] = Field(default_factory=list)
    recommendation: str = ""
