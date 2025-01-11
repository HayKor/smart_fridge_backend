from .abc import AbstractException, ConflictException, ForbiddenException, NotFoundException


class CartProductException(AbstractException):
    pass


class CartProductlAlreadyExistsException(CartProductException, ConflictException):
    auto_additional_info_fields = ["product_id"]

    detail = "Cart product with product id {product_id} already exists"
