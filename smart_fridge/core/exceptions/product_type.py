from .abc import AbstractException, NotFoundException


class ProductTypeException(AbstractException):
    pass


class ProductTypeNotFoundException(ProductTypeException, NotFoundException):
    detail = "product type not found"
