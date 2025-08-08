#!/usr/bin/env python3
"""
SMS Test Script
This script helps you test SMS functionality with different services.
"""

import os
import sys
import asyncio
from typing import Dict, Any

# Add the project root to the path
sys.path.append(os.path.dirname(__file__))

from agent_router_service.enhanced_agents import EnhancedAIAgent

async def test_sms_services():
    """Test different SMS services"""
    print("🤖 SMS Service Test")
    print("=" * 50)
    
    # Initialize the enhanced agent
    agent = EnhancedAIAgent()
    
    # Test phone number (replace with your actual number)
    test_phone = "1234567890"  # Replace with your phone number
    test_message = "This is a test SMS from your AI assistant! 🤖"
    
    print(f"📱 Testing SMS to: {test_phone}")
    print(f"📝 Message: {test_message}")
    print()
    
    # Test 1: Twilio
    print("1️⃣ Testing Twilio SMS...")
    twilio_result = await test_twilio_sms(agent, test_phone, test_message)
    print(f"   Result: {twilio_result}")
    print()
    
    # Test 2: TextBelt
    print("2️⃣ Testing TextBelt SMS...")
    textbelt_result = await test_textbelt_sms(agent, test_phone, test_message)
    print(f"   Result: {textbelt_result}")
    print()
    
    # Test 3: Email-to-SMS
    print("3️⃣ Testing Email-to-SMS...")
    email_sms_result = await test_email_sms(agent, test_phone, test_message)
    print(f"   Result: {email_sms_result}")
    print()
    
    print("✅ SMS testing completed!")

async def test_twilio_sms(agent: EnhancedAIAgent, phone: str, message: str) -> Dict[str, Any]:
    """Test Twilio SMS sending"""
    try:
        # Check if Twilio is configured
        twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        if not all([twilio_account_sid, twilio_auth_token, twilio_phone_number]):
            return {
                "success": False,
                "error": "Twilio not configured. Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER environment variables."
            }
        
        # Import and test Twilio
        from twilio.rest import Client
        client = Client(twilio_account_sid, twilio_auth_token)
        
        # Send SMS
        sms = client.messages.create(
            body=message,
            from_=twilio_phone_number,
            to=phone
        )
        
        return {
            "success": True,
            "message": f"SMS sent via Twilio",
            "twilio_sid": sms.sid,
            "status": "sent"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Twilio error: {str(e)}"
        }

async def test_textbelt_sms(agent: EnhancedAIAgent, phone: str, message: str) -> Dict[str, Any]:
    """Test TextBelt SMS sending"""
    try:
        import httpx
        
        # Use TextBelt API with test key
        response = httpx.post(
            "https://textbelt.com/text",
            data={
                "phone": phone,
                "message": message,
                "key": "textbelt_test"  # Free test key
            },
            timeout=10.0
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                return {
                    "success": True,
                    "message": f"SMS sent via TextBelt",
                    "textbelt_id": result.get("textId"),
                    "status": "sent"
                }
            else:
                return {
                    "success": False,
                    "error": f"TextBelt error: {result.get('error')}"
                }
        else:
            return {
                "success": False,
                "error": f"TextBelt HTTP error: {response.status_code}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"TextBelt error: {str(e)}"
        }

async def test_email_sms(agent: EnhancedAIAgent, phone: str, message: str) -> Dict[str, Any]:
    """Test Email-to-SMS gateway"""
    try:
        # Carrier gateways
        carrier_gateways = {
            "verizon": f"{phone}@vtext.com",
            "att": f"{phone}@txt.att.net",
            "tmobile": f"{phone}@tmomail.net",
            "sprint": f"{phone}@messaging.sprintpcs.com"
        }
        
        print(f"   📧 Available gateways: {list(carrier_gateways.keys())}")
        
        # For now, just return info about available gateways
        return {
            "success": True,
            "message": "Email-to-SMS gateways available",
            "gateways": carrier_gateways,
            "note": "Email-to-SMS requires email service configuration"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Email-to-SMS error: {str(e)}"
        }

def check_environment():
    """Check environment variables for SMS services"""
    print("🔍 Checking SMS Service Configuration")
    print("=" * 40)
    
    # Check Twilio
    twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
    
    print("📱 Twilio Configuration:")
    print(f"   Account SID: {'✅ Set' if twilio_account_sid else '❌ Not set'}")
    print(f"   Auth Token: {'✅ Set' if twilio_auth_token else '❌ Not set'}")
    print(f"   Phone Number: {'✅ Set' if twilio_phone_number else '❌ Not set'}")
    
    if all([twilio_account_sid, twilio_auth_token, twilio_phone_number]):
        print("   🎉 Twilio is fully configured!")
    else:
        print("   ⚠️  Twilio is not fully configured")
    
    print()
    print("📧 TextBelt Configuration:")
    print("   TextBelt uses a free test key by default")
    print("   For production, get a paid API key from https://textbelt.com")
    print()
    
    print("📋 Next Steps:")
    print("1. Set up Twilio account at https://www.twilio.com")
    print("2. Get your Account SID and Auth Token")
    print("3. Purchase a phone number from Twilio")
    print("4. Set environment variables:")
    print("   export TWILIO_ACCOUNT_SID=your_account_sid")
    print("   export TWILIO_AUTH_TOKEN=your_auth_token")
    print("   export TWILIO_PHONE_NUMBER=your_twilio_number")
    print()

if __name__ == "__main__":
    print("🚀 SMS Service Test Suite")
    print("=" * 50)
    
    # Check environment first
    check_environment()
    
    # Ask user if they want to run tests
    response = input("Do you want to run SMS tests? (y/n): ").lower().strip()
    
    if response == 'y':
        # Get test phone number
        test_phone = input("Enter your phone number for testing (format: 1234567890): ").strip()
        
        if test_phone and len(test_phone) == 10:
            print(f"\n📱 Using phone number: {test_phone}")
            asyncio.run(test_sms_services())
        else:
            print("❌ Invalid phone number format. Please use 10 digits.")
    else:
        print("👋 Skipping SMS tests. Run again when ready!")
