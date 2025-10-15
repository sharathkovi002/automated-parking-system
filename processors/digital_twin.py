"""
Digital twin processor for creating enhanced 3D models with simulation capabilities
"""

import asyncio
import json
import numpy as np
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DigitalTwinProcessor:
    """Processor for creating digital twin features from 3D models"""
    
    def __init__(self):
        self.default_materials = {
            "metal": {
                "name": "Metal",
                "color": "#808080",
                "metallic": 0.9,
                "roughness": 0.1,
                "opacity": 1.0,
                "emissive": "#000000"
            },
            "plastic": {
                "name": "Plastic",
                "color": "#0066cc",
                "metallic": 0.0,
                "roughness": 0.3,
                "opacity": 1.0,
                "emissive": "#000000"
            },
            "glass": {
                "name": "Glass",
                "color": "#ffffff",
                "metallic": 0.0,
                "roughness": 0.0,
                "opacity": 0.3,
                "emissive": "#000000"
            },
            "wood": {
                "name": "Wood",
                "color": "#8b4513",
                "metallic": 0.0,
                "roughness": 0.8,
                "opacity": 1.0,
                "emissive": "#000000"
            }
        }
        
        self.default_physics = {
            "rigid_body": {
                "mass": 1.0,
                "friction": 0.5,
                "restitution": 0.3,
                "collision_shape": "mesh"
            },
            "soft_body": {
                "mass": 0.5,
                "friction": 0.7,
                "restitution": 0.1,
                "collision_shape": "convex_hull"
            }
        }
    
    async def create_digital_twin(
        self, 
        file_id: str, 
        model_data: Dict[str, Any], 
        source_type: str
    ) -> Dict[str, Any]:
        """Create digital twin data from 3D model"""
        try:
            logger.info(f"Creating digital twin for file: {file_id}")
            
            # Analyze model characteristics
            model_analysis = await self._analyze_model(model_data)
            
            # Generate materials based on analysis
            materials = await self._generate_materials(model_analysis, source_type)
            
            # Generate physics properties
            physics_properties = await self._generate_physics_properties(model_analysis)
            
            # Generate animations
            animations = await self._generate_animations(model_analysis)
            
            # Create digital twin metadata
            digital_twin_data = {
                "model_data": model_data,
                "materials": materials,
                "physics_properties": physics_properties,
                "animations": animations,
                "metadata": {
                    "file_id": file_id,
                    "source_type": source_type,
                    "created_at": datetime.utcnow().isoformat(),
                    "version": "1.0.0",
                    "analysis": model_analysis
                }
            }
            
            return digital_twin_data
            
        except Exception as e:
            logger.error(f"Error creating digital twin: {e}")
            raise
    
    async def _analyze_model(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze 3D model characteristics"""
        try:
            vertices = np.array(model_data.get("vertices", []))
            faces = np.array(model_data.get("faces", []))
            colors = np.array(model_data.get("colors", []))
            
            analysis = {
                "vertex_count": len(vertices),
                "face_count": len(faces),
                "has_colors": len(colors) > 0,
                "is_watertight": model_data.get("is_watertight", False),
                "volume": model_data.get("volume", 0.0),
                "surface_area": model_data.get("surface_area", 0.0),
                "complexity": self._calculate_complexity(vertices, faces),
                "bounding_box": model_data.get("bounds", []),
                "center": model_data.get("center", []),
                "scale": model_data.get("scale", 1.0)
            }
            
            # Determine material type based on analysis
            if analysis["has_colors"]:
                analysis["suggested_material_type"] = "colored"
            elif analysis["is_watertight"] and analysis["volume"] > 0:
                analysis["suggested_material_type"] = "solid"
            else:
                analysis["suggested_material_type"] = "surface"
            
            # Determine physics type
            if analysis["is_watertight"] and analysis["volume"] > 0:
                analysis["suggested_physics_type"] = "rigid_body"
            else:
                analysis["suggested_physics_type"] = "soft_body"
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing model: {e}")
            raise
    
    def _calculate_complexity(self, vertices: np.ndarray, faces: np.ndarray) -> str:
        """Calculate model complexity"""
        try:
            vertex_count = len(vertices)
            face_count = len(faces)
            
            if vertex_count < 1000 and face_count < 1000:
                return "low"
            elif vertex_count < 10000 and face_count < 10000:
                return "medium"
            else:
                return "high"
        except:
            return "unknown"
    
    async def _generate_materials(
        self, 
        analysis: Dict[str, Any], 
        source_type: str
    ) -> List[Dict[str, Any]]:
        """Generate materials based on model analysis"""
        try:
            materials = []
            
            # Base material based on source type
            if source_type == "cad":
                base_material = self.default_materials["metal"].copy()
            else:  # image
                base_material = self.default_materials["plastic"].copy()
            
            # Adjust material based on analysis
            if analysis["suggested_material_type"] == "colored":
                base_material["name"] = "Colored Material"
                base_material["metallic"] = 0.3
                base_material["roughness"] = 0.4
            elif analysis["suggested_material_type"] == "solid":
                base_material["name"] = "Solid Material"
                base_material["metallic"] = 0.7
                base_material["roughness"] = 0.2
            else:  # surface
                base_material["name"] = "Surface Material"
                base_material["metallic"] = 0.1
                base_material["roughness"] = 0.6
            
            # Add material ID
            base_material["id"] = "material_0"
            materials.append(base_material)
            
            # Add additional materials for complex models
            if analysis["complexity"] == "high":
                # Add glass material for transparency
                glass_material = self.default_materials["glass"].copy()
                glass_material["id"] = "material_1"
                materials.append(glass_material)
                
                # Add wood material for variety
                wood_material = self.default_materials["wood"].copy()
                wood_material["id"] = "material_2"
                materials.append(wood_material)
            
            return materials
            
        except Exception as e:
            logger.error(f"Error generating materials: {e}")
            return [self.default_materials["plastic"]]
    
    async def _generate_physics_properties(
        self, 
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate physics properties based on model analysis"""
        try:
            physics_type = analysis["suggested_physics_type"]
            base_physics = self.default_physics[physics_type].copy()
            
            # Adjust properties based on model characteristics
            if analysis["is_watertight"] and analysis["volume"] > 0:
                # Calculate density based on volume
                density = 1.0 / max(analysis["volume"], 0.001)
                base_physics["mass"] = min(density, 10.0)
                
                # Adjust friction based on surface area
                if analysis["surface_area"] > 0:
                    roughness_factor = min(analysis["surface_area"] / 10.0, 1.0)
                    base_physics["friction"] = 0.3 + (roughness_factor * 0.4)
            
            # Add additional properties
            base_physics["density"] = base_physics["mass"] / max(analysis["volume"], 0.001)
            base_physics["center_of_mass"] = analysis["center"]
            base_physics["inertia"] = self._calculate_inertia(analysis)
            
            return base_physics
            
        except Exception as e:
            logger.error(f"Error generating physics properties: {e}")
            return self.default_physics["rigid_body"]
    
    def _calculate_inertia(self, analysis: Dict[str, Any]) -> List[float]:
        """Calculate moment of inertia for the model"""
        try:
            # Simplified inertia calculation
            # In a real implementation, this would be more sophisticated
            volume = max(analysis["volume"], 0.001)
            scale = analysis["scale"]
            
            # Approximate inertia for a box
            inertia = [
                volume * scale**2 / 12,  # Ixx
                volume * scale**2 / 12,  # Iyy
                volume * scale**2 / 12   # Izz
            ]
            
            return inertia
        except:
            return [1.0, 1.0, 1.0]
    
    async def _generate_animations(
        self, 
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate animations for the digital twin"""
        try:
            animations = []
            
            # Basic rotation animation
            rotation_animation = {
                "id": "rotation_animation",
                "name": "Rotation",
                "type": "rotation",
                "duration": 10.0,
                "loop": True,
                "keyframes": [
                    {
                        "timestamp": 0.0,
                        "rotation": [0, 0, 0]
                    },
                    {
                        "timestamp": 5.0,
                        "rotation": [0, 180, 0]
                    },
                    {
                        "timestamp": 10.0,
                        "rotation": [0, 360, 0]
                    }
                ]
            }
            animations.append(rotation_animation)
            
            # Scale animation for complex models
            if analysis["complexity"] == "high":
                scale_animation = {
                    "id": "scale_animation",
                    "name": "Scale Pulse",
                    "type": "scale",
                    "duration": 2.0,
                    "loop": True,
                    "keyframes": [
                        {
                            "timestamp": 0.0,
                            "scale": [1.0, 1.0, 1.0]
                        },
                        {
                            "timestamp": 1.0,
                            "scale": [1.1, 1.1, 1.1]
                        },
                        {
                            "timestamp": 2.0,
                            "scale": [1.0, 1.0, 1.0]
                        }
                    ]
                }
                animations.append(scale_animation)
            
            return animations
            
        except Exception as e:
            logger.error(f"Error generating animations: {e}")
            return []
    
    async def add_sensor_data(
        self, 
        digital_twin_data: Dict[str, Any], 
        sensor_id: str, 
        sensor_type: str, 
        value: Any,
        unit: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add sensor data to digital twin"""
        try:
            if "sensor_data" not in digital_twin_data:
                digital_twin_data["sensor_data"] = {}
            
            digital_twin_data["sensor_data"][sensor_id] = {
                "sensor_type": sensor_type,
                "value": value,
                "unit": unit,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return digital_twin_data
            
        except Exception as e:
            logger.error(f"Error adding sensor data: {e}")
            raise
    
    async def update_material_properties(
        self, 
        digital_twin_data: Dict[str, Any], 
        material_id: str, 
        properties: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update material properties"""
        try:
            if "materials" in digital_twin_data:
                for material in digital_twin_data["materials"]:
                    if material.get("id") == material_id:
                        material.update(properties)
                        break
            
            return digital_twin_data
            
        except Exception as e:
            logger.error(f"Error updating material properties: {e}")
            raise
    
    async def add_animation(
        self, 
        digital_twin_data: Dict[str, Any], 
        animation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add animation to digital twin"""
        try:
            if "animations" not in digital_twin_data:
                digital_twin_data["animations"] = []
            
            digital_twin_data["animations"].append(animation)
            
            return digital_twin_data
            
        except Exception as e:
            logger.error(f"Error adding animation: {e}")
            raise