"""The Incident Commander agent: recall -> reason (Groq) -> respond -> retain (learn)."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from . import instructions
from .llm import FallbackLLM, get_llm
from .memory import MemoryHit, MemoryStore, get_memory_store


@dataclass
class IncidentResponse:
    answer: str
    recalled: list[MemoryHit] = field(default_factory=list)
    runbooks: list[str] = field(default_factory=list)
    model: str = ""
    memory_backend: str = ""
    used_fallback: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "answer": self.answer,
            "recalled": [h.to_dict() for h in self.recalled],
            "runbooks": self.runbooks,
            "model": self.model,
            "memory_backend": self.memory_backend,
            "used_fallback": self.used_fallback,
        }


class IncidentAgent:
    def __init__(self, memory: MemoryStore | None = None, llm=None, verbose: bool = True):
        self.memory = memory or get_memory_store(verbose=verbose)
        self.llm = llm or get_llm()

    # ---------- respond to an active incident ----------
    def handle_incident(
        self, description: str, *, service: str | None = None, recall_limit: int = 4
    ) -> IncidentResponse:
        query = f"{service + ': ' if service else ''}{description}"
        recalled = self.memory.recall(query, limit=recall_limit)
        runbooks = instructions.match_runbooks(query, limit=2)

        system = instructions.system_prompt()
        user = self._build_prompt(description, service, recalled, runbooks)
        result = self.llm.complete(system, user)

        return IncidentResponse(
            answer=result.text,
            recalled=recalled,
            runbooks=[slug for slug, _ in runbooks],
            model=result.model,
            memory_backend=self.memory.name,
            used_fallback=getattr(result, "used_fallback", False),
        )

    # ---------- close the loop: learn from resolution ----------
    def resolve_incident(
        self,
        *,
        incident_id: str,
        service: str,
        symptoms: str,
        root_cause: str,
        resolution: str,
        what_worked: str = "",
        timestamp: str | None = None,
    ) -> None:
        """Write a durable postmortem to memory (world fact + experience fact)."""
        ts = timestamp or datetime.now(timezone.utc).isoformat()
        meta = {
            "incident_id": incident_id,
            "service": service,
            "root_cause": root_cause,
        }
        world = (
            f"[{incident_id}] {service}: {symptoms} "
            f"Root cause: {root_cause}. Resolution: {resolution}."
        )
        self.memory.retain(
            world, context=f"postmortem:{incident_id}", timestamp=ts, metadata=meta
        )
        if what_worked:
            experience = (
                f"[{incident_id}] On {service}, this WORKED: {what_worked} "
                f"(root cause was {root_cause})."
            )
            self.memory.retain(
                experience,
                context=f"experience:{incident_id}",
                timestamp=ts,
                metadata={**meta, "kind": "what_worked"},
            )

    # ---------- trend questions ----------
    def insights(self, query: str) -> str:
        return self.memory.reflect(query)

    # ---------- prompt assembly ----------
    def _build_prompt(
        self,
        description: str,
        service: str | None,
        recalled: list[MemoryHit],
        runbooks: list[tuple[str, str]],
    ) -> str:
        parts: list[str] = []
        parts.append("# TRIAGE PLAYBOOK\n" + instructions.triage_playbook())

        if recalled:
            parts.append("# RECALLED MEMORIES (from Hindsight — most relevant past incidents)")
            for i, h in enumerate(recalled, 1):
                when = h.timestamp.split("T")[0] if h.timestamp else "unknown date"
                parts.append(f"- ({when}, score={h.score}) {h.text}")
        else:
            parts.append("# RECALLED MEMORIES\n(none — no similar past incident in memory)")

        if runbooks:
            parts.append("# RELEVANT RUNBOOKS")
            for slug, body in runbooks:
                parts.append(f"## Runbook: {slug}\n{body}")

        parts.append("# ACTIVE INCIDENT")
        parts.append(f"Service: {service or 'unknown'}")
        parts.append(f"Report: {description}")
        parts.append(
            "\nDiagnose the ACTIVE INCIDENT now. Ground your answer in the recalled "
            "memories and runbooks above, and follow the response structure exactly."
        )
        return "\n\n".join(parts)
