"""FastAPI routes for file upload and download operations."""

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from typing import Generator
import io

from app.api.legacy.schemas.file_schemas import FileUploadResponse
from app.api.legacy.services.file_service import FileService

router = APIRouter(prefix="", tags=["File Operations"])

# Initialize service instance
_file_service = FileService()


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)) -> FileUploadResponse:
    """Upload a file and store it in memory.

    Reads the file content entirely in memory without writing to disk.
    Generates a SHA-256 checksum as the file identifier.

    Args:
        file: The uploaded file from multipart/form-data.

    Returns:
        FileUploadResponse with file metadata and checksum.

    Raises:
        HTTPException: If file is empty or cannot be processed.

    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename cannot be empty")

    # Read file content in memory (no disk access)
    content = await file.read()

    if not content:
        raise HTTPException(status_code=400, detail="File content cannot be empty")

    # Store in memory and generate checksum
    file_id = _file_service.store_file(content, file.filename)

    return FileUploadResponse(
        message="File uploaded successfully",
        file_id=file_id,
        filename=file.filename,
        size_bytes=len(content),
    )


@router.get("/download/{file_id}")
async def download_file(file_id: str) -> StreamingResponse:
    """Download a file as a generated text file.

    Retrieves the file from memory storage and returns it as
    a downloadable text file using StreamingResponse.

    Args:
        file_id: SHA-256 checksum of the file to download.

    Returns:
        StreamingResponse with the generated text file.

    Raises:
        HTTPException: If file_id is not found in storage.

    """
    # Retrieve file content from memory
    original_content = _file_service.get_file(file_id)

    if original_content is None:
        raise HTTPException(status_code=404, detail=f"File with ID {file_id} not found")

    # Generate text content for download
    text_content = _file_service.generate_text_content(file_id, len(original_content))

    # Create generator for streaming response
    def file_generator() -> Generator[bytes, None, None]:
        """Generator to yield text content in chunks."""
        yield text_content.encode("utf-8")

    return StreamingResponse(
        file_generator(),
        media_type="text/plain",
        headers={
            "Content-Disposition": f'attachment; filename="download_{file_id[:16]}.txt"'
        },
    )
