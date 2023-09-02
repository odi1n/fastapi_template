from pydantic import BaseModel, Field, PrivateAttr


class BaseFilter(BaseModel):
    id: int | None


class BaseListFilter(BaseModel):
    limit: int = Field(100, gt=0)
    offset: int = Field(0, ge=0)
    sort: str | None
    search: str | None

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

    def get_sort(self) -> tuple[str | None, int]:
        if not isinstance(self.sort, str):
            return None, 0

        field = self.sort.strip("+- ")
        if not field:
            return None, 0

        direct = 0 if self.sort.strip().startswith("-") else 1
        if self.__filter_config__.sort == "*" or field in self.__filter_config__.sort:
            return field, direct

        return None, 0
