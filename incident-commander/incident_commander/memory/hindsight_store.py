"""Hindsight-backed memory store (the required hackathon technology).

This wraps the `hindsight-client` SDK's three core operations:
    - retain(bank_id, content, context=, timestamp=)   -> write a memory
    - recall(bank_id, query=)                            -> multi-strategy retrieval
    - reflect(bank_id, query=)                           -> synthesized observations

Docs: https://hindsight.vectorize.io/  ·  SDK: `pip install hindsight-client`

The SDK is imported lazily so the rest of the project runs without it installed. If a call
fails (network, auth, or a schema mismatch across SDK versions), we surface a clear error;
the app factory can then fall back to LocalMemory in "auto" mode.
"""
from __future__ import annotations

from typing import Any

from .base import MemoryHit, MemoryStore


class HindsightMemory(MemoryStore):
    name = "Hindsight"

    def __init__(self, api_url: str, bank_id: str, api_key: str | None = None,
                 ui_url: str | None = None):
        try:
            from hindsight_client import Hindsight  # type: ignore
        except Exception as exc:  # pragma: no cover - depends on optional dep
            raise RuntimeError(
                "hindsight-client is not installed. Run `pip install hindsight-client` "
                "or set MEMORY_BACKEND=local."
            ) from exc

        self.bank_id = bank_id
        self.ui_url = ui_url
        kwargs: dict[str, Any] = {"base_url": api_url}
        if api_key:
            # different SDK versions name this differently; pass both defensively
            kwargs["api_key"] = api_key
        try:
            self._client = Hindsight(**kwargs)
        except TypeError:
            kwargs.pop("api_key", None)
            self._client = Hindsight(base_url=api_url)
        self.name = f"Hindsight ({api_url})"

    def retain(
        self,
        content: str,
        *,
        context: str | None = None,
        timestamp: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        kwargs: dict[str, Any] = {"bank_id": self.bank_id, "content": content}
        if context:
            kwargs["context"] = context
        if timestamp:
            kwargs["timestamp"] = timestamp
        if metadata:
            kwargs["metadata"] = metadata
        try:
            self._client.retain(**kwargs)
        except TypeError:
            # older/newer SDKs may not accept metadata/context — retry minimally
            self._client.retain(bank_id=self.bank_id, content=content)

    def recall(self, query: str, *, limit: int = 5) -> list[MemoryHit]:
        try:
            res = self._client.recall(bank_id=self.bank_id, query=query)
        except TypeError:
            res = self._client.recall(self.bank_id, query)
        return _normalize_recall(res, limit)

    def reflect(self, query: str) -> str:
        try:
            res = self._client.reflect(bank_id=self.bank_id, query=query)
        except TypeError:
            res = self._client.reflect(self.bank_id, query)
        # SDK returns an object with `.text` (or `.answer`); be defensive
        for attr in ("text", "answer", "content"):
            val = getattr(res, attr, None)
            if val:
                return str(val)
        return str(res)

    def all_memories(self) -> list[MemoryHit]:
        # Hindsight is a server-side store; listing every document is not the primary
        # access pattern. We approximate the UI timeline via a broad recall.
        return self.recall("incident postmortem root cause resolution", limit=100)


def _normalize_recall(res: Any, limit: int) -> list[MemoryHit]:
    """Coerce various SDK response shapes into a list[MemoryHit]."""
    items = getattr(res, "results", None)
    if items is None and isinstance(res, dict):
        items = res.get("results")
    if items is None and isinstance(res, (list, tuple)):
        items = res
    if not items:
        return []
    hits: list[MemoryHit] = []
    for it in items[:limit]:
        text = _get(it, "text") or _get(it, "content") or str(it)
        hits.append(
            MemoryHit(
                text=str(text),
                score=float(_get(it, "score") or 0.0),
                context=str(_get(it, "context") or ""),
                timestamp=str(_get(it, "timestamp") or ""),
                metadata=_get(it, "metadata") or {},
            )
        )
    return hits


def _get(obj: Any, key: str) -> Any:
    if isinstance(obj, dict):
        return obj.get(key)
    return getattr(obj, key, None)
