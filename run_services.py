#!/usr/bin/env python3
"""
Script to run all microservices for the AI Assistant including Web GUI
"""

import subprocess
import sys
import time
import signal
import os
from multiprocessing import Process

def run_service(service_name, port, is_web_gui=False):
    """Run a single service"""
    print(f"Starting {service_name} on port {port}...")
    try:
        if is_web_gui:
            subprocess.run([
                sys.executable, "-m", "uvicorn", 
                "web_gui:app",
                "--host", "0.0.0.0",
                "--port", str(port),
                "--reload"
            ])
        else:
            subprocess.run([
                sys.executable, "-m", "uvicorn", 
                f"services.{service_name}:app",
                "--host", "0.0.0.0",
                "--port", str(port),
                "--reload"
            ])
    except KeyboardInterrupt:
        print(f"\n{service_name} stopped.")

def main():
    """Main function to start all services"""
    services = [
        ("chat_service", 8000, False),
        ("knowledge_base_service", 8001, False),
        ("search_service", 8002, False),
        ("history_service", 8003, False),
        ("web_gui", 8080, True)
    ]
    
    processes = []
    
    try:
        # Start all services
        for service_name, port, is_web_gui in services:
            process = Process(target=run_service, args=(service_name, port, is_web_gui))
            process.start()
            processes.append(process)
            time.sleep(2)  # Stagger startup
        
        print("\n" + "="*60)
        print("🚀 AI Assistant System is running!")
        print("="*60)
        print("🌐 Web Interface:      http://localhost:8080")
        print("📊 Admin Panel:        http://localhost:8080/admin")
        print("="*60)
        print("API Services:")
        print("💬 Chat Service:       http://localhost:8000")
        print("📚 Knowledge Base:     http://localhost:8001")
        print("🔍 Search Service:     http://localhost:8002")
        print("📝 History Service:    http://localhost:8003")
        print("="*60)
        print("Press Ctrl+C to stop all services")
        print("="*60)
        
        # Wait for all processes
        for process in processes:
            process.join()
            
    except KeyboardInterrupt:
        print("\n\nShutting down all services...")
        for process in processes:
            process.terminate()
        
        # Wait for clean shutdown
        for process in processes:
            process.join(timeout=5)
            if process.is_alive():
                process.kill()
        
        print("All services stopped.")

if __name__ == "__main__":
    main()