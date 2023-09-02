from typing import Optional

from src.common.mixins.services import ServiceRepositoryMixin
from src.user import schemas as sc
from src.user.interfaces import UserRepositoryInterface


class UserService(ServiceRepositoryMixin[UserRepositoryInterface, sc.UserView]):
    async def authenticate_user(
        self,
        email: str,
        password: str,
    ) -> Optional[sc.UserUnprotectedView]:
        user = await self.repository.get_by_email(email)
        if user and self.password_verify(password, user.password):
            return user
        return None
