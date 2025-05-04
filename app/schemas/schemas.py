from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List, Dict
from app.models.models import TradeStatus, ReconciliationStatus
import json

class TradeBase(BaseModel):
    """
    base trade schema
    attributes:
        trade_id: unique trade identifier
        trader: name of the trader
        asset_class: type of asset traded
        quantity: quantity of the trade
        price: price of the trade
    """
    trade_id: str = Field(..., min_length=1, description="unique trade identifier")
    trader: str = Field(..., min_length=1, description="name of the trader")
    asset_class: str = Field(..., min_length=1, description="type of asset traded")
    quantity: float = Field(..., gt=0, description="quantity of the trade")
    price: float = Field(..., gt=0, description="price of the trade")

    @validator('quantity', 'price')
    def validate_positive_values(cls, v):
        """
        validate that quantity and price are positive
        args:
            v: value to validate
        returns:
            float: validated value
        raises:
            ValueError: if value is not positive
        """
        if v <= 0:
            raise ValueError("value must be positive")
        return v

class TradeCreate(TradeBase):
    """
    schema for creating a new trade
    inherits from TradeBase
    """
    pass

class Trade(TradeBase):
    """
    schema for trade response
    inherits from TradeBase
    attributes:
        id: unique identifier
        timestamp: when the trade was created
        status: current status of the trade
    """
    id: int
    timestamp: datetime
    status: TradeStatus

    class Config:
        """
        pydantic configuration
        """
        from_attributes = True

class Discrepancy(BaseModel):
    """
    schema for reconciliation discrepancy
    attributes:
        asset_class: type of asset
        type: type of discrepancy (quantity or price)
        position_value: value from positions
        trade_value: value from trades
        difference: difference between values
    """
    asset_class: str
    type: str
    position_value: float
    trade_value: float
    difference: float

class ReconciliationLogBase(BaseModel):
    """
    base reconciliation log schema
    attributes:
        summary: summary of the reconciliation
        status: status of the reconciliation
        discrepancies: list of discrepancies found
    """
    summary: str
    status: ReconciliationStatus
    discrepancies: Optional[str] = None  # Store as JSON string

class ReconciliationLogCreate(ReconciliationLogBase):
    """
    schema for creating a new reconciliation log
    inherits from ReconciliationLogBase
    """
    pass

class ReconciliationLog(ReconciliationLogBase):
    """
    schema for reconciliation log response
    inherits from ReconciliationLogBase
    attributes:
        id: unique identifier
        run_time: when the reconciliation was run
    """
    id: int
    run_time: datetime

    @property
    def discrepancies_list(self) -> Optional[List[Discrepancy]]:
        """
        convert discrepancies JSON string to list of Discrepancy objects
        returns:
            Optional[List[Discrepancy]]: list of discrepancies or None
        """
        if not self.discrepancies:
            return None
        try:
            return [Discrepancy(**d) for d in json.loads(self.discrepancies)]
        except Exception:
            return None

    class Config:
        """
        pydantic configuration
        """
        from_attributes = True

class OperationalLogBase(BaseModel):
    """
    base operational log schema
    attributes:
        message: operational message
    """
    message: str = Field(..., min_length=1, description="operational message")

class OperationalLogCreate(OperationalLogBase):
    """
    schema for creating a new operational log
    inherits from OperationalLogBase
    """
    pass

class OperationalLog(OperationalLogBase):
    """
    schema for operational log response
    inherits from OperationalLogBase
    attributes:
        id: unique identifier
        timestamp: when the message was created
    """
    id: int
    timestamp: datetime

    class Config:
        """
        pydantic configuration
        """
        from_attributes = True 