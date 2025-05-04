from fastapi import APIRouter
from app.api import trades, reconciliation, logs, database

# create main router
router = APIRouter()

# include all api routers
router.include_router(
    trades.router,
    prefix="/trades",
    tags=["trades"],
    responses={404: {"description": "not found"}}
)

router.include_router(
    reconciliation.router,
    prefix="/reconciliation",
    tags=["reconciliation"],
    responses={404: {"description": "not found"}}
)

router.include_router(
    logs.router,
    prefix="/logs",
    tags=["logs"],
    responses={404: {"description": "not found"}}
)

router.include_router(
    database.router,
    prefix="/database",
    tags=["database"],
    responses={404: {"description": "not found"}}
) 