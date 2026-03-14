import uuid
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models.stock import Stock
from models.ledger import StockLedger
from schemas.inventory import StockOut, LedgerOut
from auth.dependencies import require_role

router = APIRouter(tags=["Stock & Ledger"])
AnyDep     = Depends(require_role("inventory_manager", "warehouse_staff"))
ManagerDep = Depends(require_role("inventory_manager"))


@router.get("/stock", response_model=list[StockOut], dependencies=[AnyDep])
async def get_stock(
    db: Annotated[AsyncSession, Depends(get_db)],
    warehouse_id: Optional[uuid.UUID] = Query(None),
    product_id: Optional[uuid.UUID] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    query = select(Stock)
    if warehouse_id:
        query = query.where(Stock.warehouse_id == warehouse_id)
    if product_id:
        query = query.where(Stock.product_id == product_id)
    query = query.limit(min(limit, 100)).offset(offset)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/ledger", response_model=list[LedgerOut], dependencies=[ManagerDep])
async def get_ledger(
    db: Annotated[AsyncSession, Depends(get_db)],
    product_id: Optional[uuid.UUID] = Query(None),
    warehouse_id: Optional[uuid.UUID] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    query = select(StockLedger)
    if product_id:
        query = query.where(StockLedger.product_id == product_id)
    if warehouse_id:
        query = query.where(StockLedger.warehouse_id == warehouse_id)
    query = query.order_by(StockLedger.created_at.desc()).limit(min(limit, 100)).offset(offset)
    result = await db.execute(query)
    return result.scalars().all()
