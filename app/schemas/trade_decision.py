from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import DecisionStatus, DecisionType


class TradeDecisionCreate(BaseModel):
    """Payload for inserting a draft decision."""

    symbol: str | None = None
    decision_type: DecisionType | None = None
    thesis_summary: str | None = None
    time_horizon: str | None = None
    confidence_score: float = Field(default=0.5, ge=0.0, le=1.0)
    signal_sources: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    invalidation_conditions: list[str] = Field(default_factory=list)
    counter_arguments: list[str] = Field(default_factory=list)
    max_position_size_pct: float | None = None
    planned_entry_price: float | None = None
    planned_exit_conditions: list[str] = Field(default_factory=list)
    max_loss_pct: float | None = None
    notes: str = ""


class TradeDecisionUpdate(BaseModel):
    """Partial update of an existing decision."""

    symbol: str | None = None
    decision_type: DecisionType | None = None
    thesis_summary: str | None = None
    time_horizon: str | None = None
    confidence_score: float | None = Field(default=None, ge=0.0, le=1.0)
    signal_sources: list[str] | None = None
    assumptions: list[str] | None = None
    invalidation_conditions: list[str] | None = None
    counter_arguments: list[str] | None = None
    max_position_size_pct: float | None = None
    planned_entry_price: float | None = None
    planned_exit_conditions: list[str] | None = None
    max_loss_pct: float | None = None
    notes: str | None = None


class TradeDecisionRead(BaseModel):
    """ORM projection for APIs and tests."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    symbol: str | None
    decision_type: DecisionType | None
    status: DecisionStatus
    created_at: datetime
    updated_at: datetime
    thesis_summary: str | None
    time_horizon: str | None
    confidence_score: float
    signal_sources: list[str]
    assumptions: list[str]
    invalidation_conditions: list[str]
    counter_arguments: list[str]
    max_position_size_pct: float | None
    planned_entry_price: float | None
    planned_exit_conditions: list[str]
    max_loss_pct: float | None
    notes: str
