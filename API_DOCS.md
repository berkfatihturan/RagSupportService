# Rog API Documentation

Rog is a headless knowledge service designed to be used by other AI agents. It provides a simple protocol for storing unstructured data with structured tags (keys) and retrieving it via semantic search.

## Base URL
`http://localhost:8000` (Default)

## Endpoints

### 1. Ingest Document
Push a file into the knowledge base.

- **URL:** `/ingest`
- **Method:** `POST`
- **Content-Type:** `multipart/form-data`
- **Parameters:**
    - `file` (File, required): The document to process (PDF, ZIP, Image, etc.).
    - `keys` (String, required): A JSON array of strings representing tags. Example: `["category:flowers", "source:wiki"]`.
    - `metadata` (String, optional): A JSON object with extra info. Example: `{"author": "Unknown"}`.

**Example Response:**
```json
{
  "status": "received",
  "filename": "flowers.pdf",
  "keys": ["category:flowers"],
  "message": "File processing started."
}
```

### 2. Search
Retrieve information using natural language and key filters.

- **URL:** `/search`
- **Method:** `POST`
- **Content-Type:** `application/json`
- **Body:**
```json
{
  "query": "What are the characteristics of a rose?",
  "filter_keys": ["category:flowers"],
  "exclude_keys": ["type:artificial"],
  "top_k": 3
}
```

**Example Response:**
```json
{
  "results": [
    {
      "text": "The rose is a woody perennial flowering plant...",
      "score": 0.89,
      "metadata": { "source": "flowers.pdf", "page": 12 }
    }
  ]
}
```

### 3. List Keys
See what tags are available in the system.

- **URL:** `/keys`
- **Method:** `GET`

**Example Response:**
```json
{
  "keys": ["category:flowers", "category:cars", "type:manual"]
}
```
