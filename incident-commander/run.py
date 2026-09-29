"""Convenience launcher: `python run.py` starts the web console.

Seeds memory on first run so the demo works immediately.
"""
from incident_commander import config
from incident_commander.agent import IncidentAgent
from incident_commander.seed import seed
from incident_commander.web import run


def main() -> None:
    agent = IncidentAgent()
    if agent.memory.count() == 0:
        print("[run] Empty memory — seeding historical incidents for the demo...")
        seed(agent=agent, verbose=True)
    print("\n  Incident Commander is live at http://127.0.0.1:8000")
    print(f"  LLM: {'Groq ' + config.GROQ_MODEL if config.llm_configured() else 'offline fallback (set GROQ_API_KEY)'}")
    print(f"  Memory: {agent.memory.name}\n")
    run()


if __name__ == "__main__":
    main()
