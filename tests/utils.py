import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base, get_db
from app.main import app
from fastapi.testclient import TestClient
import os
import shutil

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(test_db):
    connection = test_db.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def setup_test_data():
    # Create test data directory
    test_data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(test_data_dir, exist_ok=True)
    
    # Create test positions.csv
    positions_data = """asset_class,quantity,price,last_updated
EQUITY,1000,50.0,2024-03-20
FIXED_INCOME,500,100.0,2024-03-20
COMMODITY,200,75.0,2024-03-20
FOREX,10000,1.2,2024-03-20"""
    
    with open(os.path.join(test_data_dir, 'positions.csv'), 'w') as f:
        f.write(positions_data)
    
    yield
    
    # Cleanup
    shutil.rmtree(test_data_dir) 