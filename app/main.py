from fastapi import FastAPI

from app.api.routers.integrations_intercom import router as intercom_router
from app.api.routers.internal_conversations import router as internal_router
from app.repositories.conversations import ConversationRepository
from fastapi.exceptions import RequestValidationError
from app.core.error_handlers import request_validation_exception_handler


def create_app() -> FastAPI:
    app = FastAPI(
        title="KBMS Backend Integration Service (Skeleton)",
        version="0.0.1",
    )
    app.add_exception_handler(RequestValidationError, request_validation_exception_handler)

    repo = ConversationRepository()
    repo._init_db()
    app.state.repo = repo


    app.include_router(intercom_router)
    app.include_router(internal_router)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
