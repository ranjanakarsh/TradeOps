from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from app.services.reconciliation_service import run_reconciliation
from app.models.models import OperationalLog
from typing import Optional
import os
from datetime import datetime

# create scheduler instance
scheduler = BackgroundScheduler()

def log_operational_message(db: Session, message: str) -> OperationalLog:
    """
    log an operational message to the database
    args:
        db (Session): database session
        message (str): message to log
    returns:
        OperationalLog: created log entry
    raises:
        ValueError: if logging fails
    """
    try:
        log = OperationalLog(message=message)
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
    except Exception as e:
        db.rollback()
        raise ValueError(f"error logging operational message: {str(e)}")

def schedule_reconciliation_job(db: Session) -> None:
    """
    schedule the daily reconciliation job
    args:
        db (Session): database session
    raises:
        ValueError: if scheduling fails
    """
    try:
        # schedule job for 6pm daily
        scheduler.add_job(
            run_scheduled_reconciliation,
            trigger=CronTrigger(hour=18, minute=0),
            args=[db],
            id='daily_reconciliation',
            replace_existing=True
        )
        log_operational_message(db, "scheduled daily reconciliation job for 6pm")
    except Exception as e:
        raise ValueError(f"error scheduling reconciliation job: {str(e)}")

def run_scheduled_reconciliation(db: Session) -> Optional[OperationalLog]:
    """
    run the scheduled reconciliation and log results
    args:
        db (Session): database session
    returns:
        Optional[OperationalLog]: log entry if successful
    raises:
        ValueError: if reconciliation fails
    """
    try:
        # log start of reconciliation
        log_operational_message(db, "starting scheduled reconciliation run")
        
        # run reconciliation
        reconciliation_result = run_reconciliation(db)
        
        # create summary message
        current_time = datetime.now().replace(microsecond=0)
        summary = f"reconciliation completed at {current_time}. status: {reconciliation_result.status}"
        if reconciliation_result.discrepancies:
            summary += f" discrepancies found: {reconciliation_result.discrepancies}"
        
        # log summary
        return log_operational_message(db, summary)
        
    except Exception as e:
        error_message = f"error during scheduled reconciliation: {str(e)}"
        log_operational_message(db, error_message)
        raise ValueError(error_message)

def start_scheduler(db: Session) -> BackgroundScheduler:
    """
    start the scheduler and schedule all jobs
    args:
        db (Session): database session
    returns:
        BackgroundScheduler: started scheduler instance
    raises:
        ValueError: if scheduler fails to start
    """
    try:
        if not scheduler.running:
            # schedule daily reconciliation
            scheduler.add_job(
                run_scheduled_reconciliation,
                'cron',
                minute=0,
                hour=18,
                id='daily_reconciliation',
                args=[db]
            )
            
            # start scheduler
            scheduler.start()
            log_operational_message(db, "scheduler started successfully")
        
        return scheduler
        
    except Exception as e:
        raise ValueError(f"error starting scheduler: {str(e)}")

def stop_scheduler() -> None:
    """
    stop the scheduler
    raises:
        ValueError: if scheduler fails to stop
    """
    try:
        if scheduler.running:
            scheduler.shutdown()
    except Exception as e:
        raise ValueError(f"error stopping scheduler: {str(e)}") 