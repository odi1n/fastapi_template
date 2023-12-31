from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PrimaryKeyMixin(BaseModel):
    id: int


class CreatedUpdatedMixin(BaseModel):
    created_at: datetime
    updated_at: Optional[datetime] = None
