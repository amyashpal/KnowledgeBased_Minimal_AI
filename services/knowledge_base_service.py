from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import logging
import os
from typing import List, Optional
import uuid
import hashlib
import requests
import json
import re
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Knowledge Base Service", version="1.0.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.15"))

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
    
    # Simple file-based storage as fallback
    STORAGE_FILE = "knowledge_base_storage.json"
    document_store = []
    
    # Load existing documents from file on startup
    def load_documents_from_file():
        global document_store
        try:
            if os.path.exists(STORAGE_FILE):
                with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
                    document_store = json.load(f)
                logger.info(f"Loaded {len(document_store)} documents from storage file")
            else:
                document_store = []
                logger.info("No existing storage file found, starting with empty knowledge base")
        except Exception as e:
            logger.error(f"Error loading documents from file: {e}")
            document_store = []
    
    def save_documents_to_file():
        try:
            with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
                json.dump(document_store, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(document_store)} documents to storage file")
        except Exception as e:
            logger.error(f"Error saving documents to file: {e}")
    
    # Load documents on startup
    load_documents_from_file()

class QueryRequest(BaseModel):
    text: str

class QueryResponse(BaseModel):
    answer: str
    relevant: bool
    confidence: float
    source_documents: Optional[List[str]] = []
    processing_method: str = "unknown"

class IngestResponse(BaseModel):
    message: str
    documents_added: int
    duplicates_skipped: int = 0
    files_processed: List[str] = []

@app.post("/ingest", response_model=IngestResponse)
async def ingest_documents(files: List[UploadFile] = File(...)):
    """Ingest documents into the knowledge base with deduplication"""
    documents_added = 0
    duplicates_skipped = 0
    files_processed = []
    
    try:
        for file in files:
            logger.info(f"Processing file: {file.filename}")
            content = await file.read()
            text_content = content.decode('utf-8')
            
            # Create content hash for deduplication
            content_hash = hashlib.md5(text_content.encode()).hexdigest()
            
            # Split content into chunks with better overlap
            chunks = split_text_with_overlap(text_content)
            logger.info(f"Split {file.filename} into {len(chunks)} chunks")
            
            if USE_EMBEDDINGS:
                # Check for existing content by hash in metadata
                existing_docs = collection.get(where={"content_hash": content_hash})
                if existing_docs['ids']:
                    logger.info(f"Skipping duplicate file: {file.filename}")
                    duplicates_skipped += 1
                    continue
                
                # Use ChromaDB with embeddings
                for i, chunk in enumerate(chunks):
                    doc_id = f"{file.filename}_{i}_{uuid.uuid4()}"
                    embedding = embedding_model.encode([chunk])[0].tolist()
                    
                    metadata = {
                        "filename": file.filename,
                        "chunk_id": i,
                        "content_hash": content_hash,
                        "upload_timestamp": datetime.now().isoformat(),
                        "chunk_length": len(chunk)
                    }
                    
                    collection.add(
                        embeddings=[embedding],
                        documents=[chunk],
                        metadatas=[metadata],
                        ids=[doc_id]
                    )
                    documents_added += 1
            else:
                # Check for duplicates in simple storage
                existing_hashes = [doc.get('content_hash') for doc in document_store]
                if content_hash in existing_hashes:
                    logger.info(f"Skipping duplicate file: {file.filename}")
                    duplicates_skipped += 1
                    continue
                
                # Use simple text storage
                for i, chunk in enumerate(chunks):
                    doc_entry = {
                        "id": f"{file.filename}_{i}_{uuid.uuid4()}",
                        "text": chunk,
                        "filename": file.filename,
                        "chunk_id": i,
                        "content_hash": content_hash,
                        "upload_timestamp": datetime.now().isoformat(),
                        "chunk_length": len(chunk)
                    }
                    document_store.append(doc_entry)
                    documents_added += 1
                
                # Save to file after adding documents
                save_documents_to_file()
            
            files_processed.append(file.filename)
        
        # Save to file after processing all files (for embeddings mode too)
        if not USE_EMBEDDINGS:
            save_documents_to_file()
        
        logger.info(f"Ingestion complete: {documents_added} chunks added, {duplicates_skipped} duplicates skipped")
        
        return IngestResponse(
            message=f"Successfully processed {len(files)} files",
            documents_added=documents_added,
            duplicates_skipped=duplicates_skipped,
            files_processed=files_processed
        )
    
    except Exception as e:
        logger.error(f"Error ingesting documents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to ingest documents: {str(e)}")

