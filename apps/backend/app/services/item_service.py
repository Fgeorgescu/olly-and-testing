import logging
from uuid import UUID

from fastapi import HTTPException

from app.core.metrics import item_events
from app.repositories.protocols import ItemRepository
from app.schemas.item import ItemCreate, ItemResponse, ItemStatus, ItemUpdate

logger = logging.getLogger(__name__)


class ItemService:
    def __init__(self, repo: ItemRepository) -> None:
        self._repo = repo

    async def create(self, data: ItemCreate, seller_id: UUID) -> ItemResponse:
        item = await self._repo.create(data, seller_id)
        item_events.labels(event="created", actor="").inc()
        logger.info(
            "item lifecycle", extra={"event": "created", "item_id": str(item.id)}
        )
        return item

    async def get(self, item_id: UUID) -> ItemResponse:
        item = await self._repo.get_by_id(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        return item

    async def update(
        self, item_id: UUID, data: ItemUpdate, caller_id: UUID
    ) -> ItemResponse:
        item = await self._repo.get_by_id(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        if item.seller_id != caller_id:
            raise HTTPException(status_code=403, detail="Not the owner")
        updated = await self._repo.update(item_id, data)
        return updated  # type: ignore[return-value]

    async def delete(self, item_id: UUID, caller_id: UUID) -> None:
        item = await self._repo.get_by_id(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        if item.seller_id != caller_id:
            raise HTTPException(status_code=403, detail="Not the owner")
        if item.status == ItemStatus.on_hold:
            raise HTTPException(
                status_code=409, detail="Release the hold before deleting"
            )
        await self._repo.delete(item_id)
        item_events.labels(event="deleted", actor="").inc()
        logger.info(
            "item lifecycle", extra={"event": "deleted", "item_id": str(item_id)}
        )
