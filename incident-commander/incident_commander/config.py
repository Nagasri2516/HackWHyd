"""Configuration loaded from environment variables (.env supported)."""
from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # dotenv is optional
    pass

# Project paths
ROOT = Path(__file__).resolve().parent.parent
INSTRUCTIONS_DIR = ROOT / "instructions"
RUNBOOKS_DIR = INSTRUCTIONS_DIR / "runbooks"
DATA_DIR = ROOT / "data"
WEB_DIR = ROOT / "web"

# --- LLM (Groq) ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
# Recommended by the hackathon docs: openai/gpt-oss-120b and qwen/qwen3-32b
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b").strip()
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com").strip()

# --- Memory (Hindsight) ---
# MEMORY_BACKEND: "auto" (use Hindsight if configured, else local), "hindsight", or "local"
MEMORY_BACKEND = os.getenv("MEMORY_BACKEND", "auto").strip().lower()
HINDSIGHT_API_URL = os.getenv("HINDSIGHT_API_URL", "").strip()
HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY", "").strip()
HINDSIGHT_UI_URL = os.getenv("HINDSIGHT_UI_URL", "").strip()
HINDSIGHT_BANK_ID = os.getenv("HINDSIGHT_BANK_ID", "incident-commander").strip()

# Local fallback memory store location
LOCAL_MEMORY_PATH = Path(
    os.getenv("LOCAL_MEMORY_PATH", str(DATA_DIR / "memory_store.json"))
)


def llm_configured() -> bool:
    return bool(GROQ_API_KEY)


def hindsight_configured() -> bool:
    return bool(HINDSIGHT_API_URL)
