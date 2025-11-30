#!/usr/bin/env python3
"""
Test Gemini API Connection
Run: python3 scripts/test_gemini.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import GEMINI_API_KEY, GEMINI_MODEL, EMBEDDING_MODEL

def test_gemini():
    print("=" * 50)
    print("Gemini API Test")
    print("=" * 50)

    # Check API key
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY not set in .env")
        return False
    print(f"✓ API Key found (ends with ...{GEMINI_API_KEY[-4:]})")
    print(f"✓ Chat model: {GEMINI_MODEL}")
    print(f"✓ Embedding model: {EMBEDDING_MODEL}")

    # Test imports
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        print("✓ google.generativeai imported and configured")
    except ImportError:
        print("❌ google-generativeai not installed. Run: pip install google-generativeai")
        return False

    # Test 1: Text generation
    print("\n--- Test 1: Text Generation ---")
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content("Say 'Hello from Gemini!' in exactly 5 words.")
        print(f"✓ Response: {response.text.strip()}")
    except Exception as e:
        print(f"❌ Text generation failed: {e}")
        return False

    # Test 2: Embedding generation
    print("\n--- Test 2: Embedding Generation ---")
    try:
        test_text = "Software Engineer at Google, Computer Science major, interested in AI and Machine Learning"
        result = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=test_text,
            task_type="retrieval_document"
        )
        embedding = result['embedding']
        print(f"✓ Embedding generated: {len(embedding)} dimensions")
        print(f"  First 5 values: {embedding[:5]}")
    except Exception as e:
        print(f"❌ Embedding generation failed: {e}")
        return False

    print("\n" + "=" * 50)
    print("✓ All tests passed! Gemini API is working.")
    print("=" * 50)
    return True

if __name__ == "__main__":
    success = test_gemini()
    sys.exit(0 if success else 1)
