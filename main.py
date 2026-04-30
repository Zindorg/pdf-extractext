"""Main application entry point with MongoDB configuration."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import pdf_routes
from app.routes.pdf_routes import set_pdf_repository
from app.config.settings import settings
from app.infrastructure.database_setup import setup_database
from app.repositories.repository_factory import RepositoryFactory


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
    )

    # CORS middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ============================================================
    # MongoDB Connection Setup
    # ============================================================
    # Initialize database with indexes
    setup_database()

    # Get repository from factory (singleton pattern)
    mongo_repository = RepositoryFactory.get_pdf_repository()

    # Inject repository into routes
    set_pdf_repository(mongo_repository)
    # ============================================================

    # Include routers
    application.include_router(pdf_routes.router)

    return application


app = create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
