from .abc import AbstractException, ConflictException, ForbiddenException, NotFoundException


class CartProductException(AbstractException):
    pass


class CartProductNotFoundException(CartProductException, NotFoundException):
    detail = "cart product not found"


class CartProductForbiddenException(CartProductException, ForbiddenException):
    detail = "cart product forbidden"


class CartProductAlreadyExistsException(CartProductException, ConflictException):
    auto_additional_info_fields = ["product_id"]

    detail = "Cart product with product id {product_id} already exists"
