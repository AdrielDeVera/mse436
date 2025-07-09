#!/usr/bin/env python3
"""
Quick launcher for the Stock IDSS Enhanced Dashboard
Run this script from the project root to launch the dashboard
"""

import subprocess
import sys
import os

def main():
    print("🚀 Launching Stock IDSS Enhanced Dashboard...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("app/enhanced_dashboard.py"):
        print("❌ Error: enhanced_dashboard.py not found!")
        print("Please run this script from the stock_idss project root directory.")
        sys.exit(1)
    
    # Change to app directory
    os.chdir("app")
    
    print("📊 Starting Streamlit server...")
    print("🌐 Dashboard will open in your browser automatically")
    print("📱 If it doesn't open, go to: http://localhost:8501")
    print("=" * 50)
    print("💡 Tips:")
    print("   - Try tickers like: AAPL, MSFT, GOOGL, TSLA, NVDA")
    print("   - Enable 'Include Fundamental Analysis' for best results")
    print("   - Use date range: 2023-01-01 to 2024-01-01")
    print("=" * 50)
    
    try:
        # Launch the enhanced dashboard
        subprocess.run([sys.executable, "-m", "streamlit", "run", "enhanced_dashboard.py"])
    except KeyboardInterrupt:
        print("\n👋 Dashboard closed by user")
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")
        print("💡 Make sure you have streamlit installed: pip install streamlit")

if __name__ == "__main__":
    main() 