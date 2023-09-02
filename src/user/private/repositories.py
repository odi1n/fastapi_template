from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.repositories.sqlalchemy import SqlAlchemyRepository
from src.user import schemas as sc
from src.user.interfaces import UserRepositoryInterface

from .models.user import User


class UserRepository(
    UserRepositoryInterface,
    SqlAlchemyRepository[
        User,
        sc.UserView,
        sc.UserCreate,
        sc.UserUpdate,
        sc.UserFilter,
        sc.UserListFilter,
    ],
):
    def __init__(self, session: AsyncSession):
        super().__init__(
            view_model=sc.UserView,
            model=User,
            session=session,
        )

    async def get_by_email(self, email: str) -> Optional[sc.UserUnprotectedView]:
        stmt = select(User).where(User.email == email)
        result = await self.session.scalars(stmt)
        user = result.first()
        if user:
            return sc.UserUnprotectedView.parse_obj(user.__dict__)
        return None
