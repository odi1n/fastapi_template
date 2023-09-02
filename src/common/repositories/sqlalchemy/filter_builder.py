from typing import Optional

from sqlalchemy import Select, or_, select
from sqlalchemy.orm import (
    ColumnProperty,
    DeclarativeMeta,
    RelationshipProperty,
    class_mapper,
)

from src.common.schemas.filters import ListFilter


class FilterBuilder:
    def __init__(self, model: DeclarativeMeta):
        self._model = model

    def build(self, filter_: ListFilter, stmt: Select | None = None) -> Select:
        if stmt is None:
            stmt = select(self._model)

        stmt = self._search(stmt, filter_).limit(filter_.limit).offset(filter_.offset)

        return self._sort(
            stmt,
            filter_,
        )

    def get_model_field_to_filter(
        self,
        path: list[str],
        model: Optional[DeclarativeMeta] = None,
    ) -> Optional[ColumnProperty]:
        field = model if model else self._model
        for p in path:
            if isinstance(field, DeclarativeMeta):
                if hasattr(field, p):
                    field = getattr(field, p)
                else:
                    return None
            elif isinstance(field.prop, RelationshipProperty):
                if hasattr(field.property.mapper.class_, p):
                    field = getattr(field.property.mapper.class_, p)
                else:
                    return None

        return field

    def _sort(self, stmt: Select, filter_: ListFilter) -> Select:
        field, order = filter_.get_sort()
        if not field:
            return stmt

        attr = self.get_model_field_to_filter(field.split("__"))
        if attr:
            stmt = stmt.order_by(attr if order else attr.desc())

        return stmt

    def _search(self, stmt: Select, filter_: ListFilter) -> Select:
        if not filter_.search or not isinstance(filter_.search, str):
            return stmt
        q = []
        for prop in class_mapper(self._model).iterate_properties:
            if isinstance(prop, RelationshipProperty):
                continue
            field = getattr(self._model, prop.key)
            if field.type.python_type is str:
                q.append(field.icontains(filter_.search))
        return stmt.where(or_(*q)) if q else stmt
