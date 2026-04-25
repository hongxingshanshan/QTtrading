@echo off
echo Starting QTtrading Frontend Development Server...
cd /d "%~dp0"
cd frontend
call npm install
call npm run dev
