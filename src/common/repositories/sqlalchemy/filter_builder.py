from typing import Optional

from sqlalchemy import Select, select
from sqlalchemy.orm import ColumnProperty, DeclarativeMeta, RelationshipProperty

from src.common.schemas.filters import ListFilter


class FilterBuilder:
    def __init__(self, model: DeclarativeMeta):
        self._model = model

    def build(self, filter_: ListFilter, stmt: Optional[Select] = None) -> Select:
        if stmt is None:
            stmt = select(self._model)

        stmt = stmt.limit(filter_.limit).offset(filter_.offset)

        return stmt

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
