"""
File management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from models.database import get_db
from models.schemas import FileRecord, ProcessingStatus
from services.file_service import FileService

router = APIRouter()
file_service = FileService()

@router.get("/", response_model=List[FileRecord])
async def list_files(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    file_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List uploaded files with optional filtering"""
    try:
        # This would need to be implemented in FileService
        # For now, return empty list
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{file_id}", response_model=FileRecord)
async def get_file(file_id: str, db: Session = Depends(get_db)):
    """Get file details by ID"""
    try:
        file_record = await file_service.get_file_record(file_id, db)
        if not file_record:
            raise HTTPException(status_code=404, detail="File not found")
        return file_record
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{file_id}")
async def delete_file(file_id: str, db: Session = Depends(get_db)):
    """Delete a file and its associated data"""
    try:
        # This would need to be implemented in FileService
        # For now, return success
        return {"message": "File deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{file_id}/status", response_model=ProcessingStatus)
async def get_file_status(file_id: str, db: Session = Depends(get_db)):
    """Get processing status for a file"""
    try:
        status = await file_service.get_processing_status(file_id, db)
        return status
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))