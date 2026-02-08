#!/usr/bin/env python3
"""
Test script for Document Analyzer API
Tests all endpoints and functionality
"""
import sys
import time
import requests
from pathlib import Path

API_BASE = "http://localhost:8000"

def test_health():
    """Test health endpoint."""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            print("✓ Health check passed")
            data = response.json()
            print(f"  Status: {data.get('status')}")
            print(f"  Model: {data.get('model')}")
            return True
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Cannot connect to API: {e}")
        print("  Make sure backend is running on port 8000")
        return False


def test_analyze(file_path):
    """Test document analysis."""
    print(f"\nTesting document analysis with: {file_path}")
    
    # Check if file exists
    if not Path(file_path).exists():
        print(f"✗ File not found: {file_path}")
        return False
    
    try:
        # Upload file
        print("  Uploading file...")
        with open(file_path, 'rb') as f:
            files = {'file': (Path(file_path).name, f)}
            response = requests.post(f"{API_BASE}/api/analyze", files=files)
        
        if response.status_code != 200:
            print(f"✗ Upload failed: {response.status_code}")
            print(f"  {response.text}")
            return False
        
        data = response.json()
        job_id = data.get('job_id')
        print(f"✓ File uploaded, job ID: {job_id}")
        
        # Poll for completion
        print("  Waiting for analysis to complete...")
        max_wait = 60  # seconds
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            status_response = requests.get(f"{API_BASE}/api/status/{job_id}")
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data.get('status')
                
                if status == 'completed':
                    print(f"✓ Analysis completed!")
                    print(f"  Pages: {status_data.get('page_count')}")
                    
                    # Get results
                    results_response = requests.get(f"{API_BASE}/api/results/{job_id}")
                    if results_response.status_code == 200:
                        print("✓ Results retrieved successfully")
                        results = results_response.json()
                        
                        # Show sample data
                        if results.get('results'):
                            first_result = results['results'][0]
                            doc_type = first_result.get('document_classification', {}).get('type', 'N/A')
                            language = first_result.get('document_classification', {}).get('primary_language', 'N/A')
                            print(f"  Document type: {doc_type}")
                            print(f"  Language: {language}")
                        
                        return True
                    else:
                        print(f"✗ Failed to get results: {results_response.status_code}")
                        return False
                
                elif status == 'failed':
                    print(f"✗ Analysis failed: {status_data.get('error')}")
                    return False
                
                else:
                    print(f"  Status: {status}...")
                    time.sleep(2)
            else:
                print(f"✗ Status check failed: {status_response.status_code}")
                return False
        
        print("✗ Analysis timed out")
        return False
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


def test_list_jobs():
    """Test list jobs endpoint."""
    print("\nTesting list jobs endpoint...")
    try:
        response = requests.get(f"{API_BASE}/api/jobs")
        if response.status_code == 200:
            data = response.json()
            jobs = data.get('jobs', [])
            print(f"✓ Found {len(jobs)} jobs")
            return True
        else:
            print(f"✗ List jobs failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 50)
    print("Document Analyzer API Tests")
    print("=" * 50)
    
    # Test health
    if not test_health():
        print("\n✗ Health check failed. Backend may not be running.")
        sys.exit(1)
    
    # Test list jobs
    test_list_jobs()
    
    # Test analysis (if file provided)
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        test_analyze(file_path)
    else:
        print("\nSkipping analysis test (no file provided)")
        print("Usage: python test_api.py <path-to-document>")
    
    print("\n" + "=" * 50)
    print("Tests completed!")
    print("=" * 50)


if __name__ == "__main__":
    main()
