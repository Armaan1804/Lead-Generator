import subprocess
import webbrowser
import time
import os
import sys
from pathlib import Path

def launch_website_and_dashboard():
    """Launch both the website and Streamlit dashboard"""
    
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    
    print("🚀 Starting Caprae Lead Generator...")
    
    # Start the website (simple HTTP server)
    website_dir = Path(__file__).parent
    print(f"📁 Website directory: {website_dir}")
    
    try:
        # Start simple HTTP server for the website
        print("🌐 Starting website server...")
        website_process = subprocess.Popen([
            sys.executable, "-m", "http.server", "8000"
        ], cwd=website_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for the server to start
        time.sleep(2)
        
        # Open the website
        webbrowser.open("http://localhost:8000")
        print("✅ Website launched at: http://localhost:8000")
        
        # Start Streamlit dashboard
        print("📊 Starting Streamlit dashboard...")
        dashboard_process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "app.py", "--server.port=8501"
        ], cwd=project_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for Streamlit to start
        time.sleep(3)
        print("✅ Dashboard launched at: http://localhost:8501")
        
        print("\n🎉 Both services are running!")
        print("📱 Website: http://localhost:8000")
        print("📊 Dashboard: http://localhost:8501")
        print("\n⚠️  Press Ctrl+C to stop both services")
        
        # Keep the script running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping services...")
            website_process.terminate()
            dashboard_process.terminate()
            print("✅ Services stopped successfully!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    launch_website_and_dashboard()