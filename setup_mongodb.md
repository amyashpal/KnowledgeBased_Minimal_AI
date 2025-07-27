# MongoDB Setup Guide

## Option 1: Local MongoDB Installation

### Windows:
1. Download MongoDB Community Server from: https://www.mongodb.com/try/download/community
2. Install MongoDB with default settings
3. MongoDB will run as a Windows service on port 27017

### Alternative - Using MongoDB with Docker:
```bash
# Run MongoDB in Docker container
docker run -d --name mongodb -p 27017:27017 mongo:latest

# Or with persistent data
docker run -d --name mongodb -p 27017:27017 -v mongodb_data:/data/db mongo:latest
```

### Verify MongoDB is Running:
```bash
# Check if MongoDB is running on port 27017
netstat -an | findstr 27017

# Or try connecting with MongoDB shell (if installed)
mongosh
```

## Option 2: MongoDB Atlas (Cloud)

1. Go to https://www.mongodb.com/atlas
2. Create a free account
3. Create a new cluster
4. Get your connection string (looks like: mongodb+srv://username:password@cluster.mongodb.net/)
5. Update the MONGO_URL in .env file

## Enable MongoDB in the System

1. Edit the `.env` file
2. Uncomment the MONGO_URL line:
   ```
   MONGO_URL=mongodb://localhost:27017/
   ```
3. Restart the services

## Database Structure

When MongoDB is enabled, the system will create:
- **Database**: `ai_assistant`
- **Collection**: `chat_history`

### Document Structure:
```json
{
  "_id": ObjectId("..."),
  "chat_id": "user-session-123",
  "message": "What is Python?",
  "sender": "user",
  "timestamp": ISODate("2024-01-01T12:00:00Z")
}
```

## Verify MongoDB is Working

After enabling MongoDB and restarting services, you should see:
```
✅ Using MongoDB for history storage
```

Instead of:
```
📁 Using file-based storage for history (MongoDB not configured)
```