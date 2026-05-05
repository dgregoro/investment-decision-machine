from enum import StrEnum


class DecisionType(StrEnum):
    buy = "buy"
    sell = "sell"
    hold = "hold"
    watch = "watch"
    reduce = "reduce"
    increase = "increase"


class DecisionStatus(StrEnum):
    draft = "draft"
    proposed = "proposed"
    approved = "approved"
    active = "active"
    closed = "closed"
    evaluated = "evaluated"
    rejected = "rejected"
