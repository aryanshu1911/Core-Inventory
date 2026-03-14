import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.transfer import Transfer
from models.adjustment import Adjustment
from schemas.inventory import TransferCreate, AdjustmentCreate
from services.stock_service import upsert_stock
from services.ledger_service import create_ledger_entry
from services.alert_service import check_and_create_alert
from fastapi import HTTPException, BackgroundTasks


# ── Transfer service ──────────────────────────────────────────────────────────

async def create_transfer(
    db: AsyncSession, data: TransferCreate, user_id: uuid.UUID, background_tasks: BackgroundTasks
) -> Transfer:
    if data.from_warehouse_id == data.to_warehouse_id:
        raise HTTPException(
            status_code=400,
            detail={"code": "VALIDATION_ERROR", "message": "Source and destination warehouses must differ", "details": None},
        )

    # Deduct from source
    await upsert_stock(db, data.product_id, data.from_warehouse_id, -data.quantity)
    # Add to destination
    await upsert_stock(db, data.product_id, data.to_warehouse_id, data.quantity)

    transfer = Transfer(
        product_id=data.product_id,
        from_warehouse_id=data.from_warehouse_id,
        to_warehouse_id=data.to_warehouse_id,
        quantity=data.quantity,
        status="completed",
        created_by=user_id,
        updated_by=user_id,
    )
    db.add(transfer)
    await db.flush()

    # Ledger entries for both warehouses
    await create_ledger_entry(db, data.product_id, data.from_warehouse_id, "transfer_out", -data.quantity, transfer.id, user_id)
    await create_ledger_entry(db, data.product_id, data.to_warehouse_id, "transfer_in", data.quantity, transfer.id, user_id)

    background_tasks.add_task(check_and_create_alert, db, data.product_id, data.from_warehouse_id)
    await db.refresh(transfer)
    return transfer


async def list_transfers(db: AsyncSession, limit: int = 20, offset: int = 0) -> List[Transfer]:
    result = await db.execute(
        select(Transfer).order_by(Transfer.created_at.desc()).limit(min(limit, 100)).offset(offset)
    )
    return result.scalars().all()


# ── Adjustment service ────────────────────────────────────────────────────────

async def create_adjustment(
    db: AsyncSession, data: AdjustmentCreate, user_id: uuid.UUID, background_tasks: BackgroundTasks
) -> Adjustment:
    await upsert_stock(db, data.product_id, data.warehouse_id, data.quantity_change)

    adj = Adjustment(
        product_id=data.product_id,
        warehouse_id=data.warehouse_id,
        quantity_change=data.quantity_change,
        reason=data.reason,
        created_by=user_id,
        updated_by=user_id,
    )
    db.add(adj)
    await db.flush()

    await create_ledger_entry(db, data.product_id, data.warehouse_id, "adjustment", data.quantity_change, adj.id, user_id)
    background_tasks.add_task(check_and_create_alert, db, data.product_id, data.warehouse_id)

    await db.refresh(adj)
    return adj


async def list_adjustments(db: AsyncSession, limit: int = 20, offset: int = 0) -> List[Adjustment]:
    result = await db.execute(
        select(Adjustment).order_by(Adjustment.created_at.desc()).limit(min(limit, 100)).offset(offset)
    )
    return result.scalars().all()
