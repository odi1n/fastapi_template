from typing import Any, Generic, List, Type, TypeVar

from pydantic import BaseModel as PydanticModel
from pydantic._internal._model_construction import ModelMetaclass
from sqlalchemy import Select, delete, func, inspect, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeMeta, collections

from src.common.interfaces.repository import AsyncBaseRepositoryInterface
from src.common.schemas.filters import Filter, ListFilter
from src.database import BaseModel

from .filter_builder import FilterBuilder

ModelType = TypeVar("ModelType", bound=BaseModel, covariant=True)
FilterType = TypeVar("FilterType", bound=Filter)
ListFilterType = TypeVar("ListFilterType", bound=ListFilter)
CreateType = TypeVar("CreateType", bound=PydanticModel)
UpdateType = TypeVar("UpdateType", bound=PydanticModel)
ViewType = TypeVar("ViewType", bound=PydanticModel)
SelectType = TypeVar("SelectType", bound=PydanticModel)
ArraySelectionType = TypeVar("ArraySelectionType", bound=BaseModel)


class SqlAlchemyRepository(
    AsyncBaseRepositoryInterface,
    Generic[ModelType, FilterType, ListFilterType, CreateType, UpdateType, ViewType],
):
    def _get_statement(self, filter_: FilterType, stmt: Select = None) -> Select:
        if stmt is None:
            stmt = select(self.model)

        for field, value in filter_.dict(exclude_unset=True, exclude_none=True).items():
            if hasattr(self.model, field):
                stmt = stmt.where(getattr(self.model, field) == value)

        return stmt

    def _apply_options(self, stmt: Select) -> Select:
        return stmt

    def _apply_filters(self, filter_: ListFilterType, stmt: Select = None) -> Select:
        if stmt is None:
            stmt = select(self.model)
        return self.filter_builder.build(filter_, stmt)

    def _get_list_statement(
        self,
        filter_: ListFilterType,
        stmt: Select = None,
    ) -> Select:
        if stmt is None:
            stmt = select(self.model)
        stmt = self._apply_options(stmt)
        return self._apply_filters(filter_, stmt)

    # flake8: noqa
    def _pydantic_to_model(
        self,
        obj_in: PydanticModel | dict,
        model: DeclarativeMeta | BaseModel,
    ) -> BaseModel:
        if isinstance(obj_in, PydanticModel):
            obj_in = obj_in.dict(exclude_unset=True)

        if isinstance(model, DeclarativeMeta):
            model = model()

        mapper = inspect(model)

        if hasattr(mapper, "mapper"):
            mapper = mapper.mapper

        for name, field in mapper.relationships.items():
            class_ = field.mapper.class_
            try:
                relation_obj = obj_in.pop(name)
            except KeyError:
                continue

            attr = getattr(model, name)

            if attr is None:
                attr = [] if field.uselist else class_()

            if field.uselist and not isinstance(relation_obj, list):
                relation_obj = [relation_obj]

            if field.uselist:
                length = len(attr)
                for idx, obj in enumerate(relation_obj):
                    if length > 0:
                        attr[idx] = self._pydantic_to_model(obj, attr[idx])
                    else:
                        attr.append(self._pydantic_to_model(obj, class_))
                    length -= 1
            else:
                attr = self._pydantic_to_model(relation_obj, attr)

            obj_in[name] = attr
        if isinstance(obj_in, dict):
            for field, value in obj_in.items():
                if hasattr(mapper.attrs, field):
                    setattr(model, field, value)

        return model

    def _model_to_dict(self, model: BaseModel) -> dict[str | Any]:
        model_dict = model.__dict__

        for name, field in model_dict.items():
            if isinstance(field, BaseModel):
                model_dict[name] = self._model_to_dict(field)
            elif isinstance(field, collections.InstrumentedList):
                items = []
                for i in list(field):
                    if isinstance(i, BaseModel):
                        items.append(self._model_to_dict(i))
                    else:
                        items.append(i)
                model_dict[name] = items
        return model_dict

    def _model_to_pydantic(
        self,
        model: BaseModel,
        view_model: ModelMetaclass,
    ) -> ViewType | SelectType:
        return view_model.parse_obj(
            self._model_to_dict(model),
        )

    def __init__(
        self,
        model: ModelType,
        view_model: Type["ViewType"],
        session: AsyncSession,
        filter_builder: FilterBuilder | None = None,
    ):
        self.model = model
        self.view_model = view_model
        self.session = session

        if filter_builder is None:
            self.filter_builder = FilterBuilder(model)
        else:
            self.filter_builder = filter_builder

    async def get(self, filter_: FilterType) -> ViewType | None:
        stmt = self._get_statement(filter_)
        model = await self.session.scalar(stmt)
        return (
            self._model_to_pydantic(model, self.view_model)
            if model is not None
            else None
        )

    async def get_list(self, filter_: ListFilterType) -> List[ViewType]:
        stmt = self._get_list_statement(filter_)
        result = await self.session.scalars(stmt)
        filter_.set_total(
            await self.session.scalar(
                select(func.count()).select_from(
                    stmt.offset(None).limit(None).order_by(None),
                ),
            ),
        )
        return [self._model_to_pydantic(model, self.view_model) for model in result]

    async def get_all(
        self,
        filter_: ListFilterType,
    ) -> List[ViewType]:
        stmt = self._get_list_statement(filter_)
        result = await self.session.scalars(stmt.limit(None).offset(None))
        return [self._model_to_pydantic(model, self.view_model) for model in result]

    async def create(self, obj_in: CreateType) -> ViewType | None:
        model = self._pydantic_to_model(obj_in, self.model)
        self.session.add(model)
        await self.session.flush()
        return self._model_to_pydantic(model, self.view_model)

    async def update(self, obj_in: UpdateType, filter_: FilterType) -> ViewType | None:
        stmt = self._get_statement(filter_)
        result = await self.session.scalar(stmt)

        if result is None:
            return None
        result.__dict__
        model = self._pydantic_to_model(obj_in, result)

        self.session.add(result)
        await self.session.flush()
        return self._model_to_pydantic(model, self.view_model)

    async def delete(self, filter_: FilterType) -> bool:
        stmt = delete(self.model).where(self.model.id == filter_.id)
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount > 0
