from uuid import UUID

from fastapi import HTTPException

from app.repositories.protocols import ItemRepository
from app.schemas.item import ItemCreate, ItemResponse, ItemStatus, ItemUpdate


class ItemService:
    def __init__(self, repo: ItemRepository) -> None:
        self._repo = repo

    async def create(self, data: ItemCreate, seller_id: UUID) -> ItemResponse:
        return await self._repo.create(data, seller_id)

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
