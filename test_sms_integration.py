#!/usr/bin/env python3
"""
Test SMS Integration
"""

import asyncio
import os
import sys

# Add project root to path
sys.path.append('.')

from agent_router_service.enhanced_agents import EnhancedAIAgent

async def test_sms_integration():
    """Test SMS integration"""
    print("🧪 Testing SMS Integration")
    print("=" * 40)
    
    # Set up environment
    os.environ["TEXTBELT_API_KEY"] = "1da744a12ee14d51d8f48d88cdbd864dba5482d9m74wkDcWwTKLRsSTbkZjSlUym"
    
    # Create agent
    agent = EnhancedAIAgent()
    
    # Test 1: Process user request with phone number
    print("\n1️⃣ Testing phone number setup...")
    result1 = await agent.process_user_request(
        user_id="test_user",
        message="My phone number is 1234567890"
    )
    
    print(f"Result 1: {result1['success']}")
    print(f"Response: {result1['response']}")
    print(f"Intent: {result1['intent']['primary_action']}")
    print(f"Tool Actions: {result1['tool_actions']}")
    
    # Test 2: Process SMS request
    print("\n2️⃣ Testing SMS request...")
    result2 = await agent.process_user_request(
        user_id="test_user",
        message="Send me an SMS reminder"
    )
    
    print(f"Result 2: {result2['success']}")
    print(f"Response: {result2['response']}")
    print(f"Intent: {result2['intent']['primary_action']}")
    print(f"Tool Actions: {result2['tool_actions']}")
    
    # Test 3: Direct SMS sending
    print("\n3️⃣ Testing direct SMS sending...")
    sms_result = await agent.send_sms(
        user_id="test_user",
        message="This is a test SMS from your AI assistant! 🤖"
    )
    
    print(f"SMS Result: {sms_result}")
    
    print("\n✅ SMS integration test completed!")

if __name__ == "__main__":
    asyncio.run(test_sms_integration())
