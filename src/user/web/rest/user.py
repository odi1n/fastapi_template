from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from src.common.exceptions.http import HTTPNotFoundException
from src.common.schemas.response import ResponseList
from src.user import schemas as sc
from src.user.auth import Auth
from src.user.services import UserService

router = APIRouter()


@router.get("/", tags=["Пользователи"])
@inject
async def user_list(
    _: Auth = Depends(Auth()),
    filter_: sc.UserListFilter = Depends(),
    user_service: UserService = Depends(Provide["services.user_service"]),
) -> ResponseList[sc.UserView]:
    data = await user_service.repository_objects(filter_)
    return ResponseList[sc.UserView](
        data=data,
        meta=filter_.meta,
    )


@router.get(
    "/{id}",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Not Found"},
    },
    tags=["Пользователи"],
)
@inject
async def user(
    _: Auth = Depends(Auth()),
    filter_: sc.UserFilter = Depends(),
    user_service: UserService = Depends(Provide["services.user_service"]),
) -> sc.UserView:
    model = await user_service.repository_object(filter_)
    if not model:
        raise HTTPNotFoundException
    return model


@router.put(
    "/{id}",
    tags=["Пользователи"],
    status_code=status.HTTP_202_ACCEPTED,
)
@inject
async def user_update(
    id: int,
    obj_in: sc.UserUpdate,
    _: Auth = Depends(Auth()),
    user_service: UserService = Depends(Provide["services.user_service"]),
) -> Optional[sc.UserView]:
    filter_ = sc.UserFilter(id=id)

    result = await user_service.repository_update_object(filter_, obj_in)
    if result:
        return result
    raise HTTPNotFoundException


@router.delete(
    "/{id}",
    tags=["Пользователи"],
    status_code=status.HTTP_204_NO_CONTENT,
)
@inject
async def user_delete(
    id: int,
    _: Auth = Depends(Auth()),
    user_service: UserService = Depends(Provide["services.user_service"]),
) -> None:
    filter_ = sc.UserFilter(id=id)
    deleted = await user_service.repository_delete_object(filter_)
    if not deleted:
        raise HTTPNotFoundException
