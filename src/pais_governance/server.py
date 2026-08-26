"""FastAPI boundary for the PAIS Agent Reliability Gateway."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import yaml
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

from pais_governance.core.gateway import PolicyGateway

gateway: PolicyGateway | None = None


def _build_gateway() -> PolicyGateway:
    config_path = Path(os.getenv("PAIS_CONFIG", "pais_config.yaml"))
    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) if config_path.exists() else {}
    return PolicyGateway(config or {})


@asynccontextmanager
async def lifespan(_: FastAPI):
    global gateway
    gateway = _build_gateway()
    yield


app = FastAPI(
    title="PAIS Agent Reliability Gateway",
    description="Policy decisions and tamper-evident audit records for AI-agent tool calls.",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if origin
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["content-type", "authorization", "x-request-id"],
)


class PolicyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trigger: str = "agent_tool_call"
    agent_id: str = Field(min_length=1, max_length=200)
    user: str | None = Field(default=None, max_length=320)
    tool: str = Field(min_length=1, max_length=200)
    operation: str = Field(min_length=1, max_length=100)
    environment: str = Field(default="development", pattern="^(development|staging|production)$")
    has_side_effect: bool | None = None
    resource: str | None = Field(default=None, max_length=500)
    destination: str | None = Field(default=None, max_length=500)
    data_classification: str = Field(
        default="internal", pattern="^(public|internal|confidential|restricted)$"
    )
    risk_score: int = Field(default=0, ge=0, le=100)
    data: dict[str, Any] | None = None


def _gateway() -> PolicyGateway:
    if gateway is None:
        raise HTTPException(status_code=503, detail="Gateway is not initialised")
    return gateway


@app.get("/health")
async def health() -> dict[str, Any]:
    service = _gateway()
    return {
        "status": "healthy",
        "version": "0.1.0",
        "audit_integrity": service.audit_logger.verify_integrity()["valid"],
    }


@app.post("/api/v1/decisions")
async def decide(request: PolicyRequest) -> dict[str, Any]:
    return _gateway().enforce_policy(request.model_dump(exclude_none=True))


@app.get("/api/v1/audit/integrity")
async def audit_integrity() -> dict[str, Any]:
    return _gateway().audit_logger.verify_integrity()


@app.get("/api/v1/audit/events")
async def audit_events(event_type: str | None = None, limit: int = 100) -> dict[str, Any]:
    if not 1 <= limit <= 1000:
        raise HTTPException(status_code=422, detail="limit must be between 1 and 1000")
    events = _gateway().audit_logger.get_events(event_type=event_type, limit=limit)
    return {"count": len(events), "events": events}


@app.get("/api/v1/reviews/{decision_id}")
async def review_status(decision_id: str) -> dict[str, Any]:
    review = _gateway().pending_reviews.get(decision_id)
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return {"decision_id": decision_id, **review}
