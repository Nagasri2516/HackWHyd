"""Factory that picks the memory backend based on configuration."""
from __future__ import annotations

from .. import config
from .base import MemoryStore
from .local_store import LocalMemory


def get_memory_store(verbose: bool = True) -> MemoryStore:
    """Return a MemoryStore.

    - MEMORY_BACKEND=hindsight -> require Hindsight (error if it can't init)
    - MEMORY_BACKEND=local     -> always local
    - MEMORY_BACKEND=auto      -> Hindsight if HINDSIGHT_API_URL is set and initializes,
                                  otherwise fall back to local.
    """
    backend = config.MEMORY_BACKEND

    def _local() -> MemoryStore:
        store = LocalMemory(config.LOCAL_MEMORY_PATH)
        if verbose:
            print(f"[memory] Using {store.name} at {config.LOCAL_MEMORY_PATH}")
        return store

    if backend == "local":
        return _local()

    if backend in ("hindsight", "auto") and config.hindsight_configured():
        try:
            from .hindsight_store import HindsightMemory

            store = HindsightMemory(
                api_url=config.HINDSIGHT_API_URL,
                bank_id=config.HINDSIGHT_BANK_ID,
                api_key=config.HINDSIGHT_API_KEY or None,
                ui_url=config.HINDSIGHT_UI_URL or None,
            )
            if verbose:
                print(f"[memory] Using {store.name} (bank={config.HINDSIGHT_BANK_ID})")
            return store
        except Exception as exc:
            if backend == "hindsight":
                raise
            if verbose:
                print(f"[memory] Hindsight unavailable ({exc}); falling back to local.")
            return _local()

    if backend == "hindsight":
        raise RuntimeError(
            "MEMORY_BACKEND=hindsight but HINDSIGHT_API_URL is not set. "
            "Set it in your .env or use MEMORY_BACKEND=local."
        )

    return _local()
