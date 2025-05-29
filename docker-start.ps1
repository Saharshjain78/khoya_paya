#!/usr/bin/env powershell
# Docker start script for Khoya Paya Face Recognition App

Write-Host "🚀 Starting Khoya Paya Face Recognition App with Docker..." -ForegroundColor Green

# Check if Docker is running
try {
    docker info | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    Write-Host "Starting Docker Desktop..." -ForegroundColor Yellow
    Start-Process "Docker Desktop" -ErrorAction SilentlyContinue
    Write-Host "⏳ Please wait for Docker Desktop to start, then run this script again." -ForegroundColor Yellow
    exit 1
}

# Check if image exists
$imageExists = docker images khoya-paya:latest --format "{{.Repository}}" | Select-String "khoya-paya"
if (-not $imageExists) {
    Write-Host "⚠️ Docker image not found. Building it first..." -ForegroundColor Yellow
    .\docker-build.ps1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to build Docker image. Exiting." -ForegroundColor Red
        exit 1
    }
}

Write-Host "`n🚀 Starting application with Docker Compose..." -ForegroundColor Cyan

try {
    # Stop any existing containers
    docker-compose down 2>$null
    
    # Start the application
    docker-compose up -d
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ Application started successfully!" -ForegroundColor Green
        Write-Host "🌐 Access your app at: http://localhost:8501" -ForegroundColor Cyan
        Write-Host "🔐 Login credentials:" -ForegroundColor Yellow
        Write-Host "   • Admin: admin / admin123" -ForegroundColor Gray
        Write-Host "   • User: user / user123" -ForegroundColor Gray
        
        Write-Host "`n📊 Useful commands:" -ForegroundColor Yellow
        Write-Host "   • View logs: docker-compose logs -f" -ForegroundColor Gray
        Write-Host "   • Stop app: docker-compose down" -ForegroundColor Gray
        Write-Host "   • Restart: docker-compose restart" -ForegroundColor Gray
        
        # Wait for app to start and test
        Write-Host "`n⏳ Waiting for app to initialize..." -ForegroundColor Yellow
        Start-Sleep -Seconds 10
        
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8501" -TimeoutSec 5 -UseBasicParsing -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ App is responding! Ready to use." -ForegroundColor Green
            }
        } catch {
            Write-Host "⏳ App is still starting up. Please wait a moment." -ForegroundColor Yellow
        }
        
    } else {
        Write-Host "❌ Failed to start application" -ForegroundColor Red
        Write-Host "Check logs with: docker-compose logs" -ForegroundColor Gray
        exit 1
    }
} catch {
    Write-Host "❌ Error starting application: $_" -ForegroundColor Red
    exit 1
}
