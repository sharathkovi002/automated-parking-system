"""
CAD file processing module using FreeCAD and OpenCASCADE
"""

import os
import sys
import asyncio
import trimesh
import numpy as np
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CADProcessor:
    """Processor for CAD files using FreeCAD and OpenCASCADE"""
    
    def __init__(self):
        self.supported_formats = {
            '.step': self._process_step,
            '.stp': self._process_step,
            '.iges': self._process_iges,
            '.igs': self._process_iges,
            '.stl': self._process_stl,
            '.obj': self._process_obj,
            '.ply': self._process_ply,
            '.3ds': self._process_3ds,
            '.fbx': self._process_fbx,
            '.dae': self._process_dae,
            '.gltf': self._process_gltf,
            '.glb': self._process_glb
        }
    
    async def process_file(self, file_path: str, file_extension: str) -> Dict[str, Any]:
        """Process CAD file and return 3D model data"""
        try:
            logger.info(f"Processing CAD file: {file_path}")
            
            if file_extension not in self.supported_formats:
                raise ValueError(f"Unsupported CAD format: {file_extension}")
            
            # Process the file
            processor_func = self.supported_formats[file_extension]
            model_data = await processor_func(file_path)
            
            # Extract metadata
            metadata = self._extract_metadata(model_data)
            
            return {
                "model_data": model_data,
                "metadata": metadata,
                "file_type": "cad",
                "format": file_extension
            }
            
        except Exception as e:
            logger.error(f"Error processing CAD file {file_path}: {str(e)}")
            raise
    
    async def _process_step(self, file_path: str) -> Dict[str, Any]:
        """Process STEP files using FreeCAD"""
        try:
            # For now, use trimesh as a fallback
            # In production, this would use FreeCAD Python API
            mesh = trimesh.load(file_path)
            return self._mesh_to_dict(mesh)
        except Exception as e:
            logger.warning(f"FreeCAD processing failed, using trimesh fallback: {e}")
            return await self._process_with_trimesh(file_path)
    
    async def _process_iges(self, file_path: str) -> Dict[str, Any]:
        """Process IGES files using FreeCAD"""
        try:
            # For now, use trimesh as a fallback
            mesh = trimesh.load(file_path)
            return self._mesh_to_dict(mesh)
        except Exception as e:
            logger.warning(f"FreeCAD processing failed, using trimesh fallback: {e}")
            return await self._process_with_trimesh(file_path)
    
    async def _process_stl(self, file_path: str) -> Dict[str, Any]:
        """Process STL files"""
        return await self._process_with_trimesh(file_path)
    
    async def _process_obj(self, file_path: str) -> Dict[str, Any]:
        """Process OBJ files"""
        return await self._process_with_trimesh(file_path)
    
    async def _process_ply(self, file_path: str) -> Dict[str, Any]:
        """Process PLY files"""
        return await self._process_with_trimesh(file_path)
    
    async def _process_3ds(self, file_path: str) -> Dict[str, Any]:
        """Process 3DS files"""
        return await self._process_with_trimesh(file_path)
    
    async def _process_fbx(self, file_path: str) -> Dict[str, Any]:
        """Process FBX files"""
        return await self._process_with_trimesh(file_path)
    
    async def _process_dae(self, file_path: str) -> Dict[str, Any]:
        """Process DAE (Collada) files"""
        return await self._process_with_trimesh(file_path)
    
    async def _process_gltf(self, file_path: str) -> Dict[str, Any]:
        """Process GLTF files"""
        return await self._process_with_trimesh(file_path)
    
    async def _process_glb(self, file_path: str) -> Dict[str, Any]:
        """Process GLB files"""
        return await self._process_with_trimesh(file_path)
    
    async def _process_with_trimesh(self, file_path: str) -> Dict[str, Any]:
        """Process file using trimesh library"""
        try:
            mesh = trimesh.load(file_path)
            return self._mesh_to_dict(mesh)
        except Exception as e:
            logger.error(f"Error loading file with trimesh: {e}")
            raise
    
    def _mesh_to_dict(self, mesh: trimesh.Trimesh) -> Dict[str, Any]:
        """Convert trimesh object to dictionary"""
        try:
            # Ensure mesh is watertight and has proper normals
            if not mesh.is_watertight:
                mesh.fill_holes()
            
            if not mesh.vertex_normals.any():
                mesh.compute_vertex_normals()
            
            # Get bounding box for scaling
            bounds = mesh.bounds
            center = mesh.centroid
            scale = np.max(bounds[1] - bounds[0])
            
            # Normalize mesh to unit size
            normalized_vertices = (mesh.vertices - center) / scale
            
            return {
                "vertices": normalized_vertices.tolist(),
                "faces": mesh.faces.tolist(),
                "normals": mesh.vertex_normals.tolist(),
                "uvs": mesh.visual.uv.tolist() if hasattr(mesh.visual, 'uv') and mesh.visual.uv is not None else [],
                "colors": mesh.visual.vertex_colors.tolist() if hasattr(mesh.visual, 'vertex_colors') and mesh.visual.vertex_colors is not None else [],
                "bounds": bounds.tolist(),
                "center": center.tolist(),
                "scale": float(scale),
                "is_watertight": mesh.is_watertight,
                "volume": float(mesh.volume) if mesh.is_watertight else 0.0,
                "surface_area": float(mesh.surface_area)
            }
        except Exception as e:
            logger.error(f"Error converting mesh to dictionary: {e}")
            raise
    
    def _extract_metadata(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from model data"""
        return {
            "vertex_count": len(model_data.get("vertices", [])),
            "face_count": len(model_data.get("faces", [])),
            "has_normals": len(model_data.get("normals", [])) > 0,
            "has_uvs": len(model_data.get("uvs", [])) > 0,
            "has_colors": len(model_data.get("colors", [])) > 0,
            "is_watertight": model_data.get("is_watertight", False),
            "volume": model_data.get("volume", 0.0),
            "surface_area": model_data.get("surface_area", 0.0),
            "bounds": model_data.get("bounds", []),
            "center": model_data.get("center", []),
            "scale": model_data.get("scale", 1.0)
        }
    
    async def convert_to_gltf(self, model_data: Dict[str, Any], output_path: str) -> Dict[str, Any]:
        """Convert model data to GLTF format"""
        try:
            import pygltflib
            
            # Create GLTF scene
            gltf = pygltflib.GLTF2()
            
            # Create scene
            scene = pygltflib.Scene()
            scene.name = "Digital Twin Scene"
            gltf.scenes.append(scene)
            
            # Create node
            node = pygltflib.Node()
            node.name = "Model"
            scene.nodes.append(0)  # Reference to node index
            gltf.nodes.append(node)
            
            # Prepare vertex data
            vertices = np.array(model_data["vertices"], dtype=np.float32)
            faces = np.array(model_data["faces"], dtype=np.uint32)
            normals = np.array(model_data["normals"], dtype=np.float32) if model_data.get("normals") else None
            
            # Create accessors for vertices
            vertex_buffer = pygltflib.Buffer()
            vertex_buffer.byteLength = len(vertices.tobytes())
            gltf.buffers.append(vertex_buffer)
            
            vertex_view = pygltflib.BufferView()
            vertex_view.buffer = 0
            vertex_view.byteOffset = 0
            vertex_view.byteLength = len(vertices.tobytes())
            gltf.bufferViews.append(vertex_view)
            
            vertex_accessor = pygltflib.Accessor()
            vertex_accessor.bufferView = 0
            vertex_accessor.byteOffset = 0
            vertex_accessor.componentType = pygltflib.FLOAT
            vertex_accessor.count = len(vertices)
            vertex_accessor.type = pygltflib.VEC3
            gltf.accessors.append(vertex_accessor)
            
            # Create accessors for faces
            face_buffer = pygltflib.Buffer()
            face_buffer.byteLength = len(faces.tobytes())
            gltf.buffers.append(face_buffer)
            
            face_view = pygltflib.BufferView()
            face_view.buffer = 1
            face_view.byteOffset = 0
            face_view.byteLength = len(faces.tobytes())
            gltf.bufferViews.append(face_view)
            
            face_accessor = pygltflib.Accessor()
            face_accessor.bufferView = 1
            face_accessor.byteOffset = 0
            face_accessor.componentType = pygltflib.UNSIGNED_INT
            face_accessor.count = len(faces) * 3
            face_accessor.type = pygltflib.SCALAR
            gltf.accessors.append(face_accessor)
            
            # Create mesh
            mesh = pygltflib.Mesh()
            primitive = pygltflib.Primitive()
            primitive.attributes = pygltflib.Attributes(POSITION=0)
            primitive.indices = 1
            mesh.primitives.append(primitive)
            gltf.meshes.append(mesh)
            
            # Assign mesh to node
            node.mesh = 0
            
            # Add normals if available
            if normals is not None:
                normal_buffer = pygltflib.Buffer()
                normal_buffer.byteLength = len(normals.tobytes())
                gltf.buffers.append(normal_buffer)
                
                normal_view = pygltflib.BufferView()
                normal_view.buffer = 2
                normal_view.byteOffset = 0
                normal_view.byteLength = len(normals.tobytes())
                gltf.bufferViews.append(normal_view)
                
                normal_accessor = pygltflib.Accessor()
                normal_accessor.bufferView = 2
                normal_accessor.byteOffset = 0
                normal_accessor.componentType = pygltflib.FLOAT
                normal_accessor.count = len(normals)
                normal_accessor.type = pygltflib.VEC3
                gltf.accessors.append(normal_accessor)
                
                primitive.attributes.NORMAL = 2
            
            # Set binary data
            gltf.set_binary_data(0, vertices.tobytes())
            gltf.set_binary_data(1, faces.tobytes())
            if normals is not None:
                gltf.set_binary_data(2, normals.tobytes())
            
            # Save GLTF file
            gltf.save(output_path)
            
            logger.info(f"GLTF file saved to: {output_path}")
            
            return {
                "gltf_path": output_path,
                "format": "gltf",
                "vertex_count": len(vertices),
                "face_count": len(faces),
                "has_normals": normals is not None
            }
            
        except Exception as e:
            logger.error(f"Error converting to GLTF: {e}")
            raise