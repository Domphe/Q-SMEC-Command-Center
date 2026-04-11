"""AI router — complexity scoring, model selection, and live execution."""

import asyncio
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session

from backend.database import get_session
from backend.models.task import AITask
from backend.services.model_router import score_complexity, select_model, select_tool
from backend.services.ai_service import call_claude, call_gemini, is_anthropic_configured, is_gemini_configured

router = APIRouter()


class RouteRequest(BaseModel):
    task_description: str
    context: Optional[dict] = None
    preferred_model: Optional[str] = None


class ExecuteRequest(BaseModel):
    task_description: str
    model: str
    context: Optional[dict] = None


@router.post("/route")
def route_task(req: RouteRequest):
    context = req.context or {}
    score = score_complexity(req.task_description, context)
    model_info = select_model(score, req.preferred_model)
    tool = select_tool(req.task_description)

    return {
        "complexity_score": score,
        "tool": tool,
        "estimated_tokens": max(500, score * 100),
        **model_info,
    }


@router.post("/execute")
async def execute_task(req: ExecuteRequest, session: Session = Depends(get_session)):
    """Execute a task using the specified AI model."""
    context = req.context or {}
    score = score_complexity(req.task_description, context)

    # Create task record
    task = AITask(
        description=req.task_description,
        complexity_score=score,
        recommended_model=req.model,
        actual_model=req.model,
        tool=select_tool(req.task_description),
        status="executing",
        created_at=datetime.now(timezone.utc),
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    # Dispatch to the right API
    model_lower = req.model.lower()
    if model_lower in ("gemini", "gemini-flash", "gemini-pro"):
        if not is_gemini_configured():
            task.status = "failed"
            task.result = "Gemini API key not configured"
            session.add(task)
            session.commit()
            return {"task_id": task.id, "status": "failed", "error": task.result}
        result = await call_gemini(req.task_description)
    else:
        if not is_anthropic_configured():
            task.status = "failed"
            task.result = "Anthropic API key not configured"
            session.add(task)
            session.commit()
            return {"task_id": task.id, "status": "failed", "error": task.result}

        # Map friendly names to model IDs
        model_map = {
            "opus": "claude-opus-4-20250514",
            "sonnet": "claude-sonnet-4-20250514",
            "haiku": "claude-haiku-4-5-20251001",
        }
        model_id = model_map.get(model_lower, model_lower)
        result = await call_claude(req.task_description, model=model_id)

    # Update task with result
    task.status = "completed" if not result.get("error") else "failed"
    task.result = result.get("result") or result.get("error")
    task.actual_model = result.get("model_used", req.model)
    task.tokens_used = result.get("tokens_used")
    task.duration_ms = result.get("duration_ms")
    task.completed_at = datetime.now(timezone.utc)
    session.add(task)
    session.commit()
    session.refresh(task)

    return {
        "task_id": task.id,
        "status": task.status,
        "result": task.result,
        "model_used": task.actual_model,
        "tokens_used": task.tokens_used,
        "duration_ms": task.duration_ms,
    }


@router.get("/status")
def ai_status():
    """Check which AI services are configured."""
    return {
        "anthropic": is_anthropic_configured(),
        "gemini": is_gemini_configured(),
    }
