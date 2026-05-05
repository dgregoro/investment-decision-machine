from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.enums import DecisionStatus
from app.schemas.trade_decision import TradeDecisionCreate, TradeDecisionRead, TradeDecisionUpdate
from app.services import decision_service as decision_svc

router = APIRouter(prefix="/decisions", tags=["trade decisions"])

SessionDep = Annotated[Session, Depends(get_db)]


@router.post("/", response_model=TradeDecisionRead, status_code=status.HTTP_201_CREATED)
def create_decision(payload: TradeDecisionCreate, db: SessionDep) -> TradeDecisionRead:
    row = decision_svc.create_decision(db, payload)
    return TradeDecisionRead.model_validate(row)


@router.get("/", response_model=list[TradeDecisionRead])
def list_decisions(
    db: SessionDep,
    status_filter: Annotated[
        DecisionStatus | None,
        Query(alias="status", description="Filter by lifecycle status."),
    ] = None,
) -> list[TradeDecisionRead]:
    rows = decision_svc.list_decisions(db, status=status_filter)
    return [TradeDecisionRead.model_validate(row) for row in rows]


@router.get("/{decision_id}", response_model=TradeDecisionRead)
def get_decision(decision_id: int, db: SessionDep) -> TradeDecisionRead:
    row = decision_svc.get_decision(db, decision_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Decision not found")
    return TradeDecisionRead.model_validate(row)


@router.put("/{decision_id}", response_model=TradeDecisionRead)
def update_decision(
    decision_id: int,
    payload: TradeDecisionUpdate,
    db: SessionDep,
) -> TradeDecisionRead:
    row = decision_svc.update_decision(db, decision_id, payload)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Decision not found")
    return TradeDecisionRead.model_validate(row)
