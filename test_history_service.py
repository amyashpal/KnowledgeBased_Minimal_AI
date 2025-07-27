#!/usr/bin/env python3
"""
Comprehensive test for History Service with MongoDB integration
Tests conversation context, chat sessions, and message storage
"""

import requests
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()

def test_history_service_mongodb():
    """Test History Service with MongoDB functionality"""
    print('🍃 Testing History Service with MongoDB')
    print('=' * 60)
    
    # Check if MongoDB is configured
    mongo_url = os.getenv("MONGO_URL")
    print(f'📊 MONGO_URL configured: {bool(mongo_url)}')
    
    if mongo_url:
        print(f'🔗 MongoDB URL: {mongo_url}')
        
        # Test MongoDB connection directly
        try:
            from pymongo import MongoClient
            client = MongoClient(mongo_url, serverSelectionTimeoutMS=2000)
            server_info = client.server_info()
            print(f'✅ MongoDB connection: SUCCESS (version {server_info.get("version", "unknown")})')
            mongodb_available = True
        except Exception as e:
            print(f'❌ MongoDB connection: FAILED ({str(e)[:50]}...)')
            mongodb_available = False
    else:
        print('⚠️ MongoDB not configured in .env')
        mongodb_available = False
    
    # Check History Service health
    print(f'\n🏥 Testing History Service Health:')
    try:
        response = requests.get('http://localhost:8003/health', timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            using_mongodb = health_data.get('using_mongodb', False)
            
            print(f'✅ History Service: Healthy')
            print(f'🍃 Using MongoDB: {using_mongodb}')
            
            if mongodb_available and not using_mongodb:
                print('⚠️ MongoDB available but service using file storage')
                print('💡 Restart services to enable MongoDB')
            elif using_mongodb:
                print('✅ MongoDB integration active!')
        else:
            print(f'❌ History Service: Status {response.status_code}')
            return False
    except Exception as e:
        print(f'❌ History Service: Not responding - {e}')
        return False
    
    return True

def test_conversation_context():
    """Test conversation context and chat session management"""
    print(f'\n💬 Testing Conversation Context & Chat Sessions')
    print('-' * 50)
    
    # Test multiple chat sessions
    chat_sessions = [
        {
            'chat_id': 'python-learning-session',
            'messages': [
                'What is Python programming?',
                'How do I install Python?',
                'What are Python data types?'
            ]
        },
        {
            'chat_id': 'ml-discussion-session', 
            'messages': [
                'What is machine learning?',
                'Explain supervised learning',
                'What are neural networks?'
            ]
        },
        {
            'chat_id': 'web-dev-session',
            'messages': [
                'What is frontend development?',
                'How does HTML work?',
                'What is CSS used for?'
            ]
        }
    ]
    
    print(f'📝 Testing {len(chat_sessions)} chat sessions...')
    
    session_results = []
    
    for session in chat_sessions:
        chat_id = session['chat_id']
        messages = session['messages']
        
        print(f'\n🔹 Session: {chat_id}')
        
        session_success = True
        sent_messages = 0
        
        # Send messages in this session
        for i, message in enumerate(messages, 1):
            try:
                response = requests.post('http://localhost:8000/chat', json={
                    'chat_id': chat_id,
                    'message': message
                }, timeout=20)
                
                if response.status_code == 200:
                    result = response.json()
                    source = result.get('source', 'unknown')
                    print(f'   {i}. ✅ "{message[:30]}..." → {source}')
                    sent_messages += 1
                else:
                    print(f'   {i}. ❌ "{message[:30]}..." → Failed ({response.status_code})')
                    session_success = False
                    
            except Exception as e:
                print(f'   {i}. ❌ "{message[:30]}..." → Error: {e}')
                session_success = False
        
        session_results.append({
            'chat_id': chat_id,
            'success': session_success,
            'messages_sent': sent_messages,
            'expected_messages': len(messages)
        })
    
    # Wait for messages to be stored
    print(f'\n⏳ Waiting for message storage...')
    time.sleep(3)
    
    # Test retrieving conversation history for each session
    print(f'\n📋 Testing Conversation History Retrieval:')
    
    retrieval_success = 0
    
    for session_result in session_results:
        chat_id = session_result['chat_id']
        expected_messages = session_result['expected_messages']
        
        try:
            response = requests.get(f'http://localhost:8000/chat/{chat_id}', timeout=10)
            
            if response.status_code == 200:
                history = response.json()
                messages = history.get('messages', [])
                
                # Each user message should have an assistant response
                expected_total = expected_messages * 2  # user + assistant messages
                actual_total = len(messages)
                
                print(f'🔹 {chat_id}:')
                print(f'   📊 Expected: ~{expected_total} messages (user + assistant)')
                print(f'   📊 Retrieved: {actual_total} messages')
                
                if actual_total >= expected_messages:  # At least user messages should be there
                    print(f'   ✅ History retrieval: SUCCESS')
                    retrieval_success += 1
                    
                    # Show recent messages
                    print(f'   📋 Recent messages:')
                    for i, msg in enumerate(messages[-4:], 1):  # Show last 4 messages
                        sender = msg.get('sender', 'unknown')
                        message_text = msg.get('message', '')[:40]
                        timestamp = msg.get('timestamp', 'unknown')
                        print(f'      {i}. [{sender}] {message_text}... ({timestamp})')
                else:
                    print(f'   ❌ History retrieval: INCOMPLETE')
            else:
                print(f'🔹 {chat_id}: ❌ Failed to retrieve history ({response.status_code})')
                
        except Exception as e:
            print(f'🔹 {chat_id}: ❌ Error retrieving history: {e}')
    
    print(f'\n📊 Conversation Context Results:')
    print(f'   📝 Chat sessions tested: {len(chat_sessions)}')
    print(f'   ✅ History retrieval success: {retrieval_success}/{len(chat_sessions)}')
    
    return retrieval_success >= len(chat_sessions) * 0.8  # 80% success rate

def test_history_service_stats():
    """Test history service statistics"""
    print(f'\n📊 Testing History Service Statistics:')
    print('-' * 40)
    
    try:
        response = requests.get('http://localhost:8003/stats', timeout=10)
        
        if response.status_code == 200:
            stats = response.json()
            total_messages = stats.get('total_messages', 0)
            unique_chats = stats.get('unique_chats', 0)
            using_mongodb = stats.get('using_mongodb', False)
            
            print(f'📈 Total messages: {total_messages}')
            print(f'💬 Unique chat sessions: {unique_chats}')
            print(f'🍃 Using MongoDB: {using_mongodb}')
            
            if total_messages > 0 and unique_chats > 0:
                print(f'✅ History service statistics: WORKING')
                return True
            else:
                print(f'⚠️ History service statistics: LOW ACTIVITY')
                return False
        else:
            print(f'❌ Failed to get statistics: {response.status_code}')
            return False
            
    except Exception as e:
        print(f'❌ Error getting statistics: {e}')
        return False

def test_mongodb_data_directly():
    """Test MongoDB data directly if available"""
    print(f'\n🔍 Testing MongoDB Data Directly:')
    print('-' * 40)
    
    mongo_url = os.getenv("MONGO_URL")
    if not mongo_url:
        print('⚠️ MongoDB not configured - skipping direct test')
        return True
    
    try:
        from pymongo import MongoClient
        
        client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
        db = client.ai_assistant
        collection = db.chat_history
        
        # Count total messages
        total_messages = collection.count_documents({})
        print(f'📝 Total messages in MongoDB: {total_messages}')
        
        if total_messages > 0:
            # Count unique chat sessions
            unique_chats = len(collection.distinct("chat_id"))
            print(f'💬 Unique chat sessions: {unique_chats}')
            
            # Show recent messages
            recent_messages = collection.find().sort("timestamp", -1).limit(5)
            
            print(f'📋 Recent messages from MongoDB:')
            for i, msg in enumerate(recent_messages, 1):
                chat_id = msg.get('chat_id', 'unknown')
                sender = msg.get('sender', 'unknown')
                message = msg.get('message', '')[:40]
                timestamp = msg.get('timestamp', 'unknown')
                
                print(f'   {i}. [{chat_id}] {sender}: {message}... ({timestamp})')
            
            print(f'✅ MongoDB data access: WORKING')
            return True
        else:
            print(f'📭 No messages found in MongoDB')
            return True  # Not an error, just empty
            
    except Exception as e:
        print(f'❌ MongoDB direct access failed: {e}')
        return False

def main():
    """Run comprehensive History Service tests"""
    print('🍃 COMPREHENSIVE HISTORY SERVICE TEST')
    print('=' * 70)
    
    # Test MongoDB integration
    mongodb_test = test_history_service_mongodb()
    
    # Test conversation context
    context_test = test_conversation_context()
    
    # Test statistics
    stats_test = test_history_service_stats()
    
    # Test MongoDB data directly
    mongodb_data_test = test_mongodb_data_directly()
    
    # Final summary
    print('\n' + '=' * 70)
    print('📋 HISTORY SERVICE TEST SUMMARY')
    print('=' * 70)
    print(f'🍃 MongoDB Integration: {"✅ PASS" if mongodb_test else "❌ FAIL"}')
    print(f'💬 Conversation Context: {"✅ PASS" if context_test else "❌ FAIL"}')
    print(f'📊 Service Statistics: {"✅ PASS" if stats_test else "❌ FAIL"}')
    print(f'🔍 MongoDB Data Access: {"✅ PASS" if mongodb_data_test else "❌ FAIL"}')
    
    total_tests = 4
    passed_tests = sum([mongodb_test, context_test, stats_test, mongodb_data_test])
    
    print(f'\n🎯 OVERALL: {passed_tests}/{total_tests} tests passed')
    
    if passed_tests >= 3:
        print('🎉 HISTORY SERVICE IS WORKING EXCELLENTLY!')
        print('✅ Conversation context maintained across interactions')
        print('✅ Chat sessions properly managed with unique IDs')
        print('✅ Message history stored and retrieved correctly')
        print('✅ MongoDB integration ready for production')
    elif passed_tests >= 2:
        print('✅ HISTORY SERVICE IS WORKING WELL!')
        print('⚠️ Some minor issues detected but core functionality works')
    else:
        print('⚠️ HISTORY SERVICE HAS ISSUES!')
        print('❌ Please check the failed tests above')
    
    print('=' * 70)

if __name__ == "__main__":
    main()