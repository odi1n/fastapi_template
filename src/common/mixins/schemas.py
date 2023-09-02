from datetime import datetime

from pydantic import BaseModel


class PrimaryKeyMixin(BaseModel):
    id: int


class CreatedUpdatedMixin(BaseModel):
    created_at: datetime
    updated_at: datetime | None = None
