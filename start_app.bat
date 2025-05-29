@echo off
cd /d "%~dp0"
echo Starting Khoya Paya Face Recognition App...
echo.
echo Make sure your virtual environment is activated!
echo.
streamlit run main.py --server.port 8502
pause
