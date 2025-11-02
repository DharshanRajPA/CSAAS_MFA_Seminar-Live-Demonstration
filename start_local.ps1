# MFA Demo Start Script for Windows PowerShell
# This script sets up the environment and starts the MFA demo server

Write-Host "🚀 Starting MFA Demo Setup..." -ForegroundColor Green

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.7+ from https://python.org" -ForegroundColor Red
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path ".venv")) {
    Write-Host "📦 Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "📥 Installing dependencies..." -ForegroundColor Yellow
pip install -r backend-minimal-flask\requirements.txt

# Initialize database
Write-Host "🗄️ Initializing database..." -ForegroundColor Yellow
python backend-minimal-flask\db_init.py

# Start the server
Write-Host "🌐 Starting MFA Demo Server..." -ForegroundColor Green
Write-Host "📍 Server will be available at: http://localhost:5000" -ForegroundColor Cyan
Write-Host "📍 Frontend will be served at: http://localhost:5000" -ForegroundColor Cyan
Write-Host "📍 Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python backend-minimal-flask\server.py
