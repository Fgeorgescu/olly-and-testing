import logging
from uuid import UUID

from fastapi import HTTPException

from app.core.metrics import item_events
from app.repositories.protocols import HoldRepository, ItemRepository
from app.schemas.hold import (
    ConfirmResponse,
    HoldReleaseResponse,
    HoldResponse,
    SellerContact,
)
from app.schemas.item import ItemStatus

logger = logging.getLogger(__name__)


class HoldService:
    def __init__(self, item_repo: ItemRepository, hold_repo: HoldRepository) -> None:
        self._items = item_repo
        self._holds = hold_repo

    async def place_hold(self, item_id: UUID, buyer_id: UUID) -> HoldResponse:
        item = await self._items.get_by_id(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        if item.seller_id == buyer_id:
            raise HTTPException(status_code=409, detail="Cannot hold your own listing")
        if item.status != ItemStatus.available:
            raise HTTPException(status_code=409, detail=f"Item is {item.status.value}")

        await self._items.update_status(item_id, ItemStatus.on_hold)
        hold = await self._holds.create(item_id, buyer_id)
        hold.seller_contact = SellerContact(
            seller_id=item.seller_id,
            display_name=str(item.seller_id),  # placeholder until user model exists
            email=f"{item.seller_id}@placeholder.local",
        )
        item_events.labels(event="on_hold", actor="").inc()
        logger.info(
            "item lifecycle",
            extra={"event": "on_hold", "item_id": str(item_id), "actor": str(buyer_id)},
        )
        return hold

    async def get_contact(self, item_id: UUID, caller_id: UUID) -> SellerContact:
        item = await self._items.get_by_id(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        hold = await self._holds.get_by_item_id(item_id)
        if not hold or hold.held_by != caller_id:
            raise HTTPException(status_code=403, detail="Not the active holder")
        return SellerContact(
            seller_id=item.seller_id,
            display_name=str(item.seller_id),
            email=f"{item.seller_id}@placeholder.local",
        )

    async def release(self, item_id: UUID, caller_id: UUID) -> HoldReleaseResponse:
        item = await self._items.get_by_id(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        hold = await self._holds.get_by_item_id(item_id)
        if not hold:
            raise HTTPException(status_code=404, detail="No active hold")
        if caller_id not in (hold.held_by, item.seller_id):
            raise HTTPException(status_code=403, detail="Not the holder or seller")

        actor = "buyer" if caller_id == hold.held_by else "seller"
        await self._holds.release(item_id)
        updated = await self._items.update_status(item_id, ItemStatus.available)
        item_events.labels(event="hold_released", actor=actor).inc()
        logger.info(
            "item lifecycle",
            extra={"event": "hold_released", "item_id": str(item_id), "actor": actor},
        )
        return HoldReleaseResponse(item_id=item_id, status=updated.status)  # type: ignore[union-attr]

    async def confirm(self, item_id: UUID, confirmer_id: UUID) -> ConfirmResponse:
        item = await self._items.get_by_id(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        if item.status != ItemStatus.on_hold:
            raise HTTPException(status_code=409, detail="Item is not on hold")

        hold = await self._holds.get_by_item_id(item_id)
        if not hold:
            raise HTTPException(status_code=404, detail="No active hold")

        if confirmer_id == hold.held_by:
            role = "buyer"
            if hold.buyer_confirmed:
                raise HTTPException(status_code=409, detail="Already confirmed")
        elif confirmer_id == item.seller_id:
            role = "seller"
            if hold.seller_confirmed:
                raise HTTPException(status_code=409, detail="Already confirmed")
        else:
            raise HTTPException(status_code=403, detail="Not the holder or seller")

        updated_hold = await self._holds.confirm(item_id, role)
        item_events.labels(event="confirmed", actor=role).inc()
        logger.info(
            "item lifecycle",
            extra={"event": "confirmed", "item_id": str(item_id), "actor": role},
        )

        final_status = ItemStatus.on_hold
        if updated_hold.buyer_confirmed and updated_hold.seller_confirmed:
            await self._items.update_status(item_id, ItemStatus.sold)
            final_status = ItemStatus.sold
            item_events.labels(event="sold", actor="").inc()
            logger.info(
                "item lifecycle", extra={"event": "sold", "item_id": str(item_id)}
            )

        return ConfirmResponse(
            item_id=item_id,
            confirmed_by=role,
            buyer_confirmed=updated_hold.buyer_confirmed,
            seller_confirmed=updated_hold.seller_confirmed,
            status=final_status,
        )
