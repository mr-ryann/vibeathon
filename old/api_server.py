"""
FastAPI Server for CreatorForge Nexus

This provides a REST API endpoint to run the complete multi-agent pipeline.
Your frontend can call this API to get complete content packages.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

# Import the NexusCore
from nexus_core import run_nexus

# Initialize FastAPI app
app = FastAPI(
    title="CreatorForge Nexus API",
    description="Multi-agent content creation system powered by LangGraph",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request/Response Models ---

class ContentRequest(BaseModel):
    """Request model for content generation"""
    topic: str
    user_vibe: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Rabbit R1 vs Humane AI Pin",
                "user_vibe": "Sarcastic tech reviews with dark humor"
            }
        }

class ContentResponse(BaseModel):
    """Response model with complete content package"""
    topic: str
    user_vibe: str
    scouted_trends: list
    content_pack: dict
    engage_plan: dict
    success: bool
    message: str

# --- API Endpoints ---

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "CreatorForge Nexus API",
        "version": "1.0.0",
        "agents": ["TrendScout", "ForgeMaster", "EngageBot"],
        "endpoints": {
            "forge_content": "/api/forge",
            "health": "/health"
        }
    }

@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "agents_available": 3,
        "langgraph_enabled": True
    }

@app.post("/api/forge", response_model=ContentResponse)
async def forge_content(request: ContentRequest):
    """
    Main endpoint: Runs the complete multi-agent pipeline
    
    This endpoint:
    1. Takes a topic and creator vibe
    2. Runs all 3 agents (TrendScout → ForgeMaster → EngageBot)
    3. Returns a complete content package
    
    Expected processing time: 30-45 seconds
    """
    
    try:
        print(f"\n🚀 API Request received:")
        print(f"   Topic: {request.topic}")
        print(f"   Vibe: {request.user_vibe}")
        
        # Run the complete NexusCore pipeline
        final_state = run_nexus(
            topic=request.topic,
            user_vibe=request.user_vibe
        )
        
        # Return the complete state as JSON
        return ContentResponse(
            topic=final_state.get('topic', ''),
            user_vibe=final_state.get('user_vibe', ''),
            scouted_trends=final_state.get('scouted_trends', []),
            content_pack=final_state.get('content_pack', {}),
            engage_plan=final_state.get('engage_plan', {}),
            success=True,
            message="Content package generated successfully!"
        )
    
    except Exception as e:
        print(f"❌ Error in API: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating content: {str(e)}"
        )

@app.post("/api/quick-test")
async def quick_test():
    """
    Quick test endpoint with default values
    Useful for testing without providing input
    """
    
    default_request = ContentRequest(
        topic="AI gadgets review",
        user_vibe="Sarcastic tech reviews"
    )
    
    return await forge_content(default_request)

# --- Run Server ---

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🚀 Starting CreatorForge Nexus API Server")
    print("=" * 80)
    print("\n📍 API will be available at:")
    print("   • Local:   http://localhost:8000")
    print("   • Docs:    http://localhost:8000/docs")
    print("   • Health:  http://localhost:8000/health")
    print("\n📡 Main endpoint:")
    print("   POST http://localhost:8000/api/forge")
    print("\n" + "=" * 80)
    
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
