from fastapi.testclient import TestClient

from src.api import API_KEY, app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_missing_api_key_is_rejected():
    response = client.post("/predict", json={"url": "https://www.google.com"})
    assert response.status_code == 401


def test_invalid_url_is_rejected():
    response = client.post(
        "/predict", json={"url": "not-a-url"}, headers={"X-API-Key": API_KEY}
    )
    assert response.status_code == 422


def test_prediction_response():
    response = client.post(
        "/predict",
        json={"url": "http://secure-login-verify.example.com"},
        headers={"X-API-Key": API_KEY},
    )
    assert response.status_code == 200
    assert response.json()["prediction"] in {"legitimate", "phishing"}
    assert 0 <= response.json()["confidence"] <= 1
