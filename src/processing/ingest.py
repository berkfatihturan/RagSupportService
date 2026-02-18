import os
import shutil
from fastapi import UploadFile, HTTPException
from typing import List, Dict, Any
import logging

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

logger = logging.getLogger("rog.ingest")

async def save_upload_file(upload_file: UploadFile, destination_folder: str = UPLOAD_DIR) -> str:
    """
    Saves the uploaded file to disk.
    """
    try:
        file_path = os.path.join(destination_folder, upload_file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        return file_path
    except Exception as e:
        logger.error(f"Failed to save file: {e}")
        raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}")

async def process_file_path(file_path: str, keys: List[str], metadata: Dict[str, Any], job_id: str, depth: int = 0):
    """
    Process a local file path. Handles specific file types and recursion.
    """
    from .jobs import get_job_manager
    job_manager = get_job_manager()

    if depth > 3: # Safety limit for recursion
        logger.warning(f"Max recursion depth reached for {file_path}")
        job_manager.add_error(job_id, "max_depth_reached", file_path)
        return {"status": "skipped", "reason": "max_depth"}

    logger.info(f"Processing file: {file_path}")
    filename = os.path.basename(file_path).lower()
    
    extraction_result = {"text": "", "pages": []}
    
    if filename.endswith(".pdf"):
        from .loaders.pdf_loader import load_pdf
        extraction_result = load_pdf(file_path)
        if extraction_result.get("needs_ocr"):
            logger.info(f"PDF {filename} needs OCR.")
            
    elif filename.endswith(".zip"):
        from .loaders.archive_loader import extract_and_process_zip
        # Extract
        parent_dir = os.path.dirname(file_path)
        result = extract_and_process_zip(file_path, parent_dir, None)
        
        if result["status"] == "success":
            extracted_files = result["extracted_files"]
            sub_results = []
            for sub_file in extracted_files:
                # Recursively process
                sub_res = await process_file_path(sub_file, keys, metadata, job_id, depth + 1)
                sub_results.append(sub_res)
            
            return {
                "status": "expanded",
                "original_file": file_path,
                "sub_files": sub_results
            }
        else:
            return {"status": "error", "error": result.get("error")}
            
    elif filename.endswith((".jpg", ".jpeg", ".png", ".bmp", ".tiff")):
        from .loaders.image_loader import load_image
        extraction_result = load_image(file_path)
        
    elif filename.endswith((".txt", ".md", ".json", ".csv", ".xml", ".py", ".js")):
        from .loaders.text_loader import load_text
        extraction_result = load_text(file_path)
        
    else:
        logger.warning(f"Unsupported file type: {filename}")
        return {"status": "skipped", "reason": "unsupported_type"}
    
    # If text was extracted, proceed to storage
    full_text = extraction_result.get("text", "")
    if full_text:
        from .chunking import recursive_character_chunking
        from ..storage.embeddings import get_embedding_service
        from ..storage.vector_db import get_vector_db
        
        # 1. Chunking
        chunks = recursive_character_chunking(full_text)
        logger.info(f"Generated {len(chunks)} chunks for {filename}")
        
        if chunks:
            # 2. Embedding
            embed_service = get_embedding_service()
            embeddings = embed_service.embed_batch(chunks)
            
            # 3. Storage
            vector_db = get_vector_db()
            vector_db.upsert_chunks(
                chunks=chunks,
                embeddings=embeddings,
                keys=keys,
                metadata={
                    "original_file": file_path,
                    "file_type": filename.split('.')[-1],
                    **metadata
                },
                filename=filename
            )
    
    return {
        "file_path": file_path,
        "status": "processed",
        "keys": keys,
        "chunk_count": len(chunks) if full_text else 0,
        "result": extraction_result
    }

async def process_job(file_path: str, keys: List[str], metadata: Dict[str, Any], job_id: str):
    """
    Wrapper to handle the full lifecycle of a background job.
    """
    from .jobs import get_job_manager, JobStatus
    job_manager = get_job_manager()
    
    try:
        job_manager.update_job_status(job_id, JobStatus.PROCESSING)
        
        # Process
        result = await process_file_path(file_path, keys, metadata, job_id)
        
        # Check errors
        job_errors = job_manager.get_job(job_id).get("errors", [])
        final_status = JobStatus.COMPLETED
        
        if job_errors:
             if result.get("status") == "error":
                 final_status = JobStatus.FAILED
             else:
                 final_status = JobStatus.PARTIAL
        
        job_manager.update_job_status(job_id, final_status, {"result": result})
        
    except Exception as e:
        logger.error(f"Job {job_id} failed logic: {e}")
        job_manager.update_job_status(job_id, JobStatus.FAILED, {"error": str(e)})
        job_manager.add_error(job_id, str(e))
