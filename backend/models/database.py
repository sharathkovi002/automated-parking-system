"""
Database models and connection setup
"""

from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
import os
from typing import Generator

# Database URL - using SQLite for development, can be changed to PostgreSQL for production
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./digital_twin.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

class FileRecord(Base):
    """Database model for file records"""
    __tablename__ = "file_records"
    
    id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # 'cad' or 'image'
    file_size = Column(Integer, nullable=False)
    status = Column(String, default="uploaded")  # uploaded, processing, completed, failed
    processed_path = Column(String, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ProcessingJob(Base):
    """Database model for processing jobs"""
    __tablename__ = "processing_jobs"
    
    id = Column(String, primary_key=True, index=True)
    file_id = Column(String, nullable=False, index=True)
    job_type = Column(String, nullable=False)  # 'cad_processing' or 'image_processing'
    status = Column(String, default="pending")  # pending, running, completed, failed
    progress = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

class DigitalTwinData(Base):
    """Database model for digital twin data"""
    __tablename__ = "digital_twin_data"
    
    id = Column(String, primary_key=True, index=True)
    file_id = Column(String, nullable=False, index=True)
    model_data = Column(JSON, nullable=False)
    materials = Column(JSON, nullable=True)
    animations = Column(JSON, nullable=True)
    physics_properties = Column(JSON, nullable=True)
    sensor_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class SensorData(Base):
    """Database model for real-time sensor data"""
    __tablename__ = "sensor_data"
    
    id = Column(String, primary_key=True, index=True)
    file_id = Column(String, nullable=False, index=True)
    sensor_id = Column(String, nullable=False)
    sensor_type = Column(String, nullable=False)
    value = Column(JSON, nullable=False)
    unit = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Dependency to get database session
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database
create_tables()