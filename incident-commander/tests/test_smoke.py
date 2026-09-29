import os
import tempfile

from incident_commander.agent import IncidentAgent
from incident_commander.memory.local_store import LocalMemory
from incident_commander.seed import seed


def _fresh_agent() -> IncidentAgent:
    tmp = os.path.join(tempfile.mkdtemp(), "mem.json")
    return IncidentAgent(memory=LocalMemory(tmp), verbose=False)


def test_empty_memory_recall_is_empty():
    agent = _fresh_agent()
    resp = agent.handle_incident("payments-api 500s, connection pool timeouts")
    assert resp.recalled == []
    assert resp.answer  # still produces a response


def test_learning_loop_recalls_after_resolve():
    agent = _fresh_agent()
    agent.resolve_incident(
        incident_id="INC-9001",
        service="payments-api",
        symptoms="HikariCP connection timeouts, pg connections maxed",
        root_cause="connection pool exhaustion under traffic spike",
        resolution="deployed PgBouncer, right-sized pool",
        what_worked="killing idle-in-transaction backends + PgBouncer",
    )
    resp = agent.handle_incident(
        "payments-api throwing 500s, HikariCP 'Connection is not available' timeouts, connections maxed",
        service="payments-api",
    )
    assert len(resp.recalled) >= 1
    assert "INC-9001" in resp.recalled[0].text


def test_seed_populates_memory():
    agent = _fresh_agent()
    n = seed(agent=agent, verbose=False)
    assert n == 8
    assert agent.memory.count() >= 8


def test_runbook_matching():
    agent = _fresh_agent()
    resp = agent.handle_incident("pods OOMKilled exit code 137 after deploy", service="orders-api")
    assert any("oom" in rb for rb in resp.runbooks)


def test_reflect_returns_text():
    agent = _fresh_agent()
    seed(agent=agent, verbose=False)
    out = agent.insights("what keeps breaking payments-api?")
    assert isinstance(out, str) and len(out) > 0
