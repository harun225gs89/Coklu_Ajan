from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GITHUB_API_BASE = os.getenv("GITHUB_API_BASE", "https://api.github.com")
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")


settings = Settings()
