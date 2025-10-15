"""
Digital twin specific API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from models.database import get_db
from models.schemas import DigitalTwinData, SensorData, DigitalTwinUpdate
from services.file_service import FileService
import json
import asyncio
from datetime import datetime

router = APIRouter()
file_service = FileService()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, file_id: str):
        await websocket.accept()
        if file_id not in self.active_connections:
            self.active_connections[file_id] = []
        self.active_connections[file_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, file_id: str):
        if file_id in self.active_connections:
            self.active_connections[file_id].remove(websocket)
            if not self.active_connections[file_id]:
                del self.active_connections[file_id]
    
    async def send_to_file(self, file_id: str, message: dict):
        if file_id in self.active_connections:
            for connection in self.active_connections[file_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    # Remove broken connections
                    self.active_connections[file_id].remove(connection)

manager = ConnectionManager()

@router.get("/{file_id}", response_model=DigitalTwinData)
async def get_digital_twin(file_id: str, db: Session = Depends(get_db)):
    """Get complete digital twin data"""
    try:
        digital_twin_data = await file_service.get_digital_twin_data(file_id, db)
        if not digital_twin_data:
            raise HTTPException(status_code=404, detail="Digital twin not found")
        return digital_twin_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{file_id}")
async def update_digital_twin(
    file_id: str, 
    update: DigitalTwinUpdate, 
    db: Session = Depends(get_db)
):
    """Update digital twin data"""
    try:
        # Get current digital twin data
        current_data = await file_service.get_digital_twin_data(file_id, db)
        if not current_data:
            raise HTTPException(status_code=404, detail="Digital twin not found")
        
        # Apply updates
        updated_model_data = current_data.model_data.copy()
        updated_model_data.update(update.updates)
        
        # Save updated data
        await file_service.save_digital_twin_data(
            file_id=file_id,
            model_data=updated_model_data,
            materials=current_data.materials,
            animations=current_data.animations,
            physics_properties=current_data.physics_properties,
            sensor_data=current_data.sensor_data,
            db=db
        )
        
        # Notify connected clients
        await manager.send_to_file(file_id, {
            "type": "digital_twin_updated",
            "file_id": file_id,
            "updates": update.updates
        })
        
        return {"message": "Digital twin updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{file_id}/sensor-data")
async def add_sensor_data(
    file_id: str, 
    sensor_data: SensorData, 
    db: Session = Depends(get_db)
):
    """Add real-time sensor data to digital twin"""
    try:
        # Get current digital twin data
        current_data = await file_service.get_digital_twin_data(file_id, db)
        if not current_data:
            raise HTTPException(status_code=404, detail="Digital twin not found")
        
        # Update sensor data
        current_sensor_data = current_data.sensor_data or {}
        current_sensor_data[sensor_data.sensor_id] = {
            "sensor_type": sensor_data.sensor_type,
            "value": sensor_data.value,
            "timestamp": sensor_data.timestamp.isoformat(),
            "unit": sensor_data.unit
        }
        
        # Save updated data
        await file_service.save_digital_twin_data(
            file_id=file_id,
            model_data=current_data.model_data,
            materials=current_data.materials,
            animations=current_data.animations,
            physics_properties=current_data.physics_properties,
            sensor_data=current_sensor_data,
            db=db
        )
        
        # Notify connected clients
        await manager.send_to_file(file_id, {
            "type": "sensor_data_updated",
            "file_id": file_id,
            "sensor_id": sensor_data.sensor_id,
            "sensor_data": sensor_data.dict()
        })
        
        return {"message": "Sensor data added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{file_id}/sensor-data", response_model=Dict[str, Any])
async def get_sensor_data(file_id: str, db: Session = Depends(get_db)):
    """Get all sensor data for a digital twin"""
    try:
        digital_twin_data = await file_service.get_digital_twin_data(file_id, db)
        if not digital_twin_data:
            raise HTTPException(status_code=404, detail="Digital twin not found")
        
        return digital_twin_data.sensor_data or {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/{file_id}/ws")
async def websocket_endpoint(websocket: WebSocket, file_id: str):
    """WebSocket endpoint for real-time digital twin updates"""
    await manager.connect(websocket, file_id)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
            elif message.get("type") == "request_update":
                # Send current digital twin data
                db = next(get_db())
                try:
                    digital_twin_data = await file_service.get_digital_twin_data(file_id, db)
                    if digital_twin_data:
                        await websocket.send_text(json.dumps({
                            "type": "digital_twin_data",
                            "data": digital_twin_data.dict()
                        }))
                finally:
                    db.close()
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, file_id)

@router.post("/{file_id}/simulate")
async def start_simulation(file_id: str, simulation_params: Dict[str, Any], db: Session = Depends(get_db)):
    """Start a simulation for the digital twin"""
    try:
        # This would integrate with a simulation engine
        # For now, just return success
        return {
            "message": "Simulation started",
            "simulation_id": f"sim_{file_id}_{datetime.utcnow().timestamp()}",
            "parameters": simulation_params
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{file_id}/export")
async def export_digital_twin(file_id: str, format: str = "gltf", db: Session = Depends(get_db)):
    """Export digital twin in various formats"""
    try:
        digital_twin_data = await file_service.get_digital_twin_data(file_id, db)
        if not digital_twin_data:
            raise HTTPException(status_code=404, detail="Digital twin not found")
        
        # This would implement actual export functionality
        # For now, return the model data
        return {
            "format": format,
            "data": digital_twin_data.model_data,
            "download_url": f"/api/download/{file_id}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))