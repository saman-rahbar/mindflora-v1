import os
import json
import asyncio
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
import openai
from openai import AsyncOpenAI
import anthropic
from anthropic import AsyncAnthropic

class LLMClient(ABC):
    """Abstract base class for LLM clients"""
    
    @abstractmethod
    async def generate_response(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Generate a response from the LLM"""
        pass
    
    @abstractmethod
    async def analyze_content(self, content: str, analysis_type: str) -> Dict[str, Any]:
        """Analyze content for specific insights"""
        pass

class OpenAILLMClient(LLMClient):
    """OpenAI GPT-4 client for therapy responses"""
    
    def __init__(self, api_key: str = None, model: str = "gpt-4"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.client = AsyncOpenAI(api_key=self.api_key)
        
        # Therapy-specific system prompts
        self.system_prompts = {
            "cbt": """You are a Cognitive Behavioral Therapy (CBT) specialist. Your role is to:
1. Identify cognitive distortions in the user's thoughts
2. Help reframe negative thinking patterns
3. Suggest evidence-based CBT techniques
4. Provide compassionate, supportive responses
5. Never give medical advice or replace professional therapy

Always maintain a warm, empathetic tone while being clinically accurate.""",
            
            "logotherapy": """You are a Logotherapy specialist inspired by Viktor Frankl's work. Your role is to:
1. Help users find meaning and purpose in their experiences
2. Explore existential themes and values
3. Guide users through meaning-centered interventions
4. Support growth through suffering and challenges
5. Never give medical advice or replace professional therapy

Focus on helping users discover their unique sources of meaning.""",
            
            "act": """You are an Acceptance and Commitment Therapy (ACT) specialist. Your role is to:
1. Help users accept difficult thoughts and feelings
2. Guide commitment to value-based actions
3. Teach mindfulness and defusion techniques
4. Support psychological flexibility
5. Never give medical advice or replace professional therapy

Emphasize acceptance, mindfulness, and values-based living.""",
            
            "dbt": """You are a Dialectical Behavior Therapy (DBT) specialist. Your role is to:
1. Teach emotional regulation skills
2. Improve interpersonal effectiveness
3. Enhance distress tolerance
4. Develop mindfulness practices
5. Never give medical advice or replace professional therapy

Focus on balancing acceptance and change through dialectical thinking.""",
            
            "somotherapy": """You are a Somotherapy (body-centered therapy) specialist. Your role is to:
1. Help users develop body awareness
2. Guide somatic experiencing for trauma recovery
3. Teach body-based mindfulness techniques
4. Support mind-body integration
5. Never give medical advice or replace professional therapy

Emphasize the connection between physical sensations and emotional well-being.""",
            
            "positive_psychology": """You are a Positive Psychology specialist. Your role is to:
1. Help users identify and build on their strengths
2. Cultivate gratitude and positive emotions
3. Foster optimism and hope
4. Support flourishing and well-being
5. Never give medical advice or replace professional therapy

Focus on building positive habits and enhancing life satisfaction."""
        }
    
    async def generate_response(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Generate a therapeutic response"""
        try:
            therapy_type = context.get("therapy_type", "cbt") if context else "cbt"
            system_prompt = self.system_prompts.get(therapy_type, self.system_prompts["cbt"])
            
            # Extract user context for personalization
            user_context = context.get("user_context", "") if context else ""
            user_name = ""
            user_age = ""
            user_education = ""
            
            if user_context:
                # Parse user context string to extract information
                context_lines = user_context.split('\n')
                for line in context_lines:
                    if line.startswith('User:'):
                        user_name = line.split(': ')[-1] if ': ' in line else ""
                    elif line.startswith('Age:'):
                        user_age = line.split(': ')[-1] if ': ' in line else ""
                    elif line.startswith('Education:'):
                        user_education = line.split(': ')[-1] if ': ' in line else ""
            
            # Create personalized system prompt
            personalized_system_prompt = system_prompt
            
            if user_name:
                personalized_system_prompt += f"\n\nIMPORTANT: The user's name is {user_name}. Always address them by their first name in your responses to create a more personal and supportive therapeutic relationship."
            
            if user_age:
                personalized_system_prompt += f"\n\nThe user is {user_age} years old. Consider age-appropriate language and examples in your responses."
            
            if user_education:
                personalized_system_prompt += f"\n\nThe user's education level is {user_education}. Adjust the complexity of your language and examples accordingly."
            
            # Build the full prompt with context
            full_prompt = f"{prompt}\n\nPlease provide a therapeutic response that is compassionate, evidence-based, and tailored to the user's needs."
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": personalized_system_prompt},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"I'm here to support you. Let's work together to explore what's on your mind. (Note: AI service temporarily unavailable)"
    
    async def analyze_content(self, content: str, analysis_type: str) -> Dict[str, Any]:
        """Analyze user content for therapeutic insights"""
        try:
            analysis_prompts = {
                "cognitive_distortions": f"""Analyze the following text for cognitive distortions. Return a JSON object with:
{{
    "distortions_found": ["list of identified distortions"],
    "thought_patterns": {{
        "negative_thoughts": count,
        "positive_thoughts": count,
        "thought_balance": "positive/negative/balanced"
    }},
    "emotion_analysis": {{
        "primary_emotion": "emotion name",
        "intensity": 1-10
    }}
}}

Text: {content}""",
                
                "existential_themes": f"""Analyze the following text for existential themes. Return a JSON object with:
{{
    "themes_found": ["list of existential themes"],
    "meaning_sources": ["potential sources of meaning"],
    "values_identified": ["core values mentioned"],
    "suffering_patterns": ["patterns of suffering/growth"]
}}

Text: {content}""",
                
                "emotional_regulation": f"""Analyze the following text for emotional regulation needs. Return a JSON object with:
{{
    "emotion_identification": ["emotions present"],
    "regulation_needs": ["specific regulation skills needed"],
    "interpersonal_aspects": ["relationship dynamics"],
    "mindfulness_opportunities": ["mindfulness practice suggestions"]
}}

Text: {content}"""
            }
            
            prompt = analysis_prompts.get(analysis_type, analysis_prompts["cognitive_distortions"])
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a clinical psychologist analyzing text for therapeutic insights. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            try:
                return json.loads(response.choices[0].message.content)
            except json.JSONDecodeError:
                return {"error": "Analysis failed", "raw_response": response.choices[0].message.content}
                
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}

class AnthropicLLMClient(LLMClient):
    """Anthropic Claude client for therapy responses"""
    
    def __init__(self, api_key: str = None, model: str = "claude-3-sonnet-20240229"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self.client = AsyncAnthropic(api_key=self.api_key)
        
        # Same system prompts as OpenAI client
        self.system_prompts = {
            "cbt": """You are a Cognitive Behavioral Therapy (CBT) specialist...""",
            "logotherapy": """You are a Logotherapy specialist inspired by Viktor Frankl's work...""",
            # ... (same prompts as OpenAI client)
        }
    
    async def generate_response(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Generate a therapeutic response using Claude"""
        try:
            therapy_type = context.get("therapy_type", "cbt") if context else "cbt"
            system_prompt = self.system_prompts.get(therapy_type, self.system_prompts["cbt"])
            
            # Extract user context for personalization
            user_context = context.get("user_context", "") if context else ""
            user_name = ""
            user_age = ""
            user_education = ""
            
            if user_context:
                # Parse user context string to extract information
                context_lines = user_context.split('\n')
                for line in context_lines:
                    if line.startswith('User:'):
                        user_name = line.split(': ')[-1] if ': ' in line else ""
                    elif line.startswith('Age:'):
                        user_age = line.split(': ')[-1] if ': ' in line else ""
                    elif line.startswith('Education:'):
                        user_education = line.split(': ')[-1] if ': ' in line else ""
            
            # Create personalized system prompt
            personalized_system_prompt = system_prompt
            
            if user_name:
                personalized_system_prompt += f"\n\nIMPORTANT: The user's name is {user_name}. Always address them by their first name in your responses to create a more personal and supportive therapeutic relationship."
            
            if user_age:
                personalized_system_prompt += f"\n\nThe user is {user_age} years old. Consider age-appropriate language and examples in your responses."
            
            if user_education:
                personalized_system_prompt += f"\n\nThe user's education level is {user_education}. Adjust the complexity of your language and examples accordingly."
            
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=500,
                system=personalized_system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text
            
        except Exception as e:
            return f"I'm here to support you. Let's work together to explore what's on your mind. (Note: AI service temporarily unavailable)"
    
    async def analyze_content(self, content: str, analysis_type: str) -> Dict[str, Any]:
        """Analyze user content for therapeutic insights using Claude"""
        # Similar implementation to OpenAI but using Claude
        pass

class MockLLMClient(LLMClient):
    """Mock LLM client for development and testing"""
    
    def __init__(self):
        self.responses = {
            "cbt": [
                "I notice you're experiencing some challenging thoughts. Let's explore these together. What evidence supports or contradicts these thoughts?",
                "It sounds like you might be engaging in some cognitive distortions. Let's identify them and work on reframing these thoughts.",
                "I hear the anxiety in your words. Let's practice some cognitive restructuring techniques together."
            ],
            "logotherapy": [
                "I sense you're searching for deeper meaning in this situation. What values are most important to you right now?",
                "Even in difficult times, we can find meaning. Let's explore what this experience might be teaching you.",
                "Your search for purpose is deeply human. Let's discover what gives your life meaning."
            ]
        }
    
    async def generate_response(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Generate a mock therapeutic response based on user input"""
        import random
        
        therapy_type = context.get("therapy_type", "cbt") if context else "cbt"
        user_message = prompt.lower()
        
        # Contextual responses based on user input
        if "anxiety" in user_message or "worried" in user_message or "nervous" in user_message:
            if therapy_type == "cbt":
                return "I can sense the anxiety in your words. Let's work together to identify the specific thoughts that are fueling this anxiety. Can you tell me more about what's making you feel this way? Try this exercise: Write down three thoughts that are causing your anxiety, then ask yourself: 'What evidence supports this thought? What evidence contradicts it?'"
            elif therapy_type == "act":
                return "Anxiety is a natural response, and I hear how challenging it feels. Let's practice accepting these anxious feelings while focusing on what matters most to you. Here's what you can do: Take 5 deep breaths, acknowledging the anxiety without trying to push it away. Notice how it feels in your body."
            else:
                return "I understand how overwhelming anxiety can feel. You're not alone in this experience. Let's explore what's behind these feelings together."
        
        elif "sad" in user_message or "depressed" in user_message or "down" in user_message:
            if therapy_type == "cbt":
                return "I hear the sadness in your voice. Let's examine the thoughts and beliefs that might be contributing to these feelings. What's been on your mind lately?"
            elif therapy_type == "positive_psychology":
                return "I acknowledge the difficulty you're experiencing. Even in dark times, we can find small moments of light. Let's focus on your strengths and what brings you joy."
            else:
                return "Your feelings are valid, and I'm here to listen. Depression can feel isolating, but you don't have to face this alone. What would be most supportive for you right now?"
        
        elif "stress" in user_message or "overwhelmed" in user_message or "pressure" in user_message:
            if therapy_type == "cbt":
                return "Stress can feel like it's taking over. Let's break this down together - what specific situations are causing you the most stress right now? Try this exercise: Make a list of your stressors and rate each one from 1-10. Then identify which ones you can control and which ones you can't."
            elif therapy_type == "dbt":
                return "I can see how overwhelmed you're feeling. Let's practice some distress tolerance skills together. Here's what you can do: Use the 'STOP' technique - Stop, Take a step back, Observe your thoughts and feelings, Proceed mindfully."
            else:
                return "Stress can be incredibly challenging. You're showing real strength by reaching out. Let's work on finding some relief together."
        
        elif "relationship" in user_message or "partner" in user_message or "family" in user_message:
            if therapy_type == "cbt":
                return "Relationships can be complex and challenging. Let's explore the thoughts and patterns that might be affecting your connections with others."
            elif therapy_type == "dbt":
                return "Interpersonal relationships can be both rewarding and difficult. Let's work on some skills to help you communicate more effectively and set healthy boundaries."
            else:
                return "Relationships are fundamental to our well-being. I'm here to help you navigate these important connections in your life."
        
        elif "goal" in user_message or "future" in user_message or "purpose" in user_message:
            if therapy_type == "logotherapy":
                return "I sense you're searching for deeper meaning and purpose. Let's explore what truly matters to you and how you can align your actions with your values."
            elif therapy_type == "positive_psychology":
                return "Your desire to grow and achieve is inspiring. Let's focus on your strengths and how you can use them to move toward your goals."
            else:
                return "Having goals and dreams is wonderful. Let's work together to break them down into manageable steps and overcome any obstacles."
        
        else:
            # Generic responses based on therapy type
            responses = self.responses.get(therapy_type, self.responses["cbt"])
            return random.choice(responses)
    
    async def analyze_content(self, content: str, analysis_type: str) -> Dict[str, Any]:
        """Generate mock analysis"""
        return {
            "distortions_found": ["catastrophizing", "all-or-nothing thinking"],
            "thought_patterns": {
                "negative_thoughts": 3,
                "positive_thoughts": 1,
                "thought_balance": "negative"
            },
            "emotion_analysis": {
                "primary_emotion": "anxiety",
                "intensity": 7
            }
        }

# Factory function to create LLM client
def create_llm_client(client_type: str = "mock", **kwargs) -> LLMClient:
    """Create an LLM client based on configuration"""
    if client_type == "openai":
        return OpenAILLMClient(**kwargs)
    elif client_type == "anthropic":
        return AnthropicLLMClient(**kwargs)
    else:
        return MockLLMClient()

# Note: LLM client is initialized in the router files 