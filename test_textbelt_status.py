#!/usr/bin/env python3
"""
Check TextBelt API Key Status
"""

import os
import httpx
import json

def check_textbelt_status():
    """Check TextBelt API key status and quota"""
    print("🔍 Checking TextBelt API Key Status")
    print("=" * 40)
    
    # Get API key
    api_key = os.getenv("TEXTBELT_API_KEY")
    if not api_key:
        print("❌ TEXTBELT_API_KEY not found in environment")
        return
    
    print(f"✅ Using API key: {api_key[:10]}...")
    
    try:
        # Check quota by making a test request
        response = httpx.post(
            "https://textbelt.com/text",
            data={
                "phone": "1234567890",  # Test number
                "message": "Test",
                "key": api_key
            },
            timeout=10.0
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📄 Response JSON: {json.dumps(result, indent=2)}")
            
            if result.get("success"):
                print("✅ API key is working!")
                print(f"   Quota Remaining: {result.get('quotaRemaining')}")
            else:
                print("❌ API key issue:")
                print(f"   Error: {result.get('error')}")
                print(f"   Quota Remaining: {result.get('quotaRemaining')}")
                
                # Check if it's a quota issue
                if "quota" in result.get('error', '').lower():
                    print("\n💡 Solution: Get a new TextBelt API key")
                    print("   1. Visit: https://textbelt.com")
                    print("   2. Get a new free API key")
                    print("   3. Update your environment variable")
                elif "invalid" in result.get('error', '').lower():
                    print("\n💡 Solution: Check your API key")
                    print("   The API key might be invalid or expired")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    check_textbelt_status()
