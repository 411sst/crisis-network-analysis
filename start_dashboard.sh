#!/bin/bash

# Quick Start Script for Crisis Network Analysis Dashboard
# For Final Review Presentation

echo "======================================"
echo "🌐 Crisis Network Analysis Dashboard"
echo "======================================"
echo ""

# Navigate to project directory
cd "/home/shrish/Desktop/Shrish/Social Computing Mini Project/crisis-network-analysis"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import streamlit" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

echo ""
echo "✅ Environment ready!"
echo ""
echo "🚀 Starting dashboard..."
echo "📍 URL: http://localhost:8501"
echo "🛑 Press Ctrl+C to stop"
echo ""
echo "======================================"
echo ""

# Run the dashboard
python run_dashboard.py
