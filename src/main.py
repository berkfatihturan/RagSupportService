from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from typing import List, Optional
import json
import os
from .models import SearchQuery, SearchResponse, SearchResultChunk

app = FastAPI(
    title="Rog Knowledge Service",
    description="A headless AI knowledge service for ingesting and retrieving documents based on keys.",
    version="1.0.0"
)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def root():
    return RedirectResponse(url="/static/index.html")

@app.post("/ingest", summary="Ingest a document (Async)")
async def ingest_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    keys: str = Form(..., description="JSON string list of keys, e.g. '[\"flowers\", \"rose\"]'"),
    metadata: Optional[str] = Form(None, description="JSON string metadata")
):
    """
    Ingest a file (PDF, Image, Text, Zip) associated with specific keys.
    Returns a Job ID immediately.
    """
    try:
        keys_list = json.loads(keys)
        if not isinstance(keys_list, list):
            raise ValueError("Keys must be a list")
            
        metadata_dict = {}
        if metadata:
            metadata_dict = json.loads(metadata)
            
        # Create Job
        from .processing.jobs import get_job_manager
        job_manager = get_job_manager()
        job_id = job_manager.create_job()
        
        # Dispatch to background

        # 1. Save file synchronously (or await in handler)
        from .processing.ingest import save_upload_file
        file_path = await save_upload_file(file)
        
        # 2. Dispatch background task with file path
        from .processing.ingest import process_job
        
        background_tasks.add_task(process_job, file_path, keys_list, metadata_dict, job_id)
        
        return {
            "status": "queued", 
            "job_id": job_id,
            "filename": file.filename, 
            "message": "File processing started in background."
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format for keys or metadata")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/job/{job_id}", summary="Check Job Status")
async def get_job_status(job_id: str):
    from .processing.jobs import get_job_manager
    job_manager = get_job_manager()
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.post("/search", response_model=SearchResponse, summary="Search for information")
async def search_documents(query: SearchQuery):
    """
    Search specifically within documents that match the provided filter keys.
    """
    try:
        from .storage.embeddings import get_embedding_service
        from .storage.vector_db import get_vector_db
        
        # 1. Embed Query
        embed_service = get_embedding_service()
        query_vector = embed_service.embed_text(query.query)
        
        # 2. Search DB
        vector_db = get_vector_db()
        search_results = vector_db.search(
            query_vector=query_vector,
            filter_keys=query.filter_keys,
            exclude_keys=query.exclude_keys,
            top_k=query.top_k
        )
        
        # 3. Format Response
        formatted_results = []
        for hit in search_results:
            formatted_results.append(SearchResultChunk(
                text=hit.payload.get("text", ""),
                score=hit.score,
                metadata=hit.payload
            ))
            
        return SearchResponse(results=formatted_results)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/keys", summary="List all available keys")
async def list_keys():
    """
    Return a list of all unique keys currently in the index.
    """
    # TODO: Fetch unique keys from DB
    return {"keys": ["mock_key_1", "mock_key_2"]}
