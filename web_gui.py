#!/usr/bin/env python3
"""
Web GUI for AI Assistant - Comprehensive Interface
"""

from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests
import json
import os
from typing import List
import uvicorn

app = FastAPI(title="AI Assistant Web GUI", version="1.0.0")

# Create static and templates directories
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Service URLs
CHAT_URL = "http://localhost:8000"
KB_URL = "http://localhost:8001"
SEARCH_URL = "http://localhost:8002"
HISTORY_URL = "http://localhost:8003"

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main chat interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request):
    """Admin panel for system management"""
    return templates.TemplateResponse("admin.html", {"request": request})

@app.post("/api/chat")
async def chat_api(request: Request):
    """Chat API endpoint"""
    data = await request.json()
    chat_id = data.get("chat_id", "default")
    message = data.get("message", "")
    
    try:
        response = requests.post(f"{CHAT_URL}/chat", json={
            "chat_id": chat_id,
            "message": message
        }, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Chat service error: {response.status_code}"}
    except Exception as e:
        return {"error": f"Connection error: {str(e)}"}

@app.get("/api/history/{chat_id}")
async def get_history(chat_id: str):
    """Get chat history"""
    try:
        response = requests.get(f"{CHAT_URL}/chat/{chat_id}", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"messages": []}
    except Exception as e:
        return {"messages": [], "error": str(e)}

@app.post("/api/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    """Upload documents to knowledge base"""
    try:
        # Prepare files for knowledge base service
        file_data = []
        for file in files:
            content = await file.read()
            file_data.append(("files", (file.filename, content, file.content_type)))
        
        response = requests.post(f"{KB_URL}/ingest", files=file_data, timeout=60)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Upload failed: {response.status_code}"}
    except Exception as e:
        return {"error": f"Upload error: {str(e)}"}

@app.get("/api/stats")
async def get_system_stats():
    """Get system statistics"""
    stats = {}
    
    services = [
        ("chat", f"{CHAT_URL}/health"),
        ("knowledge_base", f"{KB_URL}/stats"),
        ("search", f"{SEARCH_URL}/health"),
        ("history", f"{HISTORY_URL}/stats")
    ]
    
    for service_name, url in services:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                stats[service_name] = {
                    "status": "healthy",
                    "data": response.json()
                }
            else:
                stats[service_name] = {
                    "status": "error",
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            stats[service_name] = {
                "status": "offline",
                "error": str(e)
            }
    
    return stats

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)