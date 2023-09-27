from fastapi import FastAPI

from src.configuration import Configuration
from src.containers import Container
from src.settings import setting
from src.user.web.rest import auth_router, user_router

__routers__ = Configuration(routers=((user_router, "/user"), (auth_router, "/auth")))
__middleware__ = Configuration(middlewares_class=None)


class Server:
    __app = FastAPI

    def __init__(self, app: FastAPI) -> None:
        self.__app = app
        self.__register_middleware(app)
        self.__register_routes(app)
        self.__register_di_container(app)

    def get_app(self) -> FastAPI:
        return self.__app

    @staticmethod
    def __register_middleware(app: FastAPI) -> None:
        __middleware__.register_middleware(app)

    @staticmethod
    def __register_routes(app: FastAPI) -> None:
        __routers__.register_routes(app)

    @staticmethod
    def __register_di_container(app: FastAPI) -> None:
        container = Container()
        container.config.from_dict(setting.dict())
        app.container = container
