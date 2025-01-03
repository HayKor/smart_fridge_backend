from .abc import AbstractException, NotFoundException


class ProductException(AbstractException):
    pass


class ProductNotFoundException(ProductException, NotFoundException):
    detail = "product not found"
