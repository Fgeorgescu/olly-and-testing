from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.item import Item
from app.schemas.item import ItemListResponse, ItemStatus, ItemSummary
from app.search.protocols import SearchQuery


class SimpleSearchBackend:
    """SQL ILIKE search on title and description. Swap via SEARCH_BACKEND env var."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def search(self, query: SearchQuery) -> ItemListResponse:
        stmt = select(Item).where(Item.status != ItemStatus.sold.value)

        if query.q:
            pattern = f"%{query.q}%"
            stmt = stmt.where(
                Item.title.ilike(pattern) | Item.description.ilike(pattern)
            )
        if query.categories:
            stmt = stmt.where(Item.category.in_([c.value for c in query.categories]))
        if query.tags:
            for tag in query.tags:
                stmt = stmt.where(Item.tags.contains([tag.value]))

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self._session.execute(count_stmt)).scalar_one()

        stmt = stmt.order_by(Item.created_at.desc())
        stmt = stmt.offset((query.page - 1) * query.limit).limit(query.limit)
        rows = (await self._session.execute(stmt)).scalars().all()

        return ItemListResponse(
            items=[ItemSummary.model_validate(row) for row in rows],
            total=total,
            page=query.page,
            limit=query.limit,
        )
