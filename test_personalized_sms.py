#!/usr/bin/env python3
"""
Test Personalized SMS Message Generation
"""

import asyncio
import sys
import os
sys.path.append('.')

from agent_router_service.enhanced_agents import EnhancedAIAgent

async def test_personalized_sms():
    """Test personalized SMS message generation"""
    print("🧪 Testing Personalized SMS Message Generation")
    print("=" * 50)
    
    # Create agent instance
    agent = EnhancedAIAgent()
    
    # Test user profile
    user_profile = {
        "first_name": "Sam",
        "username": "demo_user",
        "phone_number": "6048135997",
        "preferred_contact_method": "sms",
        "ai_agent_personality": {"tone": "friendly", "emojis": True}
    }
    
    # Test different user requests
    test_requests = [
        "send me a beautiful motivational quote with my name",
        "send me an SMS reminder",
        "send me a motivational message",
        "send me a daily inspiration"
    ]
    
    for request in test_requests:
        print(f"\n📝 Testing request: '{request}'")
        print("-" * 40)
        
        try:
            # Generate personalized message
            personalized_message = await agent._generate_sms_message(request, user_profile)
            print(f"✅ Generated message: {personalized_message}")
            print(f"📏 Length: {len(personalized_message)} characters")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_personalized_sms())
