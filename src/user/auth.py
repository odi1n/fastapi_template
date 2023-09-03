from datetime import datetime, timedelta

from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from src.settings import setting
from src.user import schemas as sc
from src.user.exceptions import credentials_exception
from src.user.private.repositories import UserRepository

token_scheme = OAuth2PasswordBearer(tokenUrl="/signin")


class Auth:
    @inject
    async def __call__(
        self,
        token: str = Depends(token_scheme),
        repository: UserRepository = Depends(Provide["repositories.user_repository"]),
    ) -> sc.UserUnprotectedView:
        try:
            payload = jwt.decode(
                token=token,
                key=setting.JWT_SECRET_KEY,
                algorithms="HS256",
            )
            email = payload.get("sub")
            if email is None:
                raise credentials_exception from None
        except JWTError:
            raise credentials_exception from None
        user = await repository.get_by_email(email)
        if user is None:
            raise credentials_exception from None
        return user

    @staticmethod
    def check_refresh_token(token: str) -> str:
        try:
            payload = jwt.decode(
                token=token,
                key=setting.JWT_REFRESH_SECRET_KEY,
                algorithms="HS256",
            )
            email = payload.get("sub")
            if email is None:
                raise credentials_exception from None
        except JWTError:
            raise credentials_exception from None
        return email

    @staticmethod
    def create_access_token(data: dict) -> str:
        to_encode = data.copy()
        if setting.JWT_ACCESS_TOKEN_EXPIRE_MINUTES:
            to_encode.update(
                {
                    "exp": datetime.utcnow()
                    + timedelta(minutes=setting.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
                },
            )
        token = jwt.encode(
            to_encode,
            setting.JWT_SECRET_KEY,
            algorithm="HS256",
        )
        return token

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        to_encode = data.copy()
        if setting.JWT_REFRESH_TOKEN_EXPIRE_MINUTES:
            to_encode.update(
                {
                    "exp": datetime.utcnow()
                    + timedelta(minutes=setting.JWT_REFRESH_TOKEN_EXPIRE_MINUTES),
                },
            )
        token = jwt.encode(
            to_encode,
            setting.JWT_REFRESH_SECRET_KEY,
            algorithm="HS256",
        )
        return token
