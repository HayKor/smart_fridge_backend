from logging import getLogger
from typing import Any, TypeVar

from sqlalchemy import Select
from sqlalchemy.orm import InstrumentedAttribute

from smart_fridge.lib.models.abc import AbstractModel
from smart_fridge.lib.schemas.abc import BaseSchema
from smart_fridge.lib.schemas.enums.filter import FilterType, OrderByType


logger = getLogger(__name__)

_SelectType = TypeVar("_SelectType", bound=Any)


def add_filters_to_query(
    query: Select[_SelectType], table: type[AbstractModel], body: BaseSchema, *, include_order_by: bool = True
) -> Select[_SelectType]:
    groups: set[str] = set()

    for field_name, field in body.model_fields.items():
        field_value = getattr(body, field_name)
        if field_value is None:
            continue

        extra: dict[str, Any]
        if callable(field.json_schema_extra):
            logger.warning(
                "Filter schema extra for field %s.%s is not a dict, but a callable", body.__class__.__name__, field_name
            )
            continue

        if field.json_schema_extra is not None:
            extra = field.json_schema_extra
        else:
            if hasattr(field, "_inititial_kwargs"):
                extra = field._inititial_kwargs  # type: ignore
            else:
                extra = {}

        table_column = extra.get("table_column", field_name)
        filter_type = extra.get("filter_type", FilterType.eq)
        # Check if filter group is already in use, if set
        filter_group = extra.get("group", None)
        if filter_group is not None:
            groups.add(filter_group)

        logger.debug("Filtering by %s with %s and %s", table_column, filter_type, field_value)

        if filter_type in (FilterType.like, FilterType.ilike):
            field_value = field_value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_").replace("~", "\\~")
            field_value = "%" + field_value + "%"

        table_column_obj: InstrumentedAttribute[Any] | None = None
        current_model = table
        for col in table_column.split("."):
            table_column_obj = getattr(current_model, col, None)
            if table_column_obj is None:
                raise ValueError(f"Table {current_model} has no column {col}")
            if hasattr(table_column_obj, "property") and hasattr(table_column_obj.property, "mapper"):
                current_model = table_column_obj.property.mapper.class_
            else:
                break

        match filter_type:
            case FilterType.eq:
                query = query.filter(table_column_obj == field_value)
            case FilterType.ne:
                query = query.filter(table_column_obj != field_value)
            case FilterType.gt:
                query = query.filter(table_column_obj > field_value)
            case FilterType.ge:
                query = query.filter(table_column_obj >= field_value)
            case FilterType.lt:
                query = query.filter(table_column_obj < field_value)
            case FilterType.le:
                query = query.filter(table_column_obj <= field_value)
            case FilterType.like:
                query = query.filter(table_column_obj.like(field_value))
            case FilterType.ilike:
                query = query.filter(table_column_obj.ilike(field_value))
            case FilterType.order_by:
                if include_order_by:
                    query = query.order_by(
                        table_column_obj.asc() if field_value == OrderByType.ASC else table_column_obj.desc()
                    )
            case _:
                raise NotImplementedError(f"Filter type {filter_type} is not implemented")

    logger.debug("Filtered query: %s", query)

    return query
