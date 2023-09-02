from . import base


class Filter(base.BaseFilter):
    ...


class ListFilter(base.BaseListFilter):
    ...


__all__ = [
    "Filter",
    "ListFilter",
]
