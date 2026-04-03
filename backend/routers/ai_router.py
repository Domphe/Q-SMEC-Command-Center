"""AI router — complexity scoring and model selection."""

from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session

from backend.database import get_session
from backend.models.task import AITask

router = APIRouter()


class RouteRequest(BaseModel):
    task_description: str
    context: Optional[dict] = None
    preferred_model: Optional[str] = None


class ExecuteRequest(BaseModel):
    task_description: str
    model: str
    context: Optional[dict] = None


def score_complexity(task: str, context: dict) -> int:
    """Score task complexity on 0-100 scale."""
    score = 0

    # Length/depth indicators
    if len(task) > 500:
        score += 15
    if context.get("multi_repo"):
        score += 20
    if context.get("file_count", 0) > 5:
        score += 15

    # Task type indicators
    research_keywords = ["analyze", "synthesize", "architecture", "design", "strategy", "plan"]
    routine_keywords = ["categorize", "tag", "status", "check", "list", "format", "summarize"]

    task_lower = task.lower()
    if any(k in task_lower for k in research_keywords):
        score += 25
    if any(k in task_lower for k in routine_keywords):
        score -= 15

    # Domain complexity
    if "physics" in task_lower or "dft" in task_lower:
        score += 20
    if "playbook" in task_lower:
        score += 15
    if context.get("requires_web_search"):
        score += 10

    # UC count
    uc_count = context.get("uc_count", 0)
    if uc_count > 3:
        score += 15

    return max(0, min(100, score))


def select_model(score: int, preferred: Optional[str] = None) -> dict:
    """Select model based on complexity score."""
    if preferred:
        return {
            "recommended_model": preferred,
            "confidence": 0.9,
            "reasoning": "User preferred model: {}".format(preferred),
        }

    if score <= 30:
        return {
            "recommended_model": "sonnet",
            "confidence": 0.85,
            "reasoning": "Low complexity ({}) — Sonnet handles routine tasks efficiently".format(score),
            "alternate": None,
        }
    elif score <= 65:
        return {
            "recommended_model": "sonnet",
            "confidence": 0.7,
            "reasoning": "Medium complexity ({}) — Sonnet default with Opus fallback".format(score),
            "alternate": "opus",
        }
    else:
        return {
            "recommended_model": "opus",
            "confidence": 0.85,
            "reasoning": "High complexity ({}) — Opus for deep reasoning".format(score),
            "alternate": "sonnet",
        }


def select_tool(task: str) -> Optional[str]:
    """Determine which Claude tool should execute the task."""
    task_lower = task.lower()
    if any(k in task_lower for k in ["git", "script", "database", "ci", "pipeline", "deploy", "test"]):
        return "code"
    if any(k in task_lower for k in ["file", "document", "write", "edit", "bulk"]):
        return "cowork"
    if any(k in task_lower for k in ["research", "plan", "web", "strategy"]):
        return "project"
    return None


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
def execute_task(req: ExecuteRequest, session: Session = Depends(get_session)):
    """Placeholder for actual AI execution — Phase 5."""
    task = AITask(
        description=req.task_description,
        complexity_score=score_complexity(req.task_description, req.context or {}),
        recommended_model=req.model,
        actual_model=req.model,
        tool=select_tool(req.task_description),
        status="pending",
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return {
        "task_id": task.id,
        "status": "queued",
        "model": req.model,
        "message": "AI execution not yet wired — see Phase 5 in spec",
    }
