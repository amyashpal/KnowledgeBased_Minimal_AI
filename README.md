# AI Assistant - Complete Microservices System

A comprehensive AI assistant system built with microservices architecture, featuring a modern web interface, intelligent responses using knowledge base and web search, with persistent chat history.

## 🚀 Features

- **Modern Web Interface**: Beautiful, responsive chat interface with admin panel
- **Intelligent Responses**: Knowledge base search with web search fallback
- **Gemini AI Integration**: Enhanced responses using Google's Gemini API
- **Persistent History**: Chat conversations saved across sessions
- **Document Upload**: Easy knowledge base management through web interface
- **Real-time Status**: Live system monitoring and health checks
- **Graceful Fallbacks**: Works even with minimal dependencies

## 🏗️ Architecture

### Microservices
- **Chat Service** (Port 8000): Central orchestrator coordinating all responses
- **Knowledge Base Service** (Port 8001): Document storage and semantic search
- **Search Service** (Port 8002): Web search using DuckDuckGo + Gemini enhancement
- **History Service** (Port 8003): Persistent conversation storage
- **Web GUI** (Port 8080): Modern web interface and admin panel(Might Not Store Chat)

### Data Flow
1. User sends message via web interface
2. Chat service checks knowledge base first
3. Falls back to web search if no relevant knowledge found
4. Gemini API enhances responses for better quality
5. All interactions saved to history service

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# Automatic installation (recommended)
python install.py

# Or manual installation
pip install -r requirements.txt
```

### 2. Start the System
```bash
python run_services.py
```

### 3. Access the Interface
- **Web Chat**: http://localhost:8080
- **Admin Panel**: http://localhost:8080/admin

## 🌐 Web Interface

### Main Chat Interface
- **Real-time Chat**: Instant responses with typing indicators
- **Source Attribution**: See whether answers come from knowledge base or web search
- **Quick Actions**: Pre-defined questions for common topics
- **Document Upload**: Drag-and-drop knowledge base management
- **Session Management**: Multiple chat sessions with persistent history

### Admin Panel
- **System Overview**: Real-time service status and statistics
- **Service Monitoring**: Detailed health checks and performance metrics
- **API Documentation**: Complete endpoint reference
- **Configuration**: System settings and feature toggles

## 📚 Knowledge Base

### Upload Documents
1. Go to the main chat interface
2. Use the "Upload Knowledge" section in the sidebar
3. Select text files (.txt, .md, .pdf)
4. Click "Upload Files"

### Sample Knowledge
The system includes sample knowledge about AI and machine learning. Test with questions like:
- "What is artificial intelligence?"
- "What are the types of machine learning?"
- "Why is Python popular for AI?"

## 🔧 API Endpoints

### Chat Service (Port 8000)
- `POST /chat` - Submit user query and receive response
- `GET /chat/{chat_id}` - Retrieve chat history
- `GET /health` - Service health check

### Knowledge Base Service (Port 8001)
- `GET /query?text={query}` - Search knowledge base
- `POST /ingest` - Upload documents (multipart/form-data)
- `GET /stats` - Knowledge base statistics
- `GET /health` - Service health check

### Search Service (Port 8002)
- `GET /search?query={query}` - Perform web search
- `GET /health` - Service health check

### History Service (Port 8003)
- `POST /history` - Save message to history
- `GET /history/{chat_id}` - Retrieve conversation history
- `GET /stats` - History statistics
- `GET /health` - Service health check

## 🤖 Gemini AI Integration

The system uses Google's Gemini API for enhanced responses:

- **API Key**: Pre-configured ()
- **Enhanced Search**: Web search results processed by Gemini for better answers
- **Knowledge Enhancement**: Document-based responses improved with context
- **Direct Fallback**: Gemini provides answers when other sources fail

## 🛠️ System Requirements

### Core Dependencies (Required)
- Python 3.8+
- FastAPI
- Uvicorn
- Requests
- Jinja2

### Optional Dependencies (Enhanced Features)
- **Vector Embeddings**: ChromaDB + Sentence Transformers
- **Chat History**: MongoDB (falls back to JSON files)
- **Web Search**: DuckDuckGo Search library

## 🔧 Configuration

### Environment Variables
```bash
GEMINI_API_KEY=your-gemini-api-key  # Already configured
MONGO_URL=mongodb://localhost:27017/  # Optional
```

### Service URLs (Default)
- Chat Service: http://localhost:8000
- Knowledge Base: http://localhost:8001
- Search Service: http://localhost:8002
- History Service: http://localhost:8003
- Web Interface: http://localhost:8080

## 🧪 Testing

### Quick Test
```bash
python test_final.py
```

### Manual API Testing
```bash
# Test chat endpoint
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"chat_id": "test-123", "message": "What is AI?"}'

# Upload knowledge
curl -X POST "http://localhost:8001/ingest" \
  -F "files=@sample_knowledge.txt"
```

## 📁 Project Structure

```
ai-assistant/
├── services/
│   ├── chat_service.py          # Main orchestrator
│   ├── knowledge_base_service.py # Document storage & search
│   ├── search_service.py        # Web search with Gemini
│   └── history_service.py       # Conversation storage
├── templates/
│   ├── index.html              # Main chat interface
│   └── admin.html              # Admin panel
├── web_gui.py                  # Web interface server
├── run_services.py             # Start all services
├── install.py                  # Dependency installer
├── requirements.txt            # Python dependencies
├── sample_knowledge.txt        # Sample AI/ML knowledge
└── README.md                   # This file
```

## 🚨 Troubleshooting

### Services Won't Start
- Check if ports 8000-8003, 8080 are available
- Install missing dependencies: `python install.py`
- Check Python version (3.8+ required)

### Knowledge Base Issues
- Embedding dependencies missing: Falls back to text search (still works)
- Upload fails: Check file format (.txt, .md supported)

### Search Not Working
- DuckDuckGo blocked: System falls back to Gemini direct answers
- Gemini API issues: Check API key configuration

### History Not Saving
- MongoDB unavailable: System falls back to JSON file storage
- File permissions: Check write access to project directory

## 🎯 1-Day Challenge Compliance

This system fully implements the 1-Day AI Agent MVP requirements:

✅ **Microservices Architecture**: 4 independent services with clear APIs  
✅ **Chat Functionality**: Web interface with real-time responses  
✅ **Knowledge Base**: Document upload and semantic search  
✅ **Web Search Fallback**: DuckDuckGo integration with Gemini enhancement  
✅ **Conversation History**: Persistent chat sessions  
✅ **Error Handling**: Graceful degradation and fallbacks  
✅ **Documentation**: Complete API docs and setup instructions  
✅ **Sample Content**: Pre-loaded AI/ML knowledge base  

## 📄 License

This project is open source and available under the MIT License.