from typing import Any, Callable, Sequence

from .abc import BaseSchema


class BaseJob(BaseSchema):
    func: Callable
    trigger: str
    args: Sequence[Any]


class TimeJob(BaseJob):
    hour: int | None = None
    minute: int | None = None
    second: int | None = None
