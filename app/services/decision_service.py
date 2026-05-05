from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import DecisionStatus
from app.models.trade_decision import TradeDecision
from app.schemas.trade_decision import TradeDecisionCreate, TradeDecisionUpdate


def create_decision(db: Session, payload: TradeDecisionCreate) -> TradeDecision:
    data = payload.model_dump()
    row = TradeDecision(status=DecisionStatus.draft, **data)
    db.add(row)
    db.flush()
    db.refresh(row)
    return row


def list_decisions(db: Session, *, status: DecisionStatus | None = None) -> list[TradeDecision]:
    stmt = select(TradeDecision).order_by(
        TradeDecision.created_at.desc(),
        TradeDecision.id.desc(),
    )
    if status is not None:
        stmt = stmt.where(TradeDecision.status == status)
    return list(db.scalars(stmt).unique().all())


def get_decision(db: Session, decision_id: int) -> TradeDecision | None:
    return db.get(TradeDecision, decision_id)


def update_decision(
    db: Session,
    decision_id: int,
    payload: TradeDecisionUpdate,
) -> TradeDecision | None:
    row = db.get(TradeDecision, decision_id)
    if row is None:
        return None

    updates = payload.model_dump(exclude_unset=True)

    writable = {
        "symbol",
        "decision_type",
        "thesis_summary",
        "time_horizon",
        "confidence_score",
        "signal_sources",
        "assumptions",
        "invalidation_conditions",
        "counter_arguments",
        "max_position_size_pct",
        "planned_entry_price",
        "planned_exit_conditions",
        "max_loss_pct",
        "notes",
    }

    for key, value in updates.items():
        if key in writable:
            setattr(row, key, value)

    db.flush()
    db.refresh(row)
    return row
