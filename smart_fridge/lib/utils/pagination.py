from typing import Any, TypeVar

from sqlalchemy import Select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from smart_fridge.lib.schemas.pagination import PaginationRequest


_SelectType = TypeVar("_SelectType", bound=Any)


def add_pagination_to_query(query: Select[_SelectType], body: PaginationRequest) -> Select[_SelectType]:
    return query.slice((body.page - 1) * body.limit, body.page * body.limit)


async def get_rows_count_in(
    db: AsyncSession, id_column: InstrumentedAttribute[Any] | Select[Any], limit: int
) -> tuple[int, int]:
    if isinstance(id_column, Select):
        # If id_column is a query, execute it and get the result
        res = (await db.execute(id_column)).scalar()
    else:
        # Otherwise, construct a query to count the rows
        res = (await db.execute(func.count(id_column))).scalar()

    if not isinstance(res, int):
        raise TypeError("Rows count is not an integer")

    pages = res / limit
    if pages % 1 != 0:
        pages = int(pages) + 1

    return res, int(pages)
