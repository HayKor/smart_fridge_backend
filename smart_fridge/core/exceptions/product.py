from .abc import AbstractException, ForbiddenException, NotFoundException


class ProductException(AbstractException):
    pass


class ProductNotFoundException(ProductException, NotFoundException):
    detail = "product not found"


class ProductForbiddenException(ProductException, ForbiddenException):
    detail = "product forbidden"
