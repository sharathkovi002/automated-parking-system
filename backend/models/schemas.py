"""
Pydantic schemas for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class FileType(str, Enum):
    CAD = "cad"
    IMAGE = "image"

class ProcessingStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class FileUploadResponse(BaseModel):
    file_id: str
    filename: str
    file_type: FileType
    status: ProcessingStatus
    message: str

class ProcessingStatus(BaseModel):
    file_id: str
    status: ProcessingStatus
    progress: Optional[int] = Field(None, ge=0, le=100)
    message: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class FileRecord(BaseModel):
    id: str
    filename: str
    file_path: str
    file_type: FileType
    file_size: int
    status: ProcessingStatus
    processed_path: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

class DigitalTwinData(BaseModel):
    file_id: str
    model_data: Dict[str, Any]
    materials: Optional[List[Dict[str, Any]]] = None
    animations: Optional[List[Dict[str, Any]]] = None
    physics_properties: Optional[Dict[str, Any]] = None
    sensor_data: Optional[Dict[str, Any]] = None

class MaterialProperty(BaseModel):
    name: str
    color: Optional[str] = None
    metallic: Optional[float] = Field(None, ge=0.0, le=1.0)
    roughness: Optional[float] = Field(None, ge=0.0, le=1.0)
    opacity: Optional[float] = Field(None, ge=0.0, le=1.0)
    emissive: Optional[str] = None

class AnimationKeyframe(BaseModel):
    timestamp: float
    position: Optional[List[float]] = None
    rotation: Optional[List[float]] = None
    scale: Optional[List[float]] = None

class PhysicsProperty(BaseModel):
    mass: Optional[float] = None
    friction: Optional[float] = None
    restitution: Optional[float] = None
    collision_shape: Optional[str] = None

class SensorData(BaseModel):
    sensor_id: str
    sensor_type: str
    value: Any
    timestamp: datetime
    unit: Optional[str] = None

class DigitalTwinUpdate(BaseModel):
    file_id: str
    updates: Dict[str, Any]

class ProcessingJob(BaseModel):
    job_id: str
    file_id: str
    job_type: str
    status: ProcessingStatus
    progress: int = Field(0, ge=0, le=100)
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None