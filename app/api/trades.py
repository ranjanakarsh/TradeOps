from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.base import get_db
from app.schemas.schemas import Trade, TradeCreate
from app.models.models import TradeStatus
from app.services.trade_service import (
    create_trade,
    get_trades,
    get_trade_by_id,
    update_trade_status
)

# create router
router = APIRouter()

@router.post("/", response_model=Trade)
def create_trade_endpoint(
    trade: TradeCreate,
    db: Session = Depends(get_db)
) -> Trade:
    """
    create a new trade
    args:
        trade (TradeCreate): trade data to create
        db (Session): database session
    returns:
        Trade: created trade
    raises:
        HTTPException: if trade creation fails
    """
    try:
        return create_trade(db, trade)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"error creating trade: {str(e)}")

@router.get("/", response_model=List[Trade])
def get_trades_endpoint(
    trader: Optional[str] = Query(None, description="filter by trader name"),
    asset_class: Optional[str] = Query(None, description="filter by asset class"),
    skip: int = Query(0, ge=0, description="number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="maximum number of records to return"),
    db: Session = Depends(get_db)
) -> List[Trade]:
    """
    get trades with optional filtering
    args:
        trader (Optional[str]): filter by trader name
        asset_class (Optional[str]): filter by asset class
        skip (int): number of records to skip
        limit (int): maximum number of records to return
        db (Session): database session
    returns:
        List[Trade]: list of trades matching the criteria
    raises:
        HTTPException: if trade retrieval fails
    """
    try:
        return get_trades(db, trader, asset_class, skip, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"error getting trades: {str(e)}")

@router.get("/{trade_id}", response_model=Trade)
def get_trade_endpoint(
    trade_id: str,
    db: Session = Depends(get_db)
) -> Trade:
    """
    get a trade by its id
    args:
        trade_id (str): trade id to search for
        db (Session): database session
    returns:
        Trade: trade if found
    raises:
        HTTPException: if trade is not found or retrieval fails
    """
    try:
        trade = get_trade_by_id(db, trade_id)
        if not trade:
            raise HTTPException(status_code=404, detail=f"trade {trade_id} not found")
        return trade
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"error getting trade: {str(e)}")

@router.patch("/{trade_id}/status", response_model=Trade)
def update_trade_status_endpoint(
    trade_id: str,
    status: TradeStatus,
    db: Session = Depends(get_db)
) -> Trade:
    """
    update a trade's status
    args:
        trade_id (str): trade id to update
        status (TradeStatus): new status to set
        db (Session): database session
    returns:
        Trade: updated trade
    raises:
        HTTPException: if trade update fails
    """
    try:
        trade = update_trade_status(db, trade_id, status)
        if not trade:
            raise HTTPException(status_code=404, detail=f"trade {trade_id} not found")
        return trade
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"error updating trade status: {str(e)}") 