from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.postgres import PostgresItemRepository
from app.schemas.item import (
    ItemCategory,
    ItemCreate,
    ItemListResponse,
    ItemResponse,
    ItemTag,
    ItemUpdate,
)
from app.search.factory import make_search_backend
from app.search.protocols import SearchQuery
from app.services.item_service import ItemService

router = APIRouter(prefix="/items", tags=["items"])


def _item_service(db: AsyncSession = Depends(get_db)) -> ItemService:
    return ItemService(PostgresItemRepository(db))


@router.post("", response_model=ItemResponse, status_code=201)
async def create_item(body: ItemCreate, svc: ItemService = Depends(_item_service)):
    return await svc.create(body)


@router.get("", response_model=ItemListResponse)
async def search_items(
    q: str | None = Query(default=None),
    category: list[ItemCategory] = Query(default=[]),
    tags: list[ItemTag] = Query(default=[]),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    backend = make_search_backend(db)
    return await backend.search(
        SearchQuery(q=q, categories=category, tags=tags, page=page, limit=limit)
    )


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: UUID, svc: ItemService = Depends(_item_service)):
    return await svc.get(item_id)


@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: UUID,
    body: ItemUpdate,
    caller_id: UUID = Query(),
    svc: ItemService = Depends(_item_service),
):
    return await svc.update(item_id, body, caller_id)


@router.delete("/{item_id}", status_code=204)
async def delete_item(
    item_id: UUID,
    caller_id: UUID = Query(),
    svc: ItemService = Depends(_item_service),
):
    await svc.delete(item_id, caller_id)
