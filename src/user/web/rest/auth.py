from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from src.containers import Container
from src.user.auth import Auth
from src.user.schemas import AccessTokenResponse
from src.user.services import UserService

router = APIRouter()


@router.post(
    "/authorize",
    tags=["Авторизация"],
    responses={
        401: {"description": "Unauthorized"},
    },
)
@inject
async def authorize(
    credentials: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> AccessTokenResponse:
    user = await user_service.authenticate_user(
        email=credentials.username,
        password=credentials.password,
    )

    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access_token = Auth.create_access_token({"sub": user.email})
    return AccessTokenResponse(access_token=access_token)
