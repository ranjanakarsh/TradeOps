from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.db.base import get_db
from app.schemas.schemas import ReconciliationLog
from app.services.reconciliation_service import run_reconciliation
from app.models.models import ReconciliationLog as ReconciliationLogModel

# create router
router = APIRouter()

@router.post("/run", response_model=ReconciliationLog)
def trigger_reconciliation(
    db: Session = Depends(get_db)
) -> ReconciliationLog:
    """
    trigger a reconciliation run
    args:
        db (Session): database session
    returns:
        ReconciliationLog: reconciliation results
    raises:
        HTTPException: if reconciliation fails
    """
    try:
        return run_reconciliation(db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"error running reconciliation: {str(e)}")

@router.get("/logs", response_model=List[ReconciliationLog])
def get_reconciliation_logs(
    skip: int = Query(0, ge=0, description="number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="maximum number of records to return"),
    db: Session = Depends(get_db)
) -> List[ReconciliationLog]:
    """
    get reconciliation logs
    args:
        skip (int): number of records to skip
        limit (int): maximum number of records to return
        db (Session): database session
    returns:
        List[ReconciliationLog]: list of reconciliation logs
    raises:
        HTTPException: if log retrieval fails
    """
    try:
        return db.query(ReconciliationLogModel).order_by(
            ReconciliationLogModel.run_time.desc()
        ).offset(skip).limit(limit).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"error getting reconciliation logs: {str(e)}") 