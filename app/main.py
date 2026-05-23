"""Main application entry point with MongoDB configuration."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient

from app.api.exception_handlers import pdf_exception_handlers
from app.config.settings import settings
from app.infrastructure.database_setup import setup_database
from app.routes import pdf_routes


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Manage application lifecycle: startup and shutdown."""
    client = MongoClient(settings.mongodb_uri)
    database = client[settings.mongodb_database]
    application.state.mongodb_client = client
    application.state.mongodb_database = database
    setup_database(database)
    yield
    client.close()


def create_application() -> FastAPI:
    """
    Create and configure FastAPI application with MongoDB.

    Returns:
        Configured FastAPI application
    """
    application = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description="API for PDF text extraction with MongoDB persistence",
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(pdf_routes.router, prefix="/api/v1")

    # Register global exception handlers for RFC 9457 problem details
    for exc_class, handler in pdf_exception_handlers.items():
        application.add_exception_handler(exc_class, handler)

    return application


app = create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
