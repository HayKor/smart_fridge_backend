import typing as t

from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase


_T = t.TypeVar("_T", bound="AbstractModel")


class AbstractModel(DeclarativeBase):
    __abstract__ = True

    def __repr__(self) -> str:
        _repr = f"<{self.__class__.__name__} "
        for name in self._get_primary_keys():
            _repr += f"{name}={self._get_key_value(name)}, "
        return _repr[:-2] + ">"

    def __str__(self) -> str:
        return self.__repr__()

    def to_dict(self) -> dict[str, t.Any]:
        return self.__dict__

    @classmethod
    def from_dict(cls: t.Type[_T], data: dict[str, t.Any]) -> _T:
        return cls(**data)

    @classmethod
    def from_schema(cls: t.Type[_T], model: BaseModel) -> _T:
        return cls.from_dict(model.model_dump())

    @classmethod
    def _get_primary_keys(cls) -> list[str]:
        return [i.name for i in cls.__table__.primary_key.columns.values()]  # type: ignore

    def _get_key_value(self, name: str) -> t.Any:
        return getattr(self, name)
