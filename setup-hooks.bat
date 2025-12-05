@echo off
REM Setup script to install Git hooks for automatic dependency management (Windows)

echo 🔧 Setting up Git hooks...

REM Copy post-merge hook
copy hooks\post-merge .git\hooks\post-merge

echo ✅ Git hooks installed!
echo.
echo From now on, when you run 'git pull', dependencies will automatically
echo install if requirements.txt or package.json have changed.
echo.
pause
