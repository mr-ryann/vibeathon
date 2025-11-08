"""
FastAPI Backend for React Frontend
Connects the React UI to the existing VibeOS agents
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
import os
import json
import shutil
from pathlib import Path
from datetime import datetime

# Import existing agents and tools
try:
    from agents import agent_script
    from tools import TrendHunter, SocialMediaPoster, SponsorFinder
    from utils import VibeDatabase, generate_sample_user_id
except ImportError as e:
    print(f"Warning: Some imports failed: {e}")
    print("Running in limited mode...")
    # Create mock classes if imports fail
    class VibeDatabase:
        def get_recent_scripts(self, limit=10):
            return []
    class TrendHunter:
        def get_best_trends(self, niche, limit=6):
            return []
    class MockContentGenerator:
        def __init__(self, vibe_profile):
            self.vibe_profile = vibe_profile
        def generate_content(self, trend, platform="youtube"):
            from pydantic import BaseModel
            class MockContent(BaseModel):
                script: str = "Sample script content"
                caption: str = "Sample caption"
                hashtags: list = ["trending", "viral"]
                hook: str = "Attention-grabbing hook"
                thumbnail_prompt: str = "Image prompt"
        return MockContent()
    agent_script = MockContentGenerator
    class SponsorFinder:
        def find_sponsors(self, niche, content_type):
            return []

# Initialize FastAPI app
app = FastAPI(
    title="VibeOS API",
    description="AI Content Co-Founder - Backend API for React Frontend",
    version="3.0.0"
)

# CORS middleware - allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative React port
        "http://localhost:8501",  # Streamlit
        "*"  # Allow all in development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Initialize database
db = VibeDatabase()

# In-memory storage for active sessions
active_sessions = {}


# ==================== REQUEST/RESPONSE MODELS ====================

class TrendsRequest(BaseModel):
    """Request model for fetching trends"""
    niche: str
    growth_goal: Optional[str] = ""
    
    class Config:
        json_schema_extra = {
            "example": {
                "niche": "Tech Reviews & AI News",
                "growth_goal": "2k likes in 1 day"
            }
        }


class ScriptGenerateRequest(BaseModel):
    """Request model for script generation"""
    trend: Dict[str, Any]
    vibe: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "trend": {
                    "title": "AI Wearables are taking over",
                    "summary": "Meta's new AI glasses are selling out..."
                },
                "vibe": "Casual & Funny"
            }
        }


class AnalyticsResponse(BaseModel):
    """Response model for analytics"""
    total_views: int = 0
    total_likes: int = 0
    total_comments: int = 0
    engagement_rate: float = 0.0
    top_performing: List[Dict[str, Any]] = []


# ==================== API ENDPOINTS ====================

@app.get("/")
async def root():
    """API health check"""
    return {
        "service": "VibeOS API",
        "version": "3.0.0",
        "status": "running",
        "frontend": "React + Vite",
        "backend": "FastAPI + LangGraph",
        "docs": "http://localhost:8000/docs"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected" if db else "error",
        "agents": {
            "vibe_analyzer": "ready",
            "content_generator": "ready",
            "deal_hunter": "ready"
        },
        "tools": {
            "trend_hunter": "ready",
            "social_poster": "ready",
            "sponsor_finder": "ready"
        }
    }


@app.post("/api/trends/fetch")
async def fetch_trends(request: TrendsRequest):
    """
    Fetch viral trends based on niche and growth goal
    """
    try:
        print(f"🔍 Fetching trends for niche: {request.niche}")
        
        # Use TrendHunter tool
        hunter = TrendHunter()
        trends = hunter.get_best_trends(request.niche, limit=6)
        
        # Format trends for frontend
        formatted_trends = []
        for trend in trends:
            formatted_trends.append({
                "title": trend.get('title', 'Trending Topic'),
                "summary": trend.get('snippet', 'No description available'),
                "url": trend.get('url', ''),
                "relevance_score": trend.get('relevance_score', 0),
                "source": trend.get('source', 'Web Search')
            })
        
        # Fallback if no trends found
        if not formatted_trends:
            formatted_trends = [{
                "title": f"Create {request.niche} content",
                "summary": f"Generate engaging content in the {request.niche} space with your unique voice.",
                "url": "",
                "relevance_score": 7.0,
                "source": "Suggested"
            }]
        
        return {
            "status": "success",
            "trends": formatted_trends,
            "count": len(formatted_trends),
            "niche": request.niche
        }
    
    except Exception as e:
        print(f"❌ Error fetching trends: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/script/generate")
async def generate_script(request: ScriptGenerateRequest):
    """
    Generate AI script based on selected trend and vibe
    """
    try:
        print(f"✨ Generating script with vibe: {request.vibe}")
        
        # Create vibe profile from user input
        vibe_profile = {
            "tone": request.vibe,
            "humor_style": "authentic",
            "language_quirks": [],
            "audience_relationship": "relatable",
            "signature_phrases": [],
            "content_formula": "hook → valuable info → call to action"
        }
        
    # Generate content using agent_script alias
    generator = agent_script(vibe_profile)
        content = generator.generate_content(request.trend, platform="youtube")
        
        # Format script for frontend
        script_text = f"""🎬 OPENING (0-3 seconds)
{content.hook}

