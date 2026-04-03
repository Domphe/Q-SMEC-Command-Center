"""Seed data from the static prototype — runs once if tables are empty."""

from datetime import date, datetime

from sqlmodel import Session, select

from backend.database import engine
from backend.models.client import Client
from backend.models.pipeline import PipelineStatus
from backend.models.email_cache import EmailCache


def seed_if_empty():
    """Seed clients, pipeline status, and email cache if tables are empty."""
    with Session(engine) as session:
        _seed_clients(session)
        _seed_pipeline(session)
        _seed_emails(session)
        session.commit()


def _seed_clients(session: Session):
    existing = session.exec(select(Client)).first()
    if existing:
        return

    clients_data = [
        # Active clients
        {"name": "TEP (Tucson Electric Power)", "status": "active", "type": "client",
         "last_touch": date(2026, 3, 28), "uc": ["UC21", "UC22"], "data_size": "49.9 MB",
         "nda_status": "signed", "priority": "high", "contact": "Direct",
         "sector": "Energy / Utility", "notes": "Infrastructure protection, energy grid hardening"},
        {"name": "Blue Marble Technologies", "status": "active", "type": "client",
         "last_touch": date(2026, 4, 2), "uc": ["UC01", "UC02", "UC03", "UC04"], "data_size": "40.5 MB",
         "nda_status": "signed", "priority": "high", "contact": "Dan Geraci",
         "sector": "Defense / DE", "notes": "Optical warfare, directed energy, C-UAS"},
        {"name": "Dan Carothers / RAMTDR", "status": "active", "type": "client",
         "last_touch": date(2026, 4, 1), "uc": ["UC03", "UC09"], "data_size": "0.2 MB",
         "nda_status": "signed", "priority": "medium", "contact": "Dan Carothers (dcphotonics)",
         "sector": "Photonics / RF", "notes": "InP alternatives, FPA ROIC, optical interconnects"},
        {"name": "Nikolay / Drone-Laser", "status": "active", "type": "client",
         "last_touch": date(2026, 3, 25), "uc": ["UC17", "UC19"], "data_size": "0.3 MB",
         "nda_status": "signed", "priority": "medium", "contact": "Nikolay",
         "sector": "Defense / C-UAS", "notes": "Counter-UAS laser systems"},
        # Prospects
        {"name": "Precise Systems", "status": "prospect", "type": "client",
         "last_touch": date(2026, 3, 31), "uc": ["UC01", "UC02", "UC04", "UC05", "UC06"],
         "data_size": "0 MB", "nda_status": "pending", "priority": "high",
         "contact": "Michael Risik", "sector": "Defense / EW / DE",
         "notes": "Golden Dome, NAMC RPP, DONRCO DE — 3 active opportunities"},
        {"name": "Optimal Cities / CII", "status": "prospect", "type": "client",
         "last_touch": date(2026, 4, 2), "uc": ["UC07", "UC21", "UC22"], "data_size": "0.3 MB",
         "nda_status": "unsigned (Sept 2025)", "priority": "high",
         "contact": "T. Finefrock, Alex Dely", "sector": "Energy / Smart City",
         "notes": "Energy Vertical, utility cyber, water utility, O/G/P/C expansion"},
        {"name": "Airtronics", "status": "prospect", "type": "client",
         "last_touch": date(2026, 3, 20), "uc": ["UC10", "UC11", "UC12", "UC13"],
         "data_size": "0.3 MB", "nda_status": "pending", "priority": "medium",
         "contact": "Direct", "sector": "EW / Antennas",
         "notes": "Electronic warfare sensor arrays"},
        # Partners & Research
        {"name": "University of Arizona", "status": "active", "type": "research",
         "last_touch": date(2026, 4, 2), "uc": [], "data_size": "0 MB",
         "nda_status": "n/a", "priority": "high", "contact": "Boulat Bash, Janet Roveda (Board)",
         "sector": "Academic / Quantum", "notes": "Quantum research collaboration — active discussions"},
        {"name": "NBU Bulgaria", "status": "active", "type": "partner",
         "last_touch": date(2026, 4, 2), "uc": [], "data_size": "0 MB",
         "nda_status": "n/a", "priority": "medium", "contact": "Todor Kolarov",
         "sector": "Academic / Defense", "notes": "Int'l conference April 23 — Alex presenting CII/NIKET"},
        {"name": "Blue Ridge Networks", "status": "prospect", "type": "partner",
         "last_touch": date(2026, 4, 2), "uc": ["UC07", "UC21", "UC22"], "data_size": "0 MB",
         "nda_status": "pending", "priority": "medium", "contact": "John Higginbotham",
         "sector": "Cybersecurity", "notes": "DragonFly strategic alliance — infrastructure cyber"},
        {"name": "ANELLO Photonics", "status": "prospect", "type": "partner",
         "last_touch": date(2026, 4, 2), "uc": ["UC04", "UC14"], "data_size": "0 MB",
         "nda_status": "pending", "priority": "medium", "contact": "via newsletter",
         "sector": "PNT / Photonics",
         "notes": "AMIGA next-gen potential, DeUVe magnetometer, non-GPS navigation"},
        {"name": "CII International", "status": "active", "type": "partner",
         "last_touch": date(2026, 4, 2), "uc": ["UC07", "UC21", "UC22"], "data_size": "0 MB",
         "nda_status": "signed", "priority": "high", "contact": "Alex Dely (CTO/Founder)",
         "sector": "Energy / Cyber / Defense",
         "notes": "Parent/sister company — Energy Vertical, utility cyber platform"},
        # Early stage
        {"name": "AIRTH Mining", "status": "early", "type": "client",
         "last_touch": date(2026, 3, 15), "uc": ["UC07"], "data_size": "0.1 MB",
         "nda_status": "pending", "priority": "low", "contact": "Direct",
         "sector": "Mining / Infrastructure", "notes": "Deep underground sensing applications"},
        {"name": "Green Valley Water Utility", "status": "early", "type": "client",
         "last_touch": date(2026, 4, 2), "uc": ["UC22"], "data_size": "0 MB",
         "nda_status": "pending", "priority": "low", "contact": "via ACC AI Docket",
         "sector": "Water / Utility",
         "notes": "ACC AI docket response — CII Energy Vertical approach"},
    ]

    for c in clients_data:
        session.add(Client(**c))


