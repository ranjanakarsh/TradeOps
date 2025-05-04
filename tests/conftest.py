import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base import Base, get_db
import pandas as pd
import os

# Test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(clean_db):
    def override_get_db():
        try:
            yield clean_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

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