"""AI service — Anthropic (Claude) and Google (Gemini) API wrappers."""

import time

from backend.config import settings


def is_anthropic_configured() -> bool:
    return bool(settings.ANTHROPIC_API_KEY) and not settings.ANTHROPIC_API_KEY.startswith("sk-ant-REPLACE")


def is_gemini_configured() -> bool:
    return bool(settings.GEMINI_API_KEY) and not settings.GEMINI_API_KEY.startswith("AIza_REPLACE")


async def call_claude(prompt: str, model: str = "claude-sonnet-4-20250514", max_tokens: int = 1024) -> dict:
    """Call Claude API and return result with metadata."""
    if not is_anthropic_configured():
        return {"error": "Anthropic API key not configured", "result": None}

    import anthropic

    client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    start = time.time()

    try:
        response = await client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        duration_ms = int((time.time() - start) * 1000)

        result_text = ""
        for block in response.content:
            if hasattr(block, "text"):
                result_text += block.text

        return {
            "result": result_text,
            "model_used": response.model,
            "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "duration_ms": duration_ms,
            "error": None,
        }
    except Exception as e:
        return {"error": str(e), "result": None, "duration_ms": int((time.time() - start) * 1000)}


async def call_gemini(prompt: str, model: str = "gemini-2.0-flash", max_tokens: int = 1024) -> dict:
    """Call Gemini API and return result with metadata."""
    if not is_gemini_configured():
        return {"error": "Gemini API key not configured", "result": None}

    import asyncio

    from google import genai

    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    start = time.time()

    try:
        # genai Client is sync — wrap in thread to avoid blocking event loop
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=model,
            contents=prompt,
        )
        duration_ms = int((time.time() - start) * 1000)

        return {
            "result": response.text,
            "model_used": model,
            "tokens_used": getattr(response, "usage_metadata", {}).get("total_token_count", 0)
            if hasattr(response, "usage_metadata")
            else 0,
            "duration_ms": duration_ms,
            "error": None,
        }
    except Exception as e:
        return {"error": str(e), "result": None, "duration_ms": int((time.time() - start) * 1000)}
