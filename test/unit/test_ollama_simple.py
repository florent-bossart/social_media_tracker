#!/usr/bin/env python3
"""
Simple test for Ollama API connection
"""

import requests
import json
import time

def test_ollama_simple():
    """Test basic Ollama functionality"""
    print("🧪 Testing Ollama API")
    print("=" * 30)

    url = "http://localhost:11434/api/generate"

    # Simple test
    payload = {
        "model": "llama3:latest",
        "prompt": "Extract entities from: 'I love YOASOBI music!' Return JSON: {\"artists\": [\"YOASOBI\"]}",
        "stream": False,
        "format": "json"
    }

    print("🔍 Testing simple entity extraction...")
    start_time = time.time()

    try:
        response = requests.post(url, json=payload, timeout=120)
        elapsed = time.time() - start_time

        print(f"⏱️  Response time: {elapsed:.1f}s")

        if response.status_code == 200:
            result = response.json()
            print("✅ Raw response:")
            print(json.dumps(result, indent=2))

            if 'response' in result:
                try:
                    entities = json.loads(result['response'])
                    print("✅ Parsed entities:", entities)
                except json.JSONDecodeError as e:
                    print(f"❌ JSON parse error: {e}")
                    print(f"Raw response text: {result['response']}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(response.text)

    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_ollama_simple()
