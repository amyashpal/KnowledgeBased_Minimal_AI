# 🤖 AI Assistant - Microservices System

<div align="center">
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" width="50" height="50"/>
  <img src="https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png" width="50" height="50"/>
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/mongodb/mongodb-original.svg" width="50" height="50"/>
</div>

[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Framework-green?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Microservices](https://img.shields.io/badge/Microservices-Architecture-orange?style=flat)](https://microservices.io)

## ⚡ Quick Start

```bash
# 1. Install dependencies
python install.py

# 2. Start all services  
python run_services.py

# 3. Open browser
http://localhost:8080
```

## 🔧 Configuration

**Create `.env` file:**
```bash
cp .env.example .env
```

**Required settings:**
```env
GEMINI_API_KEY=your-api-key    # Get from Google AI Studio
MONGO_URL=mongodb://localhost:27017/
```

## 🌐 Services & Ports

| Service | Port | Function |
|---------|------|----------|
| 🌐 Web Interface | 8080 | Chat UI & Admin |
| 💬 Chat Service | 8000 | Main coordinator |
| 📚 Knowledge Base | 8001 | Document storage |
| 🔍 Search Service | 8002 | Web search |
| 📝 History Service | 8003 | Chat history |

## ✨ Features

- 🎨 **Modern Web UI** - Clean chat interface with admin panel
- 🧠 **Smart AI** - Knowledge base + web search + Gemini AI
- 💾 **Chat History** - Persistent conversation storage
- 📁 **File Upload** - Drag-and-drop document ingestion
- 📊 **Real-time Status** - Live service monitoring
- 🔄 **Graceful Fallbacks** - Works with minimal dependencies

## 📚 Knowledge Base Usage

1. Open chat interface
2. Use "Upload Knowledge" sidebar
3. Upload files (.txt, .md, .pdf)
4. Ask questions about uploaded content

## 🧪 Testing or use POSTMAN with goven ports(API Services:
💬 Chat Service:       http://localhost:8000
📚 Knowledge Base:     http://localhost:8001
🔍 Search Service:     http://localhost:8002
📝 History Service:    http://localhost:8003)

```bash
# System test
python test_final.py

# API test
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"chat_id": "test", "message": "What is AI?"}'
```

## 📋 Requirements

**Core:** Python 3.8+, FastAPI, Uvicorn, Requests  
**Optional:** ChromaDB, MongoDB, DuckDuckGo Search

## 🚨 Common Issues

- **Services won't start:** Check ports 8000-8003, 8080 are free
- **Upload fails:** Use supported formats (.txt, .md, .pdf)
- **No search:** System falls back to direct Gemini AI
- **No history:** Falls back to JSON file storage

## 📁 Structure

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

---

**🚀 Complete AI assistant with microservices architecture, knowledge base, and web search!**
