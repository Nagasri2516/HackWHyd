"""Abstract memory interface modeled on Hindsight's retain / recall / reflect."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class MemoryHit:
    """A single memory returned by recall()."""

    text: str
    score: float = 0.0
    context: str = ""
    timestamp: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class MemoryStore(ABC):
    """Common interface. Mirrors Hindsight's three core operations."""

    #: Human-readable backend name, e.g. "Hindsight Cloud" or "Local fallback".
    name: str = "memory"

    @abstractmethod
    def retain(
        self,
        content: str,
        *,
        context: str | None = None,
        timestamp: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Store a memory (a world fact or an experience fact)."""

    @abstractmethod
    def recall(self, query: str, *, limit: int = 5) -> list[MemoryHit]:
        """Retrieve the memories most relevant to `query`."""

    @abstractmethod
    def reflect(self, query: str) -> str:
        """Synthesize an insight across many memories."""

    @abstractmethod
    def all_memories(self) -> list[MemoryHit]:
        """Return every stored memory (newest first) — used by the UI timeline."""

    def count(self) -> int:
        return len(self.all_memories())
