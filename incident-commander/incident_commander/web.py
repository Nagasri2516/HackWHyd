"""FastAPI web app — a live incident console that makes the memory layer visible."""
from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import config
from .agent import IncidentAgent
from .seed import seed as seed_memory

app = FastAPI(title="Incident Commander", version="1.0.0")

_agent: IncidentAgent | None = None


def get_agent() -> IncidentAgent:
    global _agent
    if _agent is None:
        _agent = IncidentAgent()
    return _agent


class IncidentIn(BaseModel):
    description: str
    service: str | None = None


class ResolveIn(BaseModel):
    incident_id: str
    service: str
    symptoms: str
    root_cause: str
    resolution: str
    what_worked: str = ""


class InsightsIn(BaseModel):
    query: str


@app.get("/api/status")
def status() -> dict[str, Any]:
    agent = get_agent()
    return {
        "memory_backend": agent.memory.name,
        "memory_count": agent.memory.count(),
        "model": getattr(agent.llm, "model", "unknown"),
        "llm_live": config.llm_configured(),
    }


@app.post("/api/seed")
def api_seed() -> dict[str, Any]:
    agent = get_agent()
    n = seed_memory(agent=agent, verbose=False)
    return {"seeded": n, "memory_count": agent.memory.count()}


@app.post("/api/incident")
def api_incident(body: IncidentIn) -> dict[str, Any]:
    agent = get_agent()
    resp = agent.handle_incident(body.description, service=body.service)
    return resp.to_dict()


@app.post("/api/resolve")
def api_resolve(body: ResolveIn) -> dict[str, Any]:
    agent = get_agent()
    agent.resolve_incident(
        incident_id=body.incident_id,
        service=body.service,
        symptoms=body.symptoms,
        root_cause=body.root_cause,
        resolution=body.resolution,
        what_worked=body.what_worked,
    )
    return {"ok": True, "memory_count": agent.memory.count()}


@app.post("/api/insights")
def api_insights(body: InsightsIn) -> dict[str, Any]:
    agent = get_agent()
    return {"insight": agent.insights(body.query)}


@app.get("/api/memories")
def api_memories() -> dict[str, Any]:
    agent = get_agent()
    return {"memories": [m.to_dict() for m in agent.memory.all_memories()]}


@app.get("/")
def index() -> FileResponse:
    return FileResponse(str(config.WEB_DIR / "index.html"))


# static assets (app.js, styles.css)
app.mount("/static", StaticFiles(directory=str(config.WEB_DIR)), name="static")


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    import uvicorn

    uvicorn.run("incident_commander.web:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    run()
