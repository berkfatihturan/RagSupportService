# Rog Knowledge Service API Documentation

Rog is a headless "Knowledge as a Service" API designed for AI agents to store and retrieve information.

## Base URL
`http://localhost:8000`

---

## Endpoints

### 1. Ingest Document (Async)
Upload a file (PDF, ZIP, Image, Text) to the knowledge base. This operation is asynchronous.

- **URL:** `/ingest`
- **Method:** `POST`
- **Content-Type:** `multipart/form-data`

#### Parameters
| Name | Type | Description |
|Col | Col | Col |
| `file` | `File` | The document to upload. |
| `keys` | `String` (JSON List) | Tags/Categories for the document. Example: `["category:invoice", "project:alpha"]` |
| `metadata` | `String` (JSON Object) | Optional metadata. Example: `{"author": "bot", "year": 2024}` |

#### Response (Success)
```json
{
  "status": "queued",
  "job_id": "c5e94321-...",
  "filename": "report.pdf",
  "message": "File processing started in background."
}
```

#### Example (cURL)
```bash
curl -X 'POST' \
  'http://localhost:8000/ingest' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@/path/to/doc.pdf' \
  -F 'keys=["category:report"]' \
  -F 'metadata={"source":"email"}'
```

---

### 2. Check Job Status
Check the status of an ingestion job.

- **URL:** `/job/{job_id}`
- **Method:** `GET`

#### Parameters
| Name | Type | Description |
|Col | Col | Col |
| `job_id` | `String` | The ID returned from the `/ingest` endpoint. |

#### Response
```json
{
  "id": "c5e94321-...",
  "status": "COMPLETED", // PENDING, PROCESSING, COMPLETED, FAILED, PARTIAL
  "created_at": "2024-01-01T12:00:00",
  "files": [],
  "errors": [],
  "result": {
    "file_path": "/absolute/path/to/uploaded/doc.pdf",
    "status": "processed",
    "keys": ["category:report"],
    "chunk_count": 15
  }
}
```

---

### 3. Search Information
Retrieve relevant text chunks based on semantic similarity and filters.

- **URL:** `/search`
- **Method:** `POST`
- **Content-Type:** `application/json`

#### Request Body
```json
{
  "query": "What is the conclusion of the report?",
  "filter_keys": ["category:report"],  // Optional: Search ONLY in these tags
  "exclude_keys": ["status:draft"],    // Optional: Exclude these tags
  "top_k": 3                           // Optional: Number of results (default: 5)
}
```

#### Response
```json
{
  "results": [
    {
      "text": "The project concluded with a 20% increase in efficiency...",
      "score": 0.89,
      "metadata": {
        "source": "email",
        "filename": "report.pdf",
        "file_type": "pdf",
        "original_file": "/absolute/path/to/uploaded/report.pdf"
      }
    }
  ]
}
```

#### Example (cURL)
```bash
curl -X 'POST' \
  'http://localhost:8000/search' \
  -H 'Content-Type: application/json' \
  -d '{
  "query": "net profit 2024",
  "filter_keys": ["type:finance"],
  "top_k": 1
}'
```

---

### 4. List Keys (Mock)
List all available keys in the system.

- **URL:** `/keys`
- **Method:** `GET`

#### Response
```json
{
  "keys": ["category:report", "type:finance", ...]
}
```