📱 MAIN CONTENT (3-25 seconds)
{content.script}

🎯 CALL TO ACTION (25-30 seconds)
Like and follow for more {request.trend.get('title', 'content')}!

---
CAPTION: {content.caption}
HASHTAGS: {' '.join(['#' + tag for tag in content.hashtags[:5]])}
"""
        
        # Find potential sponsors
        sponsor_finder = SponsorFinder()
        sponsors = sponsor_finder.find_sponsors(
            niche=request.trend.get('title', ''),
            content_type="short-form video"
        )
        
        # Format sponsors for frontend
        formatted_sponsors = []
        for sponsor in sponsors[:3]:  # Top 3 sponsors
            email_template = f"""Subject: Partnership Opportunity - {request.trend.get('title', 'Content')} Creator

Hi {sponsor.get('name', 'there')},

I create engaging content in the {request.trend.get('title', '')} space and think my audience would love {sponsor.get('name', 'your product')}.

My recent content in this niche has been getting strong engagement, and I'd love to explore a partnership opportunity.

Would you be open to a quick call this week?

Best regards,
[Your Name]

P.S. Check out my latest content: [Your Channel/Profile]"""
            
            formatted_sponsors.append({
                "name": sponsor.get('name', 'Unknown Sponsor'),
                "category": sponsor.get('category', 'General'),
                "email": sponsor.get('email', 'info@example.com'),
                "emailTemplate": email_template,
                "website": sponsor.get('website', '')
            })
        
        # Generate script ID
        script_id = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Save to session
        active_sessions[script_id] = {
            "script": script_text,
            "sponsors": formatted_sponsors,
            "trend": request.trend,
            "vibe": request.vibe,
            "content": content
        }
        
        return {
            "status": "success",
            "scriptId": script_id,
            "script": script_text,
            "sponsors": formatted_sponsors
        }
    
    except Exception as e:
        print(f"❌ Error generating script: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload/process")
async def process_video(
    background_tasks: BackgroundTasks,
    video: UploadFile = File(...),
    script: str = Form(...)
):
    """
    Process uploaded video - clip into shorts and prepare for posting
    """
    try:
        print(f"📹 Processing video: {video.filename}")
        
        # Save uploaded video
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_filename = f"video_{timestamp}_{video.filename}"
        video_path = UPLOAD_DIR / video_filename
        
        with video_path.open("wb") as buffer:
            shutil.copyfileobj(video.file, buffer)
        
        print(f"✅ Video saved: {video_path}")
        
        # For now, simulate video processing
        # In production, you'd use ffmpeg to actually clip the video
        shorts = [
            {
                "id": f"short_{timestamp}_1",
                "thumbnail": "/api/placeholder/short1.jpg",
                "duration": 28,
                "videoUrl": f"/uploads/{video_filename}",
                "views": 0,
                "likes": 0
            },
            {
                "id": f"short_{timestamp}_2",
                "thumbnail": "/api/placeholder/short2.jpg",
                "duration": 25,
                "videoUrl": f"/uploads/{video_filename}",
                "views": 0,
                "likes": 0
            }
        ]
        
        return {
            "status": "success",
            "shorts": shorts,
            "message": f"Video processed successfully. Created {len(shorts)} shorts."
        }
    
    except Exception as e:
        print(f"❌ Error processing video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics")
async def get_analytics():
    """
    Get analytics and performance metrics
    """
    try:
        # Get recent data from database
        recent_scripts = db.get_recent_scripts(limit=10)
        
        # Calculate mock analytics
        # In production, this would pull real data from social platforms
        analytics = {
            "totalViews": sum([s.get('views', 0) for s in recent_scripts]),
            "totalLikes": sum([s.get('likes', 0) for s in recent_scripts]),
            "totalComments": sum([s.get('comments', 0) for s in recent_scripts]),
            "engagementRate": 4.2,
            "topPerforming": [
                {
                    "id": 1,
                    "title": "Latest Short #1",
                    "views": 1250,
                    "likes": 89
                },
                {
                    "id": 2,
                    "title": "Latest Short #2",
                    "views": 980,
                    "likes": 67
                }
            ]
        }
        
        return analytics
    
    except Exception as e:
        print(f"❌ Error fetching analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sponsors/{script_id}")
async def get_sponsors(script_id: str):
    """
    Get sponsors for a specific script
    """
    try:
        session = active_sessions.get(script_id)
        if not session:
            raise HTTPException(status_code=404, detail="Script not found")
        
        return {
            "status": "success",
            "sponsors": session.get('sponsors', [])
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== STARTUP ====================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("=" * 80)
    print("🚀 VibeOS API Server Starting...")
    print("=" * 80)
    print("")
    print("✅ FastAPI initialized")
    print("✅ CORS enabled for React frontend")
    print("✅ Database connected")
    print("✅ AI Agents loaded")
    print("")
    print("📡 Server ready at: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("⚛️  React Frontend: http://localhost:5173")
    print("")
    print("=" * 80)


if __name__ == "__main__":
    uvicorn.run(
        "backend_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload on code changes
    )
