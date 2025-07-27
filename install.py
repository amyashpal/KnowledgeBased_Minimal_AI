#!/usr/bin/env python3
"""
Installation script for AI Assistant microservices
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("🚀 Installing AI Assistant Dependencies")
    print("="*50)
    
    # Core dependencies (required)
    core_packages = [
        "fastapi>=0.100.0",
        "uvicorn[standard]>=0.20.0", 
        "pydantic>=2.0.0",
        "requests>=2.28.0",
        "beautifulsoup4>=4.11.0",
        "python-multipart>=0.0.5"
    ]
    
    print("Installing core dependencies...")
    for package in core_packages:
        print(f"  Installing {package}...")
        if install_package(package):
            print(f"  ✅ {package} installed successfully")
        else:
            print(f"  ❌ Failed to install {package}")
            return False
    
    # Optional dependencies
    print("\nInstalling optional dependencies...")
    
    # Try to install MongoDB driver
    print("  Installing MongoDB support...")
    if install_package("pymongo>=4.0.0"):
        print("  ✅ MongoDB support installed")
    else:
        print("  ⚠️  MongoDB support failed - will use file storage")
    
    # Try to install vector embedding support
    print("  Installing vector embedding support...")
    embedding_packages = ["torch>=1.13.0", "sentence-transformers>=2.2.0", "chromadb>=0.4.0"]
    
    embedding_success = True
    for package in embedding_packages:
        if not install_package(package):
            embedding_success = False
            break
    
    if embedding_success:
        print("  ✅ Vector embedding support installed")
    else:
        print("  ⚠️  Vector embedding support failed - will use simple text matching")
    
    print("\n" + "="*50)
    print("✅ Installation completed!")
    print("="*50)
    print("You can now start the services with:")
    print("  python run_services.py")
    print("\nOr test the system with:")
    print("  python test_system.py")

if __name__ == "__main__":
    main()