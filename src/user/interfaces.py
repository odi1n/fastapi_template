import abc
from typing import Optional

from src.common.interfaces.repository import AsyncBaseRepositoryInterface
from src.user import schemas as sc


class UserRepositoryInterface(
    abc.ABC,
    AsyncBaseRepositoryInterface[
        sc.UserFilter,
        sc.UserListFilter,
        sc.UserCreate,
        sc.UserUpdate,
        sc.UserView,
    ],
):
    @abc.abstractmethod
    async def get_by_email(self, email: str) -> Optional[sc.UserUnprotectedView]:
        pass
