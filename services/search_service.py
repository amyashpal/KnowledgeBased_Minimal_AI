from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import logging
import re
import os
import json

app = FastAPI(title="Search Service", version="1.0.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import duckduckgo-search, fallback to basic requests
try:
    from duckduckgo_search import DDGS
    USE_DDGS = True
    logger.info("Using duckduckgo-search library")
except ImportError:
    USE_DDGS = False
    logger.warning("duckduckgo-search not available, using fallback")
    from bs4 import BeautifulSoup

# Gemini API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCgVAm2hJGrcc-vKi3jNMDswzrgykmw3Ks")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

class SearchResponse(BaseModel):
    answer: str
    source: str

@app.get("/search", response_model=SearchResponse)
async def search(query: str):
    """Perform web search using DuckDuckGo with Gemini enhancement"""
    try:
        # Try DuckDuckGo search first (if available)
        if USE_DDGS:
            search_result = await get_ddgs_results(query)
            if search_result:
                # Enhance with Gemini if available
                enhanced_answer = await enhance_with_gemini(query, search_result)
                return SearchResponse(
                    answer=enhanced_answer or search_result,
                    source="ddgs_gemini" if enhanced_answer else "ddgs"
                )
        
        # Try DuckDuckGo Instant Answer API
        instant_answer = await get_duckduckgo_instant_answer(query)
        if instant_answer:
            # Enhance with Gemini if available
            enhanced_answer = await enhance_with_gemini(query, instant_answer)
            return SearchResponse(
                answer=enhanced_answer or instant_answer, 
                source="duckduckgo_instant_gemini" if enhanced_answer else "duckduckgo_instant"
            )
        
        # Try web scraping (if DDGS library not available)
        if not USE_DDGS:
            search_result = await scrape_duckduckgo_results(query)
            if search_result:
                enhanced_answer = await enhance_with_gemini(query, search_result)
                return SearchResponse(
                    answer=enhanced_answer or search_result,
                    source="duckduckgo_scrape_gemini" if enhanced_answer else "duckduckgo_scrape"
                )
        
        # Primary fallback: Use Gemini directly (this should work reliably)
        gemini_answer = await get_gemini_direct_answer(query)
        if gemini_answer:
            return SearchResponse(answer=gemini_answer, source="gemini_direct")
        
        # Final fallback
        return SearchResponse(
            answer="I couldn't find relevant information for your query.",
            source="fallback"
        )
    
    except Exception as e:
        logger.error(f"Error in search: {e}")
        # Even if there's an error, try Gemini as last resort
        try:
            gemini_answer = await get_gemini_direct_answer(query)
            if gemini_answer:
                return SearchResponse(answer=gemini_answer, source="gemini_emergency")
        except:
            pass
        raise HTTPException(status_code=500, detail="Search service error")

async def get_ddgs_results(query: str) -> str:
    """Get search results using duckduckgo-search library"""
    try:
        with DDGS() as ddgs:
            # Try different search approaches
            results = []
            
            # Try text search first
            try:
                results = [r for r in ddgs.text(query, max_results=3)]
            except Exception as e:
                logger.warning(f"DDGS text search failed: {e}")
                # Try with simpler query
                simple_query = query.split('?')[0].strip()  # Remove question marks
                try:
                    results = [r for r in ddgs.text(simple_query, max_results=2)]
                except Exception as e2:
                    logger.warning(f"DDGS simple search also failed: {e2}")
            
            if not results:
                logger.warning(f"No DDGS results for: {query}")
                return None
            
            # Format results into a single string
            formatted_results = "\n".join([
                f"Title: {r['title']}\nSnippet: {r['body']}" 
                for r in results
            ])
            
            logger.info(f"🔍 Search Results for '{query}':")
            logger.info(formatted_results)
            
            return clean_text(formatted_results)
    
    except Exception as e:
        logger.error(f"DDGS search failed: {e}")
        return None

async def get_duckduckgo_instant_answer(query: str) -> str:
    """Get instant answer from DuckDuckGo API"""
    try:
        url = "https://api.duckduckgo.com/"
        params = {
            'q': query,
            'format': 'json',
            'no_html': '1',
            'skip_disambig': '1'
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            # Check for abstract
            if data.get('Abstract'):
                return clean_text(data['Abstract'])
            
            # Check for definition
            if data.get('Definition'):
                return clean_text(data['Definition'])
            
            # Check for answer
            if data.get('Answer'):
                return clean_text(data['Answer'])
        
        return None
    
    except Exception as e:
        logger.error(f"DuckDuckGo instant answer failed: {e}")
        return None

async def scrape_duckduckgo_results(query: str) -> str:
    """Scrape DuckDuckGo search results as fallback"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        url = f"https://duckduckgo.com/html/?q={query}"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for result snippets
            results = soup.find_all('a', class_='result__snippet')
            if results:
                # Get the first meaningful result
                snippet = results[0].get_text().strip()
                return clean_text(snippet)
            
            # Alternative: look for any text content in results
            results = soup.find_all('div', class_='result__body')
            if results:
                snippet = results[0].get_text().strip()
                return clean_text(snippet)
        
        return None
    
    except Exception as e:
        logger.error(f"DuckDuckGo scraping failed: {e}")
        return None

async def enhance_with_gemini(query: str, search_result: str) -> str:
    """Enhance search results using Gemini API"""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your-gemini-api-key":
        return None
    
    try:
        prompt = f"""Based on this search result, provide a clear and concise answer to the question: "{query}"

Search result: {search_result}

Please provide a helpful, accurate answer in 2-3 sentences. Focus on directly answering the question."""

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

async def get_gemini_direct_answer(query: str) -> str:
    """Get direct answer from Gemini API when search fails"""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your-gemini-api-key":
        return None
    
    try:
        prompt = f"""Please provide a helpful and accurate answer to this question: "{query}"

Keep the response concise (2-3 sentences) and factual. If you're not certain about specific details, mention that."""

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
        logger.error(f"Gemini direct answer failed: {e}")
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

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
