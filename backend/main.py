"""
FastAPI backend for Document Analyzer.
"""
import uuid
import shutil
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from loguru import logger

from shared import settings, analyzer, process_uploaded_file, cleanup_processed_files


# Configure logging
log_file = settings.log_dir / f"backend_{datetime.now().strftime('%Y%m%d')}.log"
logger.add(
    log_file,
    rotation="500 MB",
    level=settings.log_level,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
)

# Initialize FastAPI app
app = FastAPI(
    title="Document Analyzer API",
    description="API for extracting structured data from document images",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class AnalysisStatus(BaseModel):
    """Status response model."""
    status: str
    message: str
    job_id: Optional[str] = None


class AnalysisResult(BaseModel):
    """Analysis result model."""
    job_id: str
    filename: str
    page_count: int
    results: List[dict]
    created_at: str


# In-memory storage for demo (use database in production)
analysis_jobs = {}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Document Analyzer API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "model": settings.model_id
    }


@app.post("/api/analyze", response_model=AnalysisStatus)
async def analyze_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Analyze a document (PDF or image).
    
    Args:
        file: Uploaded file
        background_tasks: FastAPI background tasks
        
    Returns:
        Analysis status with job ID
    """
    logger.info(f"Received file: {file.filename} ({file.content_type})")
    
    # Validate file type
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in [f".{ext}" for ext in settings.allowed_extensions_list]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {settings.allowed_extensions}"
        )
    
    # Validate file size (check Content-Length header)
    if file.size and file.size > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.max_file_size_mb}MB"
        )
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Create job directory
    job_dir = settings.upload_dir / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    
    # Save uploaded file
    file_path = job_dir / file.filename
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"Saved file to {file_path}")
    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        raise HTTPException(status_code=500, detail="Error saving file")
    
    # Initialize job status
    analysis_jobs[job_id] = {
        "status": "processing",
        "filename": file.filename,
        "created_at": datetime.now().isoformat(),
        "results": None,
        "error": None
    }
    
    # Process file in background
    background_tasks.add_task(
        process_document_task,
        job_id,
        file_path,
        job_dir
    )
    
    return AnalysisStatus(
        status="processing",
        message="Document analysis started",
        job_id=job_id
    )


async def process_document_task(job_id: str, file_path: Path, job_dir: Path):
    """
    Background task to process document.
    
    Args:
        job_id: Job identifier
        file_path: Path to uploaded file
        job_dir: Job directory
    """
    try:
        logger.info(f"Processing job {job_id}")
        
        # Process file to images
        processed_dir = job_dir / "processed"
        image_paths = process_uploaded_file(file_path, processed_dir)
        
        logger.info(f"Generated {len(image_paths)} images for job {job_id}")
        
        # Analyze images
        results = analyzer.analyze_multiple_images(image_paths)
        
        # Update job status
        analysis_jobs[job_id].update({
            "status": "completed",
            "page_count": len(results),
            "results": results
        })
        
        logger.info(f"Completed job {job_id}")
        
    except Exception as e:
        logger.error(f"Error processing job {job_id}: {str(e)}")
        analysis_jobs[job_id].update({
            "status": "failed",
            "error": str(e)
        })


@app.get("/api/status/{job_id}")
async def get_job_status(job_id: str):
    """
    Get job status.
    
    Args:
        job_id: Job identifier
        
    Returns:
        Job status information
    """
    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = analysis_jobs[job_id]
    
    return {
        "job_id": job_id,
        "status": job["status"],
        "filename": job["filename"],
        "created_at": job["created_at"],
        "page_count": job.get("page_count"),
        "error": job.get("error")
    }


@app.get("/api/results/{job_id}")
async def get_job_results(job_id: str):
    """
    Get job results.
    
    Args:
        job_id: Job identifier
        
    Returns:
        Analysis results
    """
    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = analysis_jobs[job_id]
    
    if job["status"] == "processing":
        raise HTTPException(status_code=202, detail="Analysis still in progress")
    
    if job["status"] == "failed":
        raise HTTPException(status_code=500, detail=job.get("error", "Analysis failed"))
    
    return {
        "job_id": job_id,
        "filename": job["filename"],
        "page_count": job.get("page_count", 0),
        "results": job["results"],
        "created_at": job["created_at"]
    }


@app.delete("/api/jobs/{job_id}")
async def delete_job(job_id: str):
    """
    Delete a job and its files.
    
    Args:
        job_id: Job identifier
        
    Returns:
        Deletion status
    """
    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Delete job directory
    job_dir = settings.upload_dir / job_id
    if job_dir.exists():
        shutil.rmtree(job_dir)
        logger.info(f"Deleted job directory: {job_dir}")
    
    # Remove from memory
    del analysis_jobs[job_id]
    
    return {"status": "deleted", "job_id": job_id}


@app.get("/api/jobs")
async def list_jobs():
    """
    List all jobs.
    
    Returns:
        List of all jobs
    """
    return {
        "jobs": [
            {
                "job_id": job_id,
                "status": job["status"],
                "filename": job["filename"],
                "created_at": job["created_at"]
            }
            for job_id, job in analysis_jobs.items()
        ]
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting Document Analyzer API on {settings.backend_host}:{settings.backend_port}")
    uvicorn.run(
        app,
        host=settings.backend_host,
        port=settings.backend_port,
        log_level=settings.log_level.lower()
    )
