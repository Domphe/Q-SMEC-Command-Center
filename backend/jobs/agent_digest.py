"""Background intelligence agent — runs every 30 minutes.

Summarizes recent high-urgency emails, writes to bridge.
Also generates a morning brief note at 7 AM daily.
"""

import json
import logging
import os
from datetime import datetime, timedelta

logger = logging.getLogger("agent_digest")

BRIDGE_PATH = os.getenv(
    "BRIDGE_PATH", "./bridge"
)


def run_agent_digest():
    """Main job — called by APScheduler every 30 min."""
    try:
        _run_digest()
    except Exception as e:
        logger.error("Digest failed: %s", e)


def _run_digest():
    from backend.database import engine
    from sqlmodel import Session, select
    from backend.models.email_cache import EmailCache

    cutoff = datetime.utcnow() - timedelta(minutes=35)

    with Session(engine) as session:
        stmt = (
            select(EmailCache)
            .where(EmailCache.date > cutoff)
            .where(
                (EmailCache.urgency == "respond")
                | (EmailCache.confidence < 0.6)
            )
            .order_by(EmailCache.date.desc())
            .limit(20)
        )
        emails = session.exec(stmt).all()

    summaries = []
    for email in emails:
        summary = _summarize_email(email)
        summaries.append(summary)

    digest = {
        "generated_at": datetime.utcnow().isoformat(),
        "period_minutes": 35,
        "email_count": len(summaries),
        "summaries": summaries,
        "action_items": [
            s for s in summaries
            if s.get("urgency") == "respond"
        ],
    }

    os.makedirs(BRIDGE_PATH, exist_ok=True)
    path = os.path.join(BRIDGE_PATH, "agent_digest.json")
    with open(path, "w") as f:
        json.dump(digest, f, indent=2, default=str)

    logger.info(
        "Digest written: %d emails, %d action items",
        len(summaries),
        len(digest["action_items"]),
    )


def _summarize_email(email):
    """Generate one-sentence summary via Claude Sonnet."""
    import asyncio
    from backend.services.ai_service import (
        call_claude, is_anthropic_configured,
    )

    base = {
        "email_id": email.id,
        "sender": email.from_name or email.from_addr,
        "subject": email.subject,
        "urgency": email.urgency,
        "category": email.category,
        "received_at": str(email.date),
    }

    if not is_anthropic_configured():
        base["summary"] = email.subject or ""
        return base

    prompt = (
        "Summarize this email in one sentence "
        "(max 25 words). Be specific about what "
        "action is needed if any.\n\n"
        "From: {sender}\n"
        "Subject: {subject}\n"
        "Body: {body}\n\n"
        "One sentence only:"
    ).format(
        sender=email.from_name or email.from_addr or "",
        subject=email.subject or "",
        body=(email.snippet or "")[:300],
    )

    try:
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(
            call_claude(prompt, max_tokens=60)
        )
        loop.close()
        text = result.get("result", "")
        base["summary"] = (text or email.subject).strip()
    except Exception:
        base["summary"] = email.subject or ""

    return base


def run_morning_brief():
    """Generate morning briefing note at 7 AM daily."""
    import asyncio
    from backend.database import engine
    from backend.models.note import Note
    from backend.services.ai_service import (
        call_claude, is_anthropic_configured,
    )
    from sqlmodel import Session, select

    if not is_anthropic_configured():
        logger.info("Skipping morning brief: no API key")
        return

    yesterday = datetime.utcnow() - timedelta(hours=24)

    with Session(engine) as session:
        from backend.models.email_cache import EmailCache
        stmt = (
            select(EmailCache)
            .where(EmailCache.date > yesterday)
            .order_by(EmailCache.date.desc())
        )
        emails = session.exec(stmt).all()

    respond = [
        e for e in emails if e.urgency == "respond"
    ]
    review = [
        e for e in emails if e.urgency == "review"
    ][:5]

    respond_lines = "\n".join(
        "- {} | {}".format(
            e.from_name or e.from_addr, e.subject,
        )
        for e in respond[:10]
    )
    review_lines = "\n".join(
        "- {} | {}".format(
            e.from_name or e.from_addr, e.subject,
        )
        for e in review
    )

    prompt = (
        "You are a chief of staff. Generate a concise "
        "morning briefing for Sal Dely (President/CIO, "
        "NIKET NA LLC, defense/quantum tech).\n\n"
        "Emails needing response today "
        "({respond_count} total):\n{respond_lines}\n\n"
        "Notable review items "
        "({review_count} total):\n{review_lines}\n\n"
        "Write a 3-5 sentence morning brief. Start with "
        "the most critical item. Be direct, executive "
        "tone. No bullet points."
    ).format(
        respond_count=len(respond),
        respond_lines=respond_lines or "(none)",
        review_count=len(review),
        review_lines=review_lines or "(none)",
    )

    try:
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(
            call_claude(prompt, max_tokens=300)
        )
        loop.close()
        brief_text = result.get("result", "")
        if not brief_text:
            logger.warning("Morning brief: empty response")
            return
    except Exception as e:
        logger.error("Morning brief failed: %s", e)
        return

    title = "Morning Brief - {}".format(
        datetime.now().strftime("%Y-%m-%d"),
    )

    with Session(engine) as session:
        note = Note(
            text="[{}]\n\n{}".format(title, brief_text),
            tag="action",
            status="pending",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(note)
        session.commit()

    logger.info("Morning brief note created: %s", title)
