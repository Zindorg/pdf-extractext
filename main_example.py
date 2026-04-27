"""Example main.py with MongoDB configuration.

Copy this to main.py or adapt your existing main.py.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient

from api.routes import pdf_routes
from api.routes.pdf_routes import set_pdf_repository
from core.config import settings
from repositories.mongo_pdf_repository import MongoPDFRepository


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

    # USER CONFIGURATION: Set up MongoDB connection
    # You provide the MongoDB client - the app handles the rest
    mongo_client = MongoClient(settings.mongodb_uri)
    mongo_repository = MongoPDFRepository(
        mongo_client,
        database=settings.mongodb_database
    )

    # Inject repository into routes
    set_pdf_repository(mongo_repository)

    # Include routers
    application.include_router(pdf_routes.router)

    return application


app = create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
