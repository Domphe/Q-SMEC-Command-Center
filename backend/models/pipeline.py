"""Pipeline status model — UC pipeline tracking."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class PipelineStatusBase(SQLModel):
    name: str
    phase: Optional[str] = None  # Phase 0|Phase 1|Phase 2|Phase 3
    status: Optional[str] = None  # research|baseline|enhanced|deliverable
    progress: int = 0  # 0-100
    uc_type: Optional[str] = None  # acoustic_resonator|rf_transceiver|photonic_ir|inertial_sensor|quantum_sensing


class PipelineStatus(PipelineStatusBase, table=True):
    __tablename__ = "pipeline_status"

    uc: str = Field(primary_key=True)  # UC01, UC02, etc.
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class PipelineStatusCreate(PipelineStatusBase):
    uc: str
