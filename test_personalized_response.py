#!/usr/bin/env python3
"""
Test Personalized Response with Conversation History
"""

import asyncio
import sys
import os
sys.path.append('.')

from agent_router_service.enhanced_agents import EnhancedAIAgent

async def test_personalized_response():
    """Test personalized response with conversation history"""
    print("🧪 Testing Personalized Response with Conversation History")
    print("=" * 60)
    
    # Create agent instance
    agent = EnhancedAIAgent()
    
    # Test user profile
    user_profile = {
        "first_name": "Sam",  # Use actual name
        "username": "demo_user",
        "phone_number": "6048135997",
        "preferred_contact_method": "sms",
        "ai_agent_personality": {"tone": "friendly", "emojis": True}
    }
    
    # Test conversation flow
    test_conversation = [
        "Hi, my name is Sam",
        "How are you doing today?",
        "Can you send me a beautiful motivational quote with my name?",
        "What did we talk about earlier?"
    ]
    
    user_id = "test_user_sam"
    
    for i, message in enumerate(test_conversation, 1):
        print(f"\n💬 Turn {i}: '{message}'")
        print("-" * 40)
        
        try:
            # Process the request
            result = await agent.process_user_request(user_id, message)
            
            if result.get("success"):
                response = result.get("response", "No response")
                print(f"✅ AI Response: {response}")
                
                # Check if name was extracted
                if "my name is" in message.lower():
                    print("🔍 Checking if name was extracted...")
                    # You can check the database here if needed
            else:
                print(f"❌ Error: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_personalized_response())
