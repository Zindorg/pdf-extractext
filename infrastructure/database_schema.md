# Database Schema Documentation

MongoDB database schema for PDF-Extractext application.

## Collection: `pdf_documents`

Stores metadata and extracted text from PDF files.

### Document Structure

```javascript
{
  "_id": ObjectId,           // Unique identifier (auto-generated)
  "checksum": String,        // SHA-256 hash of original file (unique index)
  "filename": String,        // Original filename
  "text_content": String,    // Extracted text content
  "content_type": String,    // MIME type (default: "application/pdf")
  "page_count": Number,      // Number of pages in PDF
  "file_size": Number,       // File size in bytes
  "deleted_at": Date,        // Soft delete timestamp (null = active)
  "created_at": Date,        // Creation timestamp
  "updated_at": Date         // Last modification timestamp
}
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `_id` | ObjectId | Auto | MongoDB generated unique identifier |
| `checksum` | String | Yes | SHA-256 hash for duplicate detection |
| `filename` | String | Yes | Original filename of uploaded PDF |
| `text_content` | String | Yes | Extracted text from PDF |
| `content_type` | String | No | MIME type (default: "application/pdf") |
| `page_count` | Number | No | Page count in PDF (default: 0) |
| `file_size` | Number | No | File size in bytes (default: 0) |
| `deleted_at` | Date | No | Soft delete timestamp. `null` = active document |
| `created_at` | Date | Auto | Document creation timestamp |
| `updated_at` | Date | Auto | Last update timestamp |

### Indexes

```javascript
// Unique constraint for duplicate detection
db.pdf_documents.createIndex(
  { "checksum": 1 },
  { unique: true, name: "idx_checksum_unique" }
)

// Filter for active/deleted documents
db.pdf_documents.createIndex(
  { "deleted_at": 1 },
  { name: "idx_deleted_at" }
)

// Chronological ordering
db.pdf_documents.createIndex(
  { "created_at": -1 },
  { name: "idx_created_at_desc" }
)
```

### Index Purposes

1. **idx_checksum_unique**: Prevents duplicate PDF uploads
2. **idx_deleted_at**: Efficient filtering of active/deleted documents
3. **idx_created_at_desc**: Chronological listing queries

### Soft Delete Strategy

- **Active documents**: `deleted_at: null`
- **Deleted documents**: `deleted_at: Date` (timestamp of deletion)
- **Queries by default**: Filter with `{"deleted_at": null}`

### Example Queries

#### Find active document by checksum
```javascript
db.pdf_documents.findOne({
  "checksum": "abc123...",
  "deleted_at": null
})
```

#### List all active documents (newest first)
```javascript
db.pdf_documents.find({
  "deleted_at": null
}).sort({ "created_at": -1 })
```

#### Soft delete document
```javascript
db.pdf_documents.updateOne(
  { "_id": ObjectId("..."), "deleted_at": null },
  { "$set": { "deleted_at": new Date() } }
)
```

## Connection Management

### Singleton Pattern

The application uses a singleton pattern for database connections:

```python
from infrastructure.database_connection import get_database

# Get singleton database instance
db = get_database()

# Access collection
collection = db["pdf_documents"]
```

### Configuration

Connection settings from `core.config.Settings`:

```python
MONGODB_URI = "mongodb://localhost:27017"  # Connection string
MONGODB_DATABASE = "pdf_extractext"         # Database name
```

### Cleanup

```python
from infrastructure.database_connection import close_connection

# Close connection and reset singleton
close_connection()
```
