"""
FastAPI Server for CreatorForge Nexus

Updated for two-phase architecture:
- POST /generate-script - Phase 1: Generate script
- POST /process-video - Phase 2: Process uploaded video and create shorts
- GET /recent-scripts - Get recent generated scripts
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
import os
import shutil
from pathlib import Path

# Import the updated NexusCore
from nexus_core import run_nexus_phase1, run_nexus_phase2, db

# Initialize FastAPI app
app = FastAPI(
    title="CreatorForge Nexus API",
    description="Two-phase multi-agent content creation system powered by LangGraph",
    version="2.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


# --- Request/Response Models ---

class ScriptRequest(BaseModel):
    """Request model for Phase 1: Script generation"""
    topic: str
    niche: str
    user_vibe: str
    goals: Optional[str] = ""
    
    class Config:
        json_schema_extra = {
            "example": {
                "topic": "AI Wearable Devices",
                "niche": "Tech reviews and gadget analysis",
                "user_vibe": "Sarcastic and brutally honest",
                "goals": "Build 100k followers and land first sponsor"
            }
        }


class ScriptResponse(BaseModel):
    """Response model for Phase 1: Generated script"""
    script_id: int
    topic: str
    niche: str
    user_vibe: str
    script: Dict[str, Any]
    scouted_trends: List[Dict[str, str]]
    status: str
    message: str


class VideoProcessResponse(BaseModel):
    """Response model for Phase 2: Processed video"""
    script_id: int
    video_id: int
    clipped_shorts: List[Dict[str, Any]]
    engage_plan: Dict[str, Any]
    deal_plan: List[Dict[str, Any]]
    status: str
    message: str


# --- API Endpoints ---

@app.get("/")
async def root():
    """API health check"""
    return {
        "service": "CreatorForge Nexus API",
        "version": "2.0.0",
        "status": "running",
        "architecture": "two-phase",
        "endpoints": {
            "POST /generate-script": "Phase 1: Generate script from trends",
            "POST /process-video": "Phase 2: Process video and create shorts",
            "GET /recent-scripts": "Get recently generated scripts"
        }
    }


@app.post("/generate-script", response_model=ScriptResponse)
async def generate_script(request: ScriptRequest):
    """
    Phase 1: Generate script from trends
    
    This endpoint:
    1. Runs TrendScout to find viral trends
    2. Runs ForgeMaster to generate a human-shootable script
    3. Returns the script for user to shoot video
    """
    try:
        # Run Phase 1
        state = run_nexus_phase1(
            topic=request.topic,
            niche=request.niche,
            user_vibe=request.user_vibe,
            goals=request.goals
        )
        
        # Check for errors
        if state.get('error'):
            raise HTTPException(status_code=500, detail=state['error'])
        
        # Check if script was generated
        if not state.get('generated_script'):
            raise HTTPException(status_code=500, detail="Failed to generate script")
        
        return ScriptResponse(
            script_id=state.get('script_id', 0),
            topic=request.topic,
            niche=request.niche,
            user_vibe=request.user_vibe,
            script=state['generated_script'],
            scouted_trends=state.get('scouted_trends', []),
            status="success",
            message="Script generated successfully. Please shoot video and upload for Phase 2."
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process-video", response_model=VideoProcessResponse)
async def process_video(
    script_id: int = Form(...),
    video: UploadFile = File(...)
):
    """
    Phase 2: Process uploaded video and create shorts
    
    This endpoint:
    1. Receives uploaded video file
    2. Runs EngageBot to clip into shorts and post
    3. Runs DealHunter to find sponsors and generate pitches
    4. Returns clipped shorts and sponsor opportunities
    """
    try:
        # Save uploaded video
        video_filename = f"video_{script_id}_{video.filename}"
        video_path = UPLOAD_DIR / video_filename
        
        with video_path.open("wb") as buffer:
            shutil.copyfileobj(video.file, buffer)
        
        print(f"📹 Video uploaded: {video_path}")
        
        # Get script from database
        scripts = db.get_recent_scripts(limit=100)
        script_state = next((s for s in scripts if s['id'] == script_id), None)
        
        if not script_state:
            raise HTTPException(status_code=404, detail=f"Script ID {script_id} not found")
        
        # Reconstruct state for Phase 2
        from agent_trendscout import GraphState
        state = GraphState(
            topic=script_state['topic'],
            niche=script_state['niche'],
            user_vibe=script_state['vibe'],
            goals="",
            scouted_trends=[],
            generated_script={
                'intro': script_state['intro'],
                'body': script_state['body'],
                'outro': script_state['outro'],
                'full_script': script_state['full_script']
            },
            video_path=str(video_path),
            clipped_shorts=[],
            engage_plan={},
            deal_plan=[],
            error=""
        )
        state['script_id'] = script_id
        
        # Run Phase 2
        final_state = run_nexus_phase2(state, str(video_path))
        
        # Check for errors
        if final_state.get('error'):
            raise HTTPException(status_code=500, detail=final_state['error'])
        
        return VideoProcessResponse(
            script_id=script_id,
            video_id=final_state.get('video_id', 0),
            clipped_shorts=final_state.get('clipped_shorts', []),
            engage_plan=final_state.get('engage_plan', {}),
            deal_plan=final_state.get('deal_plan', []),
            status="success",
            message=f"Video processed successfully. Created {len(final_state.get('clipped_shorts', []))} shorts and found {len(final_state.get('deal_plan', []))} sponsors."
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/recent-scripts")
async def get_recent_scripts(limit: int = 10):
    """
    Get recently generated scripts
    
    Args:
        limit: Maximum number of scripts to return (default: 10)
    
    Returns:
        List of recent scripts with metadata
    """
    try:
        scripts = db.get_recent_scripts(limit=limit)
        return {
            "status": "success",
            "count": len(scripts),
            "scripts": scripts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected" if db else "error",
        "ffmpeg": "available" if os.system("which ffmpeg > /dev/null 2>&1") == 0 else "not installed"
    }


# --- Main execution ---
if __name__ == "__main__":
    print("=" * 80)
    print("🚀 CreatorForge Nexus API Server")
    print("=" * 80)
    print("")
    print("📡 Starting FastAPI server...")
    print("📋 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("")
    print("Available endpoints:")
    print("  POST /generate-script - Phase 1: Generate script")
    print("  POST /process-video - Phase 2: Process video")
    print("  GET /recent-scripts - Get recent scripts")
    print("")
    print("=" * 80)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
