from app.services.reconciliation_service import run_reconciliation
from app.models.models import Trade, ReconciliationStatus
from app.schemas.schemas import TradeCreate
from app.services.trade_service import create_trade
import json
import pytest

def test_reconciliation_no_discrepancies(clean_db, setup_test_data):
    # Create trades that match the positions
    trades = [
        TradeCreate(trade_id="RECON_TEST1", trader="John Doe", asset_class="EQUITY", quantity=1000, price=50.0),
        TradeCreate(trade_id="RECON_TEST2", trader="John Doe", asset_class="FIXED_INCOME", quantity=500, price=100.0),
        TradeCreate(trade_id="RECON_TEST3", trader="John Doe", asset_class="COMMODITY", quantity=200, price=75.0),
        TradeCreate(trade_id="RECON_TEST4", trader="John Doe", asset_class="FOREX", quantity=10000, price=1.2)
    ]
    
    for trade in trades:
        create_trade(clean_db, trade)
    
    result = run_reconciliation(clean_db)
    assert result.status == ReconciliationStatus.SUCCESS
    assert not result.discrepancies

def test_reconciliation_with_quantity_discrepancy(clean_db, setup_test_data):
    # Create trades with quantity mismatch
    trades = [
        TradeCreate(trade_id="RECON_TEST1", trader="John Doe", asset_class="EQUITY", quantity=900, price=50.0),
        TradeCreate(trade_id="RECON_TEST2", trader="John Doe", asset_class="FIXED_INCOME", quantity=600, price=100.0),
        TradeCreate(trade_id="RECON_TEST3", trader="John Doe", asset_class="COMMODITY", quantity=200, price=75.0),
        TradeCreate(trade_id="RECON_TEST4", trader="John Doe", asset_class="FOREX", quantity=10000, price=1.2)
    ]
    
    for trade in trades:
        create_trade(clean_db, trade)
    
    result = run_reconciliation(clean_db)
    assert result.status == ReconciliationStatus.PARTIAL
    assert len(result.discrepancies) == 2
    assert any(d["asset_class"] == "EQUITY" and d["type"] == "quantity" for d in result.discrepancies)
    assert any(d["asset_class"] == "FIXED_INCOME" and d["type"] == "quantity" for d in result.discrepancies)

def test_reconciliation_with_price_discrepancy(clean_db, setup_test_data):
    # Create trades with price mismatch
    trades = [
        TradeCreate(trade_id="RECON_TEST1", trader="John Doe", asset_class="EQUITY", quantity=1000, price=55.0),
        TradeCreate(trade_id="RECON_TEST2", trader="John Doe", asset_class="FIXED_INCOME", quantity=500, price=105.0),
        TradeCreate(trade_id="RECON_TEST3", trader="John Doe", asset_class="COMMODITY", quantity=200, price=75.0),
        TradeCreate(trade_id="RECON_TEST4", trader="John Doe", asset_class="FOREX", quantity=10000, price=1.2)
    ]
    
    for trade in trades:
        create_trade(clean_db, trade)
    
    result = run_reconciliation(clean_db)
    assert result.status == ReconciliationStatus.PARTIAL
    assert len(result.discrepancies) == 2
    assert any(d["asset_class"] == "EQUITY" and d["type"] == "price" for d in result.discrepancies)
    assert any(d["asset_class"] == "FIXED_INCOME" and d["type"] == "price" for d in result.discrepancies)

def test_reconciliation_missing_asset_class(clean_db, setup_test_data):
    # Create trades with missing asset classes
    trades = [
        TradeCreate(trade_id="RECON_TEST1", trader="John Doe", asset_class="EQUITY", quantity=1000, price=50.0),
        TradeCreate(trade_id="RECON_TEST2", trader="John Doe", asset_class="FIXED_INCOME", quantity=500, price=100.0)
    ]
    
    for trade in trades:
        create_trade(clean_db, trade)
    
    result = run_reconciliation(clean_db)
    assert result.status == ReconciliationStatus.PARTIAL
    assert len(result.discrepancies) == 2
    assert any(d["asset_class"] == "COMMODITY" for d in result.discrepancies)
    assert any(d["asset_class"] == "FOREX" for d in result.discrepancies) 