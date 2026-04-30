"""Pydantic schemas for file upload and download operations."""

from pydantic import BaseModel, Field


class FileUploadResponse(BaseModel):
    """Response schema for file upload endpoint.

    Attributes:
        message: Success message indicating the file was processed.
        file_id: SHA-256 checksum used as unique identifier.
        filename: Original filename of the uploaded file.
        size_bytes: Size of the file content in bytes.

    """

    message: str = Field(..., description="Success message")
    file_id: str = Field(..., description="SHA-256 checksum of file content")
    filename: str = Field(..., description="Original filename")
    size_bytes: int = Field(..., ge=0, description="File size in bytes")

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "File uploaded successfully",
                "file_id": "a3f5c8e9...",
                "filename": "document.pdf",
                "size_bytes": 12345,
            }
        }
    }


class FileDownloadResponse(BaseModel):
    """Response schema for file download endpoint.

    Attributes:
        file_id: Unique identifier of the file.
        filename: Generated filename for the download.
        content_type: MIME type of the file.

    """

    file_id: str = Field(..., description="File unique identifier")
    filename: str = Field(..., description="Download filename")
    content_type: str = Field(default="text/plain", description="MIME type")

    model_config = {
        "json_schema_extra": {
            "example": {
                "file_id": "a3f5c8e9...",
                "filename": "download_a3f5c8e9.txt",
                "content_type": "text/plain",
            }
        }
    }
