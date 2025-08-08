#!/usr/bin/env python3
"""
Simple SMS Test - No database dependencies
"""

import os
import httpx
import asyncio

async def test_textbelt_sms():
    """Test TextBelt SMS sending"""
    print("📱 Testing TextBelt SMS...")
    
    # Get API key from environment or use test key
    api_key = os.getenv("TEXTBELT_API_KEY", "textbelt_test")
    
    # Test phone number (replace with yours)
    phone = input("Enter your phone number (10 digits): ").strip()
    if not phone or len(phone) != 10:
        print("❌ Invalid phone number. Please use 10 digits.")
        return
    
    message = "This is a test SMS from your AI assistant! 🤖"
    
    try:
        print(f"📤 Sending SMS to {phone}...")
        
        response = httpx.post(
            "https://textbelt.com/text",
            data={
                "phone": phone,
                "message": message,
                "key": api_key
            },
            timeout=10.0
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ SMS sent successfully!")
                print(f"   TextBelt ID: {result.get('textId')}")
                print("📱 Check your phone for the message!")
            else:
                print("❌ SMS failed to send")
                print(f"   Error: {result.get('error')}")
        else:
            print(f"❌ HTTP error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

async def test_twilio_sms():
    """Test Twilio SMS sending"""
    print("📱 Testing Twilio SMS...")
    
    # Check if Twilio is configured
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_number = os.getenv("TWILIO_PHONE_NUMBER")
    
    if not all([account_sid, auth_token, twilio_number]):
        print("❌ Twilio not configured. Set environment variables:")
        print("   TWILIO_ACCOUNT_SID")
        print("   TWILIO_AUTH_TOKEN") 
        print("   TWILIO_PHONE_NUMBER")
        return
    
    # Test phone number
    phone = input("Enter your phone number (10 digits): ").strip()
    if not phone or len(phone) != 10:
        print("❌ Invalid phone number. Please use 10 digits.")
        return
    
    message = "This is a test SMS from your AI assistant! 🤖"
    
    try:
        from twilio.rest import Client
        
        client = Client(account_sid, auth_token)
        
        print(f"📤 Sending SMS to {phone}...")
        
        sms = client.messages.create(
            body=message,
            from_=twilio_number,
            to=phone
        )
        
        print("✅ SMS sent successfully!")
        print(f"   Twilio SID: {sms.sid}")
        print("📱 Check your phone for the message!")
        
    except Exception as e:
        print(f"❌ Twilio error: {e}")

def check_config():
    """Check current SMS configuration"""
    print("🔍 SMS Configuration Check")
    print("=" * 30)
    
    # Check TextBelt
    textbelt_key = os.getenv("TEXTBELT_API_KEY")
    print(f"📧 TextBelt API Key: {'✅ Set' if textbelt_key else '❌ Not set'}")
    
    # Check Twilio
    twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
    twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_number = os.getenv("TWILIO_PHONE_NUMBER")
    
    print(f"📱 Twilio Account SID: {'✅ Set' if twilio_sid else '❌ Not set'}")
    print(f"📱 Twilio Auth Token: {'✅ Set' if twilio_token else '❌ Not set'}")
    print(f"📱 Twilio Phone Number: {'✅ Set' if twilio_number else '❌ Not set'}")
    
    print()
    
    if textbelt_key:
        print("🎉 TextBelt is ready to use!")
        return "textbelt"
    elif all([twilio_sid, twilio_token, twilio_number]):
        print("🎉 Twilio is ready to use!")
        return "twilio"
    else:
        print("⚠️  No SMS service is configured")
        return None

async def main():
    """Main function"""
    print("🚀 Simple SMS Test")
    print("=" * 20)
    
    # Check configuration
    service = check_config()
    
    if not service:
        print("\n📋 Setup Instructions:")
        print("1. For TextBelt (free): Get API key from https://textbelt.com")
        print("2. For Twilio (reliable): Sign up at https://www.twilio.com")
        print("3. Set environment variables and run this script again")
        return
    
    print(f"\n🎯 Testing {service.upper()} SMS...")
    
    if service == "textbelt":
        await test_textbelt_sms()
    elif service == "twilio":
        await test_twilio_sms()

if __name__ == "__main__":
    asyncio.run(main())
