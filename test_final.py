#!/usr/bin/env python3
"""
Final comprehensive test of the AI Assistant system
"""

import requests
import json

def test_complete_system():
    print('🚀 Testing Complete AI Assistant System')
    print('='*50)
    
    # Test 1: Knowledge base question
    print('\n1. 📚 Testing Knowledge Base Question:')
    r = requests.post('http://localhost:8000/chat', json={
        'chat_id': 'test-123',
        'message': 'What is artificial intelligence?'
    })
    print('Status:', r.status_code)
    if r.status_code == 200:
        result = r.json()
        print('✅ Source:', result['source'])
        print('✅ Answer:', result['response'][:150] + '...')
    else:
        print('❌ Error:', r.text)
    
    # Test 2: Machine Learning question
    print('\n2. 🤖 Testing Machine Learning Question:')
    r = requests.post('http://localhost:8000/chat', json={
        'chat_id': 'test-123',
        'message': 'What are the types of machine learning?'
    })
    print('Status:', r.status_code)
    if r.status_code == 200:
        result = r.json()
        print('✅ Source:', result['source'])
        print('✅ Answer:', result['response'][:150] + '...')
    else:
        print('❌ Error:', r.text)
    
    # Test 3: Search fallback question
    print('\n3. 🔍 Testing Search Fallback Question:')
    r = requests.post('http://localhost:8000/chat', json={
        'chat_id': 'test-123', 
        'message': 'What is the current weather?'
    })
    print('Status:', r.status_code)
    if r.status_code == 200:
        result = r.json()
        print('✅ Source:', result['source'])
        print('✅ Answer:', result['response'][:150] + '...')
    else:
        print('❌ Error:', r.text)
    
    # Test 4: Check conversation history
    print('\n4. 📝 Testing Conversation History:')
    r = requests.get('http://localhost:8000/chat/test-123')
    print('Status:', r.status_code)
    if r.status_code == 200:
        history = r.json()
        print(f'✅ Messages in history: {len(history["messages"])}')
        print('Recent messages:')
        for i, msg in enumerate(history['messages'][-6:]):  # Show last 6 messages
            sender = msg.get('sender', 'unknown')
            message = msg.get('message', '')[:50]
            print(f'  {i+1}. {sender}: {message}...')
    else:
        print('❌ Error:', r.text)
    
    # Test 5: Service health checks
    print('\n5. 🏥 Testing Service Health:')
    services = [
        ('Chat Service', 'http://localhost:8000/health'),
        ('Knowledge Base', 'http://localhost:8001/health'),
        ('Search Service', 'http://localhost:8002/health'),
        ('History Service', 'http://localhost:8003/health')
    ]
    
    for name, url in services:
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                print(f'✅ {name}: Healthy')
            else:
                print(f'⚠️  {name}: Status {r.status_code}')
        except Exception as e:
            print(f'❌ {name}: Failed - {e}')
    
    print('\n' + '='*50)
    print('🎉 System Test Complete!')
    print('='*50)

if __name__ == "__main__":
    test_complete_system()