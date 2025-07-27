#!/usr/bin/env python3
"""
Comprehensive test of the enhanced knowledge base functionality
Tests document upload, storage, retrieval, and search prioritization
"""

import requests
import json
import time
import os
import tempfile

def create_test_documents():
    """Create test documents with different content"""
    documents = {
        "python_basics.txt": """
Python is a high-level programming language known for its simplicity and readability.
Python supports multiple programming paradigms including procedural, object-oriented, and functional programming.
Python has a large standard library and extensive third-party packages available through pip.
Python is widely used in web development, data science, artificial intelligence, and automation.
        """.strip(),
        
        "machine_learning.txt": """
Machine learning is a subset of artificial intelligence that enables computers to learn without explicit programming.
There are three main types of machine learning: supervised learning, unsupervised learning, and reinforcement learning.
Supervised learning uses labeled data to train models for prediction tasks.
Unsupervised learning finds patterns in data without labeled examples.
Reinforcement learning learns through interaction with an environment using rewards and penalties.
        """.strip(),
        
        "web_development.txt": """
Web development involves creating websites and web applications for the internet.
Frontend development focuses on user interface and user experience using HTML, CSS, and JavaScript.
Backend development handles server-side logic, databases, and API development.
Full-stack developers work on both frontend and backend components.
Modern web development uses frameworks like React, Vue.js, Django, and Flask.
        """.strip(),
        
        "data_science.txt": """
Data science combines statistics, programming, and domain expertise to extract insights from data.
The data science process includes data collection, cleaning, analysis, and visualization.
Popular tools for data science include Python, R, SQL, and various libraries like pandas and numpy.
Data scientists use machine learning algorithms to build predictive models.
Data visualization helps communicate findings through charts, graphs, and dashboards.
        """.strip()
    }
    return documents

