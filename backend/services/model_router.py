"""Model router — complexity scoring and model/tool selection.

Moved from routers/ai_router.py to services/ for reuse across the app
(e.g., email triage AI fallback, note routing).
"""

from typing import Optional


def score_complexity(task: str, context: Optional[dict] = None) -> int:
    """Score task complexity on 0-100 scale."""
    context = context or {}
    score = 0

    if len(task) > 500:
        score += 15
    if context.get("multi_repo"):
        score += 20
    if context.get("file_count", 0) > 5:
        score += 15

    research_keywords = ["analyze", "synthesize", "architecture", "design", "strategy", "plan"]
    routine_keywords = ["categorize", "tag", "status", "check", "list", "format", "summarize"]

    task_lower = task.lower()
    if any(k in task_lower for k in research_keywords):
        score += 25
    if any(k in task_lower for k in routine_keywords):
        score -= 15

    if "physics" in task_lower or "dft" in task_lower:
        score += 20
    if "playbook" in task_lower:
        score += 15
    if context.get("requires_web_search"):
        score += 10

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
            "alternate": None,
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
