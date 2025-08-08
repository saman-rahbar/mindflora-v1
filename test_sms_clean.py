#!/usr/bin/env python3
"""
Test SMS with Cleaned Phone Number
"""

import os
import re
import httpx
import json

def test_sms_clean():
    """Test SMS sending with cleaned phone number"""
    print("🧪 Testing SMS with Cleaned Phone Number")
    print("=" * 40)
    
    # Get API key
    api_key = os.getenv("TEXTBELT_API_KEY")
    if not api_key:
        print("❌ TEXTBELT_API_KEY not found in environment")
        return
    
    print(f"✅ Using API key: {api_key[:10]}...")
    
    # Test phone number (with potential spaces)
    phone_number = " 6048135997 "  # Simulate the issue
    message = "Test SMS from MindFlora AI Assistant! 🤖"
    
    # Clean the phone number
    cleaned_phone = re.sub(r'[^\d]', '', phone_number)
    
    print(f"📱 Original phone: '{phone_number}'")
    print(f"📱 Cleaned phone: '{cleaned_phone}'")
    print(f"💬 Message: {message}")
    
    try:
        # Make the request with cleaned phone number
        response = httpx.post(
            "https://textbelt.com/text",
            data={
                "phone": cleaned_phone,
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
                print(f"   Phone Used: {cleaned_phone}")
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
    test_sms_clean()
