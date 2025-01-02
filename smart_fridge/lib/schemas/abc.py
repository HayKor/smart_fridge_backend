from abc import ABC
from typing import Any, Generator

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel, ABC):

    model_config = ConfigDict(from_attributes=True)

    def iterate_set_fields(self, exclude: list[str] = []) -> Generator[tuple[str, Any], None, None]:
        for field_name in self.model_fields_set:
            if field_name in exclude:
                continue
            attr = getattr(self, field_name)
            yield field_name, attr
