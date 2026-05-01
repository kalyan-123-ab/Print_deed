from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def base_payload():
    return {
        "envelope_id": "env1",
        "extraction": {
            "shipment_id": {"value": "SHP1", "confidence": 0.9},
            "recipient_name": {"value": "ABC", "confidence": 0.9},
            "commodity_code": {"value": "", "confidence": 0.5},
            "commodity_desc": {"value": "laptop", "confidence": 0.9},
            "ship_date": {"value": "2026-01-01", "confidence": 0.9}
        },
        "processing_instructions": {
            "workflow": "test",
            "confidence_threshold": 0.8,
            "hitl_on_failure": True
        }
    }

def test_happy_path():
    payload = base_payload()
    payload["extraction"]["commodity_code"]["confidence"] = 0.9
    res = client.post("/process", json=payload)
    assert res.status_code == 200

def test_low_confidence():
    payload = base_payload()
    payload["extraction"]["recipient_name"]["confidence"] = 0.5
    res = client.post("/process", json=payload)
    assert res.json()["decision"]["route"] == "hitl_review"

def test_invalid():
    payload = base_payload()
    del payload["extraction"]["shipment_id"]
    res = client.post("/process", json=payload)
    assert res.status_code == 422

def test_matching():
    payload = base_payload()
    res = client.post("/process", json=payload)
    assert res.json()["matching_results"] is not None

def test_llm_failure(monkeypatch):
    from app.services import matching_service

    async def fail(*args, **kwargs):
        raise Exception()

    monkeypatch.setattr(matching_service, "mock_llm", fail)

    payload = base_payload()
    res = client.post("/process", json=payload)
    assert res.json()["decision"]["route"] == "hitl_review"