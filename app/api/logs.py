from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.db.base import get_db
from app.schemas.schemas import OperationalLog, ReconciliationLog
from app.models.models import OperationalLog as OperationalLogModel
from app.models.models import ReconciliationLog as ReconciliationLogModel

# create router for log operations
router = APIRouter()

@router.get("/operational", response_model=List[OperationalLog])
def get_operational_logs(
    skip: int = Query(0, ge=0, description="number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="maximum number of records to return"),
    db: Session = Depends(get_db)
) -> List[OperationalLog]:
    """
    get operational logs
    args:
        skip (int): number of records to skip
        limit (int): maximum number of records to return
        db (Session): database session
    returns:
        List[OperationalLog]: list of operational logs
    raises:
        HTTPException: if log retrieval fails
    """
    try:
        return db.query(OperationalLogModel).order_by(
            OperationalLogModel.timestamp.desc()
        ).offset(skip).limit(limit).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"error getting operational logs: {str(e)}")

@router.post("/operational", response_model=OperationalLog)
def create_operational_log(
    message: str,
    db: Session = Depends(get_db)
) -> OperationalLog:
    """
    create a new operational log
    args:
        message (str): message to log
        db (Session): database session
    returns:
        OperationalLog: created log entry
    raises:
        HTTPException: if log creation fails
    """
    try:
        log = OperationalLogModel(message=message)
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"error creating operational log: {str(e)}")

@router.get("/reconciliation", response_model=List[ReconciliationLog])
def get_reconciliation_logs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    get a list of reconciliation logs
    args:
        skip (int): number of records to skip
        limit (int): maximum number of records to return
        db (Session): database session
    returns:
        List[ReconciliationLog]: list of reconciliation logs
    """
    return db.query(ReconciliationLogModel).offset(skip).limit(limit).all() 