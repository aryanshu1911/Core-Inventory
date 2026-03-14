import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.delivery import Delivery, DeliveryItem
from schemas.operations import DeliveryCreate
from services.stock_service import upsert_stock
from services.ledger_service import create_ledger_entry
from services.alert_service import check_and_create_alert
from fastapi import HTTPException, BackgroundTasks


async def create_delivery(db: AsyncSession, data: DeliveryCreate, user_id: uuid.UUID) -> Delivery:
    delivery = Delivery(customer=data.customer, created_by=user_id)
    db.add(delivery)
    await db.flush()

    for item in data.items:
        di = DeliveryItem(
            delivery_id=delivery.id,
            product_id=item.product_id,
            warehouse_id=item.warehouse_id,
            quantity=item.quantity,
        )
        db.add(di)

    await db.flush()
    await db.refresh(delivery)
    return delivery


async def validate_delivery(
    db: AsyncSession,
    delivery_id: uuid.UUID,
    user_id: uuid.UUID,
    background_tasks: BackgroundTasks,
) -> Delivery:
    result = await db.execute(select(Delivery).where(Delivery.id == delivery_id))
    delivery = result.scalar_one_or_none()
    if not delivery:
        raise HTTPException(status_code=404, detail={"code": "RESOURCE_NOT_FOUND", "message": "Delivery not found", "details": None})
    if delivery.status == "validated":
        raise HTTPException(status_code=400, detail={"code": "VALIDATION_ERROR", "message": "Delivery already validated", "details": None})

    items_result = await db.execute(select(DeliveryItem).where(DeliveryItem.delivery_id == delivery_id))
    items = items_result.scalars().all()

    for item in items:
        # Deduct stock — upsert_stock raises 400 if insufficient
        await upsert_stock(db, item.product_id, item.warehouse_id, -item.quantity)
        await create_ledger_entry(db, item.product_id, item.warehouse_id, "delivery", -item.quantity, delivery.id, user_id)
        background_tasks.add_task(check_and_create_alert, db, item.product_id, item.warehouse_id)

    delivery.status = "validated"
    delivery.updated_by = user_id
    await db.flush()
    await db.refresh(delivery)
    return delivery


async def list_deliveries(db: AsyncSession, status: Optional[str] = None, limit: int = 20, offset: int = 0) -> List[Delivery]:
    query = select(Delivery)
    if status:
        query = query.where(Delivery.status == status)
    query = query.order_by(Delivery.created_at.desc()).limit(min(limit, 100)).offset(offset)
    result = await db.execute(query)
    return result.scalars().all()
