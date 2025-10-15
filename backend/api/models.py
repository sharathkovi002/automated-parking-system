"""
3D model management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from models.database import get_db
from models.schemas import DigitalTwinData, MaterialProperty, AnimationKeyframe, PhysicsProperty
from services.file_service import FileService

router = APIRouter()
file_service = FileService()

@router.get("/{file_id}", response_model=DigitalTwinData)
async def get_model_data(file_id: str, db: Session = Depends(get_db)):
    """Get 3D model data for a file"""
    try:
        model_data = await file_service.get_digital_twin_data(file_id, db)
        if not model_data:
            raise HTTPException(status_code=404, detail="Model data not found")
        return model_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{file_id}/materials", response_model=List[MaterialProperty])
async def get_materials(file_id: str, db: Session = Depends(get_db)):
    """Get material properties for a model"""
    try:
        model_data = await file_service.get_digital_twin_data(file_id, db)
        if not model_data or not model_data.materials:
            return []
        return model_data.materials
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{file_id}/materials")
async def update_materials(
    file_id: str, 
    materials: List[MaterialProperty], 
    db: Session = Depends(get_db)
):
    """Update material properties for a model"""
    try:
        model_data = await file_service.get_digital_twin_data(file_id, db)
        if not model_data:
            raise HTTPException(status_code=404, detail="Model data not found")
        
        # Update materials
        materials_dict = [material.dict() for material in materials]
        await file_service.save_digital_twin_data(
            file_id=file_id,
            model_data=model_data.model_data,
            materials=materials_dict,
            animations=model_data.animations,
            physics_properties=model_data.physics_properties,
            sensor_data=model_data.sensor_data,
            db=db
        )
        
        return {"message": "Materials updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{file_id}/animations", response_model=List[dict])
async def get_animations(file_id: str, db: Session = Depends(get_db)):
    """Get animations for a model"""
    try:
        model_data = await file_service.get_digital_twin_data(file_id, db)
        if not model_data or not model_data.animations:
            return []
        return model_data.animations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{file_id}/animations")
async def update_animations(
    file_id: str, 
    animations: List[dict], 
    db: Session = Depends(get_db)
):
    """Update animations for a model"""
    try:
        model_data = await file_service.get_digital_twin_data(file_id, db)
        if not model_data:
            raise HTTPException(status_code=404, detail="Model data not found")
        
        # Update animations
        await file_service.save_digital_twin_data(
            file_id=file_id,
            model_data=model_data.model_data,
            materials=model_data.materials,
            animations=animations,
            physics_properties=model_data.physics_properties,
            sensor_data=model_data.sensor_data,
            db=db
        )
        
        return {"message": "Animations updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{file_id}/physics", response_model=PhysicsProperty)
async def get_physics_properties(file_id: str, db: Session = Depends(get_db)):
    """Get physics properties for a model"""
    try:
        model_data = await file_service.get_digital_twin_data(file_id, db)
        if not model_data or not model_data.physics_properties:
            return PhysicsProperty()
        return PhysicsProperty(**model_data.physics_properties)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{file_id}/physics")
async def update_physics_properties(
    file_id: str, 
    physics: PhysicsProperty, 
    db: Session = Depends(get_db)
):
    """Update physics properties for a model"""
    try:
        model_data = await file_service.get_digital_twin_data(file_id, db)
        if not model_data:
            raise HTTPException(status_code=404, detail="Model data not found")
        
        # Update physics properties
        await file_service.save_digital_twin_data(
            file_id=file_id,
            model_data=model_data.model_data,
            materials=model_data.materials,
            animations=model_data.animations,
            physics_properties=physics.dict(),
            sensor_data=model_data.sensor_data,
            db=db
        )
        
        return {"message": "Physics properties updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))