def _seed_pipeline(session: Session):
    existing = session.exec(select(PipelineStatus)).first()
    if existing:
        return

    pipeline_data = [
        {"uc": "UC01", "name": "MWIR Cascade Laser", "phase": "Phase 0",
         "status": "research", "progress": 40, "uc_type": "photonic_ir"},
        {"uc": "UC02", "name": "1MW DEW Thermal Mgmt", "phase": "Phase 0",
         "status": "research", "progress": 35, "uc_type": "photonic_ir"},
        {"uc": "UC03", "name": "FPA ROIC Sensor", "phase": "Phase 0",
         "status": "research", "progress": 45, "uc_type": "photonic_ir"},
        {"uc": "UC04", "name": "MEMS 10-DOF IMU", "phase": "Phase 0",
         "status": "research", "progress": 50, "uc_type": "inertial_sensor"},
        {"uc": "UC05", "name": "1GHz-5THz VCO", "phase": "Phase 1",
         "status": "baseline", "progress": 65, "uc_type": "acoustic_resonator"},
        {"uc": "UC06", "name": "GHz-THz Converter", "phase": "Phase 0",
         "status": "research", "progress": 30, "uc_type": "rf_transceiver"},
        {"uc": "UC07", "name": "Deep Underground Sensor", "phase": "Phase 0",
         "status": "research", "progress": 55, "uc_type": "quantum_sensing"},
        {"uc": "UC08", "name": "Counter-UAS EW Suite", "phase": "Phase 0",
         "status": "research", "progress": 20, "uc_type": "rf_transceiver"},
        {"uc": "UC09", "name": "FPA ROIC Advanced", "phase": "Phase 0",
         "status": "research", "progress": 30, "uc_type": "photonic_ir"},
        {"uc": "UC10", "name": "EW Jammer Module", "phase": "Phase 0",
         "status": "research", "progress": 25, "uc_type": "rf_transceiver"},
        {"uc": "UC11", "name": "EW Receiver Front-End", "phase": "Phase 0",
         "status": "research", "progress": 25, "uc_type": "rf_transceiver"},
        {"uc": "UC12", "name": "EW Signal Processor", "phase": "Phase 0",
         "status": "research", "progress": 20, "uc_type": "rf_transceiver"},
        {"uc": "UC13", "name": "EW Antenna Array", "phase": "Phase 0",
         "status": "research", "progress": 20, "uc_type": "rf_transceiver"},
        {"uc": "UC14", "name": "Rad-Hard Inertial Ref", "phase": "Phase 0",
         "status": "research", "progress": 25, "uc_type": "inertial_sensor"},
        {"uc": "UC15", "name": "Waveguide Atomic Clock", "phase": "Phase 0",
         "status": "research", "progress": 20, "uc_type": "quantum_sensing"},
        {"uc": "UC16", "name": "NKE Sensor Fusion", "phase": "Phase 0",
         "status": "research", "progress": 15, "uc_type": "quantum_sensing"},
        {"uc": "UC17", "name": "C-UAS Laser Turret", "phase": "Phase 0",
         "status": "research", "progress": 30, "uc_type": "photonic_ir"},
        {"uc": "UC18", "name": "High-Power Fiber Laser", "phase": "Phase 0",
         "status": "research", "progress": 15, "uc_type": "photonic_ir"},
        {"uc": "UC19", "name": "Drone Swarm Defeat", "phase": "Phase 0",
         "status": "research", "progress": 10, "uc_type": "rf_transceiver"},
        {"uc": "UC20", "name": "Optical Interconnect", "phase": "Phase 0",
         "status": "research", "progress": 20, "uc_type": "photonic_ir"},
        {"uc": "UC21", "name": "Microgrid Controller", "phase": "Phase 0",
         "status": "research", "progress": 35, "uc_type": "quantum_sensing"},
        {"uc": "UC22", "name": "Utility Cyber Hardening", "phase": "Phase 0",
         "status": "research", "progress": 30, "uc_type": "quantum_sensing"},
        {"uc": "UC23", "name": "NKE Comms Module", "phase": "Phase 0",
         "status": "research", "progress": 10, "uc_type": "rf_transceiver"},
    ]

    for p in pipeline_data:
        session.add(PipelineStatus(**p))


