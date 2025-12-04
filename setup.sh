#!/bin/bash

# Setup script for Render deployment

echo "🔧 Setting up application..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Set Python path
export PYTHONPATH="/app:$PYTHONPATH"

echo "✅ Setup completed!"