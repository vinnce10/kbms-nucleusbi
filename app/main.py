from fastapi import FastAPI

from app.api.routers.integrations_intercom import router as intercom_router
from app.api.routers.internal_conversations import router as internal_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="KBMS Backend Integration Service (Skeleton)",
        version="0.0.1",
    )

    app.include_router(intercom_router)
    app.include_router(internal_router)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
