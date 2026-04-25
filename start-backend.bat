@echo off
echo Starting QTtrading Backend Server...
cd /d "%~dp0"
cd backend
call venv\Scripts\activate.bat 2>nul || echo Virtual environment not found, using system Python
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
