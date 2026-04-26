"""PrecarityScan - Run this file to start the application"""

import subprocess
import webbrowser
import time
import os
import sys

def check_data_file():
    """Check if sample data exists"""
    data_path = os.path.join(os.path.dirname(__file__), "data", "sample_data.csv")
    if not os.path.exists(data_path):
        print("❌ Error: data/sample_data.csv not found!")
        print("Please create the file first.")
        return False
    print("✅ Data file found")
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Starting PrecarityScan...")
    print("=" * 50)
    
    # Check data file
    if not check_data_file():
        sys.exit(1)
    
    # Open browser to Streamlit (which has built-in login)
    print("📱 Opening dashboard in browser...")
    time.sleep(2)
    webbrowser.open("http://localhost:8501")
    
    # Start Streamlit (login is INSIDE Streamlit)
    print("🔍 Starting dashboard...")
    print("📍 Login at: http://localhost:8501")
    print("=" * 50)
    print("Demo Credentials:")
    print("  researcher / password123")
    print("  policymaker / password123")
    print("  worker1 / password123")
    print("=" * 50)
    
    # Run streamlit
    subprocess.run(["streamlit", "run", "app.py", "--server.port=8501"])