#!/usr/bin/env python3
"""
Test Name Extraction and Database Updates
"""
import asyncio
import sys
import os
sys.path.append('.')
from agent_router_service.enhanced_agents import EnhancedAIAgent

async def test_name_extraction():
    """Test name extraction and database updates"""
    print("🧪 Testing Name Extraction and Database Updates")
    
    # Initialize the agent
    agent = EnhancedAIAgent()
    
    # Test name extraction
    test_messages = [
        "Hi My name is Sam send me a motivational quote",
        "my name is Sam",
        "I am Sam",
        "call me Sam"
    ]
    
    print("\n📝 Testing name extraction:")
    for message in test_messages:
        name = agent._extract_name_from_message(message)
        print(f"  '{message}' -> {name}")
    
    # Test user profile update
    user_id = "demo_user"
    message = "Hi My name is Sam send me a motivational quote"
    
    print(f"\n👤 Testing user profile update for user_id: {user_id}")
    
    # Get initial profile
    initial_profile = await agent._get_user_profile(user_id)
    print(f"  Initial profile - First Name: {initial_profile.get('first_name', 'None')}")
    
    # Update contact info
    print(f"  Updating contact info with message: '{message}'")
    contact_updated = await agent._update_user_contact_info(user_id, {"primary_action": "chat"}, message)
    print(f"  Contact updated: {contact_updated}")
    
    # Get updated profile
    updated_profile = await agent._get_user_profile(user_id)
    print(f"  Updated profile - First Name: {updated_profile.get('first_name', 'None')}")
    
    # Test SMS message generation
    print(f"\n📱 Testing SMS message generation:")
    sms_message = await agent._generate_sms_message("send me a motivational quote", updated_profile)
    print(f"  Generated SMS: {sms_message}")
    print(f"  SMS length: {len(sms_message)} characters")

if __name__ == "__main__":
    asyncio.run(test_name_extraction())
