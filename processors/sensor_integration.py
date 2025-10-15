"""
Sensor data integration for digital twin real-time updates
"""

import asyncio
import json
import numpy as np
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
import logging
import websockets
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SensorData:
    """Sensor data structure"""
    sensor_id: str
    sensor_type: str
    value: Any
    unit: Optional[str] = None
    timestamp: datetime = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

class SensorIntegration:
    """Real-time sensor data integration for digital twins"""
    
    def __init__(self):
        self.sensors = {}
        self.subscribers = {}
        self.websocket_connections = {}
        self.data_history = {}
        self.running = False
        
    async def add_sensor(
        self, 
        file_id: str, 
        sensor_id: str, 
        sensor_type: str,
        unit: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Add a sensor to a digital twin"""
        try:
            if file_id not in self.sensors:
                self.sensors[file_id] = {}
                self.data_history[file_id] = {}
            
            sensor_info = {
                "sensor_id": sensor_id,
                "sensor_type": sensor_type,
                "unit": unit,
                "metadata": metadata or {},
                "active": True,
                "created_at": datetime.utcnow(),
                "last_update": None
            }
            
            self.sensors[file_id][sensor_id] = sensor_info
            self.data_history[file_id][sensor_id] = []
            
            logger.info(f"Added sensor {sensor_id} to digital twin {file_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding sensor: {e}")
            return False
    
    async def update_sensor_data(
        self, 
        file_id: str, 
        sensor_id: str, 
        value: Any,
        timestamp: Optional[datetime] = None
    ) -> bool:
        """Update sensor data"""
        try:
            if file_id not in self.sensors or sensor_id not in self.sensors[file_id]:
                raise ValueError(f"Sensor {sensor_id} not found for digital twin {file_id}")
            
            sensor_info = self.sensors[file_id][sensor_id]
            
            # Create sensor data
            sensor_data = SensorData(
                sensor_id=sensor_id,
                sensor_type=sensor_info["sensor_type"],
                value=value,
                unit=sensor_info["unit"],
                timestamp=timestamp or datetime.utcnow(),
                metadata=sensor_info["metadata"]
            )
            
            # Update sensor info
            sensor_info["last_update"] = sensor_data.timestamp
            
            # Store in history (keep last 1000 readings)
            self.data_history[file_id][sensor_id].append(sensor_data)
            if len(self.data_history[file_id][sensor_id]) > 1000:
                self.data_history[file_id][sensor_id] = self.data_history[file_id][sensor_id][-1000:]
            
            # Notify subscribers
            await self._notify_subscribers(file_id, sensor_data)
            
            # Send via WebSocket if connected
            await self._send_websocket_update(file_id, sensor_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating sensor data: {e}")
            return False
    
    async def get_sensor_data(
        self, 
        file_id: str, 
        sensor_id: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get sensor data"""
        try:
            if file_id not in self.sensors:
                return {}
            
            if sensor_id:
                if sensor_id in self.sensors[file_id]:
                    history = self.data_history[file_id][sensor_id][-limit:]
                    return {
                        sensor_id: {
                            "sensor_info": self.sensors[file_id][sensor_id],
                            "data": [self._serialize_sensor_data(data) for data in history]
                        }
                    }
                else:
                    return {}
            else:
                result = {}
                for sid in self.sensors[file_id]:
                    history = self.data_history[file_id][sid][-limit:]
                    result[sid] = {
                        "sensor_info": self.sensors[file_id][sid],
                        "data": [self._serialize_sensor_data(data) for data in history]
                    }
                return result
                
        except Exception as e:
            logger.error(f"Error getting sensor data: {e}")
            return {}
    
    def _serialize_sensor_data(self, sensor_data: SensorData) -> Dict[str, Any]:
        """Serialize sensor data for JSON transmission"""
        return {
            "sensor_id": sensor_data.sensor_id,
            "sensor_type": sensor_data.sensor_type,
            "value": sensor_data.value,
            "unit": sensor_data.unit,
            "timestamp": sensor_data.timestamp.isoformat(),
            "metadata": sensor_data.metadata
        }
    
    async def _notify_subscribers(self, file_id: str, sensor_data: SensorData):
        """Notify subscribers of sensor data updates"""
        try:
            if file_id in self.subscribers:
                for callback in self.subscribers[file_id]:
                    try:
                        await callback(file_id, sensor_data)
                    except Exception as e:
                        logger.error(f"Error in subscriber callback: {e}")
        except Exception as e:
            logger.error(f"Error notifying subscribers: {e}")
    
    async def _send_websocket_update(self, file_id: str, sensor_data: SensorData):
        """Send sensor data via WebSocket"""
        try:
            if file_id in self.websocket_connections:
                message = {
                    "type": "sensor_data_update",
                    "file_id": file_id,
                    "sensor_data": self._serialize_sensor_data(sensor_data)
                }
                
                for ws in self.websocket_connections[file_id]:
                    try:
                        await ws.send(json.dumps(message))
                    except websockets.exceptions.ConnectionClosed:
                        # Remove closed connections
                        self.websocket_connections[file_id].remove(ws)
                    except Exception as e:
                        logger.error(f"Error sending WebSocket message: {e}")
        except Exception as e:
            logger.error(f"Error sending WebSocket update: {e}")
    
    def subscribe(self, file_id: str, callback: Callable):
        """Subscribe to sensor data updates"""
        if file_id not in self.subscribers:
            self.subscribers[file_id] = []
        self.subscribers[file_id].append(callback)
    
    def unsubscribe(self, file_id: str, callback: Callable):
        """Unsubscribe from sensor data updates"""
        if file_id in self.subscribers:
            try:
                self.subscribers[file_id].remove(callback)
            except ValueError:
                pass
    
    def add_websocket_connection(self, file_id: str, websocket):
        """Add WebSocket connection for real-time updates"""
        if file_id not in self.websocket_connections:
            self.websocket_connections[file_id] = []
        self.websocket_connections[file_id].append(websocket)
    
    def remove_websocket_connection(self, file_id: str, websocket):
        """Remove WebSocket connection"""
        if file_id in self.websocket_connections:
            try:
                self.websocket_connections[file_id].remove(websocket)
            except ValueError:
                pass
    
    async def get_sensor_statistics(self, file_id: str, sensor_id: str) -> Dict[str, Any]:
        """Get sensor statistics"""
        try:
            if file_id not in self.data_history or sensor_id not in self.data_history[file_id]:
                return {}
            
            data_points = self.data_history[file_id][sensor_id]
            if not data_points:
                return {}
            
            # Extract numeric values
            values = []
            for data in data_points:
                if isinstance(data.value, (int, float)):
                    values.append(data.value)
            
            if not values:
                return {}
            
            values = np.array(values)
            
            stats = {
                "count": len(values),
                "mean": float(np.mean(values)),
                "std": float(np.std(values)),
                "min": float(np.min(values)),
                "max": float(np.max(values)),
                "median": float(np.median(values)),
                "first_reading": data_points[0].timestamp.isoformat(),
                "last_reading": data_points[-1].timestamp.isoformat()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating sensor statistics: {e}")
            return {}
    
    async def simulate_sensor_data(
        self, 
        file_id: str, 
        sensor_id: str, 
        duration: int = 60,
        interval: float = 1.0
    ):
        """Simulate sensor data for testing"""
        try:
            if file_id not in self.sensors or sensor_id not in self.sensors[file_id]:
                raise ValueError(f"Sensor {sensor_id} not found for digital twin {file_id}")
            
            sensor_info = self.sensors[file_id][sensor_id]
            sensor_type = sensor_info["sensor_type"]
            
            # Generate simulated data based on sensor type
            if sensor_type == "temperature":
                base_temp = 20.0
                for i in range(int(duration / interval)):
                    value = base_temp + 5 * np.sin(i * 0.1) + np.random.normal(0, 0.5)
                    await self.update_sensor_data(file_id, sensor_id, round(value, 2))
                    await asyncio.sleep(interval)
            
            elif sensor_type == "pressure":
                base_pressure = 1013.25
                for i in range(int(duration / interval)):
                    value = base_pressure + 10 * np.sin(i * 0.05) + np.random.normal(0, 1)
                    await self.update_sensor_data(file_id, sensor_id, round(value, 2))
                    await asyncio.sleep(interval)
            
            elif sensor_type == "vibration":
                for i in range(int(duration / interval)):
                    value = np.random.normal(0, 0.1) + 0.5 * np.sin(i * 0.2)
                    await self.update_sensor_data(file_id, sensor_id, round(value, 4))
                    await asyncio.sleep(interval)
            
            else:
                # Generic numeric sensor
                for i in range(int(duration / interval)):
                    value = np.random.normal(50, 10)
                    await self.update_sensor_data(file_id, sensor_id, round(value, 2))
                    await asyncio.sleep(interval)
                    
        except Exception as e:
            logger.error(f"Error simulating sensor data: {e}")
    
    def list_sensors(self, file_id: str) -> List[Dict[str, Any]]:
        """List all sensors for a digital twin"""
        if file_id in self.sensors:
            return list(self.sensors[file_id].values())
        return []
    
    def remove_sensor(self, file_id: str, sensor_id: str) -> bool:
        """Remove a sensor"""
        try:
            if file_id in self.sensors and sensor_id in self.sensors[file_id]:
                del self.sensors[file_id][sensor_id]
                if file_id in self.data_history:
                    del self.data_history[file_id][sensor_id]
                logger.info(f"Removed sensor {sensor_id} from digital twin {file_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error removing sensor: {e}")
            return False

# Global sensor integration instance
sensor_integration = SensorIntegration()