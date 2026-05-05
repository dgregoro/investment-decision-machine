from typing import Any

from fastapi.testclient import TestClient

from app.core import database as database_module
from app.main import app
from app.models.enums import DecisionStatus
from app.models.trade_decision import TradeDecision


def test_decisions_router_registered() -> None:
    """Regression: CRUD router must remain mounted on the FastAPI app."""
    paths = app.openapi()["paths"]
    assert "/decisions/" in paths
    path_item = paths["/decisions/"]
    assert "post" in path_item and "get" in path_item


def _sample_create_body() -> dict[str, Any]:
    return {
        "symbol": "ACME",
        "decision_type": "buy",
        "thesis_summary": "Price below replacement value.",
        "time_horizon": "6-12 months",
        "confidence_score": 0.55,
        "assumptions": ["Margins stable"],
        "invalidation_conditions": ["Guidance miss"],
        "counter_arguments": ["Macro headwinds"],
        "planned_exit_conditions": ["Target hit"],
        "max_position_size_pct": 8.0,
        "notes": "via API",
    }


def test_post_creates_draft(client: TestClient) -> None:
    response = client.post("/decisions/", json=_sample_create_body())
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "draft"
    assert data["symbol"] == "ACME"
    assert data["id"] >= 1


def test_list_returns_created_decisions(client: TestClient) -> None:
    created = client.post("/decisions/", json=_sample_create_body())
    cid = created.json()["id"]

    listed = client.get("/decisions/")
    assert listed.status_code == 200
    ids = [row["id"] for row in listed.json()]
    assert cid in ids


def test_get_by_id_returns_one(client: TestClient) -> None:
    cid = client.post("/decisions/", json=_sample_create_body()).json()["id"]

    got = client.get(f"/decisions/{cid}")
    assert got.status_code == 200
    assert got.json()["id"] == cid


def test_get_missing_returns_404(client: TestClient) -> None:
    assert client.get("/decisions/99999").status_code == 404


def test_put_updates_only_provided_fields(client: TestClient) -> None:
    cid = client.post(
        "/decisions/",
        json={**_sample_create_body(), "thesis_summary": "Original thesis."},
    ).json()["id"]

    response = client.put(f"/decisions/{cid}", json={"notes": "Only notes changed"})
    assert response.status_code == 200
    body = response.json()
    assert body["notes"] == "Only notes changed"
    assert body["thesis_summary"] == "Original thesis."

    fetched = client.get(f"/decisions/{cid}")
    assert fetched.json()["thesis_summary"] == "Original thesis."


def test_put_rejects_status_in_payload(client: TestClient) -> None:
    cid = client.post("/decisions/", json=_sample_create_body()).json()["id"]

    response = client.put(
        f"/decisions/{cid}",
        json={"status": DecisionStatus.active.value},
    )
    assert response.status_code == 422

    still = client.get(f"/decisions/{cid}")
    assert still.json()["status"] == DecisionStatus.draft.value


def test_list_filter_status_draft(client: TestClient) -> None:
    database_module.init_db()
    cid_draft = client.post("/decisions/", json={"symbol": "ONE"}).json()["id"]

    factory = database_module.get_session_factory()
    session = factory()

    list_field_names = (
        "signal_sources",
        "assumptions",
        "invalidation_conditions",
        "counter_arguments",
        "planned_exit_conditions",
    )

    seeded_a: dict[str, list[str]] = {name: [] for name in list_field_names}
    seeded_b: dict[str, list[str]] = {name: [] for name in list_field_names}

    try:
        session.add_all(
            [
                TradeDecision(
                    status=DecisionStatus.proposed,
                    symbol="TWO",
                    confidence_score=0.5,
                    notes="seed",
                    **seeded_a,
                ),
                TradeDecision(
                    status=DecisionStatus.closed,
                    symbol="THREE",
                    confidence_score=0.5,
                    notes="seed",
                    **seeded_b,
                ),
            ]
        )
        session.commit()
    finally:
        session.close()

    response = client.get("/decisions/", params={"status": "draft"})
    assert response.status_code == 200
    symbols = {row["symbol"] for row in response.json()}
    assert "ONE" in symbols
    assert "TWO" not in symbols
    assert "THREE" not in symbols

    by_id = {row["id"]: row["symbol"] for row in client.get("/decisions/").json()}
    assert by_id[cid_draft] == "ONE"
