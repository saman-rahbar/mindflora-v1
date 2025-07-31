# MindFlora - AI-Powered Therapy Platform

A gamified, generative AI-powered mental health platform with evidence-based therapy modalities.

## 🚀 Quick Start

### Option 1: Use the startup script (Recommended)
```bash
./start_services.sh
```

### Option 2: Manual startup

1. **Activate virtual environment:**
   ```bash
   source mindflora/bin/activate
   ```

2. **Start the backend server:**
   ```bash
   cd api_gateway
   uvicorn api_gateway.main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Start the frontend server (in a new terminal):**
   ```bash
   cd frontend
   python3 -m http.server 8080
   ```

## 🌐 Access Points

- **Frontend UI:** http://localhost:8080
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## 🎯 Features

### Core Features
- **🧠 Smart Therapy:** AI automatically determines the best therapy approach
- **🎮 Gamification:** XP, streaks, achievements, and daily missions
- **📝 Journaling:** Reflective writing with mood tracking
- **📊 Analytics:** Progress tracking and insights
- **🔒 Privacy-First:** Local Differential Privacy protection

### Therapy Modalities
- Cognitive Behavioral Therapy (CBT)
- Acceptance and Commitment Therapy (ACT)
- Dialectical Behavior Therapy (DBT)
- Logotherapy
- Somotherapy
- Positive Psychology

## 🛠️ API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Token refresh

### Therapy
- `POST /api/v1/therapy/session` - Traditional therapy session
- `POST /api/v1/therapy/smart-session` - AI-powered smart therapy

### Journaling
- `POST /api/v1/journaling/entry` - Create journal entry
- `GET /api/v1/journaling/entries` - Get journal entries

### Gamification
- `GET /api/v1/gamification/progress` - User progress
- `GET /api/v1/gamification/daily-missions` - Daily missions
- `POST /api/v1/gamification/complete-mission` - Complete mission

### Analytics
- `GET /api/v1/analytics/overview` - Progress overview
- `POST /api/v1/analytics/mood` - Track mood

## 🎨 UI Components

The frontend includes:

1. **Dashboard**
   - User progress overview
   - Daily missions
   - Quick mood check
   - XP and level display

2. **Therapy Section**
   - Smart therapy (AI-powered)
   - Traditional therapy selection
   - Therapy modality information
   - Session results display

3. **Journaling**
   - Write journal entries
   - View recent entries
   - Mood tracking integration

4. **Progress/Gamification**
   - Achievements display
   - Mission completion
   - Streak tracking

5. **Analytics**
   - Progress charts
   - Therapeutic insights
   - Activity summaries

## 🔧 Technical Stack

- **Backend:** FastAPI, Python 3.12
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Database:** SQLite (with SQLAlchemy ORM)
- **AI:** OpenAI GPT, Anthropic Claude
- **Authentication:** JWT tokens
- **Privacy:** Local Differential Privacy

## 🚨 Troubleshooting

### Server won't start
1. Make sure virtual environment is activated
2. Check if port 8000 is available
3. Verify all dependencies are installed: `pip install -r requirements.txt`

### Frontend not loading
1. Check if frontend server is running on port 8080
2. Verify backend is running on port 8000
3. Check browser console for CORS errors

### API calls failing
1. Verify backend is running
2. Check authentication tokens
3. Review API documentation at `/docs`

## 📝 Development

### Project Structure
```
mindflora_v1/
├── api_gateway/          # Backend API
│   ├── main.py          # FastAPI application
│   └── routers/         # API route handlers
├── frontend/            # Frontend UI
│   └── index.html       # Main UI file
├── database/            # Database models and services
├── therapy_agent_services/  # AI therapy agents
├── agent_router_service/    # Smart routing service
├── memory_service/      # User memory management
├── privacy_utils/       # Privacy utilities
└── requirements.txt     # Python dependencies
```

### Adding New Features
1. Add API endpoints in `api_gateway/routers/`
2. Update frontend JavaScript in `frontend/index.html`
3. Test with the provided startup script

## 🔒 Privacy & Security

- All user data is processed with Local Differential Privacy
- JWT tokens for secure authentication
- GDPR/HIPAA compliance features
- Data minimization practices

## 📞 Support

For issues or questions:
1. Check the API documentation at http://localhost:8000/docs
2. Review the browser console for frontend errors
3. Check the server logs for backend issues

---

**MindFlora** - Your journey to mental wellness starts here! 🌱
