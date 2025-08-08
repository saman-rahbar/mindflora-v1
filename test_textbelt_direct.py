#!/usr/bin/env python3
"""
Direct TextBelt API Test
"""

import os
import httpx
import json

def test_textbelt_direct():
    """Test TextBelt API directly"""
    print("🧪 Testing TextBelt API Directly")
    print("=" * 40)
    
    # Get API key
    api_key = os.getenv("TEXTBELT_API_KEY")
    if not api_key:
        print("❌ TEXTBELT_API_KEY not found in environment")
        return
    
    print(f"✅ Using API key: {api_key[:10]}...")
    
    # Test phone number (replace with your actual number)
    phone_number = "6048135997"  # Replace with your actual number
    message = "Test SMS from MindFlora AI Assistant! 🤖"
    
    print(f"📱 Sending to: {phone_number}")
    print(f"💬 Message: {message}")
    
    try:
        # Make the request
        response = httpx.post(
            "https://textbelt.com/text",
            data={
                "phone": phone_number,
                "message": message,
                "key": api_key
            },
            timeout=10.0
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📄 Response JSON: {json.dumps(result, indent=2)}")
            
            if result.get("success"):
                print("✅ SMS sent successfully!")
                print(f"   Text ID: {result.get('textId')}")
                print(f"   Quota Remaining: {result.get('quotaRemaining')}")
            else:
                print("❌ SMS failed!")
                print(f"   Error: {result.get('error')}")
                print(f"   Quota Remaining: {result.get('quotaRemaining')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_textbelt_direct()
