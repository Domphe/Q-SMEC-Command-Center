"""Email triage — rule-based categorization with content override
and AI fallback for low-confidence results."""

import json
import logging
import os
import re
from typing import Optional

logger = logging.getLogger(__name__)

AI_FALLBACK_ENABLED = (
    os.getenv("AI_FALLBACK_ENABLED", "true").lower() == "true"
)
AI_FALLBACK_THRESHOLD = float(
    os.getenv("AI_FALLBACK_THRESHOLD", "0.5")
)


# Known sender patterns
SENDER_RULES = {
    "adely@cii-international.com": {
        "default": "research", "weight": 0.6,
    },
    "a.dely@niketllc.com": {
        "default": "business", "weight": 0.7,
    },
    "mrisik@goprecise.com": {
        "default": "opportunity", "weight": 0.8,
    },
    "boulat@arizona.edu": {
        "default": "research", "weight": 0.7,
    },
    "jbh@blueridgenetworks.com": {
        "default": "business", "weight": 0.6,
    },
    "tlfinefrock@cii-international.com": {
        "default": "client", "weight": 0.6,
    },
}

# UC pattern matching
UC_PATTERNS = {
    r"directed energy|DEW|laser weapon": ["UC01", "UC02"],
    r"MWIR|cascade laser|infrared": ["UC01", "UC03"],
    r"EW|electronic warfare|jammer": [
        "UC05", "UC06", "UC10-UC13",
    ],
    r"VCO|oscillator|resonator": ["UC05"],
    r"underground|mining|infrastructure": ["UC07"],
    r"PNT|navigation|timing|inertial": ["UC14", "UC15"],
    r"counter.?UAS|drone|C-UAS": ["UC04", "UC08", "UC17"],
    r"microgrid|energy|utility|grid": ["UC21", "UC22"],
    r"FPA|ROIC|focal plane": ["UC03", "UC09"],
    r"MEMS|IMU|10-DOF": ["UC04"],
}

# Client pattern matching
CLIENT_PATTERNS = {
    r"precise|golden dome|SHIELD": "Precise Systems",
    r"blue marble|geraci": "Blue Marble Technologies",
    r"carothers|RAMTDR|dcphotonics|InP": (
        "Dan Carothers / RAMTDR"
    ),
    r"TEP|tucson electric": "TEP (Tucson Electric Power)",
    r"CII|energy vertical|utility cyber": (
        "Optimal Cities / CII"
    ),
    r"arizona|UofA|boulat": "University of Arizona",
    r"NBU|kolarov|bulgaria": "NBU Bulgaria",
    r"anello|DeUVe|AMIGA": "ANELLO Photonics",
    r"blue ridge|dragonfly|higginbotham": (
        "Blue Ridge Networks"
    ),
    r"airtronics": "Airtronics",
    r"nikolay|drone.?laser": "Nikolay / Drone-Laser",
}

# Content keyword groups for override detection
OPPORTUNITY_KEYWORDS = [
    "opportunity", "rfp", "rfq", "solicitation",
    "open call", "procurement", "contract",
    "proposal", "bid", "sow", "statement of work",
]

CLIENT_KEYWORDS = [
    "invoice", "deliverable", "milestone",
    "status update", "review meeting", "nda",
    "follow up", "follow-up",
]

PIPELINE_KEYWORDS = [
    "dft", "simulation", "benchmark", "phase 0",
    "phase 1", "phase 2", "phase 3", "pipeline",
    "use case", "uc_", "workflow",
]

# Trimmed action keywords — removed overly broad terms
ACTION_KEYWORDS = [
    "urgent", "deadline", "by end of day", "eod",
    "need by", "waiting on you", "respond", "sign",
    "approve", "contract", "proposal due", "asap",
    "action required", "reply needed",
]


def categorize_email(email):
    """Categorize an email using rule-based matching.

    Returns dict with: category, uc, client, action_required,
    urgency, confidence, categorized_by
    """
    text = "{} {} {}".format(
        email.get("subject", ""),
        email.get("snippet", ""),
        email.get("from_name", ""),
    )
    from_addr = email.get("from_addr", "").lower()
    text_lower = text.lower()

    # Step 0: Check learned sender rules first
    sender_category = None
    confidence = 0.3
    sender_category = _check_learned_rules(from_addr)
    if sender_category:
        confidence = 0.8

    # Step 1: Static sender rules (if no learned rule)
    if not sender_category:
        for sender, rule in SENDER_RULES.items():
            if sender in from_addr:
                sender_category = rule["default"]
                confidence = rule["weight"]
                break

    # Step 2: UC detection
    ucs = []
    for pattern, uc_list in UC_PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE):
            ucs.extend(uc_list)
    uc_str = "/".join(sorted(set(ucs))) if ucs else None

    # Step 3: Client detection
    client = None
    for pattern, client_name in CLIENT_PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE):
            client = client_name
            break

    # Step 4: ALWAYS run content analysis (fixes override bug)
    content_category = None
    content_score = 0

    opp_hits = sum(
        1 for k in OPPORTUNITY_KEYWORDS if k in text_lower
    )
    cli_hits = sum(
        1 for k in CLIENT_KEYWORDS if k in text_lower
    )
    pip_hits = sum(
        1 for k in PIPELINE_KEYWORDS if k in text_lower
    )

    best_hits = max(opp_hits, cli_hits, pip_hits)
    if best_hits >= 2:
        content_score = min(0.9, 0.5 + (best_hits * 0.1))
        if opp_hits >= cli_hits and opp_hits >= pip_hits:
            content_category = "opportunity"
        elif cli_hits >= pip_hits:
            content_category = "client"
        else:
            content_category = "pipeline"

    # Resolve: content wins if more confident than sender
    if content_category and content_score > confidence:
        category = content_category
        confidence = content_score
    elif sender_category:
        category = sender_category
    elif content_category:
        category = content_category
        confidence = content_score
    elif client:
        category = "client"
        confidence = 0.6
    elif ucs:
        category = "research"
        confidence = 0.5
    else:
        category = "research"
        confidence = 0.3

    # Step 4b: AI fallback for low confidence
    categorized_by = "rule"
    if confidence < AI_FALLBACK_THRESHOLD and AI_FALLBACK_ENABLED:
        ai_result = ai_categorize(email)
        if ai_result:
            ai_conf = ai_result.get("confidence", 0)
            if ai_conf > confidence:
                category = ai_result["category"]
                urgency_hint = ai_result.get("urgency")
                confidence = ai_conf
                categorized_by = "ai"

    # Step 5: Action required (trimmed keywords)
    action_required = False
    if any(k in text_lower for k in ACTION_KEYWORDS):
        action_required = True
    if category == "opportunity":
        action_required = True

    # Step 6: Three-tier urgency
    urgency = _compute_urgency(
        category, action_required, text_lower,
    )

    return {
        "category": category,
        "uc": uc_str,
        "client": client,
        "action_required": action_required,
        "urgency": urgency,
        "confidence": confidence,
        "categorized_by": categorized_by,
    }


def _compute_urgency(category, action_required, text_lower):
    """Determine urgency tier: respond / review / archive."""
    if action_required:
        return "respond"

    deadline_keywords = [
        "urgent", "deadline", "eod", "asap",
        "by end of day", "need by",
    ]
    if any(k in text_lower for k in deadline_keywords):
        return "respond"

    archive_categories = ["administrative", "personal"]
    if category in archive_categories:
        # Unless it has action keywords
        if not any(k in text_lower for k in ACTION_KEYWORDS):
            return "archive"

    if category == "noise":
        return "archive"

    return "review"


def _check_learned_rules(from_addr):
    """Check learned_sender_rules table for this sender."""
    try:
        from backend.database import engine
        from sqlmodel import Session, select
        from backend.models.email_feedback import (
            LearnedSenderRule,
        )
        with Session(engine) as session:
            stmt = select(LearnedSenderRule).where(
                LearnedSenderRule.sender == from_addr,
            )
            rule = session.exec(stmt).first()
            if rule:
                return rule.category
    except Exception:
        pass
    return None


def ai_categorize(email_dict):
    """Call Claude Sonnet when rule confidence is low.

    Runs synchronously via asyncio for background job compat.
    """
    import asyncio
    from backend.services.ai_service import (
        call_claude, is_anthropic_configured,
    )

    if not is_anthropic_configured():
        return None

    prompt = (
        "You are an email triage assistant for NIKET NA LLC, "
        "a defense/quantum technology company.\n\n"
        "Categorize this email into exactly ONE category:\n"
        "- opportunity: RFPs, contracts, sales leads\n"
        "- client: existing client communications\n"
        "- pipeline: quantum research, technical work\n"
        "- administrative: HR, IT, invoices, internal\n"
        "- personal: non-work personal emails\n"
        "- research: papers, newsletters, industry news\n\n"
        "Also determine urgency:\n"
        "- respond: needs action within 24 hours\n"
        "- review: worth reading\n"
        "- archive: can be ignored\n\n"
        "Email:\n"
        "From: {sender}\n"
        "Subject: {subject}\n"
        "Body (first 500 chars): {body}\n\n"
        'Reply JSON only: {{"category": "...", '
        '"urgency": "...", "confidence": 0.0-1.0, '
        '"reason": "one sentence"}}'
    ).format(
        sender=email_dict.get("from_addr", ""),
        subject=email_dict.get("subject", ""),
        body=(email_dict.get("snippet", "") or "")[:500],
    )

    try:
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(
            call_claude(prompt, max_tokens=200)
        )
        loop.close()

        text = result.get("result")
        if not text:
            return None
        parsed = json.loads(text.strip())
        parsed["categorized_by"] = "ai"
        return parsed
    except Exception as e:
        logger.warning("AI categorize failed: %s", e)
        return None


def maybe_learn_sender_rule(sender, session):
    """If 3+ manual corrections for same sender -> same
    category, add to learned_sender_rules."""
    from sqlmodel import select, func
    from backend.models.email_feedback import (
        EmailFeedback, LearnedSenderRule,
    )
    from backend.models.email_cache import EmailCache

    try:
        stmt = (
            select(
                EmailFeedback.corrected_category,
                func.count(EmailFeedback.id).label("cnt"),
            )
            .join(
                EmailCache,
                EmailFeedback.email_id == EmailCache.id,
            )
            .where(EmailCache.from_addr == sender)
            .where(EmailFeedback.corrected_by == "manual")
            .group_by(EmailFeedback.corrected_category)
            .order_by(
                func.count(EmailFeedback.id).desc(),
            )
            .limit(1)
        )
        row = session.exec(stmt).first()
        if row and row[1] >= 3:
            existing = session.get(
                LearnedSenderRule, sender,
            )
            if existing:
                existing.category = row[0]
                existing.sample_count = row[1]
                from datetime import datetime
                existing.updated_at = datetime.utcnow()
            else:
                rule = LearnedSenderRule(
                    sender=sender,
                    category=row[0],
                    confidence=0.8,
                    sample_count=row[1],
                )
                session.add(rule)
            session.commit()
            logger.info(
                "Learned rule: %s -> %s (%d samples)",
                sender, row[0], row[1],
            )
    except Exception as e:
        logger.warning("Learn rule failed: %s", e)
