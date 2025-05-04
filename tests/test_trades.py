from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base import Base, get_db
import pytest
from app.models.models import Trade, TradeStatus
from app.schemas.schemas import TradeCreate
from app.services.trade_service import create_trade, get_trades
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_create_trade(db_session):
    # Create a test trade
    trade_data = TradeCreate(
        trade_id="TEST001",
        trader="John Doe",
        asset_class="EQUITY",
        quantity=100,
        price=50.0
    )
    
    # Create the trade
    trade = create_trade(db_session, trade_data)
    
    # Verify the trade was created correctly
    assert trade.trade_id == "TEST001"
    assert trade.trader == "John Doe"
    assert trade.asset_class == "EQUITY"
    assert trade.quantity == 100
    assert trade.price == 50.0
    assert trade.status == TradeStatus.PENDING
    assert isinstance(trade.timestamp, datetime)

def test_get_trades_with_filters(db_session):
    # Create multiple test trades
    trades = [
        TradeCreate(trade_id=f"TEST{i}", trader="John Doe", asset_class="EQUITY", quantity=100, price=50.0)
        for i in range(1, 4)
    ]
    for trade in trades:
        create_trade(db_session, trade)
    
    # Create a trade with different asset class
    create_trade(db_session, TradeCreate(
        trade_id="TEST4",
        trader="John Doe",
        asset_class="FIXED_INCOME",
        quantity=50,
        price=100.0
    ))
    
    # Test filtering by trader
    filtered_trades = get_trades(db_session, trader="John Doe")
    assert len(filtered_trades) == 4
    
    # Test filtering by asset class
    filtered_trades = get_trades(db_session, asset_class="EQUITY")
    assert len(filtered_trades) == 3
    
    # Test pagination
    filtered_trades = get_trades(db_session, skip=1, limit=2)
    assert len(filtered_trades) == 2

def test_trade_validation(db_session):
    # Test invalid trade_id (empty)
    with pytest.raises(ValueError):
        create_trade(db_session, TradeCreate(
            trade_id="",
            trader="John Doe",
            asset_class="EQUITY",
            quantity=100,
            price=50.0
        ))
    
    # Test invalid quantity (negative)
    with pytest.raises(ValueError):
        create_trade(db_session, TradeCreate(
            trade_id="TEST001",
            trader="John Doe",
            asset_class="EQUITY",
            quantity=-100,
            price=50.0
        ))
    
    # Test invalid price (zero)
    with pytest.raises(ValueError):
        create_trade(db_session, TradeCreate(
            trade_id="TEST001",
            trader="John Doe",
            asset_class="EQUITY",
            quantity=100,
            price=0.0
        ))

def test_create_trade_api(client, db_session):
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

def test_get_trades_api(client, db_session):
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