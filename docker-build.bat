@echo off
echo Building Khoya Paya Docker Image...
echo.

REM Check if Docker is available
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed or not running.
    echo Please install Docker Desktop and ensure it's running.
    echo Download from: https://docs.docker.com/desktop/install/windows-install/
    pause
    exit /b 1
)

echo Docker found. Starting build...
echo This may take several minutes on first build...
echo.

docker build -t khoya-paya:latest .

if errorlevel 1 (
    echo.
    echo BUILD FAILED!
    echo Common solutions:
    echo - Ensure Docker Desktop has sufficient memory (4GB+)
    echo - Check internet connection for downloading dependencies
    echo - Try: docker system prune (to clean up)
    pause
    exit /b 1
) else (
    echo.
    echo BUILD SUCCESSFUL!
    echo.
    echo Next steps:
    echo - Run: docker-start.bat (to start the application)
    echo - Run: docker-compose up (manual start)
    echo - Access: http://localhost:8501 (when running)
    echo.
    pause
)
