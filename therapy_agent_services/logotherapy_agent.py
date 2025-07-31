from typing import Dict, Any, List
from .base import BaseTherapyAgent
from agent_router_service.interfaces import TherapyRequest
import re
import json

class LogotherapyAgent(BaseTherapyAgent):
    """Logotherapy Agent - Meaning-Centered Therapy"""
    
    def __init__(self):
        super().__init__("Logotherapy Agent", "logotherapy")
        self.existential_themes = [
            "meaning and purpose",
            "freedom and responsibility",
            "suffering and growth",
            "values and beliefs",
            "authenticity",
            "transcendence",
            "hope and despair",
            "life transitions"
        ]
        
        self.meaning_sources = [
            "creative values (creating/contributing)",
            "experiential values (experiencing/connecting)",
            "attitudinal values (choosing response to suffering)"
        ]
    
    async def process_therapy_request(self, request: TherapyRequest) -> Dict[str, Any]:
        """
        Process Logotherapy request
        """
        # Analyze existential themes
        themes = self._identify_existential_themes(request.session_content)
        
        # Identify meaning sources
        meaning_sources = self._identify_meaning_sources(request.session_content)
        
        # Generate logotherapy response using LLM with user context
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
        
        from llm_service.llm_client import llm_client
        
        prompt = f"""User session content: {request.session_content}

Please provide a Logotherapy-focused therapeutic response that:
1. Acknowledges the user's search for meaning
2. Explores existential themes present
3. Suggests meaning-centered interventions
4. Offers compassionate support for growth through suffering
5. Encourages further exploration of values and purpose

Keep the response warm, professional, and clinically appropriate."""
        
        # Create context with user information
        context = {
            "therapy_type": "logotherapy",
            "user_context": request.context.get("user_context", "") if request.context else ""
        }
        
        response = await llm_client.generate_response(
            prompt, 
            context=context
        )
        
        # Create structured response
        return {
            "therapy_type": "logotherapy",
            "analysis": {
                "existential_themes": themes,
                "meaning_sources": meaning_sources,
                "suffering_analysis": self._analyze_suffering_patterns(request.session_content),
                "values_analysis": self._analyze_values_and_beliefs(request.session_content)
            },
            "intervention": {
                "techniques": self._suggest_logotherapy_techniques(themes, meaning_sources),
                "response": response,
                "meaning_exploration": self._generate_meaning_exploration_questions(themes)
            },
            "progress_tracking": {
                "session_count": await self._get_session_count(request.user_id),
                "meaning_clarity_score": self._calculate_meaning_clarity(request.session_content)
            }
        }
    
    def _identify_existential_themes(self, content: str) -> List[Dict[str, Any]]:
        """
        Identify existential themes in the content
        """
        themes = []
        content_lower = content.lower()
        
        for theme in self.existential_themes:
            if theme in content_lower:
                examples = self._find_theme_examples(content, theme)
                themes.append({
                    "theme": theme,
                    "examples": examples,
                    "intensity": self._assess_theme_intensity(examples)
                })
        
        return themes
    
    def _find_theme_examples(self, content: str, theme: str) -> List[str]:
        """
        Find specific examples of existential themes in the text
        """
        examples = []
        sentences = re.split(r'[.!?]+', content)
        
        theme_keywords = {
            "meaning and purpose": ["purpose", "meaning", "why", "goal", "aim"],
            "freedom and responsibility": ["choice", "freedom", "responsible", "decide", "control"],
            "suffering and growth": ["suffer", "pain", "difficult", "challenge", "grow"],
            "values and beliefs": ["value", "believe", "important", "matter", "principle"],
            "authenticity": ["real", "authentic", "true", "genuine", "myself"],
            "transcendence": ["beyond", "transcend", "spiritual", "higher", "connection"],
            "hope and despair": ["hope", "despair", "hopeless", "future", "possibility"],
            "life transitions": ["change", "transition", "new", "different", "phase"]
        }
        
        keywords = theme_keywords.get(theme, [theme])
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in keywords):
                examples.append(sentence.strip())
        
        return examples[:3]
    
    def _assess_theme_intensity(self, examples: List[str]) -> str:
        """
        Assess the intensity of existential themes
        """
        if len(examples) >= 3:
            return "high"
        elif len(examples) >= 1:
            return "medium"
        else:
            return "low"
    
    def _identify_meaning_sources(self, content: str) -> List[Dict[str, Any]]:
        """
        Identify sources of meaning in the content
        """
        meaning_sources = []
        content_lower = content.lower()
        
        for source in self.meaning_sources:
            if any(keyword in content_lower for keyword in source.split()):
                meaning_sources.append({
                    "source": source,
                    "description": self._get_meaning_source_description(source),
                    "examples": self._find_meaning_examples(content, source)
                })
        
        return meaning_sources
    
    def _get_meaning_source_description(self, source: str) -> str:
        """
        Get description for meaning source
        """
        descriptions = {
            "creative values (creating/contributing)": "Finding meaning through creating, building, or contributing to something larger than oneself",
            "experiential values (experiencing/connecting)": "Finding meaning through experiences, relationships, and connections with others",
            "attitudinal values (choosing response to suffering)": "Finding meaning through choosing one's attitude and response to unavoidable suffering"
        }
        return descriptions.get(source, source)
    
    def _find_meaning_examples(self, content: str, source: str) -> List[str]:
        """
        Find examples of meaning sources in the content
        """
        examples = []
        sentences = re.split(r'[.!?]+', content)
        
        source_keywords = {
            "creative values (creating/contributing)": ["create", "build", "contribute", "help", "make", "work"],
            "experiential values (experiencing/connecting)": ["experience", "connect", "relationship", "love", "family", "friend"],
            "attitudinal values (choosing response to suffering)": ["choose", "attitude", "response", "suffer", "pain", "difficult"]
        }
        
        keywords = source_keywords.get(source, [])
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in keywords):
                examples.append(sentence.strip())
        
        return examples[:2]
    
    def _analyze_suffering_patterns(self, content: str) -> Dict[str, Any]:
        """
        Analyze patterns of suffering and response to suffering
        """
        suffering_keywords = ["suffer", "pain", "difficult", "hard", "struggle", "challenge"]
        response_keywords = ["choose", "attitude", "response", "handle", "cope", "grow"]
        
        suffering_count = sum(len(re.findall(rf'\b{keyword}\b', content.lower())) for keyword in suffering_keywords)
        response_count = sum(len(re.findall(rf'\b{keyword}\b', content.lower())) for keyword in response_keywords)
        
        return {
            "suffering_mentions": suffering_count,
            "response_mentions": response_count,
            "suffering_response_ratio": response_count / max(suffering_count, 1),
            "pattern": "growth-oriented" if response_count > suffering_count else "struggling"
        }
    
    def _analyze_values_and_beliefs(self, content: str) -> Dict[str, Any]:
        """
        Analyze values and beliefs expressed in the content
        """
        value_keywords = ["value", "important", "matter", "believe", "principle", "care"]
        belief_keywords = ["think", "feel", "know", "understand", "realize"]
        
        value_count = sum(len(re.findall(rf'\b{keyword}\b', content.lower())) for keyword in value_keywords)
        belief_count = sum(len(re.findall(rf'\b{keyword}\b', content.lower())) for keyword in belief_keywords)
        
        return {
            "values_expression": value_count,
            "beliefs_expression": belief_count,
            "values_clarity": "high" if value_count >= 3 else "medium" if value_count >= 1 else "low"
        }
    
    def _generate_logotherapy_response(self, content: str, themes: List[Dict[str, Any]], meaning_sources: List[Dict[str, Any]]) -> str:
        """
        Generate a logotherapy response based on identified themes and meaning sources
        """
        if not themes and not meaning_sources:
            return "I hear you sharing about your experiences. In logotherapy, we focus on finding meaning even in difficult circumstances. What matters most to you in life?"
        
        response_parts = []
        
        if themes:
            response_parts.append("I notice you're exploring some important existential themes:")
            for theme in themes[:2]:  # Focus on top 2 themes
                response_parts.append(f"- {theme['theme'].title()}: This is a fundamental aspect of human existence.")
        
        if meaning_sources:
            response_parts.append("\nI also see potential sources of meaning in your life:")
            for source in meaning_sources:
                response_parts.append(f"- {source['source']}")
        
        response_parts.append("\nLet's explore how you can connect with these sources of meaning and find purpose in your current situation.")
        
        return " ".join(response_parts)
    
    def _suggest_logotherapy_techniques(self, themes: List[Dict[str, Any]], meaning_sources: List[Dict[str, Any]]) -> List[str]:
        """
        Suggest logotherapy techniques based on identified themes and meaning sources
        """
        techniques = []
        
        # Add techniques based on themes
        for theme in themes:
            if "suffering" in theme["theme"]:
                techniques.append("Paradoxical intention")
                techniques.append("Dereflection")
            elif "meaning" in theme["theme"]:
                techniques.append("Socratic dialogue")
                techniques.append("Meaning analysis")
            elif "values" in theme["theme"]:
                techniques.append("Values clarification")
                techniques.append("Hierarchy of values exercise")
        
        # Add general logotherapy techniques
        techniques.extend([
            "Existential analysis",
            "Meaning-centered interventions",
            "Attitudinal values exploration"
        ])
        
        return list(set(techniques))
    
    def _generate_meaning_exploration_questions(self, themes: List[Dict[str, Any]]) -> List[str]:
        """
        Generate questions to explore meaning based on identified themes
        """
        questions = []
        
        for theme in themes:
            if "meaning and purpose" in theme["theme"]:
                questions.append("What gives your life meaning and purpose?")
                questions.append("What would you like to contribute to the world?")
            elif "suffering" in theme["theme"]:
                questions.append("How have you grown through difficult experiences?")
                questions.append("What meaning can you find in your current challenges?")
            elif "values" in theme["theme"]:
                questions.append("What values are most important to you?")
                questions.append("How do your actions align with your values?")
        
        # Add general meaning questions
        questions.extend([
            "What matters most to you in life?",
            "How do you want to be remembered?",
            "What would make your life feel complete?"
        ])
        
        return questions[:5]  # Limit to 5 questions
    
    async def _get_session_count(self, user_id: str) -> int:
        """
        Get the number of logotherapy sessions for a user
        """
        history = await self.get_user_history(user_id)
        return len(history)
    
    def _calculate_meaning_clarity(self, content: str) -> int:
        """
        Calculate a meaning clarity score (0-100)
        """
        meaning_keywords = ["meaning", "purpose", "value", "important", "matter", "goal"]
        meaning_count = sum(len(re.findall(rf'\b{keyword}\b', content.lower())) for keyword in meaning_keywords)
        
        # Simple scoring: more meaning-related words = higher clarity
        score = min(meaning_count * 20, 100)
        return score
    
    def _get_agent_description(self) -> str:
        return "Logotherapy agent specializing in meaning-centered therapy and existential analysis"
    
    def _get_agent_capabilities(self) -> List[str]:
        return [
            "Existential theme analysis",
            "Meaning source identification",
            "Suffering pattern analysis",
            "Values and beliefs exploration",
            "Logotherapy technique suggestions",
            "Meaning exploration questions",
            "Attitudinal values work"
        ] 