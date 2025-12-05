#!/bin/bash
# Setup script to install Git hooks for automatic dependency management

echo "🔧 Setting up Git hooks..."

# Copy post-merge hook
cp hooks/post-merge .git/hooks/post-merge
chmod +x .git/hooks/post-merge

echo "✅ Git hooks installed!"
echo ""
echo "From now on, when you run 'git pull', dependencies will automatically"
echo "install if requirements.txt or package.json have changed."
echo ""
