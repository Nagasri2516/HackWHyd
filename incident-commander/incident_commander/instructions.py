"""Loads agent instructions and runbooks from Markdown files.

All of the agent's behavior is defined in `.md` files under `instructions/`, so a
non-programmer can tune the agent by editing Markdown. Files are cached but can be
force-reloaded.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from . import config


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


@lru_cache(maxsize=1)
def system_prompt() -> str:
    return _read(config.INSTRUCTIONS_DIR / "system_prompt.md")


@lru_cache(maxsize=1)
def triage_playbook() -> str:
    return _read(config.INSTRUCTIONS_DIR / "triage_playbook.md")


@lru_cache(maxsize=1)
def memory_policy() -> str:
    return _read(config.INSTRUCTIONS_DIR / "memory_policy.md")


def load_runbooks() -> dict[str, str]:
    """Return {slug: markdown} for every runbook."""
    out: dict[str, str] = {}
    if config.RUNBOOKS_DIR.exists():
        for md in sorted(config.RUNBOOKS_DIR.glob("*.md")):
            out[md.stem] = _read(md)
    return out


def match_runbooks(text: str, limit: int = 2) -> list[tuple[str, str]]:
    """Cheap keyword scoring to attach the most relevant runbooks to an incident."""
    text_l = text.lower()
    scored: list[tuple[int, str, str]] = []
    for slug, body in load_runbooks().items():
        score = 0
        # score on the runbook title + signature keywords
        for token in set(_keywords(body)):
            if token in text_l:
                score += 1
        # slug words are strong signals
        for word in slug.split("-"):
            if len(word) > 2 and word in text_l:
                score += 3
        if score:
            scored.append((score, slug, body))
    scored.sort(key=lambda t: t[0], reverse=True)
    return [(slug, body) for _, slug, body in scored[:limit]]


_STOP = {
    "the", "and", "for", "with", "any", "are", "not", "that", "this", "from",
    "run", "check", "your", "you", "use", "add", "set", "has", "was", "will",
}


def _keywords(text: str) -> list[str]:
    words = []
    for raw in text.lower().replace("/", " ").replace("_", " ").split():
        w = "".join(c for c in raw if c.isalnum())
        if len(w) >= 4 and w not in _STOP:
            words.append(w)
    return words


def reload() -> None:
    system_prompt.cache_clear()
    triage_playbook.cache_clear()
    memory_policy.cache_clear()
