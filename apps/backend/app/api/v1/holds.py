from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.postgres import PostgresHoldRepository, PostgresItemRepository
from app.schemas.hold import (
    ConfirmRequest,
    ConfirmResponse,
    HoldCreate,
    HoldReleaseResponse,
    HoldResponse,
    SellerContact,
)
from app.services.hold_service import HoldService

router = APIRouter(prefix="/items", tags=["holds"])


def _hold_service(db: AsyncSession = Depends(get_db)) -> HoldService:
    return HoldService(PostgresItemRepository(db), PostgresHoldRepository(db))


@router.post("/{item_id}/hold", response_model=HoldResponse, status_code=201)
async def place_hold(
    item_id: UUID,
    body: HoldCreate,
    svc: HoldService = Depends(_hold_service),
):
    return await svc.place_hold(item_id, body.buyer_id)


@router.get("/{item_id}/contact", response_model=SellerContact)
async def get_contact(
    item_id: UUID,
    caller_id: UUID = Query(),
    svc: HoldService = Depends(_hold_service),
):
    return await svc.get_contact(item_id, caller_id)


@router.post("/{item_id}/confirm", response_model=ConfirmResponse)
async def confirm_purchase(
    item_id: UUID,
    body: ConfirmRequest,
    svc: HoldService = Depends(_hold_service),
):
    return await svc.confirm(item_id, body.confirmer_id)


@router.delete("/{item_id}/hold", response_model=HoldReleaseResponse)
async def release_hold(
    item_id: UUID,
    caller_id: UUID = Query(),
    svc: HoldService = Depends(_hold_service),
):
    return await svc.release(item_id, caller_id)
