import abc

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
    ...
