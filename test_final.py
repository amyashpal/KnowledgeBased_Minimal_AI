#!/usr/bin/env python3
"""
Final clean test of the AI Assistant system
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
        'message': 'What is Python programming language?'
    })
    print('Status:', r.status_code)
    if r.status_code == 200:
        result = r.json()
        print('✅ Source:', result['source'])
        print('✅ Answer:', result['response'][:150] + '...')
    else:
        print('❌ Error:', r.text)
    
    # Test 2: Search fallback question
    print('\n2. 🔍 Testing Search Fallback Question:')
    r = requests.post('http://localhost:8000/chat', json={
        'chat_id': 'test-123', 
        'message': 'What is the capital of France?'
    })
    print('Status:', r.status_code)
    if r.status_code == 200:
        result = r.json()
        print('✅ Source:', result['source'])
        print('✅ Answer:', result['response'][:150] + '...')
    else:
        print('❌ Error:', r.text)
    
    # Test 3: Service health checks
    print('\n3. 🏥 Testing Service Health:')
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
                data = r.json()
                if name == 'History Service':
                    mongodb_status = "MongoDB" if data.get('using_mongodb') else "File Storage"
                    print(f'✅ {name}: Healthy ({mongodb_status})')
                else:
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