from .abc import AbstractException, ForbiddenException, NotFoundException


class FridgeException(AbstractException):
    pass


class FridgeNotFoundException(FridgeException, NotFoundException):
    detail = "fridge not found"


class FridgeForbiddenException(FridgeException, ForbiddenException):
    detail = "fridge forbidden"
