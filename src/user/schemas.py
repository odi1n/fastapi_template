import pydantic as pd

from src.common.mixins.schemas import CreatedUpdatedMixin, PrimaryKeyMixin
from src.common.schemas.filters import Filter, ListFilter


class BaseUser(pd.BaseModel):
    first_name: str | None
    middle_name: str | None
    last_name: str | None
    position: str | None


class UserCreate(BaseUser):
    email: pd.EmailStr
    password: str = pd.Field(min_length=6)


class UserUpdate(BaseUser):
    password: str | None = pd.Field(min_length=6)


class UserView(BaseUser, PrimaryKeyMixin, CreatedUpdatedMixin):
    email: pd.EmailStr


class UserUnprotectedView(UserView):
    password: str


class UserFilter(Filter):
    ...


class UserListFilter(ListFilter):
    full_name: str | None

    class FilterConfig:
        model = UserView


class AccessTokenResponse(pd.BaseModel):
    access_token: str
