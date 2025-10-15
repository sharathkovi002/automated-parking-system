"""
AI enhancement module for digital twin intelligence and automation
"""

import asyncio
import numpy as np
import torch
import torch.nn as nn
from typing import Dict, Any, List, Optional, Tuple
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DigitalTwinAI:
    """AI enhancement for digital twin intelligence"""
    
    def __init__(self):
        self.models = {}
        self.predictions = {}
        self.anomaly_detectors = {}
        self.optimization_engines = {}
        
    async def analyze_model_complexity(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze 3D model complexity using AI"""
        try:
            vertices = np.array(model_data.get("vertices", []))
            faces = np.array(model_data.get("faces", []))
            
            if len(vertices) == 0 or len(faces) == 0:
                return {"complexity": "unknown", "score": 0}
            
            # Calculate geometric complexity metrics
            vertex_count = len(vertices)
            face_count = len(faces)
            
            # Surface area to volume ratio
            if model_data.get("is_watertight", False):
                volume = model_data.get("volume", 0)
                surface_area = model_data.get("surface_area", 0)
                sa_vol_ratio = surface_area / max(volume, 1e-6)
            else:
                sa_vol_ratio = 0
            
            # Edge length distribution
            edge_lengths = []
            for face in faces:
                if len(face) >= 3:
                    v1, v2, v3 = vertices[face[0]], vertices[face[1]], vertices[face[2]]
                    edge_lengths.extend([
                        np.linalg.norm(v2 - v1),
                        np.linalg.norm(v3 - v2),
                        np.linalg.norm(v1 - v3)
                    ])
            
            if edge_lengths:
                edge_std = np.std(edge_lengths)
                edge_mean = np.mean(edge_lengths)
                edge_variation = edge_std / max(edge_mean, 1e-6)
            else:
                edge_variation = 0
            
            # Curvature analysis (simplified)
            curvature_score = self._calculate_curvature_score(vertices, faces)
            
            # Overall complexity score
            complexity_score = (
                min(vertex_count / 10000, 1.0) * 0.3 +
                min(face_count / 20000, 1.0) * 0.3 +
                min(sa_vol_ratio / 10, 1.0) * 0.2 +
                min(edge_variation, 1.0) * 0.1 +
                min(curvature_score, 1.0) * 0.1
            )
            
            # Determine complexity level
            if complexity_score < 0.3:
                complexity_level = "low"
            elif complexity_score < 0.7:
                complexity_level = "medium"
            else:
                complexity_level = "high"
            
            return {
                "complexity": complexity_level,
                "score": float(complexity_score),
                "metrics": {
                    "vertex_count": vertex_count,
                    "face_count": face_count,
                    "surface_area_volume_ratio": float(sa_vol_ratio),
                    "edge_variation": float(edge_variation),
                    "curvature_score": float(curvature_score)
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing model complexity: {e}")
            return {"complexity": "unknown", "score": 0}
    
    def _calculate_curvature_score(self, vertices: np.ndarray, faces: np.ndarray) -> float:
        """Calculate curvature score for the model"""
        try:
            if len(vertices) == 0 or len(faces) == 0:
                return 0.0
            
            # Simplified curvature calculation
            # This is a basic implementation - in production, use proper curvature algorithms
            
            # Calculate face normals
            face_normals = []
            for face in faces:
                if len(face) >= 3:
                    v1, v2, v3 = vertices[face[0]], vertices[face[1]], vertices[face[2]]
                    normal = np.cross(v2 - v1, v3 - v1)
                    norm = np.linalg.norm(normal)
                    if norm > 1e-6:
                        face_normals.append(normal / norm)
            
            if not face_normals:
                return 0.0
            
            # Calculate normal variation (proxy for curvature)
            face_normals = np.array(face_normals)
            normal_std = np.std(face_normals, axis=0)
            curvature_score = np.mean(normal_std)
            
            return float(curvature_score)
            
        except Exception as e:
            logger.error(f"Error calculating curvature score: {e}")
            return 0.0
    
    async def suggest_materials(self, model_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Suggest materials based on model analysis"""
        try:
            complexity_analysis = await self.analyze_model_complexity(model_data)
            complexity = complexity_analysis["complexity"]
            
            # Base material suggestions
            suggestions = []
            
            if complexity == "low":
                # Simple models - suggest basic materials
                suggestions.extend([
                    {
                        "name": "Basic Plastic",
                        "type": "plastic",
                        "color": "#4CAF50",
                        "metallic": 0.0,
                        "roughness": 0.4,
                        "opacity": 1.0,
                        "confidence": 0.9,
                        "reason": "Simple geometry suitable for basic plastic material"
                    },
                    {
                        "name": "Matte Metal",
                        "type": "metal",
                        "color": "#607D8B",
                        "metallic": 0.8,
                        "roughness": 0.6,
                        "opacity": 1.0,
                        "confidence": 0.7,
                        "reason": "Simple geometry can use basic metal finish"
                    }
                ])
            
            elif complexity == "medium":
                # Medium complexity - suggest varied materials
                suggestions.extend([
                    {
                        "name": "Anodized Aluminum",
                        "type": "metal",
                        "color": "#2196F3",
                        "metallic": 0.9,
                        "roughness": 0.2,
                        "opacity": 1.0,
                        "confidence": 0.8,
                        "reason": "Medium complexity benefits from high-quality metal finish"
                    },
                    {
                        "name": "Textured Plastic",
                        "type": "plastic",
                        "color": "#FF9800",
                        "metallic": 0.0,
                        "roughness": 0.7,
                        "opacity": 1.0,
                        "confidence": 0.6,
                        "reason": "Textured surface suitable for medium complexity"
                    },
                    {
                        "name": "Glass",
                        "type": "glass",
                        "color": "#FFFFFF",
                        "metallic": 0.0,
                        "roughness": 0.0,
                        "opacity": 0.3,
                        "confidence": 0.5,
                        "reason": "Transparent material for visual appeal"
                    }
                ])
            
            else:  # high complexity
                # High complexity - suggest premium materials
                suggestions.extend([
                    {
                        "name": "Polished Steel",
                        "type": "metal",
                        "color": "#9E9E9E",
                        "metallic": 1.0,
                        "roughness": 0.1,
                        "opacity": 1.0,
                        "confidence": 0.9,
                        "reason": "High complexity requires premium metal finish"
                    },
                    {
                        "name": "Carbon Fiber",
                        "type": "composite",
                        "color": "#212121",
                        "metallic": 0.3,
                        "roughness": 0.4,
                        "opacity": 1.0,
                        "confidence": 0.8,
                        "reason": "Advanced material for complex geometry"
                    },
                    {
                        "name": "Titanium",
                        "type": "metal",
                        "color": "#BDBDBD",
                        "metallic": 0.9,
                        "roughness": 0.3,
                        "opacity": 1.0,
                        "confidence": 0.7,
                        "reason": "High-end metal for complex parts"
                    }
                ])
            
            # Apply context-based adjustments
            if context:
                if context.get("environment") == "outdoor":
                    # Add weather-resistant materials
                    suggestions.append({
                        "name": "Weather-Resistant Coating",
                        "type": "coating",
                        "color": "#795548",
                        "metallic": 0.2,
                        "roughness": 0.8,
                        "opacity": 1.0,
                        "confidence": 0.9,
                        "reason": "Outdoor environment requires weather protection"
                    })
                
                if context.get("application") == "medical":
                    # Add biocompatible materials
                    suggestions.append({
                        "name": "Medical Grade Plastic",
                        "type": "plastic",
                        "color": "#E8F5E8",
                        "metallic": 0.0,
                        "roughness": 0.2,
                        "opacity": 1.0,
                        "confidence": 0.95,
                        "reason": "Medical application requires biocompatible materials"
                    })
            
            # Sort by confidence
            suggestions.sort(key=lambda x: x["confidence"], reverse=True)
            
            return suggestions[:5]  # Return top 5 suggestions
            
        except Exception as e:
            logger.error(f"Error suggesting materials: {e}")
            return []
    
    async def detect_anomalies(self, sensor_data: List[Dict[str, Any]], sensor_type: str) -> List[Dict[str, Any]]:
        """Detect anomalies in sensor data using AI"""
        try:
            if not sensor_data:
                return []
            
            # Extract values and timestamps
            values = []
            timestamps = []
            for data in sensor_data:
                if isinstance(data.get("value"), (int, float)):
                    values.append(data["value"])
                    timestamps.append(data.get("timestamp", ""))
            
            if len(values) < 10:  # Need minimum data points
                return []
            
            values = np.array(values)
            
            # Simple anomaly detection using statistical methods
            # In production, use more sophisticated ML models
            
            # Z-score based anomaly detection
            mean = np.mean(values)
            std = np.std(values)
            z_scores = np.abs((values - mean) / (std + 1e-6))
            
            # Threshold for anomaly detection
            threshold = 2.5
            
            anomalies = []
            for i, (value, z_score, timestamp) in enumerate(zip(values, z_scores, timestamps)):
                if z_score > threshold:
                    anomalies.append({
                        "index": i,
                        "value": float(value),
                        "z_score": float(z_score),
                        "timestamp": timestamp,
                        "severity": "high" if z_score > 3.0 else "medium",
                        "description": f"Value {value} is {z_score:.2f} standard deviations from mean"
                    })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return []
    
    async def optimize_performance(self, model_data: Dict[str, Any], target_fps: int = 60) -> Dict[str, Any]:
        """Optimize 3D model for better performance"""
        try:
            vertices = np.array(model_data.get("vertices", []))
            faces = np.array(model_data.get("faces", []))
            
            if len(vertices) == 0 or len(faces) == 0:
                return model_data
            
            # Calculate current complexity
            vertex_count = len(vertices)
            face_count = len(faces)
            
            # Estimate performance impact
            estimated_fps = self._estimate_fps(vertex_count, face_count)
            
            optimizations = []
            
            # If performance is below target, suggest optimizations
            if estimated_fps < target_fps:
                # Suggest decimation
                target_vertices = int(vertex_count * 0.7)  # Reduce by 30%
                target_faces = int(face_count * 0.7)
                
                optimizations.append({
                    "type": "decimation",
                    "description": f"Reduce vertices from {vertex_count} to {target_vertices}",
                    "impact": "high",
                    "estimated_fps_improvement": min(estimated_fps * 1.5, target_fps)
                })
                
                # Suggest LOD (Level of Detail)
                optimizations.append({
                    "type": "lod",
                    "description": "Create multiple detail levels for distance-based rendering",
                    "impact": "medium",
                    "estimated_fps_improvement": min(estimated_fps * 1.2, target_fps)
                })
                
                # Suggest texture optimization
                optimizations.append({
                    "type": "texture_optimization",
                    "description": "Optimize texture resolution and compression",
                    "impact": "medium",
                    "estimated_fps_improvement": min(estimated_fps * 1.1, target_fps)
                })
            
            # Suggest material optimizations
            optimizations.append({
                "type": "material_optimization",
                "description": "Use fewer materials and optimize shader complexity",
                "impact": "low",
                "estimated_fps_improvement": min(estimated_fps * 1.05, target_fps)
            })
            
            return {
                "current_fps": estimated_fps,
                "target_fps": target_fps,
                "optimizations": optimizations,
                "recommended": optimizations[0] if optimizations else None
            }
            
        except Exception as e:
            logger.error(f"Error optimizing performance: {e}")
            return {"error": str(e)}
    
    def _estimate_fps(self, vertex_count: int, face_count: int) -> float:
        """Estimate FPS based on model complexity"""
        try:
            # Simple FPS estimation based on vertex/face count
            # This is a rough approximation - in production, use more accurate models
            
            # Base FPS for simple models
            base_fps = 120.0
            
            # Performance impact factors
            vertex_impact = vertex_count / 10000.0
            face_impact = face_count / 20000.0
            
            # Combined impact
            total_impact = (vertex_impact + face_impact) / 2.0
            
            # Calculate estimated FPS
            estimated_fps = base_fps / (1.0 + total_impact)
            
            return max(estimated_fps, 10.0)  # Minimum 10 FPS
            
        except Exception as e:
            logger.error(f"Error estimating FPS: {e}")
            return 30.0
    
    async def generate_insights(self, digital_twin_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate AI-powered insights about the digital twin"""
        try:
            insights = []
            
            # Analyze model complexity
            complexity_analysis = await self.analyze_model_complexity(digital_twin_data.get("model_data", {}))
            if complexity_analysis["complexity"] == "high":
                insights.append({
                    "type": "performance",
                    "title": "High Complexity Model",
                    "description": "This model has high geometric complexity which may impact rendering performance.",
                    "severity": "warning",
                    "recommendations": [
                        "Consider using Level of Detail (LOD) techniques",
                        "Optimize geometry for better performance",
                        "Use efficient materials and shaders"
                    ]
                })
            
            # Analyze materials
            materials = digital_twin_data.get("materials", [])
            if len(materials) > 5:
                insights.append({
                    "type": "materials",
                    "title": "Many Materials",
                    "description": f"Using {len(materials)} materials may impact performance.",
                    "severity": "info",
                    "recommendations": [
                        "Consider consolidating similar materials",
                        "Use texture atlasing to reduce draw calls"
                    ]
                })
            
            # Analyze physics properties
            physics = digital_twin_data.get("physics_properties", {})
            if physics.get("mass", 0) > 1000:
                insights.append({
                    "type": "physics",
                    "title": "Heavy Object",
                    "description": "This object has a very high mass which may affect simulation performance.",
                    "severity": "warning",
                    "recommendations": [
                        "Verify mass values are realistic",
                        "Consider using simplified collision shapes"
                    ]
                })
            
            # Analyze sensor data
            sensor_data = digital_twin_data.get("sensor_data", {})
            if sensor_data:
                sensor_count = len(sensor_data)
                if sensor_count > 10:
                    insights.append({
                        "type": "sensors",
                        "title": "Many Sensors",
                        "description": f"Using {sensor_count} sensors may impact real-time performance.",
                        "severity": "info",
                        "recommendations": [
                            "Consider data aggregation",
                            "Use efficient data transmission protocols"
                        ]
                    })
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return []

# Global AI enhancement instance
digital_twin_ai = DigitalTwinAI()