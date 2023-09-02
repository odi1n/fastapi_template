from sqlalchemy import Column, DateTime, Integer, func


class PrimaryKeyMixin:
    id = Column(Integer, autoincrement=True, primary_key=True)


class CreatedUpdatedMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=func.now())
