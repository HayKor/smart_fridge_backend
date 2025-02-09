from .abc import AbstractException, ForbiddenException, NotFoundException


class CartProductException(AbstractException):
    pass


class CartProductNotFoundException(CartProductException, NotFoundException):
    detail = "cart product not found"


class CartProductForbiddenException(CartProductException, ForbiddenException):
    detail = "cart product forbidden"
