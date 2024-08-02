import uvicorn

from app.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.application:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOADED,
        workers=settings.WORKERS,
    )
