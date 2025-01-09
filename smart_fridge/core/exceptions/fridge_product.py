from .abc import AbstractException, ForbiddenException, NotFoundException


class FridgeProductException(AbstractException):
    pass


class FridgeProductNotFoundException(FridgeProductException, NotFoundException):
    detail = "fridge product not found"


class FridgeProductForbiddenException(FridgeProductException, ForbiddenException):
    detail = "fridge product forbidden"