def upload_test_documents():
    """Upload test documents to the knowledge base"""
    print("📤 Uploading test documents...")
    
    documents = create_test_documents()
    uploaded_files = []
    
    for filename, content in documents.items():
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            # Upload file
            with open(temp_path, 'rb') as file:
                files = {'files': (filename, file, 'text/plain')}
                response = requests.post('http://localhost:8001/ingest', files=files, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Uploaded {filename}: {result['documents_added']} chunks added")
                    uploaded_files.append(filename)
                else:
                    print(f"❌ Failed to upload {filename}: {response.status_code}")
                    print(f"   Error: {response.text}")
        
        finally:
            # Clean up temporary file
            os.unlink(temp_path)
    
    return uploaded_files

def test_knowledge_base_queries():
    """Test queries that should find answers in different uploaded documents"""
    test_queries = [
        {
            "query": "What is Python programming language?",
            "expected_source": "knowledge_base",
            "expected_in_answer": ["python", "programming", "language"],
            "document": "python_basics.txt"
        },
        {
            "query": "What are the types of machine learning?",
            "expected_source": "knowledge_base", 
            "expected_in_answer": ["supervised", "unsupervised", "reinforcement"],
            "document": "machine_learning.txt"
        },
        {
            "query": "What is frontend development?",
            "expected_source": "knowledge_base",
            "expected_in_answer": ["frontend", "user interface", "HTML", "CSS", "JavaScript"],
            "document": "web_development.txt"
        },
        {
            "query": "What tools are used in data science?",
            "expected_source": "knowledge_base",
            "expected_in_answer": ["python", "pandas", "numpy", "data science"],
            "document": "data_science.txt"
        },
        {
            "query": "How does reinforcement learning work?",
            "expected_source": "knowledge_base",
            "expected_in_answer": ["reinforcement", "rewards", "environment"],
            "document": "machine_learning.txt"
        }
    ]
    
    print(f"\n🧪 Testing {len(test_queries)} knowledge base queries...")
    
    passed_tests = 0
    failed_tests = 0
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n{i}. Testing: '{test['query']}'")
        
        try:
            # Query through chat service (tests full integration)
            response = requests.post('http://localhost:8000/chat', json={
                'chat_id': f'test-kb-{i}',
                'message': test['query']
            }, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                source = result.get('source', '')
                answer = result.get('response', '').lower()
                confidence = result.get('confidence', 0)
                source_docs = result.get('source_documents', [])
                
                print(f"   📊 Source: {source}")
                print(f"   📊 Confidence: {confidence:.3f}")
                print(f"   📊 Source docs: {source_docs}")
                print(f"   💬 Answer: {answer[:100]}...")
                
                # Check if answer came from knowledge base
                if source == "knowledge_base":
                    print("   ✅ Correctly used knowledge base")
                    
                    # Check if expected keywords are in the answer
                    found_keywords = []
                    for keyword in test['expected_in_answer']:
                        if keyword.lower() in answer:
                            found_keywords.append(keyword)
                    
                    if len(found_keywords) >= 2:  # At least 2 keywords should match
                        print(f"   ✅ Found expected keywords: {found_keywords}")
                        passed_tests += 1
                    else:
                        print(f"   ❌ Missing expected keywords. Found: {found_keywords}")
                        print(f"      Expected: {test['expected_in_answer']}")
                        failed_tests += 1
                else:
                    print(f"   ❌ Expected knowledge_base but got: {source}")
                    failed_tests += 1
            else:
                print(f"   ❌ Request failed: {response.status_code}")
                failed_tests += 1
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            failed_tests += 1
    
    return passed_tests, failed_tests

def test_search_fallback():
    """Test that search fallback works for queries not in knowledge base"""
    print(f"\n🔍 Testing search fallback...")
    
    fallback_query = "What is the current weather in New York?"
    
    try:
        response = requests.post('http://localhost:8000/chat', json={
            'chat_id': 'test-fallback',
            'message': fallback_query
        }, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            source = result.get('source', '')
            
            if source.startswith('search_') or source == 'fallback':
                print(f"   ✅ Correctly fell back to search: {source}")
                return True
            else:
                print(f"   ❌ Expected search fallback but got: {source}")
                return False
        else:
            print(f"   ❌ Request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_knowledge_base_stats():
    """Test knowledge base statistics"""
    print(f"\n📊 Testing knowledge base statistics...")
    
    try:
        response = requests.get('http://localhost:8001/stats', timeout=10)
        
        if response.status_code == 200:
            stats = response.json()
            total_docs = stats.get('total_documents', 0)
            using_embeddings = stats.get('using_embeddings', False)
            
            print(f"   📈 Total documents: {total_docs}")
            print(f"   🧠 Using embeddings: {using_embeddings}")
            
            if total_docs > 0:
                print("   ✅ Knowledge base contains documents")
                return True
            else:
                print("   ❌ Knowledge base appears empty")
                return False
        else:
            print(f"   ❌ Stats request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_duplicate_upload():
    """Test that duplicate uploads are handled properly"""
    print(f"\n🔄 Testing duplicate upload handling...")
    
    # Create a simple test document
    test_content = "This is a test document for duplicate detection."
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_content)
        temp_path = f.name
    
    try:
        # Upload the same file twice
        for attempt in [1, 2]:
            with open(temp_path, 'rb') as file:
                files = {'files': ('duplicate_test.txt', file, 'text/plain')}
                response = requests.post('http://localhost:8001/ingest', files=files, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    docs_added = result.get('documents_added', 0)
                    duplicates_skipped = result.get('duplicates_skipped', 0)
                    
                    print(f"   Attempt {attempt}: {docs_added} added, {duplicates_skipped} skipped")
                    
                    if attempt == 1 and docs_added > 0:
                        print("   ✅ First upload successful")
                    elif attempt == 2 and duplicates_skipped > 0:
                        print("   ✅ Duplicate detection working")
                        return True
                else:
                    print(f"   ❌ Upload {attempt} failed: {response.status_code}")
        
        return False
        
    finally:
        os.unlink(temp_path)

def main():
    """Run comprehensive knowledge base tests"""
    print('🚀 Comprehensive Knowledge Base Test Suite')
    print('='*60)
    
    # Test service health first
    print('\n🏥 Checking service health...')
    services = [
        ('Knowledge Base', 'http://localhost:8001/health'),
        ('Chat Service', 'http://localhost:8000/health'),
        ('Search Service', 'http://localhost:8002/health')
    ]
    
    all_healthy = True
    for name, url in services:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f'   ✅ {name}: Healthy')
            else:
                print(f'   ❌ {name}: Status {response.status_code}')
                all_healthy = False
        except Exception as e:
            print(f'   ❌ {name}: Failed - {e}')
            all_healthy = False
    
    if not all_healthy:
        print("\n❌ Some services are not healthy. Please start all services first.")
        return
    
    # Upload test documents
    uploaded_files = upload_test_documents()
    if not uploaded_files:
        print("\n❌ Failed to upload test documents")
        return
    
    # Wait a moment for indexing
    print("\n⏳ Waiting for indexing...")
    time.sleep(2)
    
    # Test knowledge base statistics
    stats_ok = test_knowledge_base_stats()
    
    # Test knowledge base queries
    passed, failed = test_knowledge_base_queries()
    
    # Test search fallback
    fallback_ok = test_search_fallback()
    
    # Test duplicate handling
    duplicate_ok = test_duplicate_upload()
    
    # Summary
    print('\n' + '='*60)
    print('📋 TEST SUMMARY')
    print('='*60)
    print(f'📤 Documents uploaded: {len(uploaded_files)}')
    print(f'📊 Statistics test: {"✅ PASS" if stats_ok else "❌ FAIL"}')
    print(f'🧪 Knowledge base queries: {passed} passed, {failed} failed')
    print(f'🔍 Search fallback: {"✅ PASS" if fallback_ok else "❌ FAIL"}')
    print(f'🔄 Duplicate handling: {"✅ PASS" if duplicate_ok else "❌ FAIL"}')
    
    total_tests = 1 + passed + failed + 1 + 1  # stats + queries + fallback + duplicate
    total_passed = (1 if stats_ok else 0) + passed + (1 if fallback_ok else 0) + (1 if duplicate_ok else 0)
    
    print(f'\n🎯 OVERALL: {total_passed}/{total_tests} tests passed')
    
    if total_passed == total_tests:
        print('🎉 ALL TESTS PASSED! Knowledge base is working correctly.')
    else:
        print('⚠️  Some tests failed. Please check the issues above.')
    
    print('='*60)

if __name__ == "__main__":
    main()