# Digital Twin Platform - Deployment Guide

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- At least 8GB RAM available
- 20GB free disk space

### 1. Clone and Setup

```bash
git clone <repository-url>
cd digital-twin-platform
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 2. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Manual Setup

### Backend Setup

1. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Database**
   ```bash
   # Using PostgreSQL (recommended)
   createdb digital_twin
   
   # Or using SQLite (development)
   # No setup required
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run Database Migrations**
   ```bash
   # Database tables are created automatically on first run
   ```

5. **Start Backend**
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Frontend Setup

1. **Install Node Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start Development Server**
   ```bash
   npm start
   ```

## Production Deployment

### Using Docker Compose

1. **Production Configuration**
   ```bash
   # Update docker-compose.yml for production
   # Set proper environment variables
   # Configure reverse proxy (nginx)
   ```

2. **Deploy**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Using Kubernetes

1. **Create Kubernetes Manifests**
   ```bash
   kubectl apply -f k8s/
   ```

2. **Configure Ingress**
   ```bash
   kubectl apply -f k8s/ingress.yaml
   ```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./digital_twin.db` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `SECRET_KEY` | Secret key for JWT tokens | `your-secret-key-here` |
| `MAX_FILE_SIZE` | Maximum file upload size | `104857600` (100MB) |
| `UPLOAD_DIR` | Directory for uploaded files | `uploads` |
| `PROCESSED_DIR` | Directory for processed files | `processed` |

### Database Configuration

#### PostgreSQL (Recommended)

```env
DATABASE_URL=postgresql://username:password@localhost:5432/digital_twin
```

#### SQLite (Development)

```env
DATABASE_URL=sqlite:///./digital_twin.db
```

### Redis Configuration

```env
REDIS_URL=redis://localhost:6379
```

## Monitoring and Logging

### Health Checks

- **Backend**: `GET /health`
- **Frontend**: `GET /health`

### Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Metrics

The application exposes metrics at `/metrics` endpoint for monitoring.

## Scaling

### Horizontal Scaling

1. **Backend Scaling**
   ```bash
   # Scale backend services
   docker-compose up --scale backend=3
   ```

2. **Load Balancer**
   ```nginx
   upstream backend {
       server backend1:8000;
       server backend2:8000;
       server backend3:8000;
   }
   ```

### Vertical Scaling

1. **Increase Resources**
   ```yaml
   # docker-compose.yml
   services:
     backend:
       deploy:
         resources:
           limits:
             memory: 4G
             cpus: '2.0'
   ```

## Security

### SSL/TLS

1. **Generate Certificates**
   ```bash
   openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
   ```

2. **Configure Nginx**
   ```nginx
   server {
       listen 443 ssl;
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;
       # ... rest of configuration
   }
   ```

### Authentication

1. **JWT Configuration**
   ```env
   JWT_SECRET_KEY=your-jwt-secret-key
   JWT_ALGORITHM=HS256
   JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

2. **API Keys**
   ```env
   API_KEY_HEADER=X-API-Key
   API_KEYS=key1,key2,key3
   ```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   lsof -i :8000
   lsof -i :3000
   
   # Kill the process
   kill -9 <PID>
   ```

2. **Database Connection Issues**
   ```bash
   # Check database status
   docker-compose ps postgres
   
   # Check logs
   docker-compose logs postgres
   ```

3. **File Upload Issues**
   ```bash
   # Check disk space
   df -h
   
   # Check upload directory permissions
   ls -la uploads/
   ```

### Performance Issues

1. **Slow File Processing**
   - Increase Celery worker count
   - Use more powerful hardware
   - Optimize file processing algorithms

2. **High Memory Usage**
   - Reduce concurrent processing jobs
   - Optimize 3D model processing
   - Use model compression

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with debug mode
uvicorn backend.main:app --reload --log-level debug
```

## Backup and Recovery

### Database Backup

```bash
# PostgreSQL
pg_dump digital_twin > backup.sql

# Restore
psql digital_twin < backup.sql
```

### File Backup

```bash
# Backup uploaded files
tar -czf uploads_backup.tar.gz uploads/

# Backup processed files
tar -czf processed_backup.tar.gz processed/
```

## Updates and Maintenance

### Updating the Application

1. **Pull Latest Changes**
   ```bash
   git pull origin main
   ```

2. **Rebuild and Restart**
   ```bash
   docker-compose down
   docker-compose up --build -d
   ```

### Database Migrations

```bash
# Run migrations
docker-compose exec backend alembic upgrade head
```

### Cleanup

```bash
# Remove old containers
docker system prune -a

# Remove old images
docker image prune -a

# Clean up logs
docker-compose logs --tail=0 -f | head -n 0
```

## Support

For issues and questions:

1. Check the logs: `docker-compose logs -f`
2. Review the API documentation: http://localhost:8000/docs
3. Check the troubleshooting section above
4. Create an issue in the repository