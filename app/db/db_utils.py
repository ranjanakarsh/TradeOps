from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.models.models import Base, Trade, ReconciliationLog, OperationalLog
from app.db.sample_data import create_sample_trades
from typing import Dict, Any
import os
import json

# get database url from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tradeops.db")

# create database engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    """
    get database session
    returns:
        Session: database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def reset_database() -> None:
    """
    reset the database by dropping and recreating all tables
    raises:
        Exception: if reset fails
    """
    try:
        # drop all tables
        Base.metadata.drop_all(bind=engine)
        
        # create all tables
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        raise Exception(f"error resetting database: {str(e)}")

def initialize_database() -> None:
    """
    initialize the database with sample data
    raises:
        Exception: if initialization fails
    """
    try:
        # reset database first
        reset_database()
        
        # create new session
        db = SessionLocal()
        try:
            # create sample trades
            create_sample_trades(db)
            
            # create sample reconciliation logs
            sample_reconciliation_logs = [
                {
                    "summary": "daily reconciliation completed successfully",
                    "status": "SUCCESS",
                    "discrepancies": None
                },
                {
                    "summary": "reconciliation completed with minor discrepancies",
                    "status": "PARTIAL",
                    "discrepancies": json.dumps([
                        {
                            "asset_class": "EQUITY",
                            "type": "quantity",
                            "position_value": 1100.0,
                            "trade_value": 1000.0,
                            "difference": 100.0
                        }
                    ])
                }
            ]
            
            for log_data in sample_reconciliation_logs:
                log = ReconciliationLog(**log_data)
                db.add(log)
            
            # create sample operational logs
            sample_operational_logs = [
                "system started successfully",
                "daily reconciliation job scheduled",
                "trade database backup completed",
                "system maintenance completed"
            ]
            
            for message in sample_operational_logs:
                log = OperationalLog(message=message)
                db.add(log)
            
            db.commit()
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
            
    except Exception as e:
        raise Exception(f"error initializing database: {str(e)}")

def get_database_info() -> Dict[str, Any]:
    """
    get database information
    returns:
        Dict[str, Any]: database statistics including counts and path
    raises:
        Exception: if info retrieval fails
    """
    try:
        db = SessionLocal()
        try:
            # get counts
            trades_count = db.query(Trade).count()
            reconciliation_logs_count = db.query(ReconciliationLog).count()
            operational_logs_count = db.query(OperationalLog).count()
            
            return {
                "trades_count": trades_count,
                "reconciliation_logs_count": reconciliation_logs_count,
                "operational_logs_count": operational_logs_count,
                "database_path": DATABASE_URL
            }
        finally:
            db.close()
    except Exception as e:
        raise Exception(f"error getting database info: {str(e)}") 