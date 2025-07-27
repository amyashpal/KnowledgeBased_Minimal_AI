#!/usr/bin/env python3
"""
Test script to verify knowledge base persistence across restarts
"""

import requests
import json
import time
import os
import tempfile

def test_persistence():
    """Test that uploaded documents persist across service restarts"""
    print('🔄 Testing Knowledge Base Persistence')
    print('='*50)
    
    # Create a test document
    test_content = """
    This is a test document for persistence testing.
    It contains information about persistence functionality.
    The system should remember this content after restart.
    """
    
    print('\n1. 📤 Uploading test document...')
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_content)
        temp_path = f.name
    
    try:
        # Upload the test document
        with open(temp_path, 'rb') as file:
            files = {'files': ('persistence_test.txt', file, 'text/plain')}
            response = requests.post('http://localhost:8001/ingest', files=files, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Upload successful: {result['documents_added']} chunks added")
                print(f"   Files processed: {result['files_processed']}")
            else:
                print(f"❌ Upload failed: {response.status_code}")
                return False
    
    finally:
        os.unlink(temp_path)
    
    # Test query before restart
    print('\n2. 🔍 Testing query before restart...')
    response = requests.post('http://localhost:8000/chat', json={
        'chat_id': 'persistence-test',
        'message': 'What is this document about persistence?'
    }, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('source') == 'knowledge_base':
            print(f"✅ Query successful before restart: {result['response'][:100]}...")
            print(f"   Source: {result['source']}")
            print(f"   Confidence: {result.get('confidence', 0):.3f}")
        else:
            print(f"❌ Query didn't use knowledge base: {result.get('source')}")
            return False
    else:
        print(f"❌ Query failed: {response.status_code}")
        return False
    
    # Check if storage file exists
    print('\n3. 📁 Checking storage file...')
    storage_file = 'KnowledgeBased_Minimal_AI/knowledge_base_storage.json'
    if os.path.exists(storage_file):
        try:
            with open(storage_file, 'r', encoding='utf-8') as f:
                stored_data = json.load(f)
            print(f"✅ Storage file exists with {len(stored_data)} documents")
            
            # Check if our test document is in the storage
            test_found = False
            for doc in stored_data:
                if 'persistence' in doc.get('text', '').lower():
                    test_found = True
                    break
            
            if test_found:
                print("✅ Test document found in storage file")
            else:
                print("❌ Test document not found in storage file")
                return False
                
        except Exception as e:
            print(f"❌ Error reading storage file: {e}")
            return False
    else:
        print("❌ Storage file not found")
        return False
    
    print('\n4. ⚠️  Manual restart required!')
    print('   Please restart the services and run this test again to verify persistence.')
    print('   The system should still answer questions about the persistence document.')
    
    return True

def test_after_restart():
    """Test queries after restart to verify persistence"""
    print('\n🔄 Testing After Restart')
    print('='*30)
    
    # Test query after restart
    print('\n1. 🔍 Testing query after restart...')
    response = requests.post('http://localhost:8000/chat', json={
        'chat_id': 'persistence-test-after',
        'message': 'What is this document about persistence?'
    }, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('source') == 'knowledge_base':
            print(f"✅ Query successful after restart: {result['response'][:100]}...")
            print(f"   Source: {result['source']}")
            print(f"   Confidence: {result.get('confidence', 0):.3f}")
            print("🎉 PERSISTENCE TEST PASSED!")
            return True
        else:
            print(f"❌ Query didn't use knowledge base after restart: {result.get('source')}")
            print("❌ PERSISTENCE TEST FAILED!")
            return False
    else:
        print(f"❌ Query failed after restart: {response.status_code}")
        return False

def main():
    """Main test function"""
    # Check if services are running
    try:
        response = requests.get('http://localhost:8001/health', timeout=5)
        if response.status_code != 200:
            print("❌ Knowledge base service not running. Please start services first.")
            return
    except:
        print("❌ Knowledge base service not running. Please start services first.")
        return
    
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code != 200:
            print("❌ Chat service not running. Please start services first.")
            return
    except:
        print("❌ Chat service not running. Please start services first.")
        return
    
    # Check if this is a test after restart
    storage_file = 'KnowledgeBased_Minimal_AI/knowledge_base_storage.json'
    if os.path.exists(storage_file):
        try:
            with open(storage_file, 'r', encoding='utf-8') as f:
                stored_data = json.load(f)
            
            # Check if test document exists
            test_exists = False
            for doc in stored_data:
                if 'persistence' in doc.get('text', '').lower():
                    test_exists = True
                    break
            
            if test_exists:
                print("📋 Found existing test document. Testing after restart...")
                test_after_restart()
                return
        except:
            pass
    
    # Run initial persistence test
    test_persistence()

if __name__ == "__main__":
    main()