from typing import Optional

from fastapi import FastAPI


class Configuration:
    routers: Optional[tuple]
    middlewares_class: Optional[tuple[type]]

    def __init__(
        self,
        routers: Optional[tuple] = None,
        middlewares_class: Optional[tuple[type]] = None,
    ) -> None:
        self.routers = routers
        self.middlewares_class = middlewares_class

    def register_routes(self, app: FastAPI) -> None:
        if not self.routers:
            return None

        for router, url in self.routers:
            app.include_router(router, prefix=url)

    def register_middleware(self, app: FastAPI) -> None:
        if not self.middlewares_class:
            return None

        for middleware in self.middlewares_class:
            app.add_middleware(middleware)
