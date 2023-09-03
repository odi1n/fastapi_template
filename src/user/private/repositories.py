from typing import AsyncContextManager, Callable, Optional

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
    def __init__(
        self,
        session_factory: Callable[..., AsyncContextManager[AsyncSession]],
    ):
        super().__init__(
            view_model=sc.UserView,
            model=User,
            session_factory=session_factory,
        )

    async def get_by_email(self, email: str) -> Optional[sc.UserUnprotectedView]:
        stmt = select(User).where(User.email == email)

        async with self.session_factory() as session:
            result = await session.scalars(stmt)
            user = result.first()
            if user:
                return sc.UserUnprotectedView.parse_obj(user.__dict__)
            return None
