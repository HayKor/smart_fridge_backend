from typing import Generic, Sequence, TypeVar

from . import fields as f
from .abc import BaseSchema


# Field definitions for Pagination schemas
LIMIT = f.BaseField(description="Limit of items per page.", ge=1, le=100, default=10)
PAGE = f.BaseField(description="Page number.", ge=1, default=1)
ITEMS = f.BaseField(description="Response items.")
TOTAL_ITEMS = f.BaseField(description="Total items in the database.")
TOTAL_PAGES = f.BaseField(description="Total pages in the database.")
# Type variable for generic pagination response
_BaseSchema = TypeVar("_BaseSchema", bound=BaseSchema)


class PaginationRequest(BaseSchema):
    limit: int = LIMIT
    page: int = PAGE


class PaginationResponse(BaseSchema, Generic[_BaseSchema]):
    items: Sequence[_BaseSchema] = ITEMS
    total_items: int = TOTAL_ITEMS
    total_pages: int = TOTAL_PAGES
