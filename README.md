# investment-decision-machine

Starter API for human-in-the-loop **investment decision discipline** — structured checkpoints, journaling, and future evaluation workflows. Step 2 adds the **`TradeDecision`** persistence model plus Pydantic DTOs; SQLite tables are created when the FastAPI app starts (`lifespan`).

## Disclaimer

Nothing here is personalized financial, legal, or tax advice, and nothing here recommends buying or selling any security. The software does not execute trades. You are solely responsible for any investment choices.

## Domain (Step 2)

- **`TradeDecision`** SQLAlchemy model mapped to SQLite (`trade_decisions` table).
- Enums **`DecisionType`** and **`DecisionStatus`** (lifecycle transitions wired in later steps).
- Request/response DTOs: **`TradeDecisionCreate`**, **`TradeDecisionUpdate`**, **`TradeDecisionRead`**.

## Development

Requirements: Python 3.12+.

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
uv run mypy app
uv run uvicorn app.main:app --reload
```

Configuration: copy `.env.example` to `.env` if you need to override `DATABASE_URL`. On startup the app runs `CREATE TABLE` for registered models via SQLAlchemy `metadata.create_all`.
