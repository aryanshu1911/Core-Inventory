from typing import Annotated
from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas.inventory import TransferCreate, TransferOut, AdjustmentCreate, AdjustmentOut
from services.transfer_service import create_transfer, list_transfers, create_adjustment, list_adjustments
from auth.dependencies import get_current_user, require_role
from models.user import User

router = APIRouter(tags=["Transfers & Adjustments"])
StaffDep = Depends(require_role("warehouse_staff"))
AnyDep   = Depends(require_role("inventory_manager", "warehouse_staff"))


# ── Transfers ─────────────────────────────────────────────────────────────────

@router.post("/transfers", response_model=TransferOut, status_code=201, dependencies=[StaffDep])
async def create_tf(
    data: TransferCreate,
    background_tasks: BackgroundTasks,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await create_transfer(db, data, current_user.id, background_tasks)


@router.get("/transfers", response_model=list[TransferOut], dependencies=[AnyDep])
async def list_tf(
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    return await list_transfers(db, limit, offset)


# ── Adjustments ───────────────────────────────────────────────────────────────

@router.post("/adjustments", response_model=AdjustmentOut, status_code=201, dependencies=[StaffDep])
async def create_adj(
    data: AdjustmentCreate,
    background_tasks: BackgroundTasks,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await create_adjustment(db, data, current_user.id, background_tasks)


@router.get("/adjustments", response_model=list[AdjustmentOut], dependencies=[AnyDep])
async def list_adj(
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    return await list_adjustments(db, limit, offset)
