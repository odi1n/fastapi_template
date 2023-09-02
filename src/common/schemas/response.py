from typing import Generic, TypeVar

import pydantic as pd
from pydantic.generics import GenericModel

TypeModel = TypeVar("TypeModel", bound=pd.BaseModel)


class BaseResponse(GenericModel):
    ...


class ResponseListMeta(pd.BaseModel):
    total: int = pd.Field(0, ge=0)
    limit: int = pd.Field(100, ge=1)
    offset: int = pd.Field(0, ge=0)


class ResponseList(BaseResponse, Generic[TypeModel]):
    data: list[TypeModel]
    meta: ResponseListMeta = ResponseListMeta()
