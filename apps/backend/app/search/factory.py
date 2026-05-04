from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.search.backends.simple import SimpleSearchBackend
from app.search.protocols import SearchBackend


def make_search_backend(session: AsyncSession) -> SearchBackend:
    if settings.search_backend == "simple":
        return SimpleSearchBackend(session)
    raise ValueError(f"Unknown search backend: {settings.search_backend!r}")
