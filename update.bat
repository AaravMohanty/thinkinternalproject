@echo off
REM Update script for THINKInternalProject (Windows)
REM Run this after pulling to install all dependencies automatically

echo 🔄 Updating THINKInternalProject dependencies...
echo.

REM Install backend dependencies
echo 📦 Installing Python dependencies...
cd backend
if exist requirements.txt (
    pip install -r requirements.txt
    echo ✅ Python dependencies installed
) else (
    echo ⚠️  requirements.txt not found, skipping Python dependencies
)
cd ..

echo.

REM Install frontend dependencies
echo 📦 Installing Node.js dependencies...
cd frontend
if exist package.json (
    npm install
    echo ✅ Node.js dependencies installed
) else (
    echo ⚠️  package.json not found, skipping Node.js dependencies
)
cd ..

echo.
echo ✅ All dependencies updated successfully!
echo.
echo To start the application:
echo   Backend:  cd backend ^&^& python app.py
echo   Frontend: cd frontend ^&^& npm run dev
pause
