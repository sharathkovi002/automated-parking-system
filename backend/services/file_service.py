"""
File service for managing file operations and database records
"""

from sqlalchemy.orm import Session
from models.database import FileRecord, ProcessingJob, DigitalTwinData
from models.schemas import FileRecord as FileRecordSchema, ProcessingStatus, DigitalTwinData as DigitalTwinDataSchema
from typing import Optional, List
import uuid
from datetime import datetime

class FileService:
    """Service for file operations"""
    
    async def create_file_record(
        self, 
        file_id: str, 
        filename: str, 
        file_path: str, 
        file_type: str, 
        file_size: int,
        db: Session
    ) -> FileRecordSchema:
        """Create a new file record in the database"""
        db_record = FileRecord(
            id=file_id,
            filename=filename,
            file_path=file_path,
            file_type=file_type,
            file_size=file_size,
            status="uploaded"
        )
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        
        return FileRecordSchema(
            id=db_record.id,
            filename=db_record.filename,
            file_path=db_record.file_path,
            file_type=db_record.file_type,
            file_size=db_record.file_size,
            status=db_record.status,
            processed_path=db_record.processed_path,
            metadata=db_record.metadata,
            created_at=db_record.created_at,
            updated_at=db_record.updated_at
        )
    
    async def get_file_record(self, file_id: str, db: Session) -> Optional[FileRecordSchema]:
        """Get file record by ID"""
        db_record = db.query(FileRecord).filter(FileRecord.id == file_id).first()
        if not db_record:
            return None
        
        return FileRecordSchema(
            id=db_record.id,
            filename=db_record.filename,
            file_path=db_record.file_path,
            file_type=db_record.file_type,
            file_size=db_record.file_size,
            status=db_record.status,
            processed_path=db_record.processed_path,
            metadata=db_record.metadata,
            created_at=db_record.created_at,
            updated_at=db_record.updated_at
        )
    
    async def update_file_status(
        self, 
        file_id: str, 
        status: str, 
        processed_path: Optional[str] = None,
        metadata: Optional[dict] = None,
        db: Session
    ) -> bool:
        """Update file processing status"""
        db_record = db.query(FileRecord).filter(FileRecord.id == file_id).first()
        if not db_record:
            return False
        
        db_record.status = status
        if processed_path:
            db_record.processed_path = processed_path
        if metadata:
            db_record.metadata = metadata
        
        db.commit()
        return True
    
    async def get_processing_status(self, file_id: str, db: Session) -> ProcessingStatus:
        """Get processing status for a file"""
        db_record = db.query(FileRecord).filter(FileRecord.id == file_id).first()
        if not db_record:
            raise ValueError("File not found")
        
        # Get latest processing job
        job = db.query(ProcessingJob).filter(
            ProcessingJob.file_id == file_id
        ).order_by(ProcessingJob.created_at.desc()).first()
        
        progress = 0
        message = "File uploaded"
        
        if job:
            progress = job.progress
            if job.status == "running":
                message = "Processing in progress..."
            elif job.status == "completed":
                message = "Processing completed"
            elif job.status == "failed":
                message = f"Processing failed: {job.error_message}"
        
        return ProcessingStatus(
            file_id=file_id,
            status=db_record.status,
            progress=progress,
            message=message,
            created_at=db_record.created_at,
            updated_at=db_record.updated_at
        )
    
    async def create_processing_job(
        self, 
        file_id: str, 
        job_type: str, 
        db: Session
    ) -> str:
        """Create a new processing job"""
        job_id = str(uuid.uuid4())
        db_job = ProcessingJob(
            id=job_id,
            file_id=file_id,
            job_type=job_type,
            status="pending"
        )
        db.add(db_job)
        db.commit()
        return job_id
    
    async def update_processing_job(
        self, 
        job_id: str, 
        status: str, 
        progress: int = 0,
        error_message: Optional[str] = None,
        db: Session
    ) -> bool:
        """Update processing job status"""
        db_job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
        if not db_job:
            return False
        
        db_job.status = status
        db_job.progress = progress
        if error_message:
            db_job.error_message = error_message
        
        if status == "running" and not db_job.started_at:
            db_job.started_at = datetime.utcnow()
        elif status in ["completed", "failed"]:
            db_job.completed_at = datetime.utcnow()
        
        db.commit()
        return True
    
    async def get_digital_twin_data(self, file_id: str, db: Session) -> Optional[DigitalTwinDataSchema]:
        """Get digital twin data for a file"""
        db_record = db.query(DigitalTwinData).filter(DigitalTwinData.file_id == file_id).first()
        if not db_record:
            return None
        
        return DigitalTwinDataSchema(
            file_id=db_record.file_id,
            model_data=db_record.model_data,
            materials=db_record.materials,
            animations=db_record.animations,
            physics_properties=db_record.physics_properties,
            sensor_data=db_record.sensor_data
        )
    
    async def save_digital_twin_data(
        self, 
        file_id: str, 
        model_data: dict,
        materials: Optional[List[dict]] = None,
        animations: Optional[List[dict]] = None,
        physics_properties: Optional[dict] = None,
        sensor_data: Optional[dict] = None,
        db: Session
    ) -> bool:
        """Save digital twin data"""
        # Check if record exists
        existing = db.query(DigitalTwinData).filter(DigitalTwinData.file_id == file_id).first()
        
        if existing:
            # Update existing record
            existing.model_data = model_data
            existing.materials = materials
            existing.animations = animations
            existing.physics_properties = physics_properties
            existing.sensor_data = sensor_data
        else:
            # Create new record
            db_record = DigitalTwinData(
                id=str(uuid.uuid4()),
                file_id=file_id,
                model_data=model_data,
                materials=materials,
                animations=animations,
                physics_properties=physics_properties,
                sensor_data=sensor_data
            )
            db.add(db_record)
        
        db.commit()
        return True