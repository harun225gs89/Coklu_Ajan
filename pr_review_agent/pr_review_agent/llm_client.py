from __future__ import annotations

import json
from typing import Any

from pr_review_agent.config import settings


class LLMClient:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.DEFAULT_MODEL

    def call(self, prompt: str) -> list[dict[str, Any]]:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured. Set it in .env or pass api_key.")

        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - dependency management
            raise RuntimeError("python package 'openai' is required for LLM review support.") from exc

        client = OpenAI(api_key=self.api_key)
        response = client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            temperature=0.2,
            messages=[
                {
                    "role": "system",
                    "content": "You are a senior code review assistant. Return valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        raw = response.choices[0].message.content
        if not raw:
            return []

        data = json.loads(raw)
        if isinstance(data, dict):
            if "findings" in data:
                items = data.get("findings", [])
                return items if isinstance(items, list) else []
            if "items" in data:
                items = data.get("items", [])
                return items if isinstance(items, list) else []
            return [data]
        if isinstance(data, list):
            return data
        return []
