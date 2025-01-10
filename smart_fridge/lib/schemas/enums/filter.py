from .abc import BaseEnum


class FilterType(BaseEnum):
    eq = "eq"
    ne = "ne"
    gt = "gt"
    ge = "ge"
    lt = "lt"
    le = "le"
    like = "like"
    ilike = "ilike"
    order_by = "order_by"


class OrderByType(BaseEnum):
    ASC = "asc"
    DESC = "desc"
