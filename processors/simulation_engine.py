"""
Simulation engine for digital twin physics and behavior simulation
"""

import asyncio
import numpy as np
from typing import Dict, Any, List, Optional, Callable
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimulationEngine:
    """Physics simulation engine for digital twins"""
    
    def __init__(self):
        self.simulations = {}
        self.callbacks = {}
        self.running = False
        
    async def create_simulation(
        self, 
        file_id: str, 
        physics_properties: Dict[str, Any],
        initial_conditions: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new physics simulation"""
        try:
            simulation_id = f"sim_{file_id}_{datetime.utcnow().timestamp()}"
            
            simulation = {
                "id": simulation_id,
                "file_id": file_id,
                "physics_properties": physics_properties,
                "initial_conditions": initial_conditions or {},
                "state": self._initialize_state(physics_properties, initial_conditions),
                "running": False,
                "paused": False,
                "time": 0.0,
                "dt": 0.016,  # 60 FPS
                "created_at": datetime.utcnow(),
                "last_update": datetime.utcnow()
            }
            
            self.simulations[simulation_id] = simulation
            logger.info(f"Created simulation {simulation_id} for file {file_id}")
            
            return simulation_id
            
        except Exception as e:
            logger.error(f"Error creating simulation: {e}")
            raise
    
    def _initialize_state(self, physics_properties: Dict[str, Any], initial_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize simulation state"""
        state = {
            "position": np.array(initial_conditions.get("position", [0, 0, 0]), dtype=np.float32),
            "velocity": np.array(initial_conditions.get("velocity", [0, 0, 0]), dtype=np.float32),
            "acceleration": np.array(initial_conditions.get("acceleration", [0, 0, 0]), dtype=np.float32),
            "rotation": np.array(initial_conditions.get("rotation", [0, 0, 0]), dtype=np.float32),
            "angular_velocity": np.array(initial_conditions.get("angular_velocity", [0, 0, 0]), dtype=np.float32),
            "mass": physics_properties.get("mass", 1.0),
            "inertia": np.array(physics_properties.get("inertia", [1, 1, 1]), dtype=np.float32),
            "forces": [],
            "torques": []
        }
        
        return state
    
    async def start_simulation(self, simulation_id: str) -> bool:
        """Start a simulation"""
        try:
            if simulation_id not in self.simulations:
                raise ValueError(f"Simulation {simulation_id} not found")
            
            simulation = self.simulations[simulation_id]
            simulation["running"] = True
            simulation["paused"] = False
            
            # Start simulation loop
            asyncio.create_task(self._simulation_loop(simulation_id))
            
            logger.info(f"Started simulation {simulation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting simulation: {e}")
            return False
    
    async def pause_simulation(self, simulation_id: str) -> bool:
        """Pause a simulation"""
        try:
            if simulation_id not in self.simulations:
                raise ValueError(f"Simulation {simulation_id} not found")
            
            self.simulations[simulation_id]["paused"] = True
            logger.info(f"Paused simulation {simulation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error pausing simulation: {e}")
            return False
    
    async def resume_simulation(self, simulation_id: str) -> bool:
        """Resume a simulation"""
        try:
            if simulation_id not in self.simulations:
                raise ValueError(f"Simulation {simulation_id} not found")
            
            self.simulations[simulation_id]["paused"] = False
            logger.info(f"Resumed simulation {simulation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error resuming simulation: {e}")
            return False
    
    async def stop_simulation(self, simulation_id: str) -> bool:
        """Stop a simulation"""
        try:
            if simulation_id not in self.simulations:
                raise ValueError(f"Simulation {simulation_id} not found")
            
            self.simulations[simulation_id]["running"] = False
            self.simulations[simulation_id]["paused"] = False
            logger.info(f"Stopped simulation {simulation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping simulation: {e}")
            return False
    
    async def _simulation_loop(self, simulation_id: str):
        """Main simulation loop"""
        try:
            while self.simulations[simulation_id]["running"]:
                if not self.simulations[simulation_id]["paused"]:
                    await self._update_simulation(simulation_id)
                
                await asyncio.sleep(self.simulations[simulation_id]["dt"])
                
        except Exception as e:
            logger.error(f"Error in simulation loop: {e}")
        finally:
            self.simulations[simulation_id]["running"] = False
    
    async def _update_simulation(self, simulation_id: str):
        """Update simulation state"""
        try:
            simulation = self.simulations[simulation_id]
            state = simulation["state"]
            dt = simulation["dt"]
            
            # Apply forces
            total_force = np.array([0, 0, 0], dtype=np.float32)
            for force in state["forces"]:
                total_force += np.array(force, dtype=np.float32)
            
            # Apply torques
            total_torque = np.array([0, 0, 0], dtype=np.float32)
            for torque in state["torques"]:
                total_torque += np.array(torque, dtype=np.float32)
            
            # Update acceleration
            state["acceleration"] = total_force / state["mass"]
            
            # Update velocity
            state["velocity"] += state["acceleration"] * dt
            
            # Update position
            state["position"] += state["velocity"] * dt
            
            # Update angular velocity
            state["angular_velocity"] += total_torque / state["inertia"] * dt
            
            # Update rotation
            state["rotation"] += state["angular_velocity"] * dt
            
            # Update time
            simulation["time"] += dt
            simulation["last_update"] = datetime.utcnow()
            
            # Notify callbacks
            await self._notify_callbacks(simulation_id, state)
            
        except Exception as e:
            logger.error(f"Error updating simulation: {e}")
    
    async def _notify_callbacks(self, simulation_id: str, state: Dict[str, Any]):
        """Notify registered callbacks"""
        try:
            if simulation_id in self.callbacks:
                for callback in self.callbacks[simulation_id]:
                    try:
                        await callback(simulation_id, state)
                    except Exception as e:
                        logger.error(f"Error in callback: {e}")
        except Exception as e:
            logger.error(f"Error notifying callbacks: {e}")
    
    def add_force(self, simulation_id: str, force: List[float]):
        """Add a force to the simulation"""
        if simulation_id in self.simulations:
            self.simulations[simulation_id]["state"]["forces"].append(force)
    
    def add_torque(self, simulation_id: str, torque: List[float]):
        """Add a torque to the simulation"""
        if simulation_id in self.simulations:
            self.simulations[simulation_id]["state"]["torques"].append(torque)
    
    def clear_forces(self, simulation_id: str):
        """Clear all forces from the simulation"""
        if simulation_id in self.simulations:
            self.simulations[simulation_id]["state"]["forces"] = []
            self.simulations[simulation_id]["state"]["torques"] = []
    
    def get_simulation_state(self, simulation_id: str) -> Optional[Dict[str, Any]]:
        """Get current simulation state"""
        if simulation_id in self.simulations:
            return self.simulations[simulation_id]["state"].copy()
        return None
    
    def get_simulation_info(self, simulation_id: str) -> Optional[Dict[str, Any]]:
        """Get simulation information"""
        if simulation_id in self.simulations:
            sim = self.simulations[simulation_id]
            return {
                "id": sim["id"],
                "file_id": sim["file_id"],
                "running": sim["running"],
                "paused": sim["paused"],
                "time": sim["time"],
                "created_at": sim["created_at"],
                "last_update": sim["last_update"]
            }
        return None
    
    def register_callback(self, simulation_id: str, callback: Callable):
        """Register a callback for simulation updates"""
        if simulation_id not in self.callbacks:
            self.callbacks[simulation_id] = []
        self.callbacks[simulation_id].append(callback)
    
    def unregister_callback(self, simulation_id: str, callback: Callable):
        """Unregister a callback"""
        if simulation_id in self.callbacks:
            try:
                self.callbacks[simulation_id].remove(callback)
            except ValueError:
                pass
    
    def list_simulations(self) -> List[Dict[str, Any]]:
        """List all simulations"""
        return [self.get_simulation_info(sim_id) for sim_id in self.simulations.keys()]
    
    def delete_simulation(self, simulation_id: str) -> bool:
        """Delete a simulation"""
        try:
            if simulation_id in self.simulations:
                # Stop simulation if running
                if self.simulations[simulation_id]["running"]:
                    asyncio.create_task(self.stop_simulation(simulation_id))
                
                # Remove from dictionaries
                del self.simulations[simulation_id]
                if simulation_id in self.callbacks:
                    del self.callbacks[simulation_id]
                
                logger.info(f"Deleted simulation {simulation_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deleting simulation: {e}")
            return False

# Global simulation engine instance
simulation_engine = SimulationEngine()