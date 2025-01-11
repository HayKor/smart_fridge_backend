from .abc import AbstractException, ConflictException, ForbiddenException, NotFoundException


class FridgeProductException(AbstractException):
    pass


class FridgeProductNotFoundException(FridgeProductException, NotFoundException):
    detail = "fridge product not found"


class FridgeProductForbiddenException(FridgeProductException, ForbiddenException):
    detail = "fridge product forbidden"


class FridgeProductlAlreadyExistsException(FridgeProductException, ConflictException):
    auto_additional_info_fields = ["product_id"]

    detail = "Fridge product with product id {product_id} already exists"
