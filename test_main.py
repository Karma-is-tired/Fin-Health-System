from fastapi.testclient import TestClient
from main import app
 
client = TestClient(app)
HEADERS = {"X-API-Key": "dev-secret-key-change-later"}
 
 
def test_root_endpoint_is_public():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
 
 
def test_health_score_requires_a_key():
    response = client.get("/health-score")  # no header at all
    assert response.status_code == 422  # FastAPI: required header missing
 
 
def test_health_score_rejects_wrong_key():
    response = client.get("/health-score", headers={"X-API-Key": "wrong-key"})
    assert response.status_code == 401
 
 
def test_health_score_with_correct_key():
    response = client.get("/health-score", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "overall" in data
    assert 0 <= data["overall"] <= 100
    assert set(data["scores"].keys()) == {
        "profitability", "cash_flow", "expense_control", "receivables", "budget"
    }
 
 
def test_financial_summary_with_correct_key():
    response = client.get("/financial-summary", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "revenue" in data
    assert "net_profit" in data
 
