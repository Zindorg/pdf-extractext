"""Main application entry point with MongoDB configuration."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import pdf_routes
from app.routes.pdf_routes import set_pdf_repository
from app.config.settings import settings
from app.infrastructure.database_setup import setup_database
from app.infrastructure.database_connection import close_connection
from app.repositories.repository_factory import RepositoryFactory


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Manage application lifecycle: startup and shutdown."""
    setup_database()
    mongo_repository = RepositoryFactory.get_pdf_repository()
    set_pdf_repository(mongo_repository)
    yield
    close_connection()


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

    application.include_router(pdf_routes.router)

    return application


app = create_application()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
