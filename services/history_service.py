from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import logging
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="History Service", version="1.0.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try MongoDB, fallback to file storage
USE_MONGODB = False
HISTORY_FILE = "chat_history.json"

# Only try MongoDB if explicitly configured
MONGO_URL = os.getenv("MONGO_URL")
if MONGO_URL:
    try:
        from pymongo import MongoClient
        client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=2000, connectTimeoutMS=2000)
        # Test connection with shorter timeout
        client.server_info()
        db = client.ai_assistant
        collection = db.chat_history
        USE_MONGODB = True
        logger.info("✅ Using MongoDB for history storage")
    except Exception as e:
        logger.info(f"MongoDB connection failed, using file storage: {str(e)[:100]}...")
        USE_MONGODB = False
else:
    logger.info("📁 Using file-based storage for history (MongoDB not configured)")

# Initialize file-based storage
if not USE_MONGODB:
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'w') as f:
            json.dump([], f)

class HistoryEntry(BaseModel):
    chat_id: str
    message: str
    sender: str  # "user" or "assistant"
    timestamp: Optional[datetime] = None

class HistoryResponse(BaseModel):
    chat_id: str
    messages: List[dict]

@app.post("/history")
async def save_message(entry: HistoryEntry):
    """Save a message to chat history"""
    try:
        # Set timestamp if not provided
        if not entry.timestamp:
            entry.timestamp = datetime.utcnow()
        
        # Convert to dict
        message_doc = entry.dict()
        
        if USE_MONGODB:
            result = collection.insert_one(message_doc)
            return {"message": "Message saved", "id": str(result.inserted_id)}
        else:
            # File-based storage
            message_doc["timestamp"] = message_doc["timestamp"].isoformat()
            message_doc["id"] = f"{entry.chat_id}_{len(load_history_from_file())}"
            
            history = load_history_from_file()
            history.append(message_doc)
            save_history_to_file(history)
            
            return {"message": "Message saved", "id": message_doc["id"]}
    
    except Exception as e:
        logger.error(f"Error saving message: {e}")
        raise HTTPException(status_code=500, detail="Failed to save message")

@app.get("/history/{chat_id}", response_model=HistoryResponse)
async def get_chat_history(chat_id: str, limit: int = 50):
    """Get chat history for a specific chat_id"""
    try:
        if USE_MONGODB:
            # Query messages for the chat_id, sorted by timestamp
            cursor = collection.find(
                {"chat_id": chat_id}
            ).sort("timestamp", 1).limit(limit)
            
            messages = []
            for doc in cursor:
                # Convert ObjectId to string and format timestamp
                doc["_id"] = str(doc["_id"])
                if doc.get("timestamp"):
                    doc["timestamp"] = doc["timestamp"].isoformat()
                messages.append(doc)
        else:
            # File-based storage
            history = load_history_from_file()
            messages = [msg for msg in history if msg["chat_id"] == chat_id]
            messages = sorted(messages, key=lambda x: x.get("timestamp", ""))[:limit]
        
        return HistoryResponse(chat_id=chat_id, messages=messages)
    
    except Exception as e:
        logger.error(f"Error fetching chat history: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch chat history")

@app.get("/history/{chat_id}/recent")
async def get_recent_messages(chat_id: str, count: int = 10):
    """Get recent messages for context"""
    try:
        if USE_MONGODB:
            cursor = collection.find(
                {"chat_id": chat_id}
            ).sort("timestamp", -1).limit(count)
            
            messages = []
            for doc in cursor:
                messages.append({
                    "message": doc["message"],
                    "sender": doc["sender"],
                    "timestamp": doc["timestamp"].isoformat() if doc.get("timestamp") else None
                })
            
            # Reverse to get chronological order
            messages.reverse()
        else:
            # File-based storage
            history = load_history_from_file()
            chat_messages = [msg for msg in history if msg["chat_id"] == chat_id]
            chat_messages = sorted(chat_messages, key=lambda x: x.get("timestamp", ""), reverse=True)[:count]
            
            messages = []
            for msg in reversed(chat_messages):  # Reverse to get chronological order
                messages.append({
                    "message": msg["message"],
                    "sender": msg["sender"],
                    "timestamp": msg.get("timestamp")
                })
        
        return {"messages": messages}
    
    except Exception as e:
        logger.error(f"Error fetching recent messages: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch recent messages")

@app.delete("/history/{chat_id}")
async def delete_chat_history(chat_id: str):
    """Delete all messages for a chat_id"""
    try:
        if USE_MONGODB:
            result = collection.delete_many({"chat_id": chat_id})
            return {"message": f"Deleted {result.deleted_count} messages"}
        else:
            # File-based storage
            history = load_history_from_file()
            original_count = len(history)
            history = [msg for msg in history if msg["chat_id"] != chat_id]
            deleted_count = original_count - len(history)
            save_history_to_file(history)
            return {"message": f"Deleted {deleted_count} messages"}
    
    except Exception as e:
        logger.error(f"Error deleting chat history: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete chat history")

@app.get("/stats")
async def get_stats():
    """Get database statistics"""
    try:
        if USE_MONGODB:
            total_messages = collection.count_documents({})
            unique_chats = len(collection.distinct("chat_id"))
        else:
            # File-based storage
            history = load_history_from_file()
            total_messages = len(history)
            unique_chats = len(set(msg["chat_id"] for msg in history))
        
        return {
            "total_messages": total_messages,
            "unique_chats": unique_chats,
            "using_mongodb": USE_MONGODB
        }
    
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get stats")

def load_history_from_file():
    """Load chat history from JSON file"""
    try:
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_history_to_file(history):
    """Save chat history to JSON file"""
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "using_mongodb": USE_MONGODB}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)