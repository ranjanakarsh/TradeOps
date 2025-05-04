from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from app.services.scheduler_service import start_scheduler, stop_scheduler
from app.db.base import SessionLocal

# load environment variables
load_dotenv()

# create fastapi application with metadata
app = FastAPI(
    title="TradeOps Portal",
    description="Internal operational tool for quantitative trading firms",
    version="1.0.0",
)

# configure cors middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# startup event handler - initializes scheduler
@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    start_scheduler(db)
    db.close()

# shutdown event handler - stops scheduler
@app.on_event("shutdown")
async def shutdown_event():
    stop_scheduler()

# root endpoint - welcome message
@app.get("/")
async def root():
    return {"message": "Welcome to TradeOps Portal API"}

# import and include all api routers
from app.api import trades, reconciliation, logs, database

# register api routes with their respective prefixes
app.include_router(trades.router, prefix="/api/v1/trades", tags=["trades"])
app.include_router(reconciliation.router, prefix="/api/v1/reconciliation", tags=["reconciliation"])
app.include_router(logs.router, prefix="/api/v1/logs", tags=["logs"])
app.include_router(database.router, prefix="/api/v1/database", tags=["database"]) 