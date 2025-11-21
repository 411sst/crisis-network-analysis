#!/usr/bin/env python3
"""
Quick launcher for the Crisis Network Analysis Dashboard

Usage:
    python run_dashboard.py
"""

import subprocess
import sys
from pathlib import Path

def main():
    # Get dashboard directory
    dashboard_dir = Path(__file__).parent / 'dashboard'

    if not dashboard_dir.exists():
        print("❌ Dashboard directory not found!")
        print(f"Expected: {dashboard_dir}")
        return 1

    print("🚀 Starting Crisis Network Analysis Dashboard...")
    print(f"📁 Dashboard location: {dashboard_dir}")
    print("\n" + "="*60)
    print("🌐 Dashboard will open in your browser")
    print("📊 Access at: http://localhost:8501")
    print("🛑 Press Ctrl+C to stop the server")
    print("="*60 + "\n")

    try:
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            str(dashboard_dir / "Home.py"),
            "--server.port=8501",
            "--server.headless=false",
            "--browser.gatherUsageStats=false"
        ])

    except KeyboardInterrupt:
        print("\n\n👋 Dashboard stopped. Goodbye!")
        return 0

    except Exception as e:
        print(f"\n❌ Error starting dashboard: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure Streamlit is installed: pip install streamlit")
        print("2. Check requirements: pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
