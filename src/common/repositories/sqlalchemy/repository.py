from typing import (
    Any,
    AsyncContextManager,
    Callable,
    Generic,
    List,
    Optional,
    Type,
    TypeVar,
)

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
FilterSchemaType = TypeVar("FilterSchemaType", bound=Filter)
ListFilterSchemaType = TypeVar("ListFilterSchemaType", bound=ListFilter)
CreateSchemaType = TypeVar("CreateSchemaType", bound=PydanticModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=PydanticModel)
ViewSchemaType = TypeVar("ViewSchemaType", bound=PydanticModel)
SelectSchemaType = TypeVar("SelectSchemaType", bound=PydanticModel)


class SqlAlchemyRepository(
    AsyncBaseRepositoryInterface,
    Generic[
        ModelType,
        ViewSchemaType,
        CreateSchemaType,
        UpdateSchemaType,
        FilterSchemaType,
        ListFilterSchemaType,
    ],
):
    def _get_statement(self, filter_: FilterSchemaType, stmt: Select = None) -> Select:
        if stmt is None:
            stmt = select(self.model)

        for field, value in filter_.dict(exclude_unset=True, exclude_none=True).items():
            if hasattr(self.model, field):
                stmt = stmt.where(getattr(self.model, field) == value)

        return stmt

    @staticmethod
    def _apply_options(stmt: Select) -> Select:
        return stmt

    def _apply_filters(
        self, filter_: ListFilterSchemaType, stmt: Select = None
    ) -> Select:
        if stmt is None:
            stmt = select(self.model)
        return self.filter_builder.build(filter_, stmt)

    def _get_list_statement(
        self,
        filter_: ListFilterSchemaType,
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
    ) -> ViewSchemaType | SelectSchemaType:
        return view_model.parse_obj(
            self._model_to_dict(model),
        )

    def __init__(
        self,
        model: ModelType,
        view_model: Type["ViewSchemaType"],
        session_factory: Callable[..., AsyncContextManager[AsyncSession]],
        filter_builder: Optional[FilterBuilder] = None,
    ):
        self.model = model
        self.view_model = view_model
        self.session_factory = session_factory

        if filter_builder:
            self.filter_builder = filter_builder
        else:
            self.filter_builder = FilterBuilder(model)

    async def get(self, filter_: FilterSchemaType) -> Optional[ViewSchemaType]:
        stmt = self._get_statement(filter_)

        async with self.session_factory() as session:
            model = await session.scalar(stmt)
            return (
                self._model_to_pydantic(model, self.view_model)
                if model is not None
                else None
            )

    async def get_list(self, filter_: ListFilterSchemaType) -> List[ViewSchemaType]:
        stmt = self._get_list_statement(filter_)

        async with self.session_factory as session:
            result = await session.scalars(stmt)
            filter_.set_total(
                await session.scalar(
                    select(func.count()).select_from(
                        stmt.offset(None).limit(None).order_by(None),
                    ),
                ),
            )
            return [self._model_to_pydantic(model, self.view_model) for model in result]

    async def get_all(
        self,
        filter_: ListFilterSchemaType,
    ) -> List[ViewSchemaType]:
        stmt = self._get_list_statement(filter_)

        async with self.session_factory as session:
            result = await session.scalars(stmt.limit(None).offset(None))
            return [self._model_to_pydantic(model, self.view_model) for model in result]

    async def create(self, obj_in: CreateSchemaType) -> Optional[ViewSchemaType]:
        model = self._pydantic_to_model(obj_in, self.model)

        async with self.session_factory as session:
            session.add(model)
            await session.flush()
            return self._model_to_pydantic(model, self.view_model)

    async def update(
        self, obj_in: UpdateSchemaType, filter_: FilterSchemaType
    ) -> Optional[ViewSchemaType]:
        stmt = self._get_statement(filter_)

        async with self.session_factory as session:
            result = await session.scalar(stmt)

            if result is None:
                return None
            result.__dict__
            model = self._pydantic_to_model(obj_in, result)

            session.add(result)
            await session.flush()
            return self._model_to_pydantic(model, self.view_model)

    async def delete(self, filter_: FilterSchemaType) -> bool:
        stmt = delete(self.model).where(self.model.id == filter_.id)

        async with self.session_factory as session:
            result = await session.execute(stmt)
            await session.flush()
            return result.rowcount > 0
