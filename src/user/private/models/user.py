from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.common.mixins.models import CreatedUpdatedMixin, PrimaryKeyMixin
from src.database import BaseModel


class User(BaseModel, PrimaryKeyMixin, CreatedUpdatedMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(120))
    first_name: Mapped[str] = mapped_column(String(120))
    middle_name: Mapped[str] = mapped_column(String(120))
    last_name: Mapped[str] = mapped_column(String(120))
    password: Mapped[str] = mapped_column(String(120))
