from datetime import datetime, timedelta

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from jose.constants import ALGORITHMS

from src.settings import setting

from .private.repositories import UserRepository
from .schemas import UserUnprotectedView

token_scheme = OAuth2PasswordBearer(tokenUrl="authorize", scheme_name="email")


class Auth:
    async def __call__(
        self,
        token: str = Depends(token_scheme),
        repository: UserRepository = Depends(),
    ) -> UserUnprotectedView:
        credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, setting.JWT_SECRET_KEY)
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
    def create_access_token(data: dict) -> str:
        to_encode = data.copy()
        if setting.JWT_TOKEN_EXPIRE_MINUTES:
            to_encode.update(
                {
                    "exp": datetime.utcnow()
                    + timedelta(minutes=setting.JWT_TOKEN_EXPIRE_MINUTES),
                },
            )
        token = jwt.encode(
            to_encode,
            setting.JWT_SECRET_KEY,
            algorithm=ALGORITHMS.HS256,
        )
        return token
