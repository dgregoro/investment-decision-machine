from sqlalchemy import inspect

from app.core import database as database_module
from app.models import TradeDecision
from app.models.enums import DecisionStatus, DecisionType
from app.schemas.trade_decision import TradeDecisionCreate, TradeDecisionRead


def test_trade_decisions_table_created_on_init() -> None:
    database_module.init_db()

    inspector = inspect(database_module.get_engine())
    tables = inspector.get_table_names()

    assert "trade_decisions" in tables


def test_trade_decision_orm_round_trip_matches_read_schema() -> None:
    database_module.init_db()
    payload = TradeDecisionCreate(
        symbol="ACME",
        decision_type=DecisionType.buy,
        thesis_summary="Valuation disconnect vs peers.",
        time_horizon="6-12 months",
        assumptions=["Stable demand", "No regulatory shock"],
        invalidation_conditions=["Two margin misses"],
        counter_arguments=["Cyclical risk"],
        max_position_size_pct=5.5,
        planned_exit_conditions=["Take profit band hit"],
        confidence_score=0.41,
        notes="Step 2 smoke test.",
    )

    factory = database_module.get_session_factory()
    with factory() as session:
        row = TradeDecision(**payload.model_dump())
        session.add(row)
        session.commit()

        session.refresh(row)
        read = TradeDecisionRead.model_validate(row)

    assert read.id > 0
    assert read.symbol == "ACME"
    assert read.decision_type is DecisionType.buy
    assert read.status is DecisionStatus.draft
    assert read.signal_sources == []
    assert read.assumptions == payload.assumptions
    assert read.confidence_score == 0.41
