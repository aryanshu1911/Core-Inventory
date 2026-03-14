import uuid
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas.operations import DeliveryCreate, DeliveryOut
from services.delivery_service import create_delivery, validate_delivery, list_deliveries
from auth.dependencies import get_current_user, require_role
from models.user import User

router = APIRouter(prefix="/deliveries", tags=["Deliveries"])
StaffDep = Depends(require_role("warehouse_staff"))
AnyDep   = Depends(require_role("inventory_manager", "warehouse_staff"))


@router.post("", response_model=DeliveryOut, status_code=201, dependencies=[StaffDep])
async def create(
    data: DeliveryCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await create_delivery(db, data, current_user.id)


@router.post("/{delivery_id}/validate", response_model=DeliveryOut, dependencies=[StaffDep])
async def validate(
    delivery_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await validate_delivery(db, delivery_id, current_user.id, background_tasks)


@router.get("", response_model=list[DeliveryOut], dependencies=[AnyDep])
async def list_all(
    db: Annotated[AsyncSession, Depends(get_db)],
    status: Optional[str] = Query(None, pattern="^(draft|packed|validated)$"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    return await list_deliveries(db, status, limit, offset)
