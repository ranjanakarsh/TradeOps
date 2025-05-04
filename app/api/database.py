from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict
from app.db.base import get_db
from app.db.db_utils import (
    reset_database,
    initialize_database,
    get_database_info
)

# create router
router = APIRouter()

@router.post("/reset")
def reset_db() -> Dict[str, str]:
    """
    reset the database by dropping and recreating all tables
    returns:
        Dict[str, str]: success message
    raises:
        HTTPException: if reset fails
    """
    try:
        reset_database()
        return {"message": "database reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/initialize")
def init_db() -> Dict[str, str]:
    """
    initialize the database with sample data
    returns:
        Dict[str, str]: success message
    raises:
        HTTPException: if initialization fails
    """
    try:
        initialize_database()
        return {"message": "database initialized with sample data"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/info")
def get_db_info() -> Dict[str, int]:
    """
    get database information
    returns:
        Dict[str, int]: database statistics
    raises:
        HTTPException: if info retrieval fails
    """
    try:
        info = get_database_info()
        return {
            "trades_count": info["trades_count"],
            "operational_logs_count": info["operational_logs_count"],
            "reconciliation_logs_count": info["reconciliation_logs_count"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 