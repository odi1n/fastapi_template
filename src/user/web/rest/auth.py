from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.user import schemas as sc
from src.user.auth import Auth
from src.user.exceptions import UserEmailExistsError
from src.user.schemas import TokensResponse
from src.user.services import UserService

router = APIRouter(tags=["Авторизация"])


@router.post(
    "/signup",
    responses={
        401: {"description": "Unauthorized"},
    },
)
@inject
async def sign_up(
    obj_in: sc.UserCreate,
    user_service: UserService = Depends(Provide["services.user_service"]),
) -> Optional[sc.UserView]:
    try:
        return await user_service.repository_create_object(obj_in)
    except UserEmailExistsError as ex:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Email {ex.email} is exists",
        ) from ex


@router.post(
    "/signin",
    responses={
        401: {"description": "Unauthorized"},
    },
)
@inject
async def sign_in(
    credentials: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(Provide["services.user_service"]),
) -> sc.TokensResponse:
    user = await user_service.authenticate_user(
        email=credentials.username,
        password=credentials.password,
    )

    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access_token = Auth.create_access_token({"sub": user.email})
    refresh_token = Auth.create_refresh_token({"sub": user.email})
    return TokensResponse(access_token=access_token, refresh_token=refresh_token)
