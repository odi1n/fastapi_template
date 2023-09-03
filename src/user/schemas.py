from typing import Optional

import pydantic as pd
from pydantic import Field

from src.common.mixins.schemas import CreatedUpdatedMixin, PrimaryKeyMixin
from src.common.schemas.filters import Filter, ListFilter


class BaseUser(pd.BaseModel):
    first_name: Optional[str]
    middle_name: Optional[str]
    last_name: Optional[str]


class UserView(BaseUser, PrimaryKeyMixin, CreatedUpdatedMixin):
    email: pd.EmailStr


class UserCreate(BaseUser):
    email: pd.EmailStr
    password: str = pd.Field(min_length=6)


class UserUpdate(BaseUser):
    password: Optional[str] = pd.Field(min_length=6)


class UserUnprotectedView(UserView):
    password: str


class UserFilter(Filter):
    ...


class UserListFilter(ListFilter):
    ...


class BaseTokenResponse(pd.BaseModel):
    token_type: str = Field(default="bearer")
    access_token: str


class BaseRefreshToken(pd.BaseModel):
    refresh_token: str


class AccessTokenResponse(BaseTokenResponse):
    ...


class RefreshTokenResponse(BaseRefreshToken):
    ...


class TokensResponse(BaseTokenResponse, BaseRefreshToken):
    ...