def _seed_emails(session: Session):
    existing = session.exec(select(EmailCache)).first()
    if existing:
        return

    emails_data = [
        {"id": "1", "from_addr": "adely@cii-international.com", "from_name": "Alex Dely",
         "to_addr": "NIKET Team", "subject": "Fwd: War gaming in the age of AI",
         "date": datetime(2026, 4, 3), "snippet": "War gaming AI research forward — defense strategy relevance",
         "category": "research", "uc": None, "client": None, "has_attachment": False,
         "is_unread": True, "action_required": False, "categorized_by": "rule"},
        {"id": "2", "from_addr": "adely@cii-international.com", "from_name": "Alex Dely",
         "to_addr": "Dan Geraci, Team",
         "subject": "Re: Green Valley Water Utility Response to ACC AI Docket",
         "date": datetime(2026, 4, 2),
         "snippet": "Validating CII Energy Vertical approach for water utility cyber",
         "category": "client", "uc": None, "client": "Optimal Cities / CII",
         "has_attachment": False, "is_unread": True, "action_required": True,
         "categorized_by": "rule"},
        {"id": "3", "from_addr": "adely@cii-international.com", "from_name": "Alex Dely",
         "to_addr": "Todor Kolarov (NBU)",
         "subject": "Re: NBU Int Conf April 23 // Alex Dely CII/NIKET Presentation",
         "date": datetime(2026, 4, 2),
         "snippet": "Confirming NBU International Conference presentation April 23",
         "category": "business", "uc": None, "client": "NBU Bulgaria",
         "has_attachment": False, "is_unread": True, "action_required": True,
         "categorized_by": "rule"},
        {"id": "5", "from_addr": "adely@cii-international.com", "from_name": "Alex Dely",
         "to_addr": "NIKET Board", "subject": "Fwd: ANELLO NEWSLETTER | MAR 2026",
         "date": datetime(2026, 4, 2),
         "snippet": "QSMEC AMIGA could be next gen for ANELLO and DeUVe magnetometer",
         "category": "research", "uc": "UC04/UC14", "client": "ANELLO Photonics",
         "has_attachment": False, "is_unread": True, "action_required": True,
         "categorized_by": "rule"},
        {"id": "11", "from_addr": "mrisik@goprecise.com", "from_name": "Michael Risik (Precise)",
         "to_addr": "Sal Dely",
         "subject": "NAMC RPP A&M: Electronic Warfare Sensors & Effects",
         "date": datetime(2026, 4, 2),
         "snippet": "EW sensors procurement opportunity — NAMC RPP program",
         "category": "opportunity", "uc": "UC05/UC06/UC10-UC13", "client": "Precise Systems",
         "has_attachment": False, "is_unread": True, "action_required": True,
         "categorized_by": "rule"},
        {"id": "12", "from_addr": "mrisik@goprecise.com", "from_name": "Michael Risik (Precise)",
         "to_addr": "Sal Dely",
         "subject": "DONRCO Open Call - Directed Energy Weapon Systems",
         "date": datetime(2026, 4, 1),
         "snippet": "Navy directed energy weapons open call — UC01/UC02/UC04 relevant",
         "category": "opportunity", "uc": "UC01/UC02/UC04", "client": "Precise Systems",
         "has_attachment": False, "is_unread": True, "action_required": True,
         "categorized_by": "rule"},
        {"id": "13", "from_addr": "mrisik@goprecise.com", "from_name": "Michael Risik (Precise)",
         "to_addr": "Sal Dely",
         "subject": "RE: Precise SHIELD Golden Dome Collaboration Meetings",
         "date": datetime(2026, 3, 31),
         "snippet": "Golden Dome missile defense collaboration — active pursuit",
         "category": "opportunity", "uc": None, "client": "Precise Systems",
         "has_attachment": False, "is_unread": True, "action_required": True,
         "categorized_by": "rule"},
        {"id": "14", "from_addr": "boulat@arizona.edu", "from_name": "Boulat Bash (U of A)",
         "to_addr": "NIKET Team",
         "subject": "Re: quantum discussion NIKET and UofA team",
         "date": datetime(2026, 4, 2),
         "snippet": "University of Arizona quantum research collaboration discussion",
         "category": "business", "uc": None, "client": "University of Arizona",
         "has_attachment": False, "is_unread": True, "action_required": True,
         "categorized_by": "rule"},
    ]

    for e in emails_data:
        session.add(EmailCache(**e))