@app.get("/query", response_model=QueryResponse)
async def query_knowledge_base(text: str):
    """Query the knowledge base using semantic search or simple text matching"""
    try:
        logger.info(f"🔍 Querying knowledge base for: '{text}'")
        
        if USE_EMBEDDINGS:
            # Generate embedding for the query
            query_embedding = embedding_model.encode([text])[0].tolist()
            
            # Search in ChromaDB - get more results to search comprehensively
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=10  # Increased from 3 to search more documents
            )
            
            if not results['documents'] or not results['documents'][0]:
                logger.info("❌ No documents found in ChromaDB")
                return QueryResponse(
                    answer="No relevant information found in knowledge base.",
                    relevant=False,
                    confidence=0.0,
                    processing_method="embeddings"
                )
            
            # Analyze ALL results, not just the first one
            best_match = None
            best_confidence = 0.0
            best_metadata = None
            source_docs = []
            
            documents = results['documents'][0]
            distances = results['distances'][0] if results['distances'] else []
            metadatas = results['metadatas'][0] if results['metadatas'] else []
            
            logger.info(f"📊 Found {len(documents)} potential matches")
            
            for i, (doc, distance, metadata) in enumerate(zip(documents, distances, metadatas)):
                confidence = 1.0 - distance if distance is not None else 0.0
                filename = metadata.get('filename', 'unknown') if metadata else 'unknown'
                
                logger.info(f"  {i+1}. {filename} - Confidence: {confidence:.3f}")
                
                # Stricter threshold for better relevance
                if confidence > 0.4:  # Raised back to 0.4 for better precision
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = doc
                        best_metadata = metadata
                    
                    source_docs.append(f"{filename} (confidence: {confidence:.3f})")
            
            if best_match and best_confidence > 0.2:
                logger.info(f"✅ Best match found with confidence {best_confidence:.3f}")
                
                # Try multiple documents if confidence is low
                context_docs = []
                if best_confidence < 0.5 and len(documents) > 1:
                    # Combine top 3 results for better context
                    for i in range(min(3, len(documents))):
                        if (1.0 - distances[i]) > 0.15:  # Even lower threshold for context
                            context_docs.append(documents[i])
                    
                    if context_docs:
                        combined_context = "\n\n".join(context_docs)
                        enhanced_answer = await enhance_answer_with_gemini(text, combined_context)
                    else:
                        enhanced_answer = await enhance_answer_with_gemini(text, best_match)
                else:
                    enhanced_answer = await enhance_answer_with_gemini(text, best_match)
                
                final_answer = enhanced_answer if enhanced_answer else best_match
                
                # More lenient validation of the enhanced answer
                is_useful = (
                    final_answer and
                    len(final_answer.strip()) > 10 and
                    not final_answer.lower().startswith("no relevant information") and
                    not final_answer.lower().startswith("this document does not contain") and
                    not final_answer.lower().startswith("i don't have information")
                )
                
                if is_useful:
                    return QueryResponse(
                        answer=final_answer,
                        relevant=True,
                        confidence=best_confidence,
                        source_documents=source_docs[:3],  # Top 3 sources
                        processing_method="embeddings"
                    )
            
            logger.info("❌ No sufficiently relevant information found in embeddings")
            return QueryResponse(
                answer="No sufficiently relevant information found in knowledge base.",
                relevant=False,
                confidence=0.0,
                processing_method="embeddings"
            )
        
        else:
            # Enhanced text matching fallback
            logger.info("🔤 Using text-based search fallback")
            query_lower = text.lower()
            query_words = set(query_lower.split())
            
            matches = []
            
            for doc in document_store:
                doc_text = doc['text'].lower()
                doc_words = set(doc_text.split())
                filename = doc.get('filename', '').lower()
                
                # Multiple scoring methods
                # 1. Keyword overlap score
                overlap_score = len(query_words.intersection(doc_words)) / len(query_words) if query_words else 0
                
                # 2. Substring matching score
                substring_score = sum(1 for word in query_words if word in doc_text) / len(query_words) if query_words else 0
                
                # 3. Phrase matching bonus
                phrase_score = 1.0 if query_lower in doc_text else 0.0
                
                # 4. Filename relevance bonus
                filename_score = sum(1 for word in query_words if word in filename) / len(query_words) if query_words else 0
                
                # 5. Specific keyword matching for better relevance
                specific_matches = 0
                for word in query_words:
                    if len(word) > 3:  # Only consider longer words
                        if word in doc_text:
                            specific_matches += 1
                
                specific_score = specific_matches / len([w for w in query_words if len(w) > 3]) if [w for w in query_words if len(w) > 3] else 0
                
                # Combined score with weights
                combined_score = (overlap_score * 0.3) + (substring_score * 0.3) + (phrase_score * 0.2) + (filename_score * 0.1) + (specific_score * 0.1)
                
                if combined_score > 0.3:  # Higher threshold for better relevance
                    matches.append({
                        'doc': doc,
                        'score': combined_score,
                        'text': doc['text']
                    })
            
            # Sort by score
            matches.sort(key=lambda x: x['score'], reverse=True)
            
            logger.info(f"📊 Found {len(matches)} text matches")
            
            if matches:
                best_match = matches[0]
                logger.info(f"✅ Best text match with score {best_match['score']:.3f}")
                
                # Use top matches for context if score is low
                if best_match['score'] < 0.4 and len(matches) > 1:
                    top_texts = [m['text'] for m in matches[:3]]
                    combined_text = "\n\n".join(top_texts)
                    enhanced_answer = await enhance_answer_with_gemini(text, combined_text)
                else:
                    enhanced_answer = await enhance_answer_with_gemini(text, best_match['text'])
                
                final_answer = enhanced_answer if enhanced_answer else best_match['text']
                
                # More lenient validation
                is_useful = (
                    final_answer and
                    len(final_answer.strip()) > 10 and
                    not final_answer.lower().startswith("no relevant information") and
                    not final_answer.lower().startswith("this document does not contain")
                )
                
                if is_useful:
                    source_docs = [f"{m['doc']['filename']} (score: {m['score']:.3f})" for m in matches[:3]]
                    return QueryResponse(
                        answer=final_answer,
                        relevant=True,
                        confidence=best_match['score'],
                        source_documents=source_docs,
                        processing_method="text_search"
                    )
            
            logger.info("❌ No sufficiently relevant information found in text search")
            return QueryResponse(
                answer="No relevant information found in knowledge base.",
                relevant=False,
                confidence=0.0,
                processing_method="text_search"
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
    """Enhance knowledge base answers using Gemini API with improved prompting and fallback handling"""
    if not GEMINI_API_KEY:
        logger.debug("Gemini API key not configured, skipping enhancement")
        return None
    
    try:
        # Enhanced prompt for better responses
        prompt = f"""You are a helpful AI assistant. Based on the provided document content, answer the user's question accurately and concisely.

User Question: "{query}"

Document Content:
{document_content}

Instructions:
1. Provide a clear, direct answer based ONLY on the information in the document
2. Keep your response concise but informative (2-4 sentences)
3. If the document contains relevant information, synthesize it into a helpful answer
4. Use natural, conversational language
5. Focus on answering the specific question asked
6. Don't add information not present in the document

Answer:"""

        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.2,  # Even lower temperature for more focused responses
                "topK": 32,
                "topP": 0.9,
                "maxOutputTokens": 250,
                "stopSequences": ["User Question:", "Document Content:", "Instructions:"]
            },
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH", 
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        logger.debug(f"🤖 Enhancing answer with Gemini for query: '{query[:30]}...'")
        
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers=headers,
            json=payload,
            timeout=15  # Reasonable timeout
        )
        
        if response.status_code == 200:
            data = response.json()
            if (data.get("candidates") and 
                len(data["candidates"]) > 0 and 
                data["candidates"][0].get("content") and
                data["candidates"][0]["content"].get("parts") and
                len(data["candidates"][0]["content"]["parts"]) > 0):
                
                answer = data["candidates"][0]["content"]["parts"][0]["text"]
                cleaned_answer = clean_text(answer)
                
                # Enhanced validation of the response
                if (cleaned_answer and 
                    len(cleaned_answer.strip()) > 15 and
                    not cleaned_answer.lower().startswith("the provided document doesn't contain") and
                    not cleaned_answer.lower().startswith("i don't have") and
                    not cleaned_answer.lower().startswith("i cannot") and
                    not cleaned_answer.lower().startswith("i'm sorry") and
                    not cleaned_answer.lower().startswith("based on the document") and
                    cleaned_answer.lower() != document_content.lower()[:100]):  # Not just repeating content
                    
                    logger.info(f"✅ Gemini enhanced answer: '{cleaned_answer[:50]}...'")
                    return cleaned_answer
                else:
                    logger.debug("❌ Gemini response not useful, using original content")
                    return None
            else:
                logger.debug("❌ Gemini response structure invalid")
                return None
        elif response.status_code == 429:
            logger.warning("⚠️ Gemini API rate limit exceeded, using original content")
            return None
        elif response.status_code == 403:
            logger.warning("⚠️ Gemini API access denied, using original content")
            return None
        else:
            logger.warning(f"⚠️ Gemini API error {response.status_code}, using original content")
            return None
    
    except requests.exceptions.Timeout:
        logger.warning("⚠️ Gemini API timeout, using original content")
        return None
    except requests.exceptions.ConnectionError:
        logger.warning("⚠️ Gemini API connection error, using original content")
        return None
    except Exception as e:
        logger.warning(f"⚠️ Gemini enhancement failed: {str(e)[:100]}, using original content")
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

def split_text_with_overlap(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into chunks with overlap for better context preservation"""
    words = text.split()
    chunks = []
    start = 0
    
    while start < len(words):
        # Calculate end position
        end = min(start + chunk_size, len(words))
        
        # Create chunk
        chunk_words = words[start:end]
        chunk_text = ' '.join(chunk_words)
        
        # Only add non-empty chunks
        if chunk_text.strip():
            chunks.append(chunk_text)
        
        # Move start position with overlap
        if end >= len(words):
            break
        start = end - overlap
        
        # Ensure we don't go backwards
        if start <= 0:
            start = end
    
    return chunks

def split_text(text: str, chunk_size: int = 500) -> List[str]:
    """Simple text splitting into chunks (fallback)"""
    return split_text_with_overlap(text, chunk_size, 0)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)