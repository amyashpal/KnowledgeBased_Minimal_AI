# AI Assistant - Complete Microservices System

A comprehensive AI assistant system built with microservices architecture, featuring a modern web interface, intelligent responses using knowledge base and web search, with persistent chat history.

---

## Features <img src="https://lucide.dev/icons/rocket.svg" alt="rocket icon" width="16" style="vertical-align:middle;">

* **Modern Web Interface**: Beautiful, responsive chat interface with admin panel. Includes smooth CSS transitions and Framer Motion animations.
* **Intelligent Responses**: Knowledge base search with web search fallback powered by DuckDuckGo + Gemini.
* **Gemini AI Integration**: Enhanced responses using Google's Gemini API.
* **Persistent History**: Chat conversations saved across sessions (MongoDB or JSON fallback).
* **Document Upload**: Drag-and-drop upload support with real-time feedback.
* **Real-time Status**: Live system monitoring with animated health indicators.
* **Graceful Fallbacks**: Works even with minimal dependencies.

---

## Architecture <img src="https://lucide.dev/icons/layout.svg" alt="layout icon" width="16" style="vertical-align:middle;">

### Microservices

* **Chat Service** (Port 8000): Central orchestrator coordinating all responses
* **Knowledge Base Service** (Port 8001): Document storage and semantic search
* **Search Service** (Port 8002): Web search using DuckDuckGo + Gemini enhancement
* **History Service** (Port 8003): Persistent conversation storage
* **Web GUI** (Port 8080): Animated chat interface and admin dashboard

### Data Flow

1. User sends message via web interface (with typing animation)
2. Chat service checks knowledge base
3. Falls back to web search if needed
4. Gemini API enhances the response
5. All interactions are saved to history service

---

## Quick Start <img src="https://lucide.dev/icons/terminal.svg" alt="terminal icon" width="16" style="vertical-align:middle;">

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

* Web Chat: [http://localhost:8080](http://localhost:8080)
* Admin Panel: [http://localhost:8080/admin](http://localhost:8080/admin)

---

## Web Interface <img src="https://lucide.dev/icons/monitor.svg" alt="ui icon" width="16" style="vertical-align:middle;">

### Main Chat Interface

* Animated message bubbles with typing indicators
* Source Attribution: Knowledge Base or Web Search
* Quick Actions: Buttons for common questions
* Document Upload: Drag-and-drop area with animation glow effect
* Session Management: Tabs for each chat session

### Admin Panel

* Real-time system status with blinking indicators
* Service health checks with colored badges
* API endpoint reference in expandable sections
* Configuration toggles (dark mode, services on/off)

---

## Knowledge Base <img src="https://lucide.dev/icons/database.svg" alt="database icon" width="16" style="vertical-align:middle;">

### Upload Documents

1. Open the chat interface
2. Use the "Upload Knowledge" tab
3. Upload `.txt`, `.md`, or `.pdf` files
4. Files are indexed in real time with visual confirmation

### Sample Knowledge

Included sample content:

* What is artificial intelligence?
* Types of machine learning
* Why is Python popular for AI?

---

## API Endpoints <img src="https://lucide.dev/icons/code.svg" alt="code icon" width="16" style="vertical-align:middle;">

### Chat Service (8000)

* `POST /chat`
* `GET /chat/{chat_id}`
* `GET /health`

### Knowledge Base Service (8001)

* `GET /query?text={query}`
* `POST /ingest`
* `GET /stats`
* `GET /health`

### Search Service (8002)

* `GET /search?query={query}`
* `GET /health`

### History Service (8003)

* `POST /history`
* `GET /history/{chat_id}`
* `GET /stats`
* `GET /health`

---

## Gemini AI Integration <img src="https://lucide.dev/icons/sparkles.svg" alt="sparkle icon" width="16" style="vertical-align:middle;">

* API key-based access (set in `.env`)
* Enhances search results and document responses
* Used as a fallback when KB and Web Search fail

---

## System Requirements <img src="https://lucide.dev/icons/cpu.svg" alt="cpu icon" width="16" style="vertical-align:middle;">

### Required

* Python 3.8+
* FastAPI
* Uvicorn
* Requests
* Jinja2

### Optional (Enhancements)

* MongoDB (for persistent history)
* ChromaDB + SentenceTransformers (for semantic search)
* DuckDuckGo search library

---

## Configuration <img src="https://lucide.dev/icons/settings.svg" alt="settings icon" width="16" style="vertical-align:middle;">

### Environment Variables (`.env`)

```env
GEMINI_API_KEY=your-gemini-api-key
MONGO_URL=mongodb://localhost:27017/
CHROMA_DB_DIR=./chroma_db/
CHAT_SERVICE_PORT=8000
KB_SERVICE_PORT=8001
SEARCH_SERVICE_PORT=8002
HISTORY_SERVICE_PORT=8003
WEB_GUI_PORT=8080
```

---

## Testing <img src="https://lucide.dev/icons/beaker.svg" alt="testing icon" width="16" style="vertical-align:middle;">

```bash
# Run all tests
python test_final.py

# Example: Submit chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"chat_id": "test-123", "message": "What is AI?"}'

# Upload KB file
curl -X POST http://localhost:8001/ingest \
  -F "files=@sample_knowledge.txt"
```

---

## Project Structure <img src="https://lucide.dev/icons/folder.svg" alt="folder icon" width="16" style="vertical-align:middle;">

```
ai-assistant/
├── services/
│   ├── chat_service.py
│   ├── knowledge_base_service.py
│   ├── search_service.py
│   └── history_service.py
├── templates/
│   ├── index.html
│   └── admin.html
├── web_gui.py
├── run_services.py
├── install.py
├── requirements.txt
├── .env.example
└── sample_knowledge.txt
```

---

## Troubleshooting <img src="https://lucide.dev/icons/bug.svg" alt="bug icon" width="16" style="vertical-align:middle;">

### Services Not Starting

* Check port conflicts
* Run `python install.py`
* Ensure Python 3.8+

### Knowledge Issues

* `.txt` or `.md` not uploading? Check formatting
* Missing vector search? Falls back to keyword search

### Search Not Working

* Check DuckDuckGo accessibility
* Validate Gemini API key

### History Not Saving

* MongoDB not running? Uses local fallback JSON

---

## 1-Day MVP Compliance <img src="https://lucide.dev/icons/check-circle.svg" alt="check icon" width="16" style="vertical-align:middle;">

| Feature                    | Status |
| -------------------------- | ------ |
| Microservices Architecture | ✅      |
| Real-time Chat UI          | ✅      |
| Knowledge Base + Upload    | ✅      |
| Web Search Fallback        | ✅      |
| Gemini AI Integration      | ✅      |
| Persistent History         | ✅      |
| Animated Web Interface     | ✅      |
| Graceful Fallbacks         | ✅      |

---

## License <img src="https://lucide.dev/icons/file-text.svg" alt="license icon" width="16" style="vertical-align:middle;">

This project is open source and available under the [MIT License](LICENSE).
