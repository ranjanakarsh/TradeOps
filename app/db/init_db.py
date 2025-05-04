from app.db.base import Base, engine
from app.models.models import Trade, ReconciliationLog, OperationalLog

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    print("Creating database tables...")
    init_db()
    print("Database tables created successfully!") 