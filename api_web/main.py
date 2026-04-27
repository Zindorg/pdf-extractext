"""Main application entry point for PDF-Extractext API Web.

This module initializes the FastAPI application with CORS support
and includes the file operation routes.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router


def create_application() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance.

    """
    application = FastAPI(
        title="PDF-Extractext API Web",
        version="1.0.0",
        description="API for file upload and download operations with in-memory storage",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Configure CORS middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    application.include_router(router)

    return application


app = create_application()


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint for monitoring.

    Returns:
        Simple status message indicating the API is running.

    """
    return {"status": "healthy", "service": "pdf-extractext-api"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
