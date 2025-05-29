@echo off
echo Starting Khoya Paya Face Recognition App...
echo.

REM Check if Docker is available
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed or not running.
    echo Please install Docker Desktop and ensure it's running.
    pause
    exit /b 1
)

REM Check if image exists
docker images khoya-paya:latest -q >nul 2>&1
if errorlevel 1 (
    echo Docker image not found. Building first...
    call docker-build.bat
    if errorlevel 1 exit /b 1
)

echo Starting Docker container...
echo Access the app at: http://localhost:8501
echo Press Ctrl+C to stop the application
echo.

docker-compose up

echo.
echo Application stopped.
pause
