from typing import Optional

import bcrypt

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

    @staticmethod
    def get_password_hash(plain_password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(plain_password.encode(), salt).decode()
        return hashed

    @staticmethod
    def password_verify(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
