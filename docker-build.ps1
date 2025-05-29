# Docker build script for Khoya Paya Face Recognition App

Write-Host "Building Khoya Paya Face Recognition Docker Image..." -ForegroundColor Green

# Check if Docker is running
try {
    docker info | Out-Null
    Write-Host "Docker is running" -ForegroundColor Green
} catch {
    Write-Host "Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Build the Docker image
Write-Host "Building Docker image..." -ForegroundColor Cyan
Write-Host "This may take several minutes on first build..." -ForegroundColor Gray

$startTime = Get-Date

docker build -t khoya-paya:latest .

if ($LASTEXITCODE -eq 0) {
    $endTime = Get-Date
    $duration = ($endTime - $startTime).TotalMinutes
    $durationText = [math]::Round($duration, 1)
    
    Write-Host "Docker image built successfully! ($durationText minutes)" -ForegroundColor Green
    
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "   - Run: .\docker-start.ps1 (to start the application)" -ForegroundColor Cyan
    Write-Host "   - Run: docker-compose up (manual start)" -ForegroundColor Cyan
    Write-Host "   - Access: http://localhost:8501 (when running)" -ForegroundColor Cyan
    
} else {
    Write-Host "Docker build failed!" -ForegroundColor Red
    Write-Host "Common solutions:" -ForegroundColor Yellow
    Write-Host "   - Ensure Docker Desktop has sufficient memory (4GB+)" -ForegroundColor Gray
    Write-Host "   - Check internet connection for downloading dependencies" -ForegroundColor Gray
    Write-Host "   - Try: docker system prune (to clean up)" -ForegroundColor Gray
    exit 1
}
