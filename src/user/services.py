from typing import Optional

from passlib.context import CryptContext

from src.common.mixins.services import ServiceRepositoryMixin
from src.user import schemas as sc
from src.user.exceptions import UserEmailExistsError
from src.user.interfaces import UserRepositoryInterface

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService(ServiceRepositoryMixin[UserRepositoryInterface, sc.UserView]):
    async def repository_create_object(  # type: ignore
        self,
        obj_in: sc.UserCreate,
    ) -> Optional[sc.UserView]:
        obj_in.password = self.get_password_hash(obj_in.password)
        if await self.repository.get_by_email(obj_in.email):
            raise UserEmailExistsError(obj_in.email)
        return await super().repository_create_object(obj_in)

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
        return password_context.hash(plain_password)

    @staticmethod
    def password_verify(plain_password: str, hashed_password: str) -> bool:
        return password_context.verify(plain_password, hashed_password)
