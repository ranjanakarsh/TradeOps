from app.db.base import SessionLocal
from app.models.models import Trade, TradeStatus
from datetime import datetime, timedelta
import random

def create_sample_trades(db):
    """
    create sample trades in the database
    args:
        db (Session): database session
    """
    # Clear existing trades
    db.query(Trade).delete()
    
    # Sample traders
    traders = ["John Smith", "Sarah Johnson", "Michael Brown", "Emily Davis", "David Wilson"]
    
    # Sample asset classes with typical quantities and prices
    asset_classes = {
        "EQUITY": {"min_qty": 100, "max_qty": 10000, "min_price": 10, "max_price": 500},
        "FIXED_INCOME": {"min_qty": 1000, "max_qty": 100000, "min_price": 90, "max_price": 110},
        "COMMODITY": {"min_qty": 10, "max_qty": 1000, "min_price": 50, "max_price": 2000},
        "FOREX": {"min_qty": 10000, "max_qty": 1000000, "min_price": 0.5, "max_price": 2.0}
    }
    
    # Generate trades for the last 7 days
    for i in range(20):  # Create 20 sample trades
        # Generate random date within last 7 days
        days_ago = random.randint(0, 6)
        trade_date = datetime.now() - timedelta(days=days_ago)
        
        # Generate random hour and minute
        hour = random.randint(9, 16)  # Trading hours
        minute = random.randint(0, 59)
        
        # Create timestamp without microseconds
        timestamp = trade_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # Select random asset class
        asset_class = random.choice(list(asset_classes.keys()))
        asset_params = asset_classes[asset_class]
        
        # Generate trade data based on asset class
        trade = Trade(
            trade_id=f"TRD-{random.randint(1000, 9999)}",
            trader=random.choice(traders),
            asset_class=asset_class,
            quantity=random.randint(asset_params["min_qty"], asset_params["max_qty"]),
            price=random.uniform(asset_params["min_price"], asset_params["max_price"]),
            timestamp=timestamp,
            status=TradeStatus.COMPLETED  # Use the correct enum value
        )
        
        db.add(trade)
    
    try:
        db.commit()
        print("Successfully added sample trades to the database")
    except Exception as e:
        db.rollback()
        print(f"Error adding sample trades: {str(e)}")

if __name__ == "__main__":
    db = SessionLocal()
    create_sample_trades(db)
    db.close() 