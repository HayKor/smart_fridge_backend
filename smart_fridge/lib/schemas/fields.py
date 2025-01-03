from typing import Any, Self

from pydantic import Field
from pydantic.fields import FieldInfo


def wrap_field(field_info: FieldInfo) -> Any:
    class WrappedField(FieldInfo):
        def _get_kwargs(self) -> dict[str, Any]:
            return getattr(self, "_inititial_kwargs").copy()

        def __call__(self, **new_kwargs: Any) -> Any:
            kwargs = self._get_kwargs()
            kwargs.update(new_kwargs)
            return self.__class__._init_wrapped(kwargs)

        @classmethod
        def _init_wrapped(cls, initial_kwargs: dict[str, Any]) -> Self:
            c = cls(**initial_kwargs)
            setattr(c, "_inititial_kwargs", initial_kwargs)
            # store initial kwargs, so we can recreate the field
            return c

    dict_ = {}
    for attr in field_info.__slots__:
        dict_[attr] = getattr(field_info, attr)

    return WrappedField._init_wrapped(dict_)


BaseField = wrap_field(Field())

TIMESTAMP = BaseField(description="Timestamp in seconds since UNIX epoch.", examples=[1610000000], ge=0)
DATETIME = BaseField(description="Date and time in ISO 8601 format.", examples=["2021-01-07T12:00:00Z"])

UUID = BaseField(
    description="UUID version 4.",
    examples=["123e4567-e89b-12d3-a456-426614174000"],
)
ID = BaseField(
    description="Unique integer autoincrementing identifier.",
    examples=[1],
    ge=0,
)
