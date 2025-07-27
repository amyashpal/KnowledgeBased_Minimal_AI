#  AI Assistant - Complete Microservices System

<div align="center">
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" width="60" height="60" style="animation: bounce 2s infinite; margin: 10px;"/>
  <img src="https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png" width="60" height="60" style="animation: pulse 2s infinite; margin: 10px;"/>
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/mongodb/mongodb-original.svg" width="60" height="60" style="animation: bounce 2s infinite; margin: 10px;"/>
  
  <h3 style="background: linear-gradient(45deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: fadeInUp 1s ease-out;">
    A comprehensive AI assistant system built with microservices architecture
  </h3>
</div>

<div align="center" style="margin: 30px 0;">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/FastAPI-Framework-green?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Microservices-Architecture-orange?style=for-the-badge&logo=kubernetes&logoColor=white" alt="Microservices"/>
  <img src="https://img.shields.io/badge/AI-Powered-purple?style=for-the-badge&logo=openai&logoColor=white" alt="AI Powered"/>
</div>

## ⚡ Quick Start

```bash
# 1. Install dependencies
python install.py

# 2. Start all services
python run_services.py

# 3. Open browser
http://localhost:8080
```

## ⚙️ Configuration

```bash
# Environment Variables (Optional)
GEMINI_API_KEY=your-api-key    # Already configured
MONGO_URL=mongodb://localhost:27017/
```

**Service Ports:**
- 🌐 Web Interface: `8080`
- 💬 Chat Service: `8000`
- 📚 Knowledge Base: `8001`
- 🔍 Search Service: `8002`
- 📝 History Service: `8003`

## ✨ Features

- 🎨 **Modern Web Interface** - Beautiful chat UI with admin panel
- 🧠 **Smart Responses** - Knowledge base + web search + Gemini AI
- 💾 **Persistent History** - Chat conversations saved across sessions
- 📁 **Document Upload** - Easy knowledge base management
- 📊 **Real-time Status** - Live system monitoring
- 🔄 **Graceful Fallbacks** - Works with minimal dependencies

## 🏗️ Architecture

### 🔧 Microservices
- **Chat Service** - Central coordinator
- **Knowledge Base** - Document storage & search
- **Search Service** - Web search + AI enhancement
- **History Service** - Conversation storage
- **Web GUI** - Modern interface

### 📊 Data Flow
User → Web Interface → Chat Service → Knowledge Base/Search → Gemini AI → Response

## 🌐 Web Interface

### 💬 Main Chat
- Real-time responses with typing indicators
- Source attribution (knowledge base/web search)
- Quick action buttons
- Drag-and-drop file upload
- Multiple chat sessions

### 🛠️ Admin Panel
- System status monitoring
- Service health checks
- API documentation
- Configuration settings

## 📚 Knowledge Base

**Upload Documents:**
1. Go to main chat interface
2. Use "Upload Knowledge" sidebar
3. Select files (.txt, .md, .pdf)
4. Click "Upload Files"

**Test Questions:**
- "What is artificial intelligence?"
- "What are machine learning types?"
- "Why use Python for AI?"

## 🔗 API Endpoints

| Service | Port | Key Endpoints |
|---------|------|---------------|
| 💬 Chat | 8000 | `/chat`, `/health` |
| 📚 Knowledge | 8001 | `/query`, `/ingest`, `/stats` |
| 🔍 Search | 8002 | `/search`, `/health` |
| 📝 History | 8003 | `/history`, `/stats` |

## 🧪 Testing

```bash
# Quick system test
python test_final.py

# Manual API test
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"chat_id": "test", "message": "What is AI?"}'
```

## 🛠️ Requirements

**Core (Required):**
- Python 3.8+
- FastAPI, Uvicorn, Requests

**Optional (Enhanced Features):**
- ChromaDB + Sentence Transformers (embeddings)
- MongoDB (history storage)
- DuckDuckGo Search (web search)

## 🚨 Troubleshooting

| Issue | Solution |
|-------|----------|
| 🚫 Services won't start | Check ports 8000-8003, 8080 available |
| 📁 Upload fails | Check file format (.txt, .md supported) |
| 🔍 Search not working | System falls back to Gemini direct |
| 💾 History not saving | Falls back to JSON file storage |

## 📁 Project Structure

```
ai-assistant/
├── services/           # Microservices
├── templates/          # Web interface
├── web_gui.py         # Web server
├── run_services.py    # Service launcher
└── install.py         # Dependency installer
```

## ✅ 1-Day Challenge Compliance

✅ Microservices Architecture  
✅ Chat Functionality  
✅ Knowledge Base  
✅ Web Search Fallback  
✅ Conversation History  
✅ Error Handling  
✅ Complete Documentation  

---

<div align="center">
  <strong>🚀 Ready to chat with your AI assistant!</strong>
</div>
