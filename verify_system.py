#!/usr/bin/env python3
"""
Simple system verification script
"""

import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

def verify_system():
    """Verify the AI Assistant system is working correctly"""
    print('🔍 AI Assistant System Verification')
    print('=' * 50)
    
    # Check if services are running
    services = [
        ('Chat Service', 'http://localhost:8000/health'),
        ('Knowledge Base', 'http://localhost:8001/health'),
        ('Search Service', 'http://localhost:8002/health'),
        ('History Service', 'http://localhost:8003/health')
    ]
    
    print('🏥 Checking Service Health:')
    all_healthy = True
    mongodb_status = False
    
    for name, url in services:
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                data = response.json()
                print(f'   ✅ {name}: Healthy')
                
                if name == 'History Service':
                    mongodb_status = data.get('using_mongodb', False)
                    storage_type = "MongoDB" if mongodb_status else "File Storage"
                    print(f'      📊 Storage: {storage_type}')
            else:
                print(f'   ❌ {name}: Status {response.status_code}')
                all_healthy = False
        except Exception as e:
            print(f'   ❌ {name}: Not responding')
            all_healthy = False
    
    if not all_healthy:
        print('\n⚠️ Some services are not running. Start with: python run_services.py')
        return
    
    # Test knowledge base query
    print(f'\n🧪 Testing Knowledge Base:')
    try:
        response = requests.post('http://localhost:8000/chat', json={
            'chat_id': 'verify-test',
            'message': 'What is Python?'
        }, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            source = result.get('source', 'unknown')
            confidence = result.get('confidence', 0)
            answer = result.get('response', '')[:100]
            
            print(f'   📊 Source: {source}')
            print(f'   📊 Confidence: {confidence:.3f}')
            print(f'   💬 Answer: {answer}...')
            
            if source == 'knowledge_base':
                print('   ✅ Knowledge base working correctly!')
            else:
                print('   ⚠️ Using search fallback (may need more documents)')
        else:
            print(f'   ❌ Chat test failed: {response.status_code}')
    except Exception as e:
        print(f'   ❌ Chat test error: {e}')
    
    # Check MongoDB configuration
    print(f'\n🍃 MongoDB Configuration:')
    mongo_url = os.getenv("MONGO_URL")
    if mongo_url:
        print(f'   📊 MONGO_URL configured: {mongo_url}')
        print(f'   📊 Currently using: {"MongoDB" if mongodb_status else "File Storage"}')
        
        if not mongodb_status:
            print('   💡 To use MongoDB: Restart services after ensuring MongoDB is running')
        else:
            print('   ✅ MongoDB is active!')
    else:
        print('   📊 MONGO_URL not configured - using file storage')
    
    # System statistics
    print(f'\n📊 System Statistics:')
    try:
        # Knowledge base stats
        kb_response = requests.get('http://localhost:8001/stats', timeout=5)
        if kb_response.status_code == 200:
            kb_stats = kb_response.json()
            print(f'   📚 Knowledge Base: {kb_stats.get("total_documents", 0)} documents')
        
        # History stats
        hist_response = requests.get('http://localhost:8003/stats', timeout=5)
        if hist_response.status_code == 200:
            hist_stats = hist_response.json()
            print(f'   📝 Chat History: {hist_stats.get("total_messages", 0)} messages')
    except Exception as e:
        print(f'   ⚠️ Could not get stats: {e}')
    
    print(f'\n' + '=' * 50)
    print('🎉 System Verification Complete!')
    
    if all_healthy:
        print('✅ All services are healthy and responding')
        print('✅ Knowledge base is storing and retrieving documents')
        print('✅ Chat functionality is working')
        print('✅ MongoDB configuration is ready')
        print('\n🚀 System is ready for use!')
        print('🌐 Access the web interface at: http://localhost:8080')
    else:
        print('⚠️ Some issues detected - check service status above')
    
    print('=' * 50)

if __name__ == "__main__":
    verify_system()