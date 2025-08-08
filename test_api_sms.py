#!/usr/bin/env python3
"""
Test SMS through API
"""

import requests
import json

def test_api_sms():
    """Test SMS through the API"""
    print("🧪 Testing SMS through API")
    print("=" * 40)
    
    # Test data
    data = {
        "user_id": "demo_user",
        "message": "Send me an SMS reminder"
    }
    
    try:
        # Make request to the API
        response = requests.post(
            "http://localhost:8000/api/v1/ai-agents/enhanced-chat",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📄 Response JSON: {json.dumps(result, indent=2)}")
            
            # Check if SMS was sent
            if result.get("tool_actions", {}).get("sms_sent"):
                sms_result = result["tool_actions"]["sms_sent"]
                if isinstance(sms_result, dict) and sms_result.get("status") == "sent":
                    print("✅ SMS sent successfully through API!")
                    print(f"   Phone: {sms_result.get('phone_number')}")
                    print(f"   Service: {sms_result.get('service')}")
                else:
                    print("❌ SMS failed through API:")
                    print(f"   Result: {sms_result}")
            else:
                print("❌ No SMS action found in response")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_api_sms()
