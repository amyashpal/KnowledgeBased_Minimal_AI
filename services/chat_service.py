from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import asyncio
from typing import Optional
import logging

app = FastAPI(title="Chat Service", version="1.0.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Service URLs
KNOWLEDGE_BASE_URL = "http://localhost:8001"
SEARCH_SERVICE_URL = "http://localhost:8002"
HISTORY_SERVICE_URL = "http://localhost:8003"

class ChatRequest(BaseModel):
    chat_id: str
    message: str

class ChatResponse(BaseModel):
    chat_id: str
    response: str
    source: str  # "knowledge_base", "search", or "fallback"

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint that orchestrates the response"""
    try:
        # First, try knowledge base
        kb_response = await query_knowledge_base(request.message)
        
        # Check if knowledge base has relevant and useful information
        kb_has_answer = (
            kb_response and 
            kb_response.get("relevant", False) and 
            kb_response.get("confidence", 0) > 0.3 and
            kb_response.get("answer") and
            not kb_response.get("answer").startswith("No relevant information") and
            not kb_response.get("answer").startswith("This document does not contain") and
            len(kb_response.get("answer", "").strip()) > 20
        )
        
        if kb_has_answer:
            response_text = kb_response["answer"]
            source = "knowledge_base"
            logger.info(f"✅ Knowledge base answered: {request.message[:50]}...")
        else:
            # Fallback to web search
            logger.info(f"🔍 Falling back to search for: {request.message[:50]}...")
            search_response = await query_search_service(request.message)
            response_text = search_response.get("answer", "I'm sorry, I couldn't find relevant information.")
            source = "search" if search_response.get("answer") else "fallback"
        
        # Save to history
        await save_to_history(request.chat_id, request.message, response_text)
        
        return ChatResponse(
            chat_id=request.chat_id,
            response=response_text,
            source=source
        )
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/chat/{chat_id}")
async def get_chat_history(chat_id: str):
    """Get chat history for a specific chat_id"""
    try:
        response = requests.get(f"{HISTORY_SERVICE_URL}/history/{chat_id}")
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=404, detail="Chat history not found")
    except requests.RequestException as e:
        logger.error(f"Error fetching chat history: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch chat history")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "chat"}

async def query_knowledge_base(query: str) -> Optional[dict]:
    """Query the knowledge base service"""
    try:
        response = requests.get(f"{KNOWLEDGE_BASE_URL}/query", params={"text": query})
        if response.status_code == 200:
            return response.json()
        return None
    except requests.RequestException as e:
        logger.error(f"Knowledge base query failed: {e}")
        return None

async def query_search_service(query: str) -> Optional[dict]:
    """Query the search service"""
    try:
        response = requests.get(f"{SEARCH_SERVICE_URL}/search", params={"query": query})
        if response.status_code == 200:
            return response.json()
        return None
    except requests.RequestException as e:
        logger.error(f"Search service query failed: {e}")
        return None

async def save_to_history(chat_id: str, message: str, response: str):
    """Save conversation to history service"""
    try:
        # Save user message
        requests.post(f"{HISTORY_SERVICE_URL}/history", json={
            "chat_id": chat_id,
            "message": message,
            "sender": "user",
            "timestamp": None  # Will be set by history service
        })
        
        # Save assistant response
        requests.post(f"{HISTORY_SERVICE_URL}/history", json={
            "chat_id": chat_id,
            "message": response,
            "sender": "assistant",
            "timestamp": None
        })
    except requests.RequestException as e:
        logger.error(f"Failed to save to history: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)