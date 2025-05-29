# Khoya Paya Face Recognition App Startup Script
Write-Host "Starting Khoya Paya Face Recognition App..." -ForegroundColor Green
Write-Host "Make sure your virtual environment is activated!" -ForegroundColor Yellow
Write-Host ""

# Check if virtual environment is activated
if ($env:VIRTUAL_ENV) {
    Write-Host "Virtual environment detected: $env:VIRTUAL_ENV" -ForegroundColor Green
} else {
    Write-Host "Warning: No virtual environment detected. Consider activating .venv" -ForegroundColor Red
}

Write-Host ""
Write-Host "Starting Streamlit app on port 8502..." -ForegroundColor Cyan
streamlit run main.py --server.port 8502
