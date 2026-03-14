import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.receipt import Receipt, ReceiptItem
from schemas.operations import ReceiptCreate
from services.stock_service import upsert_stock
from services.ledger_service import create_ledger_entry
from services.alert_service import check_and_create_alert
from fastapi import HTTPException, BackgroundTasks


async def create_receipt(db: AsyncSession, data: ReceiptCreate, user_id: uuid.UUID) -> Receipt:
    receipt = Receipt(supplier=data.supplier, created_by=user_id)
    db.add(receipt)
    await db.flush()

    for item in data.items:
        ri = ReceiptItem(
            receipt_id=receipt.id,
            product_id=item.product_id,
            warehouse_id=item.warehouse_id,
            quantity=item.quantity,
        )
        db.add(ri)

    await db.flush()
    await db.refresh(receipt)
    return receipt


async def validate_receipt(
    db: AsyncSession,
    receipt_id: uuid.UUID,
    user_id: uuid.UUID,
    background_tasks: BackgroundTasks,
) -> Receipt:
    result = await db.execute(select(Receipt).where(Receipt.id == receipt_id))
    receipt = result.scalar_one_or_none()
    if not receipt:
        raise HTTPException(status_code=404, detail={"code": "RESOURCE_NOT_FOUND", "message": "Receipt not found", "details": None})
    if receipt.status == "validated":
        raise HTTPException(status_code=400, detail={"code": "VALIDATION_ERROR", "message": "Receipt already validated", "details": None})

    items_result = await db.execute(select(ReceiptItem).where(ReceiptItem.receipt_id == receipt_id))
    items = items_result.scalars().all()

    for item in items:
        await upsert_stock(db, item.product_id, item.warehouse_id, item.quantity)
        await create_ledger_entry(db, item.product_id, item.warehouse_id, "receipt", item.quantity, receipt.id, user_id)
        background_tasks.add_task(check_and_create_alert, db, item.product_id, item.warehouse_id)

    receipt.status = "validated"
    receipt.updated_by = user_id
    await db.flush()
    await db.refresh(receipt)
    return receipt


async def list_receipts(db: AsyncSession, status: Optional[str] = None, limit: int = 20, offset: int = 0) -> List[Receipt]:
    query = select(Receipt)
    if status:
        query = query.where(Receipt.status == status)
    query = query.order_by(Receipt.created_at.desc()).limit(min(limit, 100)).offset(offset)
    result = await db.execute(query)
    return result.scalars().all()
