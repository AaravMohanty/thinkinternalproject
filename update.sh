#!/bin/bash

# Update script for THINKInternalProject
# Run this after pulling to install all dependencies automatically

echo "🔄 Updating THINKInternalProject dependencies..."
echo ""

# Install backend dependencies
echo "📦 Installing Python dependencies..."
cd backend
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✅ Python dependencies installed"
else
    echo "⚠️  requirements.txt not found, skipping Python dependencies"
fi
cd ..

echo ""

# Install frontend dependencies
echo "📦 Installing Node.js dependencies..."
cd frontend
if [ -f "package.json" ]; then
    npm install
    echo "✅ Node.js dependencies installed"
else
    echo "⚠️  package.json not found, skipping Node.js dependencies"
fi
cd ..

echo ""
echo "✅ All dependencies updated successfully!"
echo ""
echo "To start the application:"
echo "  Backend:  cd backend && python app.py"
echo "  Frontend: cd frontend && npm run dev"
