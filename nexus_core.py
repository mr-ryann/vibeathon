"""
core - The Brain of Nexus (formerly NexusCore)

Updated Architecture:
1. Script Generation (ripple → quill)
2. User Shoot/Upload Step (manual intervention)
3. Shorts Clipping & Posting Loop (pulse)
4. Sponsor Pitching (envoy)

Includes SQLite storage for scripts and videos.
Name: core - the central orchestrator, the brain of the operation
"""

import os
import sqlite3
from datetime import datetime
from typing import TypedDict, List, Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# LangGraph imports
from langgraph.graph import StateGraph, END, START

# Import all agent functions
from agent_ripple import run_ripple, GraphState
from agent_quill import run_quill
from agent_pulse import run_pulse
from agent_envoy import run_envoy

# Load environment variables
load_dotenv()


# --- Database Setup ---
class NexusDatabase:
    """SQLite database for storing scripts, videos, and workflow state"""
    
    def __init__(self, db_path: str = "nexus_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Scripts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scripts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                niche TEXT,
                vibe TEXT,
                intro TEXT,
                body TEXT,
                outro TEXT,
                full_script TEXT,
                shot_count INTEGER,
                difficulty TEXT,
                props_needed TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'generated'
            )
        """)
        
        # Videos table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                script_id INTEGER,
                video_path TEXT NOT NULL,
                duration REAL,
                file_size INTEGER,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'uploaded',
                FOREIGN KEY (script_id) REFERENCES scripts(id)
            )
        """)
        
        # Shorts/Clips table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shorts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id INTEGER,
                clip_path TEXT NOT NULL,
                start_time REAL,
                duration REAL,
                file_size INTEGER,
                posted BOOLEAN DEFAULT 0,
                platform TEXT,
                post_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (video_id) REFERENCES videos(id)
            )
        """)
        
        # Sponsors table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sponsors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                script_id INTEGER,
                company_name TEXT NOT NULL,
                website TEXT,
                partnership_type TEXT,
                pitch_sent BOOLEAN DEFAULT 0,
                pitch_template TEXT,
                response_status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (script_id) REFERENCES scripts(id)
            )
        """)
        
        conn.commit()
        conn.close()
        print(f"✅ Database initialized: {self.db_path}")
    
    def save_script(self, script_data: Dict[str, Any], topic: str, niche: str, vibe: str) -> int:
        """Save generated script to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO scripts (topic, niche, vibe, intro, body, outro, full_script, 
                                shot_count, difficulty, props_needed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            topic,
            niche,
            vibe,
            script_data.get('intro', ''),
            script_data.get('body', ''),
            script_data.get('outro', ''),
            script_data.get('full_script', ''),
            script_data.get('shot_count', 1),
            script_data.get('difficulty', 'easy'),
            ','.join(script_data.get('props_needed', []))
        ))
        
        script_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"💾 Script saved to database (ID: {script_id})")
        return script_id
    
    def save_video(self, script_id: int, video_path: str, duration: float, file_size: int) -> int:
        """Save uploaded video to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO videos (script_id, video_path, duration, file_size)
            VALUES (?, ?, ?, ?)
        """, (script_id, video_path, duration, file_size))
        
        video_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"💾 Video saved to database (ID: {video_id})")
        return video_id
    
    def save_shorts(self, video_id: int, clips: List[Dict[str, Any]]):
        """Save clipped shorts to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for clip in clips:
            if clip.get('is_mock'):
                continue  # Skip mock clips
            
            cursor.execute("""
                INSERT INTO shorts (video_id, clip_path, start_time, duration, 
                                  file_size, posted, platform)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                video_id,
                clip.get('path', ''),
                clip.get('start_time', 0),
                clip.get('duration', 0),
                clip.get('size_bytes', 0),
                clip.get('posted', False),
                'Twitter/X' if clip.get('posted') else None
            ))
        
        conn.commit()
        conn.close()
        
        print(f"💾 {len(clips)} shorts saved to database")
    
    def save_sponsors(self, script_id: int, deals: List[Dict[str, Any]]):
        """Save sponsor deals to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for deal in deals:
            cursor.execute("""
                INSERT INTO sponsors (script_id, company_name, website, 
                                    partnership_type, pitch_template)
                VALUES (?, ?, ?, ?, ?)
            """, (
                script_id,
                deal.get('company_name', ''),
                deal.get('website', ''),
                deal.get('partnership_type', ''),
                deal.get('pitch_template', '')
            ))
        
        conn.commit()
        conn.close()
        
        print(f"💾 {len(deals)} sponsor opportunities saved to database")
    
    def get_recent_scripts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent scripts from database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM scripts ORDER BY created_at DESC LIMIT ?
        """, (limit,))
        
        scripts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return scripts


# Global database instance
db = NexusDatabase()


# --- API Key Validation ---
def validate_api_keys():
    """Validates that required API keys are present"""
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    if not gemini_key:
        raise EnvironmentError(
            "🚨 GEMINI_API_KEY not found in environment.\n"
            "Please create a .env file with: GEMINI_API_KEY=your_key_here"
        )
    
    if len(gemini_key.strip()) < 10:
        raise EnvironmentError(
            "🚨 GEMINI_API_KEY appears to be invalid (too short).\n"
            "Please check your .env file."
        )
    
    print("✅ API keys validated successfully")


# Validate on module import
validate_api_keys()


# --- Error Handler Node ---
def error_handler(state: GraphState) -> GraphState:
    """Handles workflow errors"""
    error_msg = state.get('error', '⚠️ Pipeline failed: One or more agents did not produce valid output')
    
    print(f"\n{error_msg}")
    print("Workflow will terminate early.\n")
    
    return state


# --- Conditional Routing Functions ---
def check_for_trends(state: GraphState) -> str:
    """Routes after ripple based on trends found"""
    scouted_trends = state.get('scouted_trends', [])
    
    if not scouted_trends or len(scouted_trends) == 0:
        print("⚠️ No trends found by ripple - routing to error handler")
        return "error_handler"
    
    print(f"✅ Found {len(scouted_trends)} trends - proceeding to quill")
    return "quill"


def check_for_script(state: GraphState) -> str:
    """Routes after quill based on script generation"""
    generated_script = state.get('generated_script', {})
    
    if not generated_script or not generated_script.get('full_script'):
        print("⚠️ No script generated - routing to error handler")
        return "error_handler"
    
    print("✅ Script generated - workflow paused for user to shoot video")
    return "awaiting_video"


def check_for_video(state: GraphState) -> str:
    """Routes based on whether video was uploaded"""
    video_path = state.get('video_path', '')
    
    if video_path and os.path.exists(video_path):
        print(f"✅ Video uploaded: {video_path} - proceeding to pulse")
        return "pulse"
    else:
        print("⚠️ No video uploaded - pulse will use mock clips")
        return "pulse"  # Still proceed, but with mock data


# --- Workflow Creation ---
def create_nexus_workflow():
    """
    Creates the complete multi-agent workflow with new architecture.
    
    Workflow:
    1. ripple → find trends
    2. quill → generate script
    3. [PAUSE] → user shoots video
    4. pulse → clip shorts & post
    5. envoy → find sponsors & pitch
    """
    
    workflow = StateGraph(GraphState)
    
    # Add agent nodes
    workflow.add_node("ripple", run_ripple)
    workflow.add_node("quill", run_quill)
    workflow.add_node("pulse", run_pulse)
    workflow.add_node("envoy", run_envoy)
    workflow.add_node("error_handler", error_handler)
    
    # Dummy node for awaiting video upload
    def awaiting_video_node(state: GraphState) -> GraphState:
        print("\n" + "=" * 80)
        print("⏸️  WORKFLOW PAUSED - AWAITING USER ACTION")
        print("=" * 80)
        print("\n📋 Next Steps:")
        print("   1. Review the generated script")
        print("   2. Shoot the video using your smartphone")
        print("   3. Upload the video to continue workflow")
        print("\n💡 Tip: Follow the [camera directions] in the script for best results")
        print("=" * 80 + "\n")
        return state
    
    workflow.add_node("awaiting_video", awaiting_video_node)
    
    # Define execution flow - use START for entry point in LangGraph 1.0+
    workflow.add_edge(START, "ripple")
    
    # ripple → conditional routing
    workflow.add_conditional_edges(
        "ripple",
        check_for_trends,
        {
            "error_handler": "error_handler",
            "quill": "quill"
        }
    )
    
    # Error handler → END
    workflow.add_edge("error_handler", END)
    
    # quill → conditional routing
    workflow.add_conditional_edges(
        "quill",
        check_for_script,
        {
            "error_handler": "error_handler",
            "awaiting_video": "awaiting_video"
        }
    )
    
    # Awaiting video → pulse (when resumed)
    workflow.add_edge("awaiting_video", "pulse")
    
    # pulse → envoy
    workflow.add_edge("pulse", "envoy")
    
    # envoy → END
    workflow.add_edge("envoy", END)
    
    # Compile the graph
    app = workflow.compile()
    
    return app


# Create compiled app
nexus_app = create_nexus_workflow()


# --- Main Execution Functions ---
def run_nexus_phase1(topic: str, niche: str, user_vibe: str, goals: str = "") -> Dict[str, Any]:
    """
    Run Phase 1: Script Generation (ripple → quill)
    
    Returns state with generated script, paused for video upload
    """
    
    print("=" * 80)
    print("🚀 CORE - Phase 1: Script Generation")
    print("=" * 80)
    
    # Initialize input state
    inputs = GraphState(
        topic=topic,
        niche=niche,
        user_vibe=user_vibe,
        goals=goals,
        scouted_trends=[],
        generated_script={},
        video_path="",
        clipped_shorts=[],
        engage_plan={},
        deal_plan=[],
        error=""
    )
    
    print(f"\n📋 Configuration:")
    print(f"   Topic: {topic}")
    print(f"   Niche: {niche}")
    print(f"   Vibe: {user_vibe}")
    print(f"   Goals: {goals}")
    print(f"\n🔄 Running script generation agents...")
    print("-" * 80)
    
    # Run workflow (will pause at awaiting_video node)
    final_state = nexus_app.invoke(inputs)
    
    print("-" * 80)
    
    # Check for errors
    if final_state.get('error'):
        print(f"\n❌ Phase 1 stopped with error: {final_state['error']}")
        return final_state
    
    # Save script to database
    if final_state.get('generated_script'):
        script_id = db.save_script(
            final_state['generated_script'],
            topic,
            niche,
            user_vibe
        )
        final_state['script_id'] = script_id
    
    print("\n✅ Phase 1 Complete! Script generated and saved.")
    print("🎬 Next: Shoot the video and run Phase 2")
    print("=" * 80)
    
    return final_state


def run_nexus_phase2(state: GraphState, video_path: str) -> Dict[str, Any]:
    """
    Run Phase 2: Video Processing & Monetization
    (pulse → envoy)
    
    Args:
        state: State from Phase 1
        video_path: Path to uploaded video
    
    Returns:
        Final state with clipped shorts and sponsor pitches
    """
    
    print("=" * 80)
    print("🚀 CORE - Phase 2: Video Processing & Monetization")
    print("=" * 80)
    
    # Update state with video path
    state['video_path'] = video_path
    
    print(f"\n📹 Video uploaded: {video_path}")
    print(f"🔄 Running processing and monetization agents...")
    print("-" * 80)
    
    # Run pulse
    print("\n--- Running pulse ---")
    engage_result = run_pulse(state)
    state.update(engage_result)
    
    # Save video and shorts to database
    if video_path and os.path.exists(video_path):
        video_size = os.path.getsize(video_path)
        from agent_pulse import get_video_duration
        duration = get_video_duration(video_path) or 0
        
        video_id = db.save_video(
            state.get('script_id', 0),
            video_path,
            duration,
            video_size
        )
        
        if state.get('clipped_shorts'):
            db.save_shorts(video_id, state['clipped_shorts'])
    
    # Run envoy
    print("\n--- Running envoy ---")
    deal_result = run_envoy(state)
    state.update(deal_result)
    
    # Save sponsors to database
    if state.get('deal_plan'):
        db.save_sponsors(
            state.get('script_id', 0),
            state['deal_plan']
        )
    
    print("-" * 80)
    print("\n✅ Phase 2 Complete! Shorts clipped and sponsors found.")
    print("=" * 80)
    
    return state


def run_nexus_full(
    topic: str,
    niche: str,
    user_vibe: str,
    goals: str = "",
    video_path: str = ""
) -> Dict[str, Any]:
    """
    Run full workflow (both phases)
    
    If video_path provided, runs both phases.
    If not, runs Phase 1 only and pauses.
    """
    
    # Run Phase 1
    state = run_nexus_phase1(topic, niche, user_vibe, goals)
    
    if state.get('error'):
        return state
    
    # If video provided, run Phase 2
    if video_path and os.path.exists(video_path):
        print(f"\n📹 Video provided - continuing to Phase 2...")
        state = run_nexus_phase2(state, video_path)
    else:
        print(f"\n⏸️  No video provided - workflow paused after Phase 1")
        print(f"💡 Run Phase 2 after uploading video")
    
    return state


# --- Display Helper ---
def display_results(state: Dict[str, Any]):
    """Pretty-print the complete pipeline results"""
    
    print("\n" + "=" * 80)
    print("📊 WORKFLOW RESULTS")
    print("=" * 80)
    
    # Script
    if state.get('generated_script'):
        script = state['generated_script']
        print("\n📝 GENERATED SCRIPT:")
        print("-" * 80)
        print(f"Intro: {script.get('intro', 'N/A')}")
        print(f"Body: {script.get('body', 'N/A')[:150]}...")
        print(f"Outro: {script.get('outro', 'N/A')}")
    
    # Shorts
    if state.get('clipped_shorts'):
        print(f"\n\n🎬 CLIPPED SHORTS: {len(state['clipped_shorts'])} clips")
        print("-" * 80)
        for clip in state['clipped_shorts'][:3]:
            print(f"   • {clip.get('filename', 'N/A')} ({clip.get('duration', 0)}s)")
    
    # Sponsors
    if state.get('deal_plan'):
        print(f"\n\n💰 SPONSOR OPPORTUNITIES: {len(state['deal_plan'])} brands")
        print("-" * 80)
        for deal in state['deal_plan']:
            print(f"   • {deal.get('company_name', 'N/A')} ({deal.get('partnership_type', 'N/A')})")
    
    print("\n" + "=" * 80)


# --- Test Harness ---
if __name__ == "__main__":
    
    print("\n" + "=" * 80)
    print("🧪 TESTING CORE - Complete Multi-Agent System")
    print("=" * 80)
    
    # Test configuration
    test_topic = "AI Wearable Devices"
    test_niche = "Tech reviews and gadget analysis"
    test_vibe = "Sarcastic and brutally honest tech reviews"
    test_goals = "Build 100k followers and land first sponsor deal"
    
    # Run Phase 1 only (no video)
    print("\n📍 Running Phase 1: Script Generation")
    state = run_nexus_phase1(test_topic, test_niche, test_vibe, test_goals)
    
    display_results(state)
    
    print("\n\n💡 To continue:")
    print("   1. Shoot a video using the script")
    print("   2. Run: run_nexus_phase2(state, 'path/to/video.mp4')")
    print("\n✅ core test complete!")
    print("=" * 80)
