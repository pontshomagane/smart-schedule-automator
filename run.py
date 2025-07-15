#!/usr/bin/env python3
"""
Smart Schedule Automator - Startup Script
Installs dependencies and runs the application
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    return True

def run_app():
    """Run the application"""
    print("🚀 Starting Smart Schedule Automator...")
    try:
        subprocess.run([sys.executable, "simple_main.py"])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Failed to start application: {e}")

def main():
    print("🎓 Smart Schedule Automator")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists("simple_main.py"):
        print("❌ Error: simple_main.py not found. Please run this script from the project directory.")
        return
    
    # Install dependencies
    if not install_dependencies():
        return
    
    # Run the application
    run_app()

if __name__ == "__main__":
    main() 