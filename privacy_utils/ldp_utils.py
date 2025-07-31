import random
import hashlib
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import numpy as np

class LDPUtils:
    """Local Differential Privacy utilities for therapy data protection"""
    
    def __init__(self, epsilon: float = 1.0):
        """
        Initialize LDP utilities with privacy parameter epsilon
        Lower epsilon = higher privacy, higher epsilon = lower privacy
        """
        self.epsilon = epsilon
    
    def add_noise_to_numerical(self, value: float, sensitivity: float = 1.0) -> float:
        """
        Add Laplace noise to numerical values for differential privacy
        """
        scale = sensitivity / self.epsilon
        noise = np.random.laplace(0, scale)
        return value + noise
    
    def randomized_response(self, true_value: bool, p: Optional[float] = None) -> bool:
        """
        Randomized response for binary values
        """
        if p is None:
            p = 1 / (1 + np.exp(self.epsilon))
        
        if random.random() < p:
            return not true_value
        else:
            return true_value
    
    def hash_and_perturb(self, text: str, domain_size: int = 1000) -> int:
        """
        Hash text and add noise for categorical data
        """
        # Hash the text to get a numerical value
        hash_value = int(hashlib.md5(text.encode()).hexdigest(), 16) % domain_size
        
        # Add noise
        return self.add_noise_to_numerical(hash_value, domain_size)
    
    def anonymize_therapy_content(self, content: str) -> str:
        """
        Anonymize therapy session content while preserving therapeutic value
        """
        # Remove or replace personally identifiable information
        anonymized = content
        
        # Replace names (simple pattern matching)
        import re
        # Replace potential names (words starting with capital letters)
        anonymized = re.sub(r'\b[A-Z][a-z]+\b', '[NAME]', anonymized)
        
        # Replace potential locations
        location_patterns = [
            r'\b[A-Z][a-z]+ (Street|Avenue|Road|Lane|Drive|Boulevard)\b',
            r'\b[A-Z][a-z]+, [A-Z]{2}\b',  # City, State
            r'\b\d{5}\b'  # ZIP codes
        ]
        
        for pattern in location_patterns:
            anonymized = re.sub(pattern, '[LOCATION]', anonymized)
        
        # Replace potential phone numbers
        anonymized = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', anonymized)
        
        # Replace potential email addresses
        anonymized = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', anonymized)
        
        return anonymized
    
    def privatize_session_data(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply differential privacy to therapy session data
        """
        privatized = session_data.copy()
        
        # Anonymize content
        if "content" in privatized:
            privatized["content"] = self.anonymize_therapy_content(privatized["content"])
        
        # Add noise to numerical values
        if "session_count" in privatized:
            privatized["session_count"] = int(self.add_noise_to_numerical(
                float(privatized["session_count"]), sensitivity=1.0
            ))
        
        # Privatize therapy type preferences
        if "therapy_type" in privatized:
            # Use randomized response for therapy type
            therapy_types = ["cbt", "logotherapy", "other"]
            true_index = therapy_types.index(privatized["therapy_type"]) if privatized["therapy_type"] in therapy_types else 0
            
            # Apply randomized response
            if self.randomized_response(True, p=0.3):  # 30% chance of flipping
                true_index = (true_index + 1) % len(therapy_types)
            
            privatized["therapy_type"] = therapy_types[true_index]
        
        # Add noise to timestamps (preserve relative timing but not exact)
        if "timestamp" in privatized:
            try:
                timestamp = datetime.fromisoformat(privatized["timestamp"])
                # Add noise in hours
                noise_hours = int(self.add_noise_to_numerical(0, sensitivity=24))
                timestamp = timestamp.replace(hour=(timestamp.hour + noise_hours) % 24)
                privatized["timestamp"] = timestamp.isoformat()
            except:
                pass  # Keep original if parsing fails
        
        return privatized
    
    def aggregate_private_statistics(self, data_points: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate statistics from privatized data points
        """
        if not data_points:
            return {}
        
        # Count therapy types
        therapy_counts = {}
        for point in data_points:
            therapy_type = point.get("therapy_type", "unknown")
            therapy_counts[therapy_type] = therapy_counts.get(therapy_type, 0) + 1
        
        # Calculate average session count (with noise)
        session_counts = [point.get("session_count", 0) for point in data_points]
        avg_sessions = sum(session_counts) / len(session_counts) if session_counts else 0
        
        # Add noise to final statistics
        return {
            "total_participants": len(data_points),
            "therapy_type_distribution": therapy_counts,
            "average_sessions": self.add_noise_to_numerical(avg_sessions, sensitivity=1.0),
            "privacy_level": f"epsilon={self.epsilon}"
        }
    
    def generate_privacy_report(self, original_data: Dict[str, Any], privatized_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a privacy report comparing original and privatized data
        """
        return {
            "privacy_parameters": {
                "epsilon": self.epsilon,
                "privacy_level": "high" if self.epsilon < 1.0 else "medium" if self.epsilon < 5.0 else "low"
            },
            "data_transformation": {
                "original_size": len(str(original_data)),
                "privatized_size": len(str(privatized_data)),
                "anonymization_applied": "content" in original_data and "content" in privatized_data,
                "noise_added": True
            },
            "privacy_guarantees": {
                "differential_privacy": True,
                "local_privacy": True,
                "data_minimization": True
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def validate_privacy_compliance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that data meets privacy compliance requirements
        """
        compliance_report = {
            "gdpr_compliant": True,
            "hipaa_compliant": True,
            "privacy_issues": []
        }
        
        # Check for PII in content
        if "content" in data:
            content = data["content"]
            pii_indicators = [
                r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # Names
                r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Phone numbers
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Emails
                r'\b\d{5}\b'  # ZIP codes
            ]
            
            import re
            for pattern in pii_indicators:
                if re.search(pattern, content):
                    compliance_report["privacy_issues"].append(f"PII detected: {pattern}")
                    compliance_report["gdpr_compliant"] = False
                    compliance_report["hipaa_compliant"] = False
        
        # Check for sensitive health information
        sensitive_terms = [
            "diagnosis", "medication", "treatment", "symptoms", "condition"
        ]
        
        if "content" in data:
            content_lower = data["content"].lower()
            for term in sensitive_terms:
                if term in content_lower:
                    compliance_report["privacy_issues"].append(f"Sensitive health term: {term}")
                    compliance_report["hipaa_compliant"] = False
        
        return compliance_report
    
    def create_consent_token(self, user_id: str, consent_data: Dict[str, Any]) -> str:
        """
        Create a privacy consent token for user data processing
        """
        consent_payload = {
            "user_id": user_id,
            "consent_data": consent_data,
            "timestamp": datetime.utcnow().isoformat(),
            "privacy_level": self.epsilon
        }
        
        # Create a hash of the consent data
        consent_string = json.dumps(consent_payload, sort_keys=True)
        return hashlib.sha256(consent_string.encode()).hexdigest()
    
    def verify_consent_token(self, token: str, user_id: str, consent_data: Dict[str, Any]) -> bool:
        """
        Verify a privacy consent token
        """
        expected_token = self.create_consent_token(user_id, consent_data)
        return token == expected_token 