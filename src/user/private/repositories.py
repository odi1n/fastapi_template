from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.repositories.sqlalchemy import SqlAlchemyRepository

# from src.database import get_session
from src.user import schemas as sc
from src.user.interfaces import UserRepositoryInterface

from ...database import get_session
from .models.user import User


class UserRepository(
    UserRepositoryInterface,
    SqlAlchemyRepository[
        User,
        sc.UserFilter,
        sc.UserListFilter,
        sc.UserCreate,
        sc.UserUpdate,
        sc.UserView,
    ],
):
    def __init__(self, session: AsyncSession = Depends(get_session)):
        super().__init__(
            view_model=sc.UserView,
            model=User,
            session=session,
        )

    async def get_by_email(self, email: str) -> sc.UserUnprotectedView | None:
        stmt = select(User).where(User.email == email)
        result = await self.session.scalars(stmt)
        user = result.first()
        if user:
            return sc.UserUnprotectedView.parse_obj(user.__dict__)
        return None
