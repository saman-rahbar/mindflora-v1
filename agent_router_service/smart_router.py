import sys
import os
sys.path.append(os.path.dirname(__file__))

from typing import Dict, Any, List, Optional
from interfaces import TherapyRequest, TherapyResponse
from therapy_agent_services.cbt_agent import CBTAgent
from therapy_agent_services.logotherapy_agent import LogotherapyAgent
import re

class SmartTherapyRouter:
    """Intelligent router that automatically determines the best therapy approach"""
    
    def __init__(self):
        self.agents = {
            "cbt": CBTAgent(),
            "logotherapy": LogotherapyAgent()
        }
        
        # Therapy modality indicators
        self.modality_indicators = {
            "cbt": {
                "keywords": [
                    "anxiety", "worry", "stress", "overwhelm", "panic", "fear",
                    "negative thoughts", "catastrophizing", "always", "never",
                    "hate", "terrible", "awful", "horrible", "failure", "worthless",
                    "perfectionist", "overthinking", "rumination", "self-doubt"
                ],
                "patterns": [
                    r"\b(always|never|everyone|nobody)\b",
                    r"\b(hate|terrible|awful|horrible)\b",
                    r"\b(failure|worthless|stupid|useless)\b",
                    r"\b(what if|worst case|disaster)\b"
                ]
            },
            "logotherapy": {
                "keywords": [
                    "meaning", "purpose", "pointless", "empty", "void",
                    "why bother", "what's the point", "no meaning", "lost",
                    "direction", "values", "beliefs", "spiritual", "existential",
                    "suffering", "pain", "growth", "transformation", "journey"
                ],
                "patterns": [
                    r"\b(meaning|purpose|point)\b",
                    r"\b(empty|void|lost)\b",
                    r"\b(why bother|what's the point)\b",
                    r"\b(suffering|pain|growth)\b"
                ]
            },
            "act": {
                "keywords": [
                    "accept", "control", "avoid", "escape", "suppress",
                    "feelings", "emotions", "thoughts", "mindfulness",
                    "present", "now", "values", "commitment", "action"
                ],
                "patterns": [
                    r"\b(control|avoid|escape)\b",
                    r"\b(suppress|ignore|push away)\b",
                    r"\b(mindfulness|present|now)\b"
                ]
            },
            "dbt": {
                "keywords": [
                    "emotion", "mood swings", "intense", "overwhelm",
                    "relationships", "conflict", "interpersonal", "borderline",
                    "regulation", "distress", "tolerance", "skills"
                ],
                "patterns": [
                    r"\b(mood swings|intense emotions)\b",
                    r"\b(relationships|conflict|interpersonal)\b",
                    r"\b(regulation|distress tolerance)\b"
                ]
            },
            "somotherapy": {
                "keywords": [
                    "body", "physical", "tension", "pain", "trauma",
                    "somatic", "sensation", "breathing", "grounding",
                    "dissociation", "numbness", "body awareness"
                ],
                "patterns": [
                    r"\b(body|physical|tension)\b",
                    r"\b(trauma|somatic|sensation)\b",
                    r"\b(breathing|grounding)\b"
                ]
            },
            "positive_psychology": {
                "keywords": [
                    "happiness", "joy", "gratitude", "strengths", "positive",
                    "optimism", "hope", "flourishing", "well-being", "growth",
                    "resilience", "thriving", "fulfillment"
                ],
                "patterns": [
                    r"\b(happiness|joy|gratitude)\b",
                    r"\b(strengths|positive|optimism)\b",
                    r"\b(flourishing|well-being)\b"
                ]
            }
        }
    
    async def analyze_and_route(self, user_input: str, mood_rating: Optional[int] = None) -> Dict[str, Any]:
        """Analyze user input and determine the best therapy approach"""
        
        # Analyze the content for different therapy modalities
        analysis = self._analyze_content(user_input.lower())
        
        # Determine primary and secondary therapy approaches
        primary_therapy = self._determine_primary_therapy(analysis, mood_rating)
        secondary_therapies = self._get_secondary_therapies(analysis, primary_therapy)
        
        # Generate personalized recommendation
        recommendation = self._generate_recommendation(primary_therapy, analysis, user_input)
        
        return {
            "primary_therapy": primary_therapy,
            "secondary_therapies": secondary_therapies,
            "analysis": analysis,
            "recommendation": recommendation,
            "confidence": self._calculate_confidence(analysis, primary_therapy),
            "mood_rating": mood_rating
        }
    
    def _analyze_content(self, content: str) -> Dict[str, Any]:
        """Analyze content for different therapy modality indicators"""
        analysis = {}
        
        for modality, indicators in self.modality_indicators.items():
            score = 0
            matches = []
            
            # Check keywords
            for keyword in indicators["keywords"]:
                if keyword in content:
                    score += 1
                    matches.append(keyword)
            
            # Check patterns
            for pattern in indicators["patterns"]:
                pattern_matches = re.findall(pattern, content)
                score += len(pattern_matches)
                matches.extend(pattern_matches)
            
            analysis[modality] = {
                "score": score,
                "matches": list(set(matches)),
                "confidence": min(score / 3, 1.0)  # Normalize confidence
            }
        
        return analysis
    
    def _determine_primary_therapy(self, analysis: Dict[str, Any], mood_rating: Optional[int]) -> str:
        """Determine the primary therapy approach"""
        
        # Get the modality with the highest score
        best_modality = max(analysis.items(), key=lambda x: x[1]["score"])
        
        # Adjust based on mood rating
        if mood_rating is not None:
            if mood_rating <= 3:
                # Low mood might indicate need for CBT or positive psychology
                if analysis.get("cbt", {}).get("score", 0) > 0:
                    return "cbt"
                elif analysis.get("positive_psychology", {}).get("score", 0) > 0:
                    return "positive_psychology"
            elif mood_rating >= 8:
                # High mood might indicate readiness for growth-focused therapies
                if analysis.get("logotherapy", {}).get("score", 0) > 0:
                    return "logotherapy"
                elif analysis.get("positive_psychology", {}).get("score", 0) > 0:
                    return "positive_psychology"
        
        return best_modality[0] if best_modality[1]["score"] > 0 else "cbt"
    
    def _get_secondary_therapies(self, analysis: Dict[str, Any], primary: str) -> List[str]:
        """Get secondary therapy approaches"""
        # Get modalities with scores > 0, excluding primary
        secondary = []
        for modality, data in analysis.items():
            if modality != primary and data["score"] > 0:
                secondary.append(modality)
        
        return secondary[:2]  # Limit to 2 secondary approaches
    
    def _generate_recommendation(self, primary_therapy: str, analysis: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """Generate personalized therapy recommendation"""
        
        therapy_descriptions = {
            "cbt": {
                "name": "Cognitive Behavioral Therapy (CBT)",
                "description": "CBT helps identify and challenge negative thought patterns that may be contributing to your distress.",
                "focus": "Thought patterns, anxiety, depression, stress management",
                "benefits": "Reduces anxiety, improves mood, develops coping skills",
                "approach": "Structured, evidence-based, practical techniques"
            },
            "logotherapy": {
                "name": "Logotherapy (Meaning-Centered Therapy)",
                "description": "Logotherapy helps you find meaning and purpose in your experiences, even during difficult times.",
                "focus": "Meaning, purpose, values, existential questions",
                "benefits": "Increases life satisfaction, provides direction, builds resilience",
                "approach": "Exploratory, value-focused, meaning-centered"
            },
            "act": {
                "name": "Acceptance and Commitment Therapy (ACT)",
                "description": "ACT helps you accept difficult thoughts and feelings while committing to actions aligned with your values.",
                "focus": "Acceptance, mindfulness, values, psychological flexibility",
                "benefits": "Reduces suffering, increases flexibility, improves well-being",
                "approach": "Mindfulness-based, acceptance-focused, value-driven"
            },
            "dbt": {
                "name": "Dialectical Behavior Therapy (DBT)",
                "description": "DBT teaches skills for emotional regulation, distress tolerance, and interpersonal effectiveness.",
                "focus": "Emotional regulation, relationships, distress tolerance",
                "benefits": "Improves emotional control, enhances relationships, builds skills",
                "approach": "Skill-based, structured, relationship-focused"
            },
            "somotherapy": {
                "name": "Somotherapy (Body-Centered Therapy)",
                "description": "Somotherapy focuses on the mind-body connection and uses body awareness for healing.",
                "focus": "Body awareness, trauma, physical sensations, grounding",
                "benefits": "Reduces physical tension, processes trauma, improves awareness",
                "approach": "Body-focused, experiential, trauma-informed"
            },
            "positive_psychology": {
                "name": "Positive Psychology",
                "description": "Positive psychology focuses on building strengths, gratitude, and positive emotions.",
                "focus": "Strengths, gratitude, optimism, well-being",
                "benefits": "Increases happiness, builds resilience, enhances life satisfaction",
                "approach": "Strength-based, positive-focused, growth-oriented"
            }
        }
        
        therapy_info = therapy_descriptions.get(primary_therapy, therapy_descriptions["cbt"])
        
        # Generate personalized message
        if primary_therapy == "cbt":
            if "anxiety" in user_input.lower() or "worry" in user_input.lower():
                personalized_message = "I notice you're experiencing anxiety and worry. CBT can help you identify the thoughts that are fueling these feelings and develop more balanced thinking patterns."
            elif "negative" in user_input.lower() or "failure" in user_input.lower():
                personalized_message = "I see you're struggling with negative thoughts about yourself. CBT can help you challenge these thoughts and develop a more compassionate perspective."
            else:
                personalized_message = "Based on what you've shared, CBT can help you identify and change the thought patterns that may be contributing to your distress."
        
        elif primary_therapy == "logotherapy":
            if "meaning" in user_input.lower() or "purpose" in user_input.lower():
                personalized_message = "I hear you're searching for meaning and purpose. Logotherapy can help you discover what truly matters to you and find direction in your life."
            elif "suffering" in user_input.lower() or "pain" in user_input.lower():
                personalized_message = "I understand you're going through difficult times. Logotherapy can help you find meaning even in suffering and grow through your challenges."
            else:
                personalized_message = "Based on your reflections, Logotherapy can help you explore what gives your life meaning and purpose."
        
        else:
            personalized_message = f"Based on what you've shared, {therapy_info['name']} seems like the best approach for your current needs."
        
        return {
            "therapy_info": therapy_info,
            "personalized_message": personalized_message,
            "next_steps": [
                "Start a therapy session with this approach",
                "Learn more about this therapy type",
                "Try a different approach if this doesn't feel right"
            ]
        }
    
    def _calculate_confidence(self, analysis: Dict[str, Any], primary_therapy: str) -> float:
        """Calculate confidence in the recommendation"""
        primary_score = analysis.get(primary_therapy, {}).get("score", 0)
        total_score = sum(data["score"] for data in analysis.values())
        
        if total_score == 0:
            return 0.5  # Default confidence if no clear indicators
        
        return min(primary_score / total_score, 1.0)
    
    async def process_smart_session(self, user_input: str, mood_rating: Optional[int] = None) -> Dict[str, Any]:
        """Process a therapy session with automatic modality selection"""
        
        # Analyze and route to best therapy
        routing_result = await self.analyze_and_route(user_input, mood_rating)
        
        # Create therapy request
        therapy_request = TherapyRequest(
            user_id="user",  # Will be set by the API
            therapy_type=routing_result["primary_therapy"],
            session_content=user_input,
            mood_before=mood_rating
        )
        
        # Process with the selected agent
        if routing_result["primary_therapy"] in self.agents:
            agent_response = await self.agents[routing_result["primary_therapy"]].process_therapy_request(therapy_request)
        else:
            # Fallback to CBT
            agent_response = await self.agents["cbt"].process_therapy_request(therapy_request)
        
        return {
            "routing_analysis": routing_result,
            "therapy_response": agent_response,
            "recommended_therapy": routing_result["primary_therapy"],
            "confidence": routing_result["confidence"]
        }

# Global smart router instance
smart_router = SmartTherapyRouter() 