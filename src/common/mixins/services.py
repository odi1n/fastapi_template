from typing import Generic, TypeVar

from pydantic import BaseModel

from src.common.interfaces.repository import AsyncBaseRepositoryInterface
from src.common.schemas.filters import Filter, ListFilter

TypeRepository = TypeVar("TypeRepository", bound=AsyncBaseRepositoryInterface)
TypeView = TypeVar("TypeView", bound=BaseModel)


class ServiceRepositoryMixin(Generic[TypeRepository, TypeView]):
    export_fields: dict[str, str] = {}

    def __init__(self, repository: TypeRepository):
        self.repository = repository

    async def repository_object(self, filter_: Filter) -> TypeView | None:
        return await self.repository.get(filter_)

    async def repository_objects(self, filter_: ListFilter) -> list[TypeView]:
        return await self.repository.get_list(filter_)

    async def repository_create_object(self, obj_in: BaseModel) -> TypeView | None:
        return await self.repository.create(obj_in)

    async def repository_update_object(
        self,
        filter_: Filter,
        obj_in: BaseModel,
    ) -> TypeView | None:
        return await self.repository.update(obj_in, filter_)

    async def repository_delete_object(self, filter_: Filter) -> bool:
        return await self.repository.delete(filter_)
