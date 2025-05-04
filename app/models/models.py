from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, func
from sqlalchemy.ext.declarative import declarative_base
import enum
from datetime import datetime
from typing import Optional

# create base class for models
Base = declarative_base()

class TradeStatus(str, enum.Enum):
    """
    status of a trade
    values:
        PENDING: trade is pending processing
        COMPLETED: trade has been processed successfully
        FAILED: trade processing failed
    """
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class ReconciliationStatus(str, enum.Enum):
    """
    status of a reconciliation run
    values:
        SUCCESS: reconciliation completed with no discrepancies
        PARTIAL: reconciliation completed with some discrepancies
        FAILED: reconciliation failed
    """
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"

class Trade(Base):
    """
    model for storing trade information
    attributes:
        id: unique identifier
        trade_id: unique trade identifier
        trader: name of the trader
        asset_class: type of asset traded
        quantity: quantity of the trade
        price: price of the trade
        timestamp: when the trade was created
        status: current status of the trade
    """
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(String, unique=True, index=True, nullable=False)
    trader = Column(String, nullable=False)
    asset_class = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(Enum(TradeStatus), default=TradeStatus.PENDING)

    def __repr__(self) -> str:
        return f"<Trade {self.trade_id} by {self.trader}>"

class ReconciliationLog(Base):
    """
    model for storing reconciliation results
    attributes:
        id: unique identifier
        run_time: when the reconciliation was run
        summary: summary of the reconciliation
        status: status of the reconciliation
        discrepancies: json string of discrepancies found
    """
    __tablename__ = "reconciliation_logs"

    id = Column(Integer, primary_key=True, index=True)
    run_time = Column(DateTime(timezone=True), server_default=func.now())
    summary = Column(String, nullable=False)
    status = Column(Enum(ReconciliationStatus), nullable=False)
    discrepancies = Column(String)  # json string of discrepancies

    def __repr__(self) -> str:
        return f"<ReconciliationLog {self.id} at {self.run_time}>"

class OperationalLog(Base):
    """
    model for storing operational messages
    attributes:
        id: unique identifier
        message: operational message
        timestamp: when the message was created
    """
    __tablename__ = "operational_logs"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<OperationalLog {self.id}: {self.message[:50]}...>" 