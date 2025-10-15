"""
Digital Twin Platform - Main FastAPI Application
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import uuid
from typing import List, Optional
import asyncio

from api import files, models, digital_twin
from services.file_service import FileService
from services.processing_service import ProcessingService
from models.database import get_db
from models.schemas import FileUploadResponse, ProcessingStatus, DigitalTwinData

# Initialize FastAPI app
app = FastAPI(
    title="Digital Twin Platform API",
    description="Convert CAD files and 2D images to digital twins",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for uploaded files and processed models
os.makedirs("uploads", exist_ok=True)
os.makedirs("processed", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/processed", StaticFiles(directory="processed"), name="processed")

# Include API routers
app.include_router(files.router, prefix="/api/files", tags=["files"])
app.include_router(models.router, prefix="/api/models", tags=["models"])
app.include_router(digital_twin.router, prefix="/api/digital-twin", tags=["digital-twin"])

# Initialize services
file_service = FileService()
processing_service = ProcessingService()

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Digital Twin Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "digital-twin-platform"}

@app.post("/api/upload", response_model=FileUploadResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db = Depends(get_db)
):
    """
    Upload a CAD file or 2D image for processing
    """
    try:
        # Validate file type
        allowed_extensions = {
            # CAD formats
            '.step', '.stp', '.iges', '.igs', '.stl', '.obj', '.ply', 
            '.3ds', '.fbx', '.dae', '.gltf', '.glb',
            # Image formats
            '.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.webp'
        }
        
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file_extension}"
            )
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Save uploaded file
        file_path = f"uploads/{file_id}{file_extension}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Determine file type and processing method
        is_cad = file_extension in {'.step', '.stp', '.iges', '.igs', '.stl', '.obj', '.ply', '.3ds', '.fbx', '.dae', '.gltf', '.glb'}
        is_image = file_extension in {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.webp'}
        
        # Store file metadata in database
        file_record = await file_service.create_file_record(
            file_id=file_id,
            filename=file.filename,
            file_path=file_path,
            file_type="cad" if is_cad else "image",
            file_size=len(content)
        )
        
        # Start background processing
        if is_cad:
            background_tasks.add_task(
                processing_service.process_cad_file,
                file_id, file_path, file_extension
            )
        elif is_image:
            background_tasks.add_task(
                processing_service.process_image_file,
                file_id, file_path, file_extension
            )
        
        return FileUploadResponse(
            file_id=file_id,
            filename=file.filename,
            file_type="cad" if is_cad else "image",
            status="uploaded",
            message="File uploaded successfully. Processing started."
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status/{file_id}", response_model=ProcessingStatus)
async def get_processing_status(file_id: str, db = Depends(get_db)):
    """Get processing status for a file"""
    try:
        status = await file_service.get_processing_status(file_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download/{file_id}")
async def download_processed_file(file_id: str, db = Depends(get_db)):
    """Download processed 3D model"""
    try:
        file_record = await file_service.get_file_record(file_id)
        if not file_record:
            raise HTTPException(status_code=404, detail="File not found")
        
        if file_record.status != "completed":
            raise HTTPException(status_code=400, detail="File processing not completed")
        
        processed_path = file_record.processed_path
        if not processed_path or not os.path.exists(processed_path):
            raise HTTPException(status_code=404, detail="Processed file not found")
        
        return FileResponse(
            processed_path,
            filename=f"{file_record.filename}_processed.gltf",
            media_type="model/gltf+json"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)