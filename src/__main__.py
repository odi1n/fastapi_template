import uvicorn

from src.settings import setting

if __name__ == "__main__":
    uvicorn.run(
        "src.app:app",
        host=setting.HOST,
        port=setting.PORT,
        reload=setting.DEBUG,
    )
