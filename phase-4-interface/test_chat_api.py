#!/usr/bin/env python3
"""
Test script for GhostEnergy API Chat endpoint
"""

import requests
import json

# API Configuration
BASE_URL = "http://localhost:8000"
CHAT_ENDPOINT = f"{BASE_URL}/api/chat"

def test_chat_endpoint():
    """Test the chat endpoint with a sample request"""
    
    # Test data
    test_request = {
        "sede": "Sede Central",
        "pregunta": "¿Cuál es el consumo total de energía y cuántas anomalías críticas hay?"
    }
    
    print("👻 Testing GhostEnergy API Chat Endpoint")
    print("=" * 50)
    print(f"URL: {CHAT_ENDPOINT}")
    print(f"Request: {json.dumps(test_request, indent=2, ensure_ascii=False)}")
    print("\n" + "=" * 50)
    
    try:
        # Make the request
        response = requests.post(
            CHAT_ENDPOINT,
            json=test_request,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Success!")
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # Check if we got a valid response
            if "respuesta" in result:
                print("\n🤖 AI Response:")
                print(result["respuesta"])
            elif "error" in result:
                print(f"\n❌ Error: {result['error']}")
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the API server is running on localhost:8000")
        print("Run: cd phase-4-interface/api && python3 main.py")
    except requests.exceptions.Timeout:
        print("❌ Timeout: The request took too long. Check if Groq API is working.")
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")

def test_api_health():
    """Test if the API is running"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ API is running!")
            print(f"Health check: {response.json()}")
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ API is not running. Start it with: cd phase-4-interface/api && python3 main.py")
        return False
    except Exception as e:
        print(f"❌ Error checking API health: {str(e)}")
        return False

if __name__ == "__main__":
    # First check if API is running
    if test_api_health():
        print("\n")
        # Then test the chat endpoint
        test_chat_endpoint()
    
    print("\n" + "=" * 50)
    print("📝 Notes:")
    print("1. Make sure GROQ_API_KEY is configured in .env file")
    print("2. The API uses the last 500 anomaly records for context")
    print("3. Response time may vary depending on Groq API")
    print("4. Check phase-4-interface/api/main.py for implementation details")
