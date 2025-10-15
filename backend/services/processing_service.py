"""
Processing service for handling file conversion and digital twin creation
"""

import asyncio
import os
import uuid
from typing import Optional
from sqlalchemy.orm import Session
from models.database import get_db
from services.file_service import FileService
from processors.cad_processor import CADProcessor
from processors.image_processor import ImageProcessor
from processors.digital_twin import DigitalTwinProcessor

class ProcessingService:
    """Service for processing uploaded files"""
    
    def __init__(self):
        self.file_service = FileService()
        self.cad_processor = CADProcessor()
        self.image_processor = ImageProcessor()
        self.digital_twin_processor = DigitalTwinProcessor()
    
    async def process_cad_file(self, file_id: str, file_path: str, file_extension: str):
        """Process CAD file and convert to 3D model"""
        db = next(get_db())
        job_id = None
        
        try:
            # Create processing job
            job_id = await self.file_service.create_processing_job(
                file_id, "cad_processing", db
            )
            
            # Update job status to running
            await self.file_service.update_processing_job(
                job_id, "running", 10, db=db
            )
            
            # Update file status
            await self.file_service.update_file_status(
                file_id, "processing", db=db
            )
            
            # Process CAD file
            await self.file_service.update_processing_job(
                job_id, "running", 30, db=db
            )
            
            processed_data = await self.cad_processor.process_file(
                file_path, file_extension
            )
            
            await self.file_service.update_processing_job(
                job_id, "running", 70, db=db
            )
            
            # Save processed file
            processed_path = f"processed/{file_id}_processed.gltf"
            os.makedirs(os.path.dirname(processed_path), exist_ok=True)
            
            # Convert to GLTF format
            gltf_data = await self.cad_processor.convert_to_gltf(
                processed_data, processed_path
            )
            
            # Create digital twin data
            digital_twin_data = await self.digital_twin_processor.create_digital_twin(
                file_id, gltf_data, "cad"
            )
            
            # Save digital twin data
            await self.file_service.save_digital_twin_data(
                file_id=file_id,
                model_data=digital_twin_data["model_data"],
                materials=digital_twin_data.get("materials"),
                physics_properties=digital_twin_data.get("physics_properties"),
                db=db
            )
            
            # Update file status to completed
            await self.file_service.update_file_status(
                file_id, "completed", processed_path, 
                metadata={"job_id": job_id, "file_type": "cad"},
                db=db
            )
            
            await self.file_service.update_processing_job(
                job_id, "completed", 100, db=db
            )
            
        except Exception as e:
            # Update job status to failed
            if job_id:
                await self.file_service.update_processing_job(
                    job_id, "failed", error_message=str(e), db=db
                )
            
            # Update file status to failed
            await self.file_service.update_file_status(
                file_id, "failed", db=db
            )
            
            print(f"Error processing CAD file {file_id}: {str(e)}")
        
        finally:
            db.close()
    
    async def process_image_file(self, file_id: str, file_path: str, file_extension: str):
        """Process 2D image and convert to 3D model"""
        db = next(get_db())
        job_id = None
        
        try:
            # Create processing job
            job_id = await self.file_service.create_processing_job(
                file_id, "image_processing", db
            )
            
            # Update job status to running
            await self.file_service.update_processing_job(
                job_id, "running", 10, db=db
            )
            
            # Update file status
            await self.file_service.update_file_status(
                file_id, "processing", db=db
            )
            
            # Process image file
            await self.file_service.update_processing_job(
                job_id, "running", 30, db=db
            )
            
            processed_data = await self.image_processor.process_file(
                file_path, file_extension
            )
            
            await self.file_service.update_processing_job(
                job_id, "running", 70, db=db
            )
            
            # Save processed file
            processed_path = f"processed/{file_id}_processed.gltf"
            os.makedirs(os.path.dirname(processed_path), exist_ok=True)
            
            # Convert to GLTF format
            gltf_data = await self.image_processor.convert_to_gltf(
                processed_data, processed_path
            )
            
            # Create digital twin data
            digital_twin_data = await self.digital_twin_processor.create_digital_twin(
                file_id, gltf_data, "image"
            )
            
            # Save digital twin data
            await self.file_service.save_digital_twin_data(
                file_id=file_id,
                model_data=digital_twin_data["model_data"],
                materials=digital_twin_data.get("materials"),
                physics_properties=digital_twin_data.get("physics_properties"),
                db=db
            )
            
            # Update file status to completed
            await self.file_service.update_file_status(
                file_id, "completed", processed_path,
                metadata={"job_id": job_id, "file_type": "image"},
                db=db
            )
            
            await self.file_service.update_processing_job(
                job_id, "completed", 100, db=db
            )
            
        except Exception as e:
            # Update job status to failed
            if job_id:
                await self.file_service.update_processing_job(
                    job_id, "failed", error_message=str(e), db=db
                )
            
            # Update file status to failed
            await self.file_service.update_file_status(
                file_id, "failed", db=db
            )
            
            print(f"Error processing image file {file_id}: {str(e)}")
        
        finally:
            db.close()