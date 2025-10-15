# Digital Twin Platform - API Documentation

## Overview

The Digital Twin Platform provides a comprehensive REST API for converting CAD files and 2D images into interactive 3D digital twins. The API is built with FastAPI and provides automatic OpenAPI documentation.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

## Authentication

Currently, the API does not require authentication for basic operations. In production, implement JWT-based authentication:

```http
Authorization: Bearer <jwt-token>
```

## File Upload

### Upload File

Upload a CAD file or 2D image for processing.

```http
POST /api/upload
Content-Type: multipart/form-data

file: <file>
```

**Supported Formats:**
- **CAD**: STEP (.step, .stp), IGES (.iges, .igs), STL (.stl), OBJ (.obj), PLY (.ply), 3DS (.3ds), FBX (.fbx), DAE (.dae), GLTF (.gltf), GLB (.glb)
- **Images**: JPEG (.jpg, .jpeg), PNG (.png), TIFF (.tiff, .tif), BMP (.bmp), WebP (.webp)

**Response:**
```json
{
  "file_id": "uuid",
  "filename": "model.step",
  "file_type": "cad",
  "status": "uploaded",
  "message": "File uploaded successfully. Processing started."
}
```

## File Management

### List Files

Get a list of all uploaded files.

```http
GET /api/files/
```

**Query Parameters:**
- `skip` (int): Number of files to skip (default: 0)
- `limit` (int): Maximum number of files to return (default: 100)
- `file_type` (string): Filter by file type ("cad" or "image")

**Response:**
```json
[
  {
    "id": "uuid",
    "filename": "model.step",
    "file_path": "uploads/uuid.step",
    "file_type": "cad",
    "file_size": 1024000,
    "status": "completed",
    "processed_path": "processed/uuid_processed.gltf",
    "metadata": {
      "vertex_count": 5000,
      "face_count": 10000
    },
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:05:00Z"
  }
]
```

### Get File Details

Get detailed information about a specific file.

```http
GET /api/files/{file_id}
```

**Response:**
```json
{
  "id": "uuid",
  "filename": "model.step",
  "file_path": "uploads/uuid.step",
  "file_type": "cad",
  "file_size": 1024000,
  "status": "completed",
  "processed_path": "processed/uuid_processed.gltf",
  "metadata": {
    "vertex_count": 5000,
    "face_count": 10000,
    "is_watertight": true,
    "volume": 1.5,
    "surface_area": 3.2
  },
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:05:00Z"
}
```

### Get Processing Status

Get the current processing status of a file.

```http
GET /api/files/{file_id}/status
```

**Response:**
```json
{
  "file_id": "uuid",
  "status": "processing",
  "progress": 75,
  "message": "Processing in progress...",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:02:30Z"
}
```

### Delete File

Delete a file and its associated data.

```http
DELETE /api/files/{file_id}
```

**Response:**
```json
{
  "message": "File deleted successfully"
}
```

## Digital Twin Management

### Get Digital Twin Data

Get complete digital twin data for a file.

```http
GET /api/digital-twin/{file_id}
```

**Response:**
```json
{
  "file_id": "uuid",
  "model_data": {
    "vertices": [[0, 0, 0], [1, 0, 0], ...],
    "faces": [[0, 1, 2], [1, 2, 3], ...],
    "normals": [[0, 0, 1], [0, 0, 1], ...]
  },
  "materials": [
    {
      "id": "material_0",
      "name": "Metal",
      "color": "#808080",
      "metallic": 0.9,
      "roughness": 0.1,
      "opacity": 1.0
    }
  ],
  "animations": [
    {
      "id": "rotation_animation",
      "name": "Rotation",
      "type": "rotation",
      "duration": 10.0,
      "loop": true,
      "keyframes": [...]
    }
  ],
  "physics_properties": {
    "mass": 1.0,
    "friction": 0.5,
    "restitution": 0.3,
    "collision_shape": "mesh"
  },
  "sensor_data": {
    "sensor_1": {
      "sensor_type": "temperature",
      "value": 25.5,
      "unit": "°C",
      "timestamp": "2024-01-01T00:00:00Z"
    }
  }
}
```

### Update Digital Twin

Update digital twin data.

```http
PUT /api/digital-twin/{file_id}
Content-Type: application/json

{
  "file_id": "uuid",
  "updates": {
    "position": [1, 2, 3],
    "rotation": [0, 45, 0],
    "scale": [1.5, 1.5, 1.5]
  }
}
```

**Response:**
```json
{
  "message": "Digital twin updated successfully"
}
```

### Add Sensor Data

Add real-time sensor data to a digital twin.

```http
POST /api/digital-twin/{file_id}/sensor-data
Content-Type: application/json

{
  "sensor_id": "temp_sensor_1",
  "sensor_type": "temperature",
  "value": 25.5,
  "unit": "°C"
}
```

**Response:**
```json
{
  "message": "Sensor data added successfully"
}
```

