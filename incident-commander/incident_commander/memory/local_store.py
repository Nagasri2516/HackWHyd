"""Local, dependency-free memory store.

Implements retain/recall/reflect over a JSON file so the whole project runs and demos
with **zero external services** — no Hindsight instance and no API keys required.

Recall uses a transparent, explainable score: keyword overlap (TF-style) + entity/service
match + recency. It is intentionally simple and deterministic so judges can see exactly why
a memory was surfaced. For production, swap in the Hindsight backend (see hindsight_store.py),
which adds vector search, an entity graph, temporal reasoning, and knowledge consolidation.
"""
from __future__ import annotations

import json
import math
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .base import MemoryHit, MemoryStore

_STOP = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "is", "are", "was",
    "were", "it", "this", "that", "for", "with", "at", "by", "from", "as", "we",
    "i", "our", "your", "after", "before", "not", "no", "but", "so", "if",
}


def _tokens(text: str) -> list[str]:
    out: list[str] = []
    for raw in text.lower().replace("/", " ").replace("_", " ").replace("-", " ").split():
        w = "".join(c for c in raw if c.isalnum())
        if w and w not in _STOP and len(w) > 1:
            out.append(w)
    return out


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class LocalMemory(MemoryStore):
    name = "Local fallback (offline)"

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._lock = threading.Lock()
        self._records: list[dict[str, Any]] = []
        self._load()

    # ---- persistence ----
    def _load(self) -> None:
        if self.path.exists():
            try:
                self._records = json.loads(self.path.read_text(encoding="utf-8"))
            except Exception:
                self._records = []

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(self._records, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    # ---- core ops ----
    def retain(
        self,
        content: str,
        *,
        context: str | None = None,
        timestamp: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        with self._lock:
            self._records.append(
                {
                    "text": content,
                    "context": context or "",
                    "timestamp": timestamp or _now_iso(),
                    "metadata": metadata or {},
                    "stored_at": _now_iso(),
                }
            )
            self._save()

    def recall(self, query: str, *, limit: int = 5) -> list[MemoryHit]:
        q_tokens = _tokens(query)
        if not q_tokens:
            return []
        q_set = set(q_tokens)

        # document frequency for a light IDF weighting (rare terms matter more)
        df: dict[str, int] = {}
        docs = []
        for rec in self._records:
            toks = set(_tokens(rec["text"] + " " + rec.get("context", "")))
            docs.append(toks)
            for t in toks:
                df[t] = df.get(t, 0) + 1
        n = max(len(self._records), 1)

        hits: list[MemoryHit] = []
        for rec, toks in zip(self._records, docs):
            overlap = q_set & toks
            if not overlap:
                continue
            # IDF-weighted overlap
            base = sum(math.log((n + 1) / (df[t])) for t in overlap)

            # service/entity boost
            svc = str(rec.get("metadata", {}).get("service", "")).lower()
            if svc and svc.replace("-", " ") in query.lower():
                base += 2.0

            # recency boost (newer memories slightly preferred)
            base += _recency_boost(rec.get("timestamp", ""))

            hits.append(
                MemoryHit(
                    text=rec["text"],
                    score=round(base, 3),
                    context=rec.get("context", ""),
                    timestamp=rec.get("timestamp", ""),
                    metadata=rec.get("metadata", {}),
                )
            )
        hits.sort(key=lambda h: h.score, reverse=True)
        return hits[:limit]

    def reflect(self, query: str) -> str:
        """Deterministic synthesis across memories (no LLM required).

        Groups resolved incidents by service and surfaces recurring root causes — a simple
        stand-in for Hindsight's server-side observation consolidation.
        """
        hits = self.recall(query, limit=50) or [
            MemoryHit(text=r["text"], context=r.get("context", ""),
                      timestamp=r.get("timestamp", ""), metadata=r.get("metadata", {}))
            for r in self._records
        ]
        by_service: dict[str, list[str]] = {}
        for h in hits:
            svc = str(h.metadata.get("service", "unknown"))
            cause = str(h.metadata.get("root_cause", "")) or h.text
            by_service.setdefault(svc, []).append(cause)
        if not by_service:
            return "No memories yet — resolve some incidents to build observations."
        lines = ["Observations synthesized from memory:"]
        for svc, causes in sorted(by_service.items(), key=lambda kv: -len(kv[1])):
            lines.append(f"- **{svc}**: {len(causes)} past incident(s). "
                         f"Most recent cause: {causes[0][:120]}")
        return "\n".join(lines)

    def all_memories(self) -> list[MemoryHit]:
        recs = sorted(
            self._records, key=lambda r: r.get("stored_at", ""), reverse=True
        )
        return [
            MemoryHit(
                text=r["text"],
                context=r.get("context", ""),
                timestamp=r.get("timestamp", ""),
                metadata=r.get("metadata", {}),
            )
            for r in recs
        ]


def _recency_boost(ts: str) -> float:
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return 0.0
    age_days = (datetime.now(timezone.utc) - dt).total_seconds() / 86400.0
    # small, bounded boost: ~0.5 for today decaying over ~90 days
    return max(0.0, 0.5 * math.exp(-age_days / 90.0))
