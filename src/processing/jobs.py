import uuid
from enum import Enum
from typing import Dict, Any, List
import logging
from datetime import datetime

logger = logging.getLogger("rog.jobs")

class JobStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"

class JobManager:
    def __init__(self):
        # In-memory job store for MVP. For production, use Redis/DB.
        self.jobs: Dict[str, Dict[str, Any]] = {}

    def create_job(self) -> str:
        job_id = str(uuid.uuid4())
        self.jobs[job_id] = {
            "id": job_id,
            "status": JobStatus.PENDING,
            "created_at": datetime.now().isoformat(),
            "files": [],
            "errors": []
        }
        return job_id

    def update_job_status(self, job_id: str, status: JobStatus, details: Dict[str, Any] = None):
        if job_id in self.jobs:
            self.jobs[job_id]["status"] = status
            if details:
                self.jobs[job_id].update(details)
            self.jobs[job_id]["updated_at"] = datetime.now().isoformat()

    def add_error(self, job_id: str, error: str, file: str = None):
        if job_id in self.jobs:
             self.jobs[job_id]["errors"].append({
                 "file": file,
                 "error": error,
                 "timestamp": datetime.now().isoformat()
             })

    def get_job(self, job_id: str):
        return self.jobs.get(job_id)

# Singleton
_job_manager = None

def get_job_manager():
    global _job_manager
    if _job_manager is None:
        _job_manager = JobManager()
    return _job_manager
