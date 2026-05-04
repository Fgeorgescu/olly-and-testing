from typing import Protocol

from pydantic import BaseModel, Field

from app.schemas.item import ItemCategory, ItemListResponse, ItemTag


class SearchQuery(BaseModel):
    q: str | None = None
    categories: list[ItemCategory] = []
    tags: list[ItemTag] = []
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)


class SearchBackend(Protocol):
    async def search(self, query: SearchQuery) -> ItemListResponse: ...
