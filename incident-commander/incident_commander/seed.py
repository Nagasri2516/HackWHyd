"""Seed the agent's memory with realistic historical incidents.

This is what gives the demo its "wow": on a fresh bank the agent is generic; after seeding
8 real postmortems it recalls the exact past fix for a new, similar incident.
"""
from __future__ import annotations

import json

from . import config
from .agent import IncidentAgent


def load_incidents() -> list[dict]:
    path = config.DATA_DIR / "incidents.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["incidents"]


def seed(agent: IncidentAgent | None = None, verbose: bool = True) -> int:
    agent = agent or IncidentAgent(verbose=verbose)
    incidents = load_incidents()
    for inc in incidents:
        agent.resolve_incident(
            incident_id=inc["incident_id"],
            service=inc["service"],
            symptoms=inc["symptoms"],
            root_cause=inc["root_cause"],
            resolution=inc["resolution"],
            what_worked=inc.get("what_worked", ""),
            timestamp=inc.get("timestamp"),
        )
    if verbose:
        print(f"[seed] Retained {len(incidents)} postmortems into "
              f"{agent.memory.name}. Total memories: {agent.memory.count()}.")
    return len(incidents)


if __name__ == "__main__":
    seed()
