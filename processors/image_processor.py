"""
2D image to 3D model conversion using AI/ML techniques
"""

import os
import asyncio
import cv2
import numpy as np
import torch
import torch.nn as nn
from PIL import Image
import trimesh
from typing import Dict, Any, Optional, Tuple
import logging
from scipy import ndimage
from skimage import measure, morphology
import open3d as o3d

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageProcessor:
    """Processor for converting 2D images to 3D models using AI/ML"""
    
    def __init__(self):
        self.supported_formats = {
            '.jpg': self._process_image,
            '.jpeg': self._process_image,
            '.png': self._process_image,
            '.tiff': self._process_image,
            '.tif': self._process_image,
            '.bmp': self._process_image,
            '.webp': self._process_image
        }
        
        # Initialize AI models (placeholder - would load actual models)
        self.depth_model = None
        self.normal_model = None
        self.mesh_generation_model = None
        
    async def process_file(self, file_path: str, file_extension: str) -> Dict[str, Any]:
        """Process 2D image and convert to 3D model"""
        try:
            logger.info(f"Processing image file: {file_path}")
            
            if file_extension not in self.supported_formats:
                raise ValueError(f"Unsupported image format: {file_extension}")
            
            # Process the image
            model_data = await self._process_image(file_path)
            
            # Extract metadata
            metadata = self._extract_metadata(model_data)
            
            return {
                "model_data": model_data,
                "metadata": metadata,
                "file_type": "image",
                "format": file_extension
            }
            
        except Exception as e:
            logger.error(f"Error processing image file {file_path}: {str(e)}")
            raise
    
    async def _process_image(self, file_path: str) -> Dict[str, Any]:
        """Process image and convert to 3D model"""
        try:
            # Load image
            image = cv2.imread(file_path)
            if image is None:
                raise ValueError(f"Could not load image: {file_path}")
            
            # Convert to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Generate depth map
            depth_map = await self._generate_depth_map(image_rgb)
            
            # Generate normal map
            normal_map = await self._generate_normal_map(depth_map)
            
            # Create 3D mesh from depth map
            mesh_data = await self._depth_to_mesh(depth_map, image_rgb)
            
            return mesh_data
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            raise
    
    async def _generate_depth_map(self, image: np.ndarray) -> np.ndarray:
        """Generate depth map from 2D image using AI/ML techniques"""
        try:
            # For now, use traditional computer vision techniques
            # In production, this would use a trained depth estimation model
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Use Canny edge detection
            edges = cv2.Canny(blurred, 50, 150)
            
            # Create depth map using edge information
            # Areas with more edges are considered closer
            depth_map = np.zeros_like(gray, dtype=np.float32)
            
            # Use distance transform to create depth
            dist_transform = cv2.distanceTransform(edges, cv2.DIST_L2, 5)
            
            # Normalize and invert (edges are closer)
            depth_map = 1.0 - (dist_transform / np.max(dist_transform))
            
            # Apply additional depth cues
            # Use gradient magnitude as depth cue
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            gradient_magnitude = gradient_magnitude / np.max(gradient_magnitude)
            
            # Combine edge and gradient information
            depth_map = 0.7 * depth_map + 0.3 * (1.0 - gradient_magnitude)
            
            # Smooth the depth map
            depth_map = cv2.GaussianBlur(depth_map, (15, 15), 0)
            
            return depth_map
            
        except Exception as e:
            logger.error(f"Error generating depth map: {e}")
            raise
    
    async def _generate_normal_map(self, depth_map: np.ndarray) -> np.ndarray:
        """Generate normal map from depth map"""
        try:
            # Calculate gradients
            grad_x = cv2.Sobel(depth_map, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(depth_map, cv2.CV_64F, 0, 1, ksize=3)
            
            # Create normal map
            normal_map = np.zeros((*depth_map.shape, 3), dtype=np.float32)
            normal_map[:, :, 0] = -grad_x
            normal_map[:, :, 1] = -grad_y
            normal_map[:, :, 2] = 1.0
            
            # Normalize
            norm = np.sqrt(np.sum(normal_map**2, axis=2, keepdims=True))
            normal_map = normal_map / (norm + 1e-8)
            
            return normal_map
            
        except Exception as e:
            logger.error(f"Error generating normal map: {e}")
            raise
    
    async def _depth_to_mesh(self, depth_map: np.ndarray, color_image: np.ndarray) -> Dict[str, Any]:
        """Convert depth map to 3D mesh"""
        try:
            height, width = depth_map.shape
            
            # Create coordinate grids
            x = np.linspace(-1, 1, width)
            y = np.linspace(-1, 1, height)
            X, Y = np.meshgrid(x, y)
            
            # Scale depth map to appropriate range
            Z = depth_map * 0.5  # Scale depth
            
            # Create vertices
            vertices = np.stack([X.flatten(), Y.flatten(), Z.flatten()], axis=1)
            
            # Create faces using triangulation
            faces = []
            for i in range(height - 1):
                for j in range(width - 1):
                    # Get vertex indices
                    v1 = i * width + j
                    v2 = i * width + (j + 1)
                    v3 = (i + 1) * width + j
                    v4 = (i + 1) * width + (j + 1)
                    
                    # Create two triangles for each quad
                    faces.append([v1, v2, v3])
                    faces.append([v2, v4, v3])
            
            faces = np.array(faces)
            
            # Calculate normals
            normals = self._calculate_vertex_normals(vertices, faces)
            
            # Create UV coordinates
            uvs = np.stack([X.flatten(), Y.flatten()], axis=1)
            uvs = (uvs + 1) / 2  # Normalize to [0, 1]
            
            # Create colors from original image
            colors = color_image.reshape(-1, 3) / 255.0
            
            # Create trimesh object for processing
            mesh = trimesh.Trimesh(
                vertices=vertices,
                faces=faces,
                vertex_normals=normals,
                vertex_colors=colors
            )
            
            # Ensure mesh is watertight
            if not mesh.is_watertight:
                mesh.fill_holes()
            
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
                "uvs": uvs.tolist(),
                "colors": colors.tolist(),
                "bounds": bounds.tolist(),
                "center": center.tolist(),
                "scale": float(scale),
                "is_watertight": mesh.is_watertight,
                "volume": float(mesh.volume) if mesh.is_watertight else 0.0,
                "surface_area": float(mesh.surface_area)
            }
            
        except Exception as e:
            logger.error(f"Error converting depth to mesh: {e}")
            raise
    
    def _calculate_vertex_normals(self, vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
        """Calculate vertex normals from faces"""
        try:
            normals = np.zeros_like(vertices)
            
            for face in faces:
                v1, v2, v3 = vertices[face]
                
                # Calculate face normal
                edge1 = v2 - v1
                edge2 = v3 - v1
                face_normal = np.cross(edge1, edge2)
                face_normal = face_normal / (np.linalg.norm(face_normal) + 1e-8)
                
                # Add to vertex normals
                normals[face] += face_normal
            
            # Normalize vertex normals
            norms = np.linalg.norm(normals, axis=1, keepdims=True)
            normals = normals / (norms + 1e-8)
            
            return normals
            
        except Exception as e:
            logger.error(f"Error calculating vertex normals: {e}")
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
            "scale": model_data.get("scale", 1.0),
            "source_type": "image_to_3d"
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
            colors = np.array(model_data["colors"], dtype=np.float32) if model_data.get("colors") else None
            uvs = np.array(model_data["uvs"], dtype=np.float32) if model_data.get("uvs") else None
            
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
            
            # Add colors if available
            if colors is not None:
                color_buffer = pygltflib.Buffer()
                color_buffer.byteLength = len(colors.tobytes())
                gltf.buffers.append(color_buffer)
                
                color_view = pygltflib.BufferView()
                color_view.buffer = 3
                color_view.byteOffset = 0
                color_view.byteLength = len(colors.tobytes())
                gltf.bufferViews.append(color_view)
                
                color_accessor = pygltflib.Accessor()
                color_accessor.bufferView = 3
                color_accessor.byteOffset = 0
                color_accessor.componentType = pygltflib.FLOAT
                color_accessor.count = len(colors)
                color_accessor.type = pygltflib.VEC3
                gltf.accessors.append(color_accessor)
                
                primitive.attributes.COLOR_0 = 3
            
            # Add UVs if available
            if uvs is not None:
                uv_buffer = pygltflib.Buffer()
                uv_buffer.byteLength = len(uvs.tobytes())
                gltf.buffers.append(uv_buffer)
                
                uv_view = pygltflib.BufferView()
                uv_view.buffer = 4
                uv_view.byteOffset = 0
                uv_view.byteLength = len(uvs.tobytes())
                gltf.bufferViews.append(uv_view)
                
                uv_accessor = pygltflib.Accessor()
                uv_accessor.bufferView = 4
                uv_accessor.byteOffset = 0
                uv_accessor.componentType = pygltflib.FLOAT
                uv_accessor.count = len(uvs)
                uv_accessor.type = pygltflib.VEC2
                gltf.accessors.append(uv_accessor)
                
                primitive.attributes.TEXCOORD_0 = 4
            
            # Set binary data
            gltf.set_binary_data(0, vertices.tobytes())
            gltf.set_binary_data(1, faces.tobytes())
            if normals is not None:
                gltf.set_binary_data(2, normals.tobytes())
            if colors is not None:
                gltf.set_binary_data(3, colors.tobytes())
            if uvs is not None:
                gltf.set_binary_data(4, uvs.tobytes())
            
            # Save GLTF file
            gltf.save(output_path)
            
            logger.info(f"GLTF file saved to: {output_path}")
            
            return {
                "gltf_path": output_path,
                "format": "gltf",
                "vertex_count": len(vertices),
                "face_count": len(faces),
                "has_normals": normals is not None,
                "has_colors": colors is not None,
                "has_uvs": uvs is not None
            }
            
        except Exception as e:
            logger.error(f"Error converting to GLTF: {e}")
            raise