### Get Sensor Data

Get all sensor data for a digital twin.

```http
GET /api/digital-twin/{file_id}/sensor-data
```

**Response:**
```json
{
  "temp_sensor_1": {
    "sensor_type": "temperature",
    "value": 25.5,
    "unit": "°C",
    "timestamp": "2024-01-01T00:00:00Z"
  },
  "pressure_sensor_1": {
    "sensor_type": "pressure",
    "value": 1013.25,
    "unit": "hPa",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

## Model Management

### Get Model Data

Get 3D model data for a file.

```http
GET /api/models/{file_id}
```

**Response:**
```json
{
  "file_id": "uuid",
  "model_data": {
    "vertices": [[0, 0, 0], [1, 0, 0], ...],
    "faces": [[0, 1, 2], [1, 2, 3], ...],
    "normals": [[0, 0, 1], [0, 0, 1], ...],
    "uvs": [[0, 0], [1, 0], ...],
    "colors": [[1, 0, 0], [0, 1, 0], ...]
  },
  "materials": [...],
  "animations": [...],
  "physics_properties": {...},
  "sensor_data": {...}
}
```

### Update Materials

Update material properties for a model.

```http
PUT /api/models/{file_id}/materials
Content-Type: application/json

[
  {
    "name": "Steel",
    "color": "#808080",
    "metallic": 0.9,
    "roughness": 0.1,
    "opacity": 1.0,
    "emissive": "#000000"
  }
]
```

**Response:**
```json
{
  "message": "Materials updated successfully"
}
```

### Update Animations

Update animations for a model.

```http
PUT /api/models/{file_id}/animations
Content-Type: application/json

[
  {
    "id": "rotation_animation",
    "name": "Rotation",
    "type": "rotation",
    "duration": 10.0,
    "loop": true,
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
]
```

**Response:**
```json
{
  "message": "Animations updated successfully"
}
```

### Update Physics Properties

Update physics properties for a model.

```http
PUT /api/models/{file_id}/physics
Content-Type: application/json

{
  "mass": 2.0,
  "friction": 0.7,
  "restitution": 0.2,
  "collision_shape": "convex_hull"
}
```

**Response:**
```json
{
  "message": "Physics properties updated successfully"
}
```

## File Download

### Download Processed File

Download the processed 3D model file.

```http
GET /api/download/{file_id}
```

**Response:**
- File download (GLTF format)

## WebSocket API

### Real-time Updates

Connect to WebSocket for real-time digital twin updates.

```javascript
const ws = new WebSocket('ws://localhost:8000/api/digital-twin/{file_id}/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Update:', data);
};
```

**Message Types:**
- `digital_twin_updated`: Digital twin data updated
- `sensor_data_updated`: Sensor data updated
- `processing_status`: File processing status update

## Error Handling

### Error Response Format

```json
{
  "detail": "Error message",
  "status_code": 400,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Common Error Codes

- `400 Bad Request`: Invalid request data
- `404 Not Found`: Resource not found
- `413 Payload Too Large`: File too large
- `415 Unsupported Media Type`: Unsupported file format
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

## Rate Limiting

- **File Upload**: 10 requests per minute
- **API Calls**: 100 requests per minute
- **WebSocket Connections**: 5 per IP

## Examples

### Complete Workflow

1. **Upload a CAD file:**
   ```bash
   curl -X POST "http://localhost:8000/api/upload" \
        -H "Content-Type: multipart/form-data" \
        -F "file=@model.step"
   ```

2. **Check processing status:**
   ```bash
   curl "http://localhost:8000/api/files/{file_id}/status"
   ```

3. **Get digital twin data:**
   ```bash
   curl "http://localhost:8000/api/digital-twin/{file_id}"
   ```

4. **Add sensor data:**
   ```bash
   curl -X POST "http://localhost:8000/api/digital-twin/{file_id}/sensor-data" \
        -H "Content-Type: application/json" \
        -d '{"sensor_id": "temp_1", "sensor_type": "temperature", "value": 25.5}'
   ```

5. **Download processed model:**
   ```bash
   curl "http://localhost:8000/api/download/{file_id}" -o model.gltf
   ```

## SDK Examples

### Python

```python
import requests

# Upload file
with open('model.step', 'rb') as f:
    response = requests.post('http://localhost:8000/api/upload', files={'file': f})
    file_data = response.json()

# Get digital twin data
response = requests.get(f'http://localhost:8000/api/digital-twin/{file_data["file_id"]}')
digital_twin = response.json()
```

### JavaScript

```javascript
// Upload file
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://localhost:8000/api/upload', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));

// Get digital twin data
fetch(`http://localhost:8000/api/digital-twin/${fileId}`)
.then(response => response.json())
.then(data => console.log(data));
```

## Interactive Documentation

Visit `http://localhost:8000/docs` for interactive API documentation with Swagger UI, or `http://localhost:8000/redoc` for ReDoc documentation.