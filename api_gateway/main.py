from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from api_gateway.routers import user, auth, gamification, therapy, journaling, analytics
import uvicorn
from datetime import datetime
import logging
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import database
from database.connection import init_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MindFlora - AI-Powered Therapy Platform",
    description="Gamified, generative AI-powered mental health platform with evidence-based therapy modalities",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Security
security = HTTPBearer()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        init_db()
        logger.info("✅ Database initialized successfully!")
    except Exception as e:
        logger.warning(f"⚠️  Database initialization warning: {e}")
        logger.info("📝 Continuing with in-memory storage...")

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(user.router, prefix="/api/v1/users", tags=["users"])
app.include_router(therapy.router, prefix="/api/v1/therapy", tags=["therapy"])
app.include_router(gamification.router, prefix="/api/v1/gamification", tags=["gamification"])
app.include_router(journaling.router, prefix="/api/v1/journaling", tags=["journaling"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])

@app.get("/")
async def root():
    return {
        "message": "MindFlora - AI-Powered Therapy Platform",
        "version": "2.0.0",
        "status": "active",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "api_gateway": "active",
            "authentication": "active",
            "therapy_agents": "active",
            "gamification": "active",
            "memory_service": "active"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/platform-info")
async def get_platform_info():
    """Get platform information and available features"""
    return {
        "platform_name": "MindFlora",
        "description": "Gamified, generative AI-powered mental health platform",
        "therapy_modalities": [
            "Cognitive Behavioral Therapy (CBT)",
            "Acceptance and Commitment Therapy (ACT)",
            "Dialectical Behavior Therapy (DBT)",
            "Logotherapy",
            "Somotherapy",
            "Positive Psychology"
        ],
        "features": [
            "Agentic AI with memory and adaptive feedback",
            "Personalized daily missions",
            "Gamification with XP, streaks, and unlocks",
            "Mood analytics and journaling",
            "Privacy-first with Local Differential Privacy",
            "Therapist collaboration portal"
        ],
        "privacy_features": [
            "Local Differential Privacy (LDP)",
            "Data minimization",
            "GDPR/HIPAA compliance",
            "End-to-end encryption",
            "User data export/deletion"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 