# Digital Twin Platform

A comprehensive digital twin software platform that converts CAD files and 2D images into interactive 3D digital twins, similar to NVIDIA Omniverse.

## Features

- **CAD File Processing**: Support for major CAD formats (STEP, IGES, STL, OBJ, PLY)
- **2D to 3D Conversion**: AI-powered conversion of 2D images to 3D models
- **Real-time 3D Visualization**: Web-based 3D viewer with interactive controls
- **Digital Twin Capabilities**: Real-time data integration and simulation
- **Cloud Processing**: Scalable backend processing with queue management
- **Modern UI**: React-based frontend with drag-and-drop file upload

## Architecture

- **Backend**: FastAPI with Python
- **Frontend**: React with Three.js for 3D rendering
- **Processing**: FreeCAD/OpenCASCADE for CAD, AI models for 2D-to-3D
- **Database**: PostgreSQL for metadata, Redis for caching
- **Queue**: Celery for background processing
- **Storage**: Local file system (configurable for cloud storage)

## Quick Start

1. Install dependencies:
   ```bash
   npm run install-all
   pip install -r requirements.txt
   ```

2. Start the development servers:
   ```bash
   npm run dev
   ```

3. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Project Structure

```
digital-twin-platform/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main application
│   ├── models/             # Database models
│   ├── services/           # Business logic
│   ├── processors/         # File processing modules
│   └── api/                # API endpoints
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API services
│   │   └── utils/          # Utilities
│   └── public/
├── processors/             # Standalone processing modules
│   ├── cad_processor.py    # CAD file processing
│   ├── image_processor.py  # 2D to 3D conversion
│   └── digital_twin.py     # Digital twin features
└── docker/                 # Docker configurations
```

## Supported File Formats

### CAD Files
- STEP (.step, .stp)
- IGES (.iges, .igs)
- STL (.stl)
- OBJ (.obj)
- PLY (.ply)
- 3DS (.3ds)
- FBX (.fbx)

### 2D Images
- JPEG (.jpg, .jpeg)
- PNG (.png)
- TIFF (.tiff, .tif)
- BMP (.bmp)
- WebP (.webp)

## Digital Twin Features

- Real-time sensor data integration
- Physics simulation
- Material properties
- Animation and keyframes
- Collaborative viewing
- Version control
- Export capabilities

## License

Apache License 2.0