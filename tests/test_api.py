from app.schemas.schemas import TradeCreate
from app.services.trade_service import create_trade
import pytest

def test_create_trade_endpoint(client, clean_db):
    response = client.post(
        "/api/v1/trades/",
        json={
            "trade_id": "TRADE001",
            "trader": "John Doe",
            "asset_class": "EQUITY",
            "quantity": 100,
            "price": 50.0
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["trade_id"] == "TRADE001"
    assert data["trader"] == "John Doe"
    assert data["asset_class"] == "EQUITY"
    assert data["quantity"] == 100
    assert data["price"] == 50.0

def test_get_trades_endpoint(client, clean_db):
    # Create a trade first
    client.post(
        "/api/v1/trades/",
        json={
            "trade_id": "TRADE001",
            "trader": "John Doe",
            "asset_class": "EQUITY",
            "quantity": 100,
            "price": 50.0
        }
    )
    
    response = client.get("/api/v1/trades/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["trade_id"] == "TRADE001"

def test_get_logs_endpoints(client, clean_db):
    response = client.get("/api/v1/logs/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_reconciliation_endpoint(client, clean_db, setup_test_data):
    response = client.post("/api/v1/reconciliation/")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "summary" in data
    assert "discrepancies" in data 