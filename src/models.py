from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class IngestMetadata(BaseModel):
    source_id: Optional[str] = Field(None, description="Unique identifier for the source document")
    timestamp: Optional[str] = Field(None, description="Timestamp of the document")
    extra: Optional[Dict[str, Any]] = Field({}, description="Any additional metadata")

class IngestRequest(BaseModel):
    keys: List[str] = Field(..., description="List of tags/keys to associate with the document")
    metadata: Optional[IngestMetadata] = Field(None, description="Metadata for the document")
    # Note: File content is handled via UploadFile in FastAPI, not in this Pydantic model for the body if sending as form-data
    # If sending as JSON (base64), we would add a field here. 
    # For now, we assume Multipart/Form-data will be used for file upload, 
    # so this model might be used for a JSON part of the form or we'll parse form fields individually.
    # Let's keep it simple: we'll use Form parameters in the endpoint for keys and metadata.

class SearchQuery(BaseModel):
    query: str = Field(..., description="Natural language query string")
    filter_keys: Optional[List[str]] = Field(None, description="List of keys to filter by (must contain at least one)")
    exclude_keys: Optional[List[str]] = Field(None, description="List of keys to exclude")
    top_k: int = Field(5, description="Number of results to return")

class SearchResultChunk(BaseModel):
    text: str
    score: float
    metadata: Dict[str, Any]

class SearchResponse(BaseModel):
    results: List[SearchResultChunk]
