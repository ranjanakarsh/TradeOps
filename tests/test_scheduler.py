import pytest
from datetime import datetime, timedelta
from app.services.scheduler_service import scheduler, run_scheduled_reconciliation, start_scheduler
from app.db.base import Base, SessionLocal
from app.models.models import OperationalLog, ReconciliationLog, ReconciliationStatus
from app.schemas.schemas import TradeCreate
from app.services.trade_service import create_trade
import os
import shutil
from apscheduler.schedulers.background import BackgroundScheduler
import pandas as pd
from sqlalchemy import create_engine

# Test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def setup_test_data(tmp_path):
    # Create a test positions.csv file in the test directory
    positions_data = {
        'asset_class': ['EQUITY', 'FIXED_INCOME', 'COMMODITY', 'FOREX'],
        'quantity': [1000, 500, 200, 10000],
        'price': [50.0, 100.0, 75.0, 1.2]
    }
    df = pd.DataFrame(positions_data)
    csv_path = tmp_path / 'positions.csv'
    df.to_csv(csv_path, index=False)
    
    # Update the path in the reconciliation service
    import app.services.reconciliation_service as rs
    rs.POSITIONS_FILE = str(csv_path)
    
    yield str(csv_path)
    
    # Clean up
    if os.path.exists(csv_path):
        os.remove(csv_path)

def test_scheduled_reconciliation(clean_db, setup_test_data):
    try:
        # Create some test trades with unique IDs
        trades = [
            TradeCreate(trade_id="SCHED_TEST1", trader="John Doe", asset_class="EQUITY", quantity=1000, price=50.0),
            TradeCreate(trade_id="SCHED_TEST2", trader="John Doe", asset_class="FIXED_INCOME", quantity=500, price=100.0),
            TradeCreate(trade_id="SCHED_TEST3", trader="John Doe", asset_class="COMMODITY", quantity=200, price=75.0),
            TradeCreate(trade_id="SCHED_TEST4", trader="John Doe", asset_class="FOREX", quantity=10000, price=1.2)
        ]
        
        for trade in trades:
            create_trade(clean_db, trade)
        
        # Run the reconciliation
        result = run_scheduled_reconciliation(clean_db)
        
        # Verify the result
        assert result is not None
        assert result.status == ReconciliationStatus.SUCCESS
        
        # Check operational log
        log = clean_db.query(OperationalLog).order_by(OperationalLog.timestamp.desc()).first()
        assert log is not None
        assert "reconciliation run completed" in log.message.lower()
        
    finally:
        clean_db.close()

def test_scheduler_job_creation(clean_db):
    try:
        # Start the scheduler
        scheduler = start_scheduler(clean_db)
        
        # Check that the job was created
        job = scheduler.get_job('daily_reconciliation')
        assert job is not None
        
        # Check that the job is scheduled for 6 PM (18:00)
        next_run = job.next_run_time
        assert next_run is not None
        assert next_run.hour == 18
        assert next_run.minute == 0
        
        # Stop the scheduler
        scheduler.shutdown()
        
    finally:
        clean_db.close() 