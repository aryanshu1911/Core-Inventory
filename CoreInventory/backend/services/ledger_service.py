import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from models.ledger import StockLedger


async def create_ledger_entry(
    db: AsyncSession,
    product_id: uuid.UUID,
    warehouse_id: uuid.UUID,
    change_type: str,
    quantity_change: int,
    reference_id: uuid.UUID | None,
    user_id: uuid.UUID | None,
) -> StockLedger:
    entry = StockLedger(
        product_id=product_id,
        warehouse_id=warehouse_id,
        change_type=change_type,
        quantity_change=quantity_change,
        reference_id=reference_id,
        user_id=user_id,
    )
    db.add(entry)
    await db.flush()
    return entry
