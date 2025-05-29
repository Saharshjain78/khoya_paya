# Docker Deployment Guide for Khoya Paya

This guide helps you run Khoya Paya using Docker to avoid dlib compilation issues and ensure consistent deployment across different platforms.

## Prerequisites

1. **Install Docker Desktop**
   - Download from: https://www.docker.com/products/docker-desktop/
   - Ensure Docker is running before proceeding

2. **Verify Docker Installation**
   ```bash
   docker --version
   docker-compose --version
   ```

## Quick Start with Docker

### Option 1: Using Docker Compose (Recommended)

1. **Start the application**
   ```powershell
   # PowerShell
   .\docker-start.ps1
   
   # Or manually
   docker-compose up --build
   ```

2. **Access the app**
   - Open browser: http://localhost:8501
   - Login credentials: admin/admin123 or user/user123

3. **Stop the application**
   ```bash
   docker-compose down
   ```

### Option 2: Using Docker Commands

1. **Build and run**
   ```powershell
   # PowerShell
   .\docker-build.ps1
   
   # Or using batch file
   .\docker-build.bat
   ```

2. **Manual Docker commands**
   ```bash
   # Build the image
   docker build -t khoya-paya .
   
   # Run the container
   docker run -p 8501:8501 \
     -v ./database:/app/database \
     -v ./known_faces:/app/known_faces \
     -v ./user_profiles:/app/user_profiles \
     --name khoya-paya-container \
     khoya-paya
   ```

## Docker Benefits

✅ **No dlib compilation issues**
✅ **Consistent environment across platforms**
✅ **Easy deployment to cloud platforms**
✅ **Isolated dependencies**
✅ **Production-ready setup**

## Cloud Deployment Options

### 1. Railway Deployment

1. **Connect to Railway**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login to Railway
   railway login
   
   # Deploy
   railway up
   ```

2. **Environment Variables**
   - No special configuration needed
   - Railway will automatically detect Dockerfile

### 2. Render Deployment

1. **Create new Web Service on Render**
   - Connect your GitHub repository
   - Use Docker environment
   - Set build command: `docker build -t khoya-paya .`
   - Set start command: `streamlit run main.py --server.address 0.0.0.0 --server.port $PORT`

### 3. DigitalOcean App Platform

1. **Create new app**
   - Connect repository
   - Select Docker environment
   - Configure port 8501

### 4. Heroku (with Docker)

1. **Install Heroku CLI and login**
   ```bash
   heroku login
   heroku container:login
   ```

2. **Create app and deploy**
   ```bash
   heroku create your-app-name
   heroku container:push web
   heroku container:release web
   ```

## Local Development with Docker

### File Persistence
The docker-compose.yml mounts local directories:
- `./database` → Container's database
- `./known_faces` → Container's face storage
- `./user_profiles` → Container's user profiles

Changes persist even when container restarts.

### Development Workflow

1. **Make code changes** in your local files
2. **Rebuild container**
   ```bash
   docker-compose up --build
   ```
3. **Test changes** at http://localhost:8501

## Troubleshooting

### Common Issues

1. **Docker not running**
   ```
   Error: Cannot connect to the Docker daemon
   ```
   **Solution**: Start Docker Desktop

2. **Port already in use**
   ```
   Error: Port 8501 is already allocated
   ```
   **Solution**: Change port in docker-compose.yml or stop existing container
   ```bash
   docker stop khoya-paya-container
   docker rm khoya-paya-container
   ```

3. **Build failures**
   ```bash
   # Clean up and rebuild
   docker system prune -f
   docker-compose up --build --force-recreate
   ```

4. **Volume mounting issues on Windows**
   - Ensure Docker Desktop has access to your drive
   - Check Docker Desktop → Settings → Resources → File Sharing

### Container Management

```bash
# View running containers
docker ps

# View all containers
docker ps -a

# Stop container
docker stop khoya-paya-container

# Remove container
docker rm khoya-paya-container

# View logs
docker logs khoya-paya-container

# Execute commands in running container
docker exec -it khoya-paya-container bash
```

### Image Management

```bash
# List images
docker images

# Remove image
docker rmi khoya-paya

# Clean up unused images
docker image prune
```

## Production Considerations

1. **Environment Variables**
   - Use `.env` files for sensitive data
   - Configure through docker-compose.yml

2. **Security**
   - Change default passwords
   - Use secrets management for production
   - Enable HTTPS in production

3. **Performance**
   - Allocate sufficient memory to Docker
   - Consider using multi-stage builds for smaller images

4. **Monitoring**
   - Add health checks
   - Monitor container logs
   - Use monitoring tools like Prometheus

## File Structure

```
khoya_paya/
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Multi-container setup
├── .dockerignore           # Files to exclude from build
├── docker-build.ps1        # Windows PowerShell build script
├── docker-build.bat        # Windows batch build script
├── docker-start.ps1        # Quick start script
├── main.py                 # Main application
├── requirements.txt        # Python dependencies
└── ...                     # Other project files
```

This Docker setup ensures your face recognition app runs consistently across all platforms without dlib compilation issues!
