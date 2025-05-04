from sqlalchemy.orm import Session
from app.models.models import Trade, TradeStatus
from app.schemas.schemas import TradeCreate
from typing import List, Optional
from datetime import datetime

def validate_trade_data(trade_data: TradeCreate) -> None:
    """
    validate trade data before creation
    args:
        trade_data (TradeCreate): trade data to validate
    raises:
        ValueError: if trade data is invalid
    """
    if not trade_data.trade_id:
        raise ValueError("trade id cannot be empty")
    if trade_data.quantity <= 0:
        raise ValueError("quantity must be positive")
    if trade_data.price <= 0:
        raise ValueError("price must be positive")

def create_trade(db: Session, trade_data: TradeCreate) -> Trade:
    """
    create a new trade in the database
    args:
        db (Session): database session
        trade_data (TradeCreate): trade data to create
    returns:
        Trade: created trade
    raises:
        ValueError: if trade data is invalid
    """
    # validate trade data
    validate_trade_data(trade_data)
    
    # create trade
    trade = Trade(
        trade_id=trade_data.trade_id,
        trader=trade_data.trader,
        asset_class=trade_data.asset_class,
        quantity=trade_data.quantity,
        price=trade_data.price,
        timestamp=datetime.now().replace(microsecond=0),
        status=TradeStatus.PENDING
    )
    
    try:
        db.add(trade)
        db.commit()
        db.refresh(trade)
        return trade
    except Exception as e:
        db.rollback()
        raise ValueError(f"error creating trade: {str(e)}")

def get_trades(
    db: Session,
    trader: Optional[str] = None,
    asset_class: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Trade]:
    """
    get trades with optional filtering
    args:
        db (Session): database session
        trader (Optional[str]): filter by trader name
        asset_class (Optional[str]): filter by asset class
        skip (int): number of records to skip
        limit (int): maximum number of records to return
    returns:
        List[Trade]: list of trades matching the criteria
    """
    query = db.query(Trade)
    
    # apply filters
    if trader:
        query = query.filter(Trade.trader == trader)
    if asset_class:
        query = query.filter(Trade.asset_class == asset_class)
    
    # apply pagination
    return query.order_by(Trade.timestamp.desc()).offset(skip).limit(limit).all()

def get_trade_by_id(db: Session, trade_id: str) -> Optional[Trade]:
    """
    get a trade by its id
    args:
        db (Session): database session
        trade_id (str): trade id to search for
    returns:
        Optional[Trade]: trade if found, None otherwise
    """
    return db.query(Trade).filter(Trade.trade_id == trade_id).first()

def update_trade_status(
    db: Session,
    trade_id: str,
    new_status: TradeStatus
) -> Optional[Trade]:
    """
    update a trade's status
    args:
        db (Session): database session
        trade_id (str): trade id to update
        new_status (TradeStatus): new status to set
    returns:
        Optional[Trade]: updated trade if found, None otherwise
    """
    trade = get_trade_by_id(db, trade_id)
    if trade:
        trade.status = new_status
        try:
            db.commit()
            db.refresh(trade)
            return trade
        except Exception as e:
            db.rollback()
            raise ValueError(f"error updating trade status: {str(e)}")
    return None 