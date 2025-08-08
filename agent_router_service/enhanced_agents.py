import asyncio
import json
import re
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from database.models import User
from database.connection import get_db
from llm_service.llm_client import create_llm_client

class EnhancedAIAgent:
    """Enhanced AI Agent with SMS, Email, and Database Integration"""
    
    def __init__(self):
        self.llm_client = create_llm_client()
        self.conversation_history = {}  # Store conversation history per user
        self.personality_traits = {
            "friendly": {
                "greeting": "Hey there! 👋",
                "emoji_style": "frequent",
                "tone": "warm and supportive"
            },
            "professional": {
                "greeting": "Hello!",
                "emoji_style": "minimal",
                "tone": "professional yet caring"
            },
            "casual": {
                "greeting": "Hi! 😊",
                "emoji_style": "moderate",
                "tone": "casual and friendly"
            }
        }
    
    async def process_user_request(self, user_id: str, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process user request with enhanced capabilities"""
        try:
            # Get user profile from database
            user_profile = await self._get_user_profile(user_id)
            
            # Analyze user intent
            intent = await self._analyze_intent(message, user_profile)
            
            # Update user profile if new contact info is provided
            contact_updated = await self._update_user_contact_info(user_id, intent, message)
            
            # Get updated user profile after contact info update
            if contact_updated:
                user_profile = await self._get_user_profile(user_id)
            
            # Handle tool requests (SMS, Email, etc.)
            tool_actions = await self._handle_tool_requests(intent, user_profile, message)
            
            # Generate personalized response with conversation history
            response = await self._generate_personalized_response(message, user_profile, intent, user_id)
            
            # Update conversation history
            self._update_conversation_history(user_id, message, response)
            
            # If there are tool actions but they're just setup confirmations, don't show them in the main response
            if tool_actions and intent["primary_action"] == "setup_sms" and contact_updated:
                # Don't include tool actions for successful setup
                tool_actions = {}
            
            return {
                "success": True,
                "response": response,
                "intent": intent,
                "tool_actions": tool_actions,
                "user_profile_updated": contact_updated
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": "I'm having a moment! 😅 Let me try again..."
            }
    
    async def _get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile from database"""
        try:
            db = next(get_db())
            try:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    # Clean phone number if it exists
                    phone_number = user.phone_number
                    if phone_number:
                        phone_number = re.sub(r'[^\d]', '', phone_number)
                    
                    # Debug: Print user info
                    print(f"Retrieved user profile - ID: {user.id}, First Name: {user.first_name}, Username: {user.username}")
                    
                    return {
                        "id": user.id,
                        "username": user.username,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "email": user.email,
                        "phone_number": phone_number,
                        "preferred_contact_method": user.preferred_contact_method,
                        "notification_preferences": user.notification_preferences or {},
                        "ai_agent_personality": user.ai_agent_personality or {},
                        "therapy_preference": user.therapy_preference
                    }
                return {}
            finally:
                db.close()
        except Exception as e:
            print(f"Error getting user profile: {e}")
            # Return default profile if database error
            return {
                "id": user_id,
                "username": "demo_user",
                "first_name": "there",  # Use "there" instead of "Demo" for more personal feel
                "preferred_contact_method": "email",
                "notification_preferences": {},
                "ai_agent_personality": {"tone": "friendly", "emojis": True},
                "therapy_preference": "cbt"
            }
    
    async def _analyze_intent(self, message: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user intent for tool usage"""
        message_lower = message.lower()
        
        intent = {
            "primary_action": "chat",
            "tools_requested": [],
            "contact_info_requested": False,
            "therapy_related": False,
            "urgency_level": "normal"
        }
        
        # Check for phone number patterns in the message
        phone_pattern = r'(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        ten_digit_pattern = r'\b(\d{10})\b'
        has_phone_number = bool(re.search(phone_pattern, message) or re.search(ten_digit_pattern, message))
        
        # Check for SMS requests
        if any(word in message_lower for word in ["sms", "text", "message", "send text", "send sms", "send me", "reminder", "notify"]):
            intent["tools_requested"].append("sms")
            intent["primary_action"] = "send_sms"
        
        # Check for email requests
        if any(word in message_lower for word in ["email", "mail", "send email", "gmail", "hotmail"]):
            intent["tools_requested"].append("email")
            intent["primary_action"] = "send_email"
        
        # Check for contact info requests or phone number provision
        if any(word in message_lower for word in ["phone", "number", "email address", "contact", "my phone", "my number"]) or has_phone_number:
            intent["contact_info_requested"] = True
            
            # If they're providing a phone number and previously asked for SMS, treat as SMS setup
            if has_phone_number and user_profile.get("phone_number") is None:
                intent["tools_requested"].append("sms")
                intent["primary_action"] = "setup_sms"
        
        # Check for therapy-related content
        therapy_keywords = ["anxiety", "depression", "stress", "therapy", "help", "feeling", "mood"]
        if any(word in message_lower for word in therapy_keywords):
            intent["therapy_related"] = True
        
        # Check for urgency
        urgent_keywords = ["urgent", "emergency", "crisis", "help now", "immediate"]
        if any(word in message_lower for word in urgent_keywords):
            intent["urgency_level"] = "high"
        
        return intent
    
    def _update_conversation_history(self, user_id: str, user_message: str, ai_response: str):
        """Update conversation history for a user"""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        # Add the conversation turn
        self.conversation_history[user_id].append({
            "user": user_message,
            "ai": ai_response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only the last 10 conversations to avoid memory issues
        if len(self.conversation_history[user_id]) > 10:
            self.conversation_history[user_id] = self.conversation_history[user_id][-10:]
    
    def _get_conversation_history(self, user_id: str) -> str:
        """Get conversation history as a formatted string"""
        if user_id not in self.conversation_history:
            return ""
        
        history = []
        for turn in self.conversation_history[user_id][-5:]:  # Last 5 conversations
            history.append(f"User: {turn['user']}")
            history.append(f"Assistant: {turn['ai']}")
        
        return "\n".join(history)
    
    async def _generate_personalized_response(self, message: str, user_profile: Dict[str, Any], intent: Dict[str, Any], user_id: str = None) -> str:
        """Generate personalized response based on user profile and intent with conversation history"""
        
        # Get personality settings
        personality = user_profile.get("ai_agent_personality", {})
        tone = personality.get("tone", "friendly")
        use_emojis = personality.get("emojis", True)
        nickname = personality.get("nickname")
        
        # Get user name - prioritize first_name, then username, then a friendly default
        user_name = user_profile.get("first_name")
        if not user_name or user_name == "Demo" or user_name == "there":
            user_name = user_profile.get("username", "there")
            # If username is "demo_user" or similar, use a more personal approach
            if user_name == "demo_user" or user_name.startswith("demo_user"):
                user_name = "there"
        
        # Check if user has phone number saved
        has_phone = bool(user_profile.get("phone_number"))
        
        # Get conversation history
        conversation_history = self._get_conversation_history(user_id) if user_id else ""
        
        # Create personalized prompt with conversation history
        prompt = f"""You are a helpful, {tone} AI assistant with SMS capabilities. The user's name is {user_name}.

User Profile:
- Name: {user_name}
- Contact Method: {user_profile.get('preferred_contact_method', 'email')}
- Phone Number: {'✅ Saved' if has_phone else '❌ Not provided'}
- Therapy Preference: {user_profile.get('therapy_preference', 'cbt')}
- Notification Preferences: {json.dumps(user_profile.get('notification_preferences', {}))}

{conversation_history}

Current User Message: {message}

Intent Analysis:
- Primary Action: {intent['primary_action']}
- Tools Requested: {intent['tools_requested']}
- Therapy Related: {intent['therapy_related']}
- Urgency: {intent['urgency_level']}

SMS CAPABILITIES:
- You can send SMS messages if the user has provided their phone number
- If they haven't provided a phone number, ask them to share it
- When they provide a phone number, confirm it's saved
- When they request SMS, send it using your SMS service

RESPONSE GUIDELINES:
- Always address the user by their name ({user_name}) in a friendly, personal way
- If user provides phone number: "Perfect! I've saved your phone number. Now I can send you SMS messages when needed."
- If user requests SMS but no phone saved: "I'd love to send you an SMS! Please provide your phone number first, like 'My phone number is 1234567890'."
- If user requests SMS and phone is saved: "Great! I'll send you an SMS right now using your saved phone number."
- Be direct and helpful with SMS requests
- Use emojis {'sparingly' if not use_emojis else 'appropriately'}
- Keep response conversational and personalized to {user_name}
- Reference previous conversation context when relevant
- Be coherent and maintain conversation flow"""
        
        # Generate response using LLM
        response = await self.llm_client.generate_response(prompt, {
            "therapy_type": user_profile.get("therapy_preference", "cbt"),
            "user_context": f"User: {user_name}\nContact Method: {user_profile.get('preferred_contact_method', 'email')}\nConversation History: {conversation_history}"
        })
        
        return response
    
    async def _handle_tool_requests(self, intent: Dict[str, Any], user_profile: Dict[str, Any], message: str) -> Dict[str, Any]:
        """Handle SMS and email tool requests"""
        tool_actions = {}
        
        # Handle SMS requests
        if "sms" in intent["tools_requested"]:
            phone_number = user_profile.get("phone_number")
            if phone_number:
                # Generate personalized SMS message based on user's request
                try:
                    # Create a personalized message based on the user's request
                    user_name = user_profile.get("first_name") or user_profile.get("username", "there")
                    
                    # Generate personalized message using LLM
                    personalized_message = await self._generate_sms_message(message, user_profile)
                    
                    sms_result = await self.send_sms("demo_user", personalized_message)
                    if sms_result.get("success"):
                        tool_actions["sms_sent"] = {
                            "to": sms_result.get("phone_number", phone_number),
                            "message": personalized_message,
                            "status": "sent",
                            "service": sms_result.get("service", "unknown")
                        }
                    else:
                        tool_actions["sms_error"] = sms_result.get("error", "Failed to send SMS")
                except Exception as e:
                    tool_actions["sms_error"] = f"Error sending SMS: {str(e)}"
            else:
                tool_actions["sms_error"] = "No phone number found. Please provide your phone number first. You can say something like 'My phone number is 1234567890' or just type your 10-digit number."
        
        # Handle SMS setup (when user provides phone number)
        if intent["primary_action"] == "setup_sms":
            # Don't add tool actions for setup - let the main response handle it
            pass
        
        # Handle email requests
        if "email" in intent["tools_requested"]:
            email = user_profile.get("email")
            if email:
                # Here you would integrate with email service (SendGrid, etc.)
                tool_actions["email_sent"] = {
                    "to": email,
                    "subject": "Your AI Assistant Update",
                    "message": "Hello! Your AI assistant is here to support you.",
                    "status": "simulated_sent"
                }
            else:
                tool_actions["email_error"] = "No email address found. Please provide your email first."
        
        return tool_actions
    
    async def _update_user_contact_info(self, user_id: str, intent: Dict[str, Any], message: str) -> bool:
        """Update user contact information if provided"""
        try:
            # Extract phone number with more flexible pattern
            phone_pattern = r'(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
            phone_match = re.search(phone_pattern, message)
            
            # Also try to find any 10-digit number
            ten_digit_pattern = r'\b(\d{10})\b'
            ten_digit_match = re.search(ten_digit_pattern, message)
            
            # Extract email
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            email_match = re.search(email_pattern, message)
            
            # Also look for phone number in words like "my number is" or "phone number"
            phone_keywords = ['phone', 'number', 'cell', 'mobile', 'tel']
            has_phone_keywords = any(keyword in message.lower() for keyword in phone_keywords)
            
            # Debug: Print what we found
            print(f"Phone match: {phone_match}")
            print(f"Ten digit match: {ten_digit_match}")
            print(f"Has phone keywords: {has_phone_keywords}")
            print(f"Message: {message}")
            
            phone_number_found = None
            
            if phone_match:
                phone_number_found = phone_match.group(0)
            elif ten_digit_match:
                phone_number_found = ten_digit_match.group(1)
            elif has_phone_keywords:
                # Extract digits from the message
                digits = re.findall(r'\d+', message)
                if len(digits) >= 1:
                    # Try to find a 10-digit number
                    for digit_group in digits:
                        if len(digit_group) == 10:
                            phone_number_found = digit_group
                            print(f"Found 10-digit number: {digit_group}")
                            break
            
            # Always check for name extraction, regardless of phone/email
            extracted_name = self._extract_name_from_message(message)
            
            if phone_number_found or email_match or extracted_name:
                db = next(get_db())
                try:
                    user = db.query(User).filter(User.id == user_id).first()
                    
                    # If user doesn't exist, create a demo user
                    if not user:
                        print(f"Creating demo user with ID: {user_id}")
                        user = User(
                            id=user_id,
                            username=f"demo_user_{user_id}",
                            email=f"demo_{user_id}@example.com",
                            hashed_password="demo_password",
                            first_name="there",  # Use "there" instead of "Demo" for more personal feel
                            last_name="User"
                        )
                        db.add(user)
                    
                    updated = False
                    
                    # Update phone number if found
                    if phone_number_found:
                        # Clean the phone number - remove spaces and non-digits
                        cleaned_phone = re.sub(r'[^\d]', '', phone_number_found)
                        user.phone_number = cleaned_phone
                        updated = True
                        print(f"Updated phone number to: {cleaned_phone}")
                    
                    # Update email if found
                    if email_match:
                        user.email = email_match.group(0)
                        updated = True
                    
                    # Try to extract and save name
                    if extracted_name and (not user.first_name or user.first_name == "there" or user.first_name == "Demo"):
                        user.first_name = extracted_name
                        updated = True
                        print(f"Updated user name to: {extracted_name}")
                        print(f"User ID: {user_id}, First Name: {user.first_name}")
                    
                    if updated:
                        try:
                            db.commit()
                            print(f"Updated user {user_id} contact info: phone={user.phone_number}, email={user.email}, name={user.first_name}")
                            return True
                        except Exception as commit_error:
                            print(f"Error committing changes: {commit_error}")
                            db.rollback()
                            return False
                finally:
                    db.close()
            
            return False
            
        except Exception as e:
            print(f"Error updating user contact info: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def send_sms(self, user_id: str, message: str) -> Dict[str, Any]:
        """Send SMS to user"""
        try:
            user_profile = await self._get_user_profile(user_id)
            phone_number = user_profile.get("phone_number")
            
            if not phone_number:
                return {
                    "success": False,
                    "error": "No phone number found. Please provide your phone number first. You can say something like 'My phone number is 1234567890' or just type your 10-digit number."
                }
            
            # Clean the phone number - remove spaces and non-digits
            phone_number = re.sub(r'[^\d]', '', phone_number)
            
            # Try to send actual SMS using multiple services
            try:
                # First try Twilio if configured
                twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
                twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
                twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
                
                if twilio_account_sid and twilio_auth_token and twilio_phone_number:
                    try:
                        from twilio.rest import Client
                        client = Client(twilio_account_sid, twilio_auth_token)
                        
                        # Send actual SMS
                        sms = client.messages.create(
                            body=message,
                            from_=twilio_phone_number,
                            to=phone_number
                        )
                        
                        return {
                            "success": True,
                            "message": f"SMS sent to {phone_number}: {message}",
                            "status": "sent",
                            "phone_number": phone_number,
                            "twilio_sid": sms.sid,
                            "service": "twilio"
                        }
                    except Exception as e:
                        print(f"Twilio SMS failed: {e}")
                
                # Try TextBelt API as alternative
                try:
                    import httpx
                    
                    # Get TextBelt API key from environment or use test key
                    textbelt_key = os.getenv("TEXTBELT_API_KEY", "textbelt_test")
                    
                    # Use TextBelt API
                    response = httpx.post(
                        "https://textbelt.com/text",
                        data={
                            "phone": phone_number,
                            "message": message,
                            "key": textbelt_key
                        },
                        timeout=10.0
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("success"):
                            return {
                                "success": True,
                                "message": f"SMS sent to {phone_number}: {message}",
                                "status": "sent",
                                "phone_number": phone_number,
                                "service": "textbelt",
                                "textbelt_id": result.get("textId")
                            }
                        else:
                            print(f"TextBelt error: {result.get('error')}")
                
                except Exception as e:
                    print(f"TextBelt SMS failed: {e}")
                
                # Try Email-to-SMS gateway as fallback
                try:
                    # Many carriers support email-to-SMS
                    carrier_gateways = {
                        "verizon": f"{phone_number}@vtext.com",
                        "att": f"{phone_number}@txt.att.net",
                        "tmobile": f"{phone_number}@tmomail.net",
                        "sprint": f"{phone_number}@messaging.sprintpcs.com"
                    }
                    
                    # Try to send via email (requires email service setup)
                    # This is a fallback option
                    print(f"Attempting email-to-SMS for {phone_number}")
                    
                except Exception as e:
                    print(f"Email-to-SMS failed: {e}")
                
                # Final fallback - return error for real SMS requirement
                return {
                    "success": False,
                    "error": f"No SMS service available. To send real SMS messages, please configure Twilio or TextBelt API keys. Current status: TextBelt quota exhausted.",
                    "phone_number": phone_number,
                    "status": "service_unavailable"
                }
                
            except Exception as e:
                print(f"SMS service error: {e}")
                return {
                    "success": False,
                    "error": f"SMS service error: {e}. To send real SMS messages, please configure Twilio or TextBelt API keys.",
                    "phone_number": phone_number,
                    "status": "service_error"
                }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_email(self, user_id: str, subject: str, message: str) -> Dict[str, Any]:
        """Send email to user"""
        try:
            user_profile = await self._get_user_profile(user_id)
            email = user_profile.get("email")
            
            if not email:
                return {
                    "success": False,
                    "error": "No email address found. Please provide your email first."
                }
            
            # Here you would integrate with email service (SendGrid, etc.)
            # For now, we'll simulate the email sending
            return {
                "success": True,
                "message": f"Email sent to {email}: {subject}",
                "status": "simulated_sent"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Update user AI agent preferences"""
        try:
            db = next(get_db())
            try:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    if "personality" in preferences:
                        user.ai_agent_personality = preferences["personality"]
                    
                    if "notification_preferences" in preferences:
                        user.notification_preferences = preferences["notification_preferences"]
                    
                    if "preferred_contact_method" in preferences:
                        user.preferred_contact_method = preferences["preferred_contact_method"]
                    
                    db.commit()
                    
                    return {
                        "success": True,
                        "message": "Preferences updated successfully!"
                    }
                else:
                    return {
                        "success": False,
                        "error": "User not found"
                    }
            finally:
                db.close()
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def update_phone_number(self, user_id: str, phone_number: str) -> Dict[str, Any]:
        """Manually update user's phone number"""
        try:
            db = next(get_db())
            try:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    user.phone_number = phone_number
                    db.commit()
                    
                    return {
                        "success": True,
                        "message": f"Phone number updated to {phone_number}"
                    }
                else:
                    return {
                        "success": False,
                        "error": "User not found"
                    }
            finally:
                db.close()
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def _generate_sms_message(self, user_request: str, user_profile: Dict[str, Any]) -> str:
        """Generate personalized SMS message based on user's request"""
        try:
            # Get user name - prioritize first_name, then username, then a friendly default
            user_name = user_profile.get("first_name")
            if not user_name or user_name == "Demo" or user_name == "there":
                user_name = user_profile.get("username", "there")
                # If username is "demo_user" or similar, use a more personal approach
                if user_name == "demo_user" or user_name.startswith("demo_user"):
                    user_name = "there"
            
            # Create a prompt for generating personalized SMS
            prompt = f"""You are a helpful AI assistant sending an SMS message to {user_name}.

User's request: "{user_request}"

Generate a personalized, motivational, and helpful SMS message (max 140 characters) that:
1. Addresses the user's specific request
2. Uses their name if provided
3. Is encouraging and positive
4. Includes relevant emojis if appropriate
5. Is concise and SMS-friendly
6. DOES NOT include any URLs, links, or web addresses
7. Focus on actionable advice and motivation
8. Keep it short and impactful

Examples:
- If they ask for motivation: "Hey {user_name}! 🌟 Every step forward is progress. You've got this! 💪"
- If they ask for a quote: "Hi {user_name}! Daily inspiration: 'The only way to do great work is to love what you do.' - Steve Jobs ✨"
- If they ask for a reminder: "Hi {user_name}! ⏰ You're doing amazing things today! Keep shining! 🌟"

Generate the SMS message (max 140 chars, no URLs):"""

            # Use the LLM to generate the message
            if hasattr(self, 'llm_client') and self.llm_client:
                try:
                    response = await self.llm_client.generate_response(prompt, {
                        "user_context": f"User: {user_name}\nRequest: {user_request}",
                        "therapy_type": "positive_psychology"  # Use positive psychology for motivational messages
                    })
                    if response and response.strip():
                        # Clean up the response and ensure it's SMS-friendly
                        message = response.strip()
                        # Remove quotes if present
                        if message.startswith('"') and message.endswith('"'):
                            message = message[1:-1]
                        # Remove any URLs or links
                        import re
                        message = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', message)
                        message = re.sub(r'www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', message)
                        # Clean up extra spaces
                        message = ' '.join(message.split())
                        # Ensure it's not too long for SMS (140 chars for safety)
                        if len(message) > 140:
                            message = message[:137] + "..."
                        return message
                except Exception as e:
                    print(f"Error generating SMS message with LLM: {e}")
            
            # Fallback message if LLM fails
            return f"Hi {user_name}! 🌟 Here's your personalized message: {user_request[:100]}... Keep shining! ✨"
            
        except Exception as e:
            print(f"Error in _generate_sms_message: {e}")
            # Ultimate fallback
            user_name = user_profile.get("first_name") or user_profile.get("username", "there")
            return f"Hi {user_name}! 🌟 Your AI assistant is here to help! 🤖"

    def _extract_name_from_message(self, message: str) -> Optional[str]:
        """Extract potential name from user message"""
        # Common patterns for name introduction
        name_patterns = [
            r"my name is (\w+)",
            r"i'm (\w+)",
            r"i am (\w+)",
            r"call me (\w+)",
            r"i'm called (\w+)",
            r"my name's (\w+)",
            r"i go by (\w+)"
        ]
        
        message_lower = message.lower()
        for pattern in name_patterns:
            match = re.search(pattern, message_lower)
            if match:
                name = match.group(1).capitalize()
                # Basic validation - name should be at least 2 characters and not common words
                if len(name) >= 2 and name.lower() not in ['the', 'and', 'but', 'for', 'you', 'are', 'was', 'had', 'her', 'his', 'its', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use']:
                    return name
        
        return None
