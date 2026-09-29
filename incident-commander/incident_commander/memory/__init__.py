"""Memory layer: a common interface with a Hindsight backend and a local fallback."""
from __future__ import annotations

from .base import MemoryHit, MemoryStore
from .factory import get_memory_store

__all__ = ["MemoryHit", "MemoryStore", "get_memory_store"]
