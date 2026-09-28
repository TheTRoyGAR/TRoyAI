"""
TRoyAI Agent Execution Server
Exposes CrewAI agents as REST endpoints.
Run with: py -3.12 server.py

Added 2026-09-28 — TRoyAI was the one company in the group without a real
persistent backend. Its Cloudflare Worker (worker/index.js) only ever wrote
tasks into D1 with status 'queued'; nothing ever drained that queue, so
every task submitted through the dashboard sat there forever, unexecuted.
This server is modeled directly on TRoyMAR/TRoyMEDIA's server.py — same
auth pattern, same route shape — so TRoyAI's real execution path is
consistent with the rest of the group.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
import os
import hmac
import threading
import httpx
from dotenv import load_dotenv
from agency import TRoyAIAgency
from agency.core.memory import shared_memory

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TRoyAI Agent Server",
    description="Execute CrewAI agents and return results",
    version="1.0.0"
)

BACKEND_API_KEY = os.getenv("BACKEND_API_KEY", "")


@app.middleware("http")
async def require_backend_key(request: Request, call_next):
    if request.url.path in ("/health", "/docs", "/openapi.json", "/redoc"):
        return await call_next(request)

    if not BACKEND_API_KEY:
        logger.warning("BACKEND_API_KEY is not set — refusing all non-health requests.")
        return JSONResponse(status_code=503, content={"detail": "Server not configured: BACKEND_API_KEY missing"})

    provided = request.headers.get("x-backend-key", "")
    if not hmac.compare_digest(provided, BACKEND_API_KEY):
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

    return await call_next(request)


agency = TRoyAIAgency()


class TaskRequest(BaseModel):
    task_id: str
    brief: str
    department: str = ""
    skill: str = ""
    callback_url: str = ""


class TaskResponse(BaseModel):
    task_id: str
    status: str
    result: str


@app.get("/health")
def health_check():
    return {"status": "online", "service": "TRoyAI Agent Executor", "agency_version": "1.0.0"}


@app.get("/status")
def status():
    return agency.status()


@app.get("/memory/records")
def memory_records(limit: int = 100):
    if limit > 500:
        limit = 500
    records = shared_memory.list_records()
    records.sort(key=lambda r: r.created_at, reverse=True)
    return {
        "count": len(records),
        "records": [
            {
                "id": r.id,
                "scope": r.scope,
                "categories": r.categories,
                "content": r.content,
                "importance": r.importance,
                "created_at": r.created_at.isoformat() if hasattr(r.created_at, "isoformat") else str(r.created_at),
            }
            for r in records[:limit]
        ],
    }


def _run_and_callback(task_id: str, department: str, skill: str, brief: str, callback_url: str) -> None:
    try:
        result = route_and_execute(department, skill, brief)
        payload = {"status": "completed", "output": result}
        logger.info(f"Task {task_id} completed successfully")
    except Exception as e:
        logger.error(f"Task {task_id} failed: {str(e)}")
        payload = {"status": "failed", "output": str(e)}

    try:
        httpx.post(callback_url, json=payload, headers={"X-Backend-Key": BACKEND_API_KEY}, timeout=30)
    except Exception as e:
        logger.error(f"Task {task_id}: callback to {callback_url} failed: {str(e)}")


@app.post("/execute", response_model=TaskResponse)
def execute_task(request: TaskRequest) -> TaskResponse:
    if request.callback_url:
        thread = threading.Thread(
            target=_run_and_callback,
            args=(request.task_id, request.department, request.skill, request.brief, request.callback_url),
            daemon=True,
        )
        thread.start()
        return TaskResponse(task_id=request.task_id, status="accepted", result="")

    try:
        result = route_and_execute(request.department, request.skill, request.brief)
        return TaskResponse(task_id=request.task_id, status="completed", result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/orchestrate", response_model=TaskResponse)
def orchestrate_brief(request: TaskRequest) -> TaskResponse:
    try:
        result = agency.intake_brief(request.brief)
        return TaskResponse(task_id=request.task_id, status="completed", result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/operations/daily-briefing", response_model=TaskResponse)
def operations_daily_briefing(request: TaskRequest) -> TaskResponse:
    try:
        result = agency.operations.daily_briefing(request.brief)
        return TaskResponse(task_id=request.task_id, status="completed", result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/operations/optimize-process", response_model=TaskResponse)
def operations_optimize_process(request: TaskRequest) -> TaskResponse:
    try:
        result = agency.operations.optimize_process(request.brief)
        return TaskResponse(task_id=request.task_id, status="completed", result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sales/run-pipeline", response_model=TaskResponse)
def sales_run_pipeline(request: TaskRequest) -> TaskResponse:
    try:
        result = agency.sales.run_pipeline(request.brief)
        return TaskResponse(task_id=request.task_id, status="completed", result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sales/write-followup-sequence", response_model=TaskResponse)
def sales_write_followup_sequence(request: TaskRequest) -> TaskResponse:
    try:
        result = agency.sales.write_followup_sequence(request.brief, request.skill or "initial")
        return TaskResponse(task_id=request.task_id, status="completed", result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/marketing/run-campaign", response_model=TaskResponse)
def marketing_run_campaign(request: TaskRequest) -> TaskResponse:
    try:
        result = agency.marketing.run_campaign(request.brief)
        return TaskResponse(task_id=request.task_id, status="completed", result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/marketing/create-content", response_model=TaskResponse)
def marketing_create_content(request: TaskRequest) -> TaskResponse:
    try:
        result = agency.marketing.create_content(request.brief, request.skill or "blog")
        return TaskResponse(task_id=request.task_id, status="completed", result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/finance/generate-report", response_model=TaskResponse)
def finance_generate_report(request: TaskRequest) -> TaskResponse:
    try:
        result = agency.finance.generate_report(request.brief or "monthly")
        return TaskResponse(task_id=request.task_id, status="completed", result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/cto/audit-codebase", response_model=TaskResponse)
def cto_audit_codebase(request: TaskRequest) -> TaskResponse:
    try:
        result = agency.cto.audit_codebase(request.brief)
        return TaskResponse(task_id=request.task_id, status="completed", result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/cto/run-task", response_model=TaskResponse)
def cto_run_task(request: TaskRequest) -> TaskResponse:
    try:
        result = agency.cto.run_task(request.brief)
        return TaskResponse(task_id=request.task_id, status="completed", result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/cto/security-audit", response_model=TaskResponse)
def cto_security_audit(request: TaskRequest) -> TaskResponse:
    try:
        result = agency.cto.security_audit(request.brief)
        return TaskResponse(task_id=request.task_id, status="completed", result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/cto/deploy", response_model=TaskResponse)
def cto_deploy(request: TaskRequest) -> TaskResponse:
    try:
        result = agency.cto.deploy(request.brief)
        return TaskResponse(task_id=request.task_id, status="completed", result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def route_and_execute(department: str, skill: str, brief: str) -> str:
    department = department.lower()
    skill = skill.lower()

    routes = {
        "orchestrator": {
            "intake_brief": agency.intake_brief,
        },
        "operations": {
            "daily_briefing": agency.operations.daily_briefing,
            "optimize_process": agency.operations.optimize_process,
        },
        "sales": {
            "run_pipeline": agency.sales.run_pipeline,
        },
        "marketing": {
            "run_campaign": agency.marketing.run_campaign,
        },
        "finance": {
            "generate_report": agency.finance.generate_report,
        },
        "cto": {
            "audit_codebase": agency.cto.audit_codebase,
            "run_task": agency.cto.run_task,
            "security_audit": agency.cto.security_audit,
            "deploy": agency.cto.deploy,
        },
    }

    dept_routes = routes.get(department)
    if not dept_routes:
        raise ValueError(f"Unknown department: {department}")
    fn = dept_routes.get(skill)
    if not fn:
        raise ValueError(f"Unknown skill '{skill}' for department '{department}'")
    return fn(brief)


if __name__ == "__main__":
    import uvicorn
    print("=" * 56)
    print("       TRoyAI Agent Execution Server")
    print("       Starting at http://localhost:8300")
    print("       API docs at http://localhost:8300/docs")
    print("=" * 56)
    uvicorn.run(app, host="0.0.0.0", port=8300)
