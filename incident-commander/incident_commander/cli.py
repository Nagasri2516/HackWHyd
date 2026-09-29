"""Command-line interface for Incident Commander.

Examples:
    python -m incident_commander.cli seed
    python -m incident_commander.cli ask "payments-api throwing 500s, HikariCP timeouts, connections maxed" --service payments-api
    python -m incident_commander.cli resolve --id INC-2099 --service payments-api --symptoms "..." --cause "..." --resolution "..." --worked "..."
    python -m incident_commander.cli insights "what keeps breaking payments-api?"
    python -m incident_commander.cli memories
    python -m incident_commander.cli demo
"""
from __future__ import annotations

import argparse
import sys

from .agent import IncidentAgent
from .seed import seed as seed_memory


def _print_response(resp) -> None:
    print("\n" + "=" * 70)
    print(f"MODEL: {resp.model}   |   MEMORY: {resp.memory_backend}")
    if resp.recalled:
        print("\n🧠 RECALLED FROM MEMORY:")
        for h in resp.recalled:
            when = h.timestamp.split("T")[0] if h.timestamp else "?"
            print(f"   • [{when}] (score {h.score}) {h.text[:110]}...")
    else:
        print("\n🧠 RECALLED FROM MEMORY: (nothing matched — novel incident)")
    if resp.runbooks:
        print(f"\n📕 RUNBOOKS: {', '.join(resp.runbooks)}")
    print("\n" + "-" * 70)
    print(resp.answer)
    print("=" * 70 + "\n")


def cmd_seed(args) -> None:
    seed_memory(verbose=True)


def cmd_ask(args) -> None:
    agent = IncidentAgent()
    resp = agent.handle_incident(args.description, service=args.service)
    _print_response(resp)


def cmd_resolve(args) -> None:
    agent = IncidentAgent()
    agent.resolve_incident(
        incident_id=args.id,
        service=args.service,
        symptoms=args.symptoms,
        root_cause=args.cause,
        resolution=args.resolution,
        what_worked=args.worked or "",
    )
    print(f"Retained postmortem {args.id}. Total memories: {agent.memory.count()}.")


def cmd_insights(args) -> None:
    agent = IncidentAgent()
    print(agent.insights(args.query))


def cmd_memories(args) -> None:
    agent = IncidentAgent()
    mems = agent.memory.all_memories()
    print(f"{len(mems)} memories in {agent.memory.name}:\n")
    for m in mems:
        when = m.timestamp.split("T")[0] if m.timestamp else "?"
        print(f" • [{when}] {m.context}: {m.text[:120]}")


def cmd_demo(args) -> None:
    """The 60-second judge demo: before vs. after memory."""
    from .memory.local_store import LocalMemory
    import tempfile, os

    novel = (
        "checkout-service suddenly returning 503s during a flash sale; "
        "HikariCP 'Connection is not available' timeouts, Postgres connections maxed out"
    )

    print("\n########## DEMO: The same incident, WITHOUT vs WITH memory ##########")

    # 1) Empty memory
    tmp = os.path.join(tempfile.gettempdir(), "ic_demo_empty.json")
    if os.path.exists(tmp):
        os.remove(tmp)
    cold = IncidentAgent(memory=LocalMemory(tmp), verbose=False)
    print("\n>>> Interaction #1 — fresh agent, EMPTY memory:")
    _print_response(cold.handle_incident(novel, service="checkout-service"))

    # 2) Seeded memory
    warm = IncidentAgent(verbose=False)
    seed_memory(agent=warm, verbose=False)
    print(">>> Same incident — agent WITH seeded incident memory:")
    _print_response(warm.handle_incident(novel, service="checkout-service"))
    print("Notice: with memory, the agent recalls INC-2041/INC-2064 and leads with the "
          "PgBouncer fix that actually worked.\n")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="incident_commander", description="AI Incident Response Agent with Hindsight memory")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("seed", help="Load historical incidents into memory").set_defaults(func=cmd_seed)

    a = sub.add_parser("ask", help="Diagnose an active incident")
    a.add_argument("description", help="What is happening / error logs")
    a.add_argument("--service", default=None)
    a.set_defaults(func=cmd_ask)

    r = sub.add_parser("resolve", help="Record a postmortem (teaches the agent)")
    r.add_argument("--id", required=True)
    r.add_argument("--service", required=True)
    r.add_argument("--symptoms", required=True)
    r.add_argument("--cause", required=True)
    r.add_argument("--resolution", required=True)
    r.add_argument("--worked", default="")
    r.set_defaults(func=cmd_resolve)

    i = sub.add_parser("insights", help="Ask a trend question (reflect)")
    i.add_argument("query")
    i.set_defaults(func=cmd_insights)

    sub.add_parser("memories", help="List stored memories").set_defaults(func=cmd_memories)
    sub.add_parser("demo", help="Run the before/after memory demo").set_defaults(func=cmd_demo)
    return p


def main(argv: list[str] | None = None) -> int:
    # Windows consoles default to cp1252; make emoji/unicode safe.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except Exception:
            pass
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
