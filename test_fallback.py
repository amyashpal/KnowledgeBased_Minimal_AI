#!/usr/bin/env python3
"""
Test script to verify knowledge base -> search fallback mechanism
"""

import requests
import json
import time

def test_fallback_mechanism():
    print('🔄 Testing Knowledge Base -> Search Fallback Mechanism')
    print('='*60)
    
    # Test cases: [question, expected_source]
    test_cases = [
        ("What is artificial intelligence?", "knowledge_base"),  # Should be in KB
        ("What is machine learning?", "knowledge_base"),        # Should be in KB  
        ("Who is the CEO of Google?", "search"),                # Should fallback to search
        ("What's the weather today?", "search"),                # Should fallback to search
        ("Who is Mandeep?", "knowledge_base"),                  # Should be in KB
        ("What is the capital of Mars?", "search"),             # Should fallback to search
    ]
    
    for i, (question, expected_source) in enumerate(test_cases, 1):
        print(f'\n{i}. Testing: "{question}"')
        print('-' * 50)
        
        try:
            # Make request to chat service
            response = requests.post('http://localhost:8000/chat', json={
                'chat_id': f'test-fallback-{i}',
                'message': question
            }, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                actual_source = result['source']
                answer = result['response']
                
                # Check if source matches expectation
                if actual_source == expected_source:
                    print(f'✅ Source: {actual_source} (Expected: {expected_source})')
                else:
                    print(f'⚠️  Source: {actual_source} (Expected: {expected_source})')
                
                print(f'📝 Answer: {answer[:100]}{"..." if len(answer) > 100 else ""}')
                
                # Show the flow
                if actual_source == "knowledge_base":
                    print('🔍 Flow: Knowledge Base ✅ → (Search skipped)')
                elif actual_source == "search":
                    print('🔍 Flow: Knowledge Base ❌ → Search ✅')
                else:
                    print(f'🔍 Flow: Unknown source: {actual_source}')
                    
            else:
                print(f'❌ HTTP Error: {response.status_code}')
                print(f'   Response: {response.text}')
                
        except requests.exceptions.ConnectionError:
            print('❌ Connection Error: Make sure services are running')
            print('   Run: python run_services.py')
            break
        except Exception as e:
            print(f'❌ Error: {e}')
        
        # Small delay between requests
        time.sleep(1)
    
    print('\n' + '='*60)
    print('🎯 Fallback Test Complete!')
    print('\nExpected behavior:')
    print('• Knowledge base questions → source: "knowledge_base"')
    print('• Unknown questions → source: "search" (DuckDuckGo)')
    print('• Failed searches → source: "fallback"')
    print('='*60)

def test_individual_services():
    """Test individual services to debug issues"""
    print('\n🔧 Testing Individual Services:')
    print('-' * 40)
    
    # Test knowledge base directly
    print('\n1. Testing Knowledge Base Service:')
    try:
        response = requests.get('http://localhost:8001/query', 
                              params={'text': 'What is artificial intelligence?'})
        if response.status_code == 200:
            result = response.json()
            print(f'   ✅ KB Response: relevant={result["relevant"]}, confidence={result["confidence"]:.2f}')
            print(f'   📝 Answer: {result["answer"][:80]}...')
        else:
            print(f'   ❌ KB Error: {response.status_code}')
    except Exception as e:
        print(f'   ❌ KB Exception: {e}')
    
    # Test search service directly  
    print('\n2. Testing Search Service:')
    try:
        response = requests.get('http://localhost:8002/search',
                              params={'query': 'Who is the CEO of Google?'})
        if response.status_code == 200:
            result = response.json()
            print(f'   ✅ Search Response: source={result["source"]}')
            print(f'   📝 Answer: {result["answer"][:80]}...')
        else:
            print(f'   ❌ Search Error: {response.status_code}')
    except Exception as e:
        print(f'   ❌ Search Exception: {e}')

if __name__ == "__main__":
    test_fallback_mechanism()
    test_individual_services()