from fastapi import FastAPI

from src.server import Server


def create_app() -> FastAPI:
    app = FastAPI()
    return Server(app).get_app()


app = create_app()
