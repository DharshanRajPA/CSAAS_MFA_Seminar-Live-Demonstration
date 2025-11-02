#!/usr/bin/env bash
# MFA Demo Start Script for Linux/Mac
# This script sets up the environment and starts the MFA demo server

echo "🚀 Starting MFA Demo Setup..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.7+ from https://python.org"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r backend-minimal-flask/requirements.txt

# Initialize database
echo "🗄️ Initializing database..."
python backend-minimal-flask/db_init.py

# Start the server
echo "🌐 Starting MFA Demo Server..."
echo "📍 Server will be available at: http://localhost:5000"
echo "📍 Frontend will be served at: http://localhost:5000"
echo "📍 Press Ctrl+C to stop the server"
echo ""

python backend-minimal-flask/server.py
