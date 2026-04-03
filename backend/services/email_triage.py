"""Email triage — rule-based categorization with AI fallback."""

import re
from typing import Optional


# Known sender patterns
SENDER_RULES = {
    "adely@cii-international.com": {"default": "research", "weight": 0.6},
    "a.dely@niketllc.com": {"default": "business", "weight": 0.7},
    "mrisik@goprecise.com": {"default": "opportunity", "weight": 0.8},
    "boulat@arizona.edu": {"default": "research", "weight": 0.7},
    "jbh@blueridgenetworks.com": {"default": "business", "weight": 0.6},
    "tlfinefrock@cii-international.com": {"default": "client", "weight": 0.6},
}

# UC pattern matching
UC_PATTERNS = {
    r"directed energy|DEW|laser weapon": ["UC01", "UC02"],
    r"MWIR|cascade laser|infrared": ["UC01", "UC03"],
    r"EW|electronic warfare|jammer": ["UC05", "UC06", "UC10-UC13"],
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
    r"carothers|RAMTDR|dcphotonics|InP": "Dan Carothers / RAMTDR",
    r"TEP|tucson electric": "TEP (Tucson Electric Power)",
    r"CII|energy vertical|utility cyber": "Optimal Cities / CII",
    r"arizona|UofA|boulat": "University of Arizona",
    r"NBU|kolarov|bulgaria": "NBU Bulgaria",
    r"anello|DeUVe|AMIGA": "ANELLO Photonics",
    r"blue ridge|dragonfly|higginbotham": "Blue Ridge Networks",
    r"airtronics": "Airtronics",
    r"nikolay|drone.?laser": "Nikolay / Drone-Laser",
}


def categorize_email(email: dict) -> dict:
    """Categorize an email using rule-based matching.

    Returns dict with: category, uc, client, action_required, confidence, categorized_by
    """
    text = "{} {} {}".format(
        email.get("subject", ""),
        email.get("snippet", ""),
        email.get("from_name", ""),
    )
    from_addr = email.get("from_addr", "").lower()

    category = None
    confidence = 0.0

    # Step 1: Sender rules
    for sender, rule in SENDER_RULES.items():
        if sender in from_addr:
            category = rule["default"]
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

    # Step 4: Override category based on content
    text_lower = text.lower()
    if not category:
        if any(k in text_lower for k in ["opportunity", "rfp", "rfq", "solicitation", "open call", "procurement"]):
            category = "opportunity"
            confidence = 0.7
        elif client:
            category = "client"
            confidence = 0.6
        elif ucs:
            category = "research"
            confidence = 0.5
        else:
            category = "research"
            confidence = 0.3

    # Step 5: Action required heuristic
    action_required = False
    if any(k in text_lower for k in [
        "action", "respond", "reply", "deadline", "urgent", "asap",
        "meeting", "conference", "collaboration", "opportunity",
        "open call", "rfp", "rfq",
    ]):
        action_required = True
    if category == "opportunity":
        action_required = True

    return {
        "category": category,
        "uc": uc_str,
        "client": client,
        "action_required": action_required,
        "confidence": confidence,
        "categorized_by": "rule",
    }
