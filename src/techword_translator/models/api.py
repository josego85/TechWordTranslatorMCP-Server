"""API response models."""

from typing import Optional, List
from pydantic import BaseModel

from .word import Word


class PaginationMeta(BaseModel):
    """Pagination metadata."""

    path: str
    per_page: int
    next_cursor: Optional[str] = None
    next_page_url: Optional[str] = None
    prev_cursor: Optional[str] = None
    prev_page_url: Optional[str] = None


class WordsResponse(BaseModel):
    """Response model for paginated words list."""

    data: List[Word]
    links: dict
    meta: PaginationMeta
