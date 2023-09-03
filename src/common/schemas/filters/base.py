from typing import Optional

from pydantic import BaseModel, Field, PrivateAttr


class BaseFilter(BaseModel):
    id: Optional[int]


class BaseListFilter(BaseModel):
    limit: int = Field(100, gt=0)
    offset: int = Field(0, ge=0)

    _total: int = PrivateAttr(0)

    def set_total(self, value: int) -> None:
        self._total = value

    @property
    def meta(self) -> dict[str, int]:
        return {
            "total": self._total,
            "limit": self.limit,
            "offset": self.offset,
        }
