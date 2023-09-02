import abc
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel

FilterModel = TypeVar("FilterModel", bound=BaseModel)
AllFilterModel = TypeVar("AllFilterModel", bound=BaseModel)
CreateModel = TypeVar("CreateModel", bound=BaseModel)
UpdateModel = TypeVar("UpdateModel", bound=BaseModel)
ViewModel = TypeVar("ViewModel", bound=BaseModel)
SelectModel = TypeVar("SelectModel", bound=BaseModel)
ArraySelectionModel = TypeVar("ArraySelectionModel", bound=BaseModel)


class AsyncBaseRepositoryInterface(
    Generic[FilterModel, AllFilterModel, CreateModel, UpdateModel, ViewModel],
):
    @abc.abstractmethod
    async def get(
        self,
        filter_: FilterModel,
    ) -> Optional[ViewModel]:
        ...

    @abc.abstractmethod
    async def get_list(
        self,
        filter_: AllFilterModel,
    ) -> List[ViewModel]:
        ...

    @abc.abstractmethod
    async def get_all(
        self,
        filter_: AllFilterModel,
    ) -> List[ViewModel]:
        ...

    @abc.abstractmethod
    async def create(
        self,
        obj_in: CreateModel,
    ) -> Optional[ViewModel]:
        ...

    @abc.abstractmethod
    async def update(
        self,
        obj_in: UpdateModel,
        filter_: FilterModel,
    ) -> Optional[ViewModel]:
        ...

    @abc.abstractmethod
    async def delete(self, filter_: FilterModel) -> bool:
        ...
