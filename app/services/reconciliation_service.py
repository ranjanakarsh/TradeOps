import pandas as pd
from sqlalchemy.orm import Session
from app.models.models import Trade, ReconciliationLog, ReconciliationStatus
from typing import Dict, List, Optional
import json
from datetime import datetime
import os

# default path for positions file
POSITIONS_FILE = 'positions.csv'

def read_positions_from_csv() -> pd.DataFrame:
    """
    read positions from the csv file
    returns:
        pd.DataFrame: positions data
    raises:
        FileNotFoundError: if positions file is not found
        ValueError: if positions file is invalid
    """
    try:
        csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'positions.csv')
        return pd.read_csv(csv_path)
    except FileNotFoundError:
        raise FileNotFoundError("positions file not found")
    except Exception as e:
        raise ValueError(f"error reading positions file: {str(e)}")

def get_trades_dataframe(db: Session) -> pd.DataFrame:
    """
    get trades from database as dataframe
    args:
        db (Session): database session
    returns:
        pd.DataFrame: trades data
    """
    trades = db.query(Trade).all()
    return pd.DataFrame([{
        'asset_class': t.asset_class,
        'quantity': float(t.quantity),
        'price': float(t.price)
    } for t in trades])

def check_quantity_discrepancy(
    asset_class: str,
    position_quantity: float,
    trade_quantity: float
) -> Optional[Dict]:
    """
    check for quantity discrepancy between position and trades
    args:
        asset_class (str): asset class to check
        position_quantity (float): position quantity
        trade_quantity (float): trade quantity
    returns:
        Optional[Dict]: discrepancy details if found, None otherwise
    """
    if abs(position_quantity - trade_quantity) > 0.01:
        return {
            'asset_class': asset_class,
            'type': 'quantity',
            'position_value': position_quantity,
            'trade_value': trade_quantity,
            'difference': position_quantity - trade_quantity
        }
    return None

def check_price_discrepancy(
    asset_class: str,
    position_price: float,
    trade_price: float,
    trade_quantity: float
) -> Optional[Dict]:
    """
    check for price discrepancy between position and trades
    args:
        asset_class (str): asset class to check
        position_price (float): position price
        trade_price (float): trade price
        trade_quantity (float): trade quantity
    returns:
        Optional[Dict]: discrepancy details if found, None otherwise
    """
    if trade_quantity > 0 and abs(position_price - trade_price) > 0.01:
        return {
            'asset_class': asset_class,
            'type': 'price',
            'position_value': position_price,
            'trade_value': trade_price,
            'difference': position_price - trade_price
        }
    return None

def run_reconciliation(db: Session) -> ReconciliationLog:
    """
    run reconciliation between positions and trades
    args:
        db (Session): database session
    returns:
        ReconciliationLog: reconciliation results
    raises:
        ValueError: if reconciliation fails
    """
    try:
        # read positions and trades
        positions_df = read_positions_from_csv()
        trades_df = get_trades_dataframe(db)
        
        discrepancies = []
        
        # compare positions with trades
        for _, position in positions_df.iterrows():
            asset_class = position['asset_class']
            position_quantity = float(position['quantity'])
            position_price = float(position['price'])
            
            # get trades for this asset class
            asset_trades = trades_df[trades_df['asset_class'] == asset_class]
            trade_quantity = float(asset_trades['quantity'].sum()) if not asset_trades.empty else 0
            trade_price = float(asset_trades['price'].mean()) if not asset_trades.empty else 0
            
            # check for discrepancies
            quantity_discrepancy = check_quantity_discrepancy(
                asset_class, position_quantity, trade_quantity
            )
            if quantity_discrepancy:
                discrepancies.append(quantity_discrepancy)
            
            price_discrepancy = check_price_discrepancy(
                asset_class, position_price, trade_price, trade_quantity
            )
            if price_discrepancy:
                discrepancies.append(price_discrepancy)
        
        # create reconciliation log
        status = ReconciliationStatus.SUCCESS if not discrepancies else ReconciliationStatus.PARTIAL
        summary = f"reconciliation completed with status {status}. found {len(discrepancies)} discrepancies."
        
        reconciliation_log = ReconciliationLog(
            run_time=datetime.now().replace(microsecond=0),
            status=status,
            summary=summary,
            discrepancies=json.dumps(discrepancies)
        )
        
        db.add(reconciliation_log)
        db.commit()
        db.refresh(reconciliation_log)
        
        return reconciliation_log
        
    except Exception as e:
        db.rollback()
        raise ValueError(f"error running reconciliation: {str(e)}") 