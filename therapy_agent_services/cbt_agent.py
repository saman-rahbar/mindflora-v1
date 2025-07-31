from typing import Dict, Any, List
from .base import BaseTherapyAgent
from agent_router_service.interfaces import TherapyRequest
import re
import json

class CBTAgent(BaseTherapyAgent):
    """Cognitive Behavioral Therapy Agent"""
    
    def __init__(self):
        super().__init__("CBT Agent", "cbt")
        self.cognitive_distortions = [
            "all-or-nothing thinking",
            "overgeneralization", 
            "mental filter",
            "disqualifying the positive",
            "jumping to conclusions",
            "catastrophizing",
            "emotional reasoning",
            "should statements",
            "labeling",
            "personalization"
        ]
    
    async def process_therapy_request(self, request: TherapyRequest) -> Dict[str, Any]:
        """
        Process CBT therapy request using LLM
        """
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
        
        from llm_service.llm_client import llm_client
        
        # Analyze the session content using LLM
        analysis = await llm_client.analyze_content(
            request.session_content, 
            "cognitive_distortions"
        )
        
        # Generate therapeutic response using LLM
        prompt = f"""User session content: {request.session_content}

Please provide a CBT-focused therapeutic response that:
1. Acknowledges the user's feelings
2. Identifies any cognitive distortions
3. Suggests evidence-based CBT techniques
4. Offers compassionate support
5. Encourages further exploration

Keep the response warm, professional, and clinically appropriate."""
        
        # Create context with user information
        context = {
            "therapy_type": "cbt",
            "user_context": request.context.get("user_context", "") if request.context else ""
        }
        
        therapeutic_response = await llm_client.generate_response(
            prompt, 
            context=context
        )
        
        # Fallback to rule-based analysis if LLM fails
        if "error" in analysis:
            distortions = self._identify_cognitive_distortions(request.session_content)
            analysis = {
                "cognitive_distortions": distortions,
                "thought_patterns": self._analyze_thought_patterns(request.session_content),
                "emotion_analysis": self._analyze_emotions(request.session_content)
            }
            therapeutic_response = self._generate_cbt_response(request.session_content, distortions)
        
        # Create structured response
        return {
            "therapy_type": "cbt",
            "analysis": analysis,
            "intervention": {
                "techniques": self._suggest_cbt_techniques(analysis.get("cognitive_distortions", [])),
                "response": therapeutic_response,
                "homework": self._generate_homework_assignment(analysis.get("cognitive_distortions", []))
            },
            "progress_tracking": {
                "session_count": await self._get_session_count(request.user_id),
                "distortion_frequency": self._calculate_distortion_frequency(analysis.get("cognitive_distortions", []))
            }
        }
    
    def _identify_cognitive_distortions(self, content: str) -> List[Dict[str, Any]]:
        """
        Identify cognitive distortions in the content
        """
        distortions = []
        content_lower = content.lower()
        
        for distortion in self.cognitive_distortions:
            if distortion in content_lower:
                # Find specific examples in the text
                examples = self._find_distortion_examples(content, distortion)
                distortions.append({
                    "type": distortion,
                    "examples": examples,
                    "severity": self._assess_distortion_severity(examples)
                })
        
        return distortions
    
    def _find_distortion_examples(self, content: str, distortion: str) -> List[str]:
        """
        Find specific examples of cognitive distortions in the text
        """
        examples = []
        sentences = re.split(r'[.!?]+', content)
        
        for sentence in sentences:
            if distortion in sentence.lower():
                examples.append(sentence.strip())
        
        return examples[:3]  # Limit to 3 examples
    
    def _assess_distortion_severity(self, examples: List[str]) -> str:
        """
        Assess the severity of cognitive distortions
        """
        if len(examples) >= 3:
            return "high"
        elif len(examples) >= 1:
            return "medium"
        else:
            return "low"
    
    def _analyze_thought_patterns(self, content: str) -> Dict[str, Any]:
        """
        Analyze thought patterns in the content
        """
        return {
            "negative_thoughts": len(re.findall(r'\b(never|always|hate|terrible|awful|horrible)\b', content.lower())),
            "positive_thoughts": len(re.findall(r'\b(good|great|wonderful|amazing|love|happy)\b', content.lower())),
            "thought_balance": "negative" if len(re.findall(r'\b(never|always|hate|terrible|awful|horrible)\b', content.lower())) > len(re.findall(r'\b(good|great|wonderful|amazing|love|happy)\b', content.lower())) else "positive"
        }
    
    def _analyze_emotions(self, content: str) -> Dict[str, Any]:
        """
        Analyze emotional content
        """
        emotion_keywords = {
            "anxiety": ["anxious", "worried", "nervous", "fear", "panic"],
            "depression": ["sad", "depressed", "hopeless", "worthless", "empty"],
            "anger": ["angry", "furious", "irritated", "frustrated", "mad"],
            "joy": ["happy", "excited", "joyful", "pleased", "content"]
        }
        
        emotion_counts = {}
        for emotion, keywords in emotion_keywords.items():
            count = sum(len(re.findall(rf'\b{keyword}\b', content.lower())) for keyword in keywords)
            if count > 0:
                emotion_counts[emotion] = count
        
        return emotion_counts
    
    def _generate_cbt_response(self, content: str, distortions: List[Dict[str, Any]]) -> str:
        """
        Generate a CBT response based on identified distortions
        """
        if not distortions:
            return "I notice your thoughts seem balanced. Let's explore what's on your mind and how we can work together to maintain this positive perspective."
        
        response_parts = []
        response_parts.append("I've identified some thought patterns that might be affecting your perspective:")
        
        for distortion in distortions:
            response_parts.append(f"- {distortion['type'].title()}: This pattern can make situations seem more negative than they actually are.")
        
        response_parts.append("\nLet's work together to challenge these thoughts and develop more balanced perspectives.")
        
        return " ".join(response_parts)
    
    def _suggest_cbt_techniques(self, distortions: List[Dict[str, Any]]) -> List[str]:
        """
        Suggest CBT techniques based on identified distortions
        """
        techniques = []
        
        for distortion in distortions:
            if "all-or-nothing" in distortion["type"]:
                techniques.append("Thought continuum exercise")
            elif "catastrophizing" in distortion["type"]:
                techniques.append("Worst-case scenario analysis")
            elif "overgeneralization" in distortion["type"]:
                techniques.append("Evidence gathering")
            elif "mental filter" in distortion["type"]:
                techniques.append("Balanced thinking worksheet")
        
        # Add general techniques
        techniques.extend([
            "Cognitive restructuring",
            "Thought record",
            "Behavioral activation"
        ])
        
        return list(set(techniques))  # Remove duplicates
    
    def _generate_homework_assignment(self, distortions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate homework assignment based on identified distortions
        """
        if not distortions:
            return {
                "type": "gratitude_journal",
                "description": "Write down three things you're grateful for each day",
                "duration": "1 week"
            }
        
        return {
            "type": "thought_record",
            "description": "Record negative thoughts and challenge them with evidence",
            "duration": "1 week",
            "focus_areas": [d["type"] for d in distortions]
        }
    
    async def _get_session_count(self, user_id: str) -> int:
        """
        Get the number of CBT sessions for a user
        """
        history = await self.get_user_history(user_id)
        return len(history)
    
    def _calculate_distortion_frequency(self, distortions: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Calculate frequency of different distortion types
        """
        frequency = {}
        for distortion in distortions:
            distortion_type = distortion["type"]
            frequency[distortion_type] = frequency.get(distortion_type, 0) + 1
        return frequency
    
    def _get_agent_description(self) -> str:
        return "Cognitive Behavioral Therapy agent specializing in identifying and challenging cognitive distortions"
    
    def _get_agent_capabilities(self) -> List[str]:
        return [
            "Cognitive distortion identification",
            "Thought pattern analysis", 
            "Emotion analysis",
            "CBT technique suggestions",
            "Homework assignment generation",
            "Progress tracking"
        ] 