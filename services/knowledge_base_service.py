from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import logging
import os
from typing import List
import uuid
import hashlib
import requests
import json
import re

app = FastAPI(title="Knowledge Base Service", version="1.0.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Gemini API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCgVAm2hJGrcc-vKi3jNMDswzrgykmw3Ks")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

# Try to import dependencies with fallbacks
try:
    import chromadb
    from sentence_transformers import SentenceTransformer
    
    # Initialize ChromaDB and embedding model
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    collection = chroma_client.get_or_create_collection(name="knowledge_base")
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    USE_EMBEDDINGS = True
    logger.info("Using ChromaDB with sentence transformers")
    
except ImportError as e:
    logger.warning(f"Could not import embedding dependencies: {e}")
    logger.info("Falling back to simple text storage")
    USE_EMBEDDINGS = False
    
    # Simple in-memory storage as fallback
    document_store = []

class QueryRequest(BaseModel):
    text: str

class QueryResponse(BaseModel):
    answer: str
    relevant: bool
    confidence: float

class IngestResponse(BaseModel):
    message: str
    documents_added: int

@app.post("/ingest", response_model=IngestResponse)
async def ingest_documents(files: List[UploadFile] = File(...)):
    """Ingest documents into the knowledge base"""
    documents_added = 0
    
    try:
        for file in files:
            content = await file.read()
            text_content = content.decode('utf-8')
            
            # Split content into chunks (simple approach)
            chunks = split_text(text_content)
            
            if USE_EMBEDDINGS:
                # Use ChromaDB with embeddings
                for i, chunk in enumerate(chunks):
                    doc_id = f"{file.filename}_{i}_{uuid.uuid4()}"
                    embedding = embedding_model.encode([chunk])[0].tolist()
                    
                    collection.add(
                        embeddings=[embedding],
                        documents=[chunk],
                        metadatas=[{"filename": file.filename, "chunk_id": i}],
                        ids=[doc_id]
                    )
                    documents_added += 1
            else:
                # Use simple text storage
                for i, chunk in enumerate(chunks):
                    doc_entry = {
                        "id": f"{file.filename}_{i}_{uuid.uuid4()}",
                        "text": chunk,
                        "filename": file.filename,
                        "chunk_id": i
                    }
                    document_store.append(doc_entry)
                    documents_added += 1
        
        return IngestResponse(
            message=f"Successfully ingested {len(files)} files",
            documents_added=documents_added
        )
    
    except Exception as e:
        logger.error(f"Error ingesting documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to ingest documents")

@app.get("/query", response_model=QueryResponse)
async def query_knowledge_base(text: str):
    """Query the knowledge base using semantic search or simple text matching"""
    try:
        if USE_EMBEDDINGS:
            # Generate embedding for the query
            query_embedding = embedding_model.encode([text])[0].tolist()
            
            # Search in ChromaDB
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=3
            )
            
            if not results['documents'] or not results['documents'][0]:
                return QueryResponse(
                    answer="No relevant information found in knowledge base.",
                    relevant=False,
                    confidence=0.0
                )
            
            # Get the best match
            best_match = results['documents'][0][0]
            confidence = 1.0 - results['distances'][0][0] if results['distances'][0] else 0.0
            
            # Consider relevant if confidence is above threshold
            is_relevant = confidence > 0.4  # Increased threshold for better precision
            
            if is_relevant:
                # Enhance with Gemini if available
                enhanced_answer = await enhance_answer_with_gemini(text, best_match)
                final_answer = enhanced_answer if enhanced_answer else best_match
                
                # Double-check if the enhanced answer is actually useful
                if (final_answer.startswith("No relevant information") or 
                    final_answer.startswith("This document does not contain") or
                    len(final_answer.strip()) < 20):
                    is_relevant = False
                    final_answer = "No sufficiently relevant information found in knowledge base."
            else:
                final_answer = "No sufficiently relevant information found in knowledge base."
            
            return QueryResponse(
                answer=final_answer,
                relevant=is_relevant,
                confidence=confidence if is_relevant else 0.0
            )
        else:
            # Simple text matching fallback
            query_lower = text.lower()
            best_match = None
            best_score = 0
            
            for doc in document_store:
                doc_text = doc['text'].lower()
                # Simple keyword matching score
                words = query_lower.split()
                score = sum(1 for word in words if word in doc_text) / len(words) if words else 0
                
                if score > best_score:
                    best_score = score
                    best_match = doc['text']
            
            if best_match and best_score > 0.3:  # Increased threshold
                # Enhance with Gemini if available
                enhanced_answer = await enhance_answer_with_gemini(text, best_match)
                final_answer = enhanced_answer if enhanced_answer else best_match
                
                # Double-check if the enhanced answer is actually useful
                is_relevant = not (
                    final_answer.startswith("No relevant information") or 
                    final_answer.startswith("This document does not contain") or
                    len(final_answer.strip()) < 20
                )
                
                if is_relevant:
                    return QueryResponse(
                        answer=final_answer,
                        relevant=True,
                        confidence=best_score
                    )
            
            return QueryResponse(
                answer="No relevant information found in knowledge base.",
                relevant=False,
                confidence=0.0
            )
    
    except Exception as e:
        logger.error(f"Error querying knowledge base: {e}")
        raise HTTPException(status_code=500, detail="Failed to query knowledge base")

@app.get("/stats")
async def get_stats():
    """Get knowledge base statistics"""
    try:
        if USE_EMBEDDINGS:
            count = collection.count()
        else:
            count = len(document_store)
        
        return {
            "total_documents": count,
            "using_embeddings": USE_EMBEDDINGS
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get stats")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "using_embeddings": USE_EMBEDDINGS}

async def enhance_answer_with_gemini(query: str, document_content: str) -> str:
    """Enhance knowledge base answers using Gemini API"""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your-gemini-api-key":
        return None
    
    try:
        prompt = f"""Based on this document content, provide a clear and direct answer to the question: "{query}"

Document content: {document_content}

Please provide a helpful, accurate answer based on the document. Keep it concise (2-3 sentences) and directly address the question. If the document doesn't contain relevant information, say so."""

        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers=headers,
            json=payload,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("candidates") and data["candidates"][0].get("content"):
                answer = data["candidates"][0]["content"]["parts"][0]["text"]
                return clean_text(answer)
        
        return None
    
    except Exception as e:
        logger.error(f"Gemini enhancement failed: {e}")
        return None

def clean_text(text: str) -> str:
    """Clean and format text response"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Limit length
    if len(text) > 500:
        text = text[:497] + "..."
    
    return text

def split_text(text: str, chunk_size: int = 500) -> List[str]:
    """Simple text splitting into chunks"""
    words = text.split()
    chunks = []
    current_chunk = []
    current_size = 0
    
    for word in words:
        current_chunk.append(word)
        current_size += len(word) + 1  # +1 for space
        
        if current_size >= chunk_size:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_size = 0
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)