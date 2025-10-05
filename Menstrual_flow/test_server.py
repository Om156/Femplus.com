#!/usr/bin/env python3
"""
Test script to check if the FastAPI server is working correctly
"""

import requests
import json

def test_server():
    base_url = "http://localhost:8000"
    
    print("Testing FastAPI server...")
    
    try:
        # Test root endpoint
        print("1. Testing root endpoint...")
        response = requests.get(f"{base_url}/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        # Test gas sensor endpoint
        print("\n2. Testing gas sensor endpoint...")
        response = requests.get(f"{base_url}/data/gas-sensor/latest")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Data keys: {list(data.keys())}")
        else:
            print(f"   Error: {response.text}")
        
        # Test flow single endpoint
        print("\n3. Testing flow single endpoint...")
        payload = {
            "user_email": "test@example.com",
            "flow_ml": 10.0
        }
        response = requests.post(f"{base_url}/flow/single", json=payload)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {data}")
        else:
            print(f"   Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - server might not be running")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_server()
