import uuid
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas.operations import ReceiptCreate, ReceiptOut
from services.receipt_service import create_receipt, validate_receipt, list_receipts
from auth.dependencies import get_current_user, require_role
from models.user import User

router = APIRouter(prefix="/receipts", tags=["Receipts"])
StaffDep   = Depends(require_role("warehouse_staff"))
AnyDep     = Depends(require_role("inventory_manager", "warehouse_staff"))


@router.post("", response_model=ReceiptOut, status_code=201, dependencies=[StaffDep])
async def create(
    data: ReceiptCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await create_receipt(db, data, current_user.id)


@router.post("/{receipt_id}/validate", response_model=ReceiptOut, dependencies=[StaffDep])
async def validate(
    receipt_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await validate_receipt(db, receipt_id, current_user.id, background_tasks)


@router.get("", response_model=list[ReceiptOut], dependencies=[AnyDep])
async def list_all(
    db: Annotated[AsyncSession, Depends(get_db)],
    status: Optional[str] = Query(None, pattern="^(draft|validated)$"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    return await list_receipts(db, status, limit, offset)
