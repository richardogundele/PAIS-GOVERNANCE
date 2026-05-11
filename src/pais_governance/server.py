"""
PAIS-Governance FastAPI Server

REST API for PAIS policy enforcement.
"""

import logging
import os
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, File, UploadFile, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yaml
from pathlib import Path

from pais_governance.core.gateway import PolicyGateway
from pais_governance.core.policy_engine import PolicyAction

# Logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="PAIS-Governance API",
    description="Enterprise-grade policy-as-code AI governance",
    version="1.0.0",
)

# CORS
_cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global gateway instance
gateway: Optional[PolicyGateway] = None


@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    global gateway

    # Load configuration
    config_path = Path("pais_config.yaml")
    if not config_path.exists():
        logger.warning(f"Config file not found: {config_path}")
        config = {}
    else:
        with open(config_path) as f:
            config = yaml.safe_load(f) or {}

    # Initialize gateway
    gateway = PolicyGateway(config)
    logger.info("PAIS-Governance started")


# Request/Response models
class PolicyRequest(BaseModel):
    """Policy enforcement request."""

    trigger: str
    file: Optional[str] = None
    user: Optional[str] = None
    shared_by: Optional[str] = None
    shared_with: Optional[str] = None
    destination: Optional[str] = None
    is_external: Optional[bool] = False


class PolicyResponse(BaseModel):
    """Policy enforcement response."""

    action: str
    decision: str
    reason: str
    timestamp: str


# Routes
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


@app.post("/api/v1/enforce")
async def enforce_policy(request: PolicyRequest) -> PolicyResponse:
    """
    Enforce policy on a request.

    Args:
        request: Policy request with trigger, file, user, etc.

    Returns:
        Policy decision
    """
    if not gateway:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        decision = gateway.enforce_policy(request.dict(exclude_none=True))

        return PolicyResponse(
            action=decision.get("action"),
            decision=decision.get("decision"),
            reason=decision.get("reason"),
            timestamp=decision.get("timestamp"),
        )

    except Exception as e:
        logger.error(f"Error enforcing policy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/redact-file")
async def redact_file(file: UploadFile = File(...)):
    """
    Upload file for redaction.

    Args:
        file: File to redact

    Returns:
        Redaction result
    """
    if not gateway:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        # Save temp file
        from tempfile import NamedTemporaryFile

        with NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp.flush()

            # Process
            result = gateway.redactor.process_file(tmp.name)

            return result

    except Exception as e:
        logger.error(f"Error redacting file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/file-share")
async def handle_file_share(
    file_path: str, shared_by: str, shared_with: str, is_external: bool = True
) -> Dict[str, Any]:
    """Handle file sharing with policy enforcement."""
    if not gateway:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        result = gateway.handle_file_share(
            file_path=file_path,
            shared_by=shared_by,
            shared_with=shared_with,
            is_external=is_external,
        )
        return result

    except Exception as e:
        logger.error(f"Error handling file share: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/audit")
async def get_audit_log(
    event_type: Optional[str] = None, user: Optional[str] = None, limit: int = 100
) -> Dict[str, Any]:
    """Get audit log entries."""
    if not gateway:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        events = gateway.audit_logger.get_events(
            event_type=event_type, user=user, limit=limit
        )

        return {"count": len(events), "events": events}

    except Exception as e:
        logger.error(f"Error retrieving audit log: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/audit/summary")
async def get_audit_summary() -> Dict[str, Any]:
    """Get audit summary statistics."""
    if not gateway:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        summary = gateway.audit_logger.get_summary()
        return summary

    except Exception as e:
        logger.error(f"Error getting audit summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/config")
async def get_config() -> Dict[str, Any]:
    """Get current configuration (sanitized)."""
    if not gateway:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        # Return config without sensitive data
        config = gateway.config.copy()

        # Remove secrets
        if "security" in config:
            if "encryption_key" in config["security"]:
                config["security"]["encryption_key"] = "***REDACTED***"

        return config

    except Exception as e:
        logger.error(f"Error getting config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unhandled exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
