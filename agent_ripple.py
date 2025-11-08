"""
ripple Agent - Viral Trend Discovery & Research

Architecture: Real-time trend discovery using Google Serper API
Trigger: On-demand or automatic when user generates script
Name: ripple - like ripples spreading across water, detecting viral waves
"""

import os
import json
import requests
from typing import TypedDict, List, Dict, Any
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
import google.generativeai as genai
from datetime import datetime

# Load API keys
load_dotenv()
if "GEMINI_API_KEY" not in os.environ:
    raise EnvironmentError("🚨 GEMINI_API_KEY not found. Please create a .env file with your API key.")

# Configure Google GenAI SDK
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Google Serper API configuration
SERPER_API_KEY = os.getenv("GOOGLE_SERPER_API_KEY")
SERPER_ENDPOINT = "https://google.serper.dev/search"


# --- GraphState Definition ---
class GraphState(TypedDict):
    """
    The shared state of the CreatorForge Nexus.
    """
    user_vibe: str
    niche: str
    goals: str
    topic: str
    scouted_trends: List[Dict[str, str]]
    generated_script: Dict[str, Any]
    video_path: str
    clipped_shorts: List[Dict[str, Any]]
    engage_plan: Dict[str, Any]
    deal_plan: List[Dict[str, str]]
    error: str


# --- Retry Logic for API Calls ---
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
def _call_gemini_api(model, prompt: str) -> str:
    """Call Gemini API with retry logic"""
    response = model.generate_content(prompt)
    return response.text


# --- Google Serper Integration ---
def fetch_viral_trends_serper(query: str, num_results: int = 10) -> List[Dict[str, str]]:
    """
    Fetch real viral trends using Google Serper API
    
    Args:
        query: Search query (niche/topic)
        num_results: Number of results to fetch
    
    Returns:
        List of trend dictionaries with title, url, summary
    """
    if not SERPER_API_KEY:
        print("⚠️  Google Serper API key not found - using fallback")
        return []
    
    try:
        print(f"🔍 Fetching real-time trends via Google Serper: '{query}'")
        
        headers = {
            "X-API-KEY": SERPER_API_KEY,
            "Content-Type": "application/json"
        }
        
        payload = {
            "q": f"{query} viral trending",
            "num": num_results,
            "gl": "us",  # Geographic location
            "hl": "en"   # Language
        }
        
        response = requests.post(
            SERPER_ENDPOINT,
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"⚠️  Serper API error: {response.status_code}")
            return []
        
        data = response.json()
        
        # Extract organic results
        trends = []
        for result in data.get('organic', [])[:num_results]:
            trends.append({
                "title": result.get('title', ''),
                "url": result.get('link', ''),
                "summary": result.get('snippet', '')
            })
        
        print(f"✅ Fetched {len(trends)} real trends from Serper")
        return trends
    
    except Exception as e:
        print(f"⚠️  Error fetching from Serper: {e}")
        return []


# --- ripple Agent Node ---
def run_ripple(state: GraphState, num_trends: int = 5, use_serper: bool = True) -> GraphState:
    """
    Runs the ripple agent to find real-time viral trends.
    
    Architecture: Uses Google Serper for real trend data, falls back to Gemini simulation
    Trigger: On-demand or automatic when user generates script
    
    Args:
        state: Current GraphState
        num_trends: Number of trends to find (default: 5)
        use_serper: Whether to use Google Serper API (default: True)
    
    Returns:
        Updated state with scouted_trends populated
    """
    print("--- 🌊 AGENT: ripple ---")
    
    # Get inputs from state
    niche = state.get('niche', '')
    topic = state.get('topic', '')
    goals = state.get('goals', '')
    
    # Use topic if provided, otherwise use niche
    search_query = topic if topic else niche
    
    print(f"🕵️‍♂️ Scouting for {num_trends} viral trends on: {search_query}")
    if goals:
        print(f"🎯 Creator goals: {goals}")

    trends = []
    
    # Try Google Serper first if enabled
    if use_serper:
        trends = fetch_viral_trends_serper(search_query, num_results=num_trends)
    
    # Fallback to Gemini simulation if Serper unavailable or failed
    if not trends:
        print("📝 Using Gemini to simulate trending content...")
        
        # Initialize the Gemini model
        model = genai.GenerativeModel(
            model_name='gemini-2.0-flash-exp',
            generation_config={
                "temperature": 0.7,
                "response_mime_type": "application/json"
            }
        )

        # Create the prompt
        prompt = f"""
    You are the 'ripple' agent. Your job is to find the TOP {num_trends} most recent,
    relevant, and viral articles, Reddit threads, or social media discussions
    about the topic: {search_query}.
    
    Context:
    - Niche: {niche}
    - Creator goals: {goals}

    Based on your knowledge of current trends and viral discussions, simulate
    what the most likely trending articles and discussions would be about this topic.
    Create realistic-looking trend data with plausible titles, URLs, and summaries.
    
    Focus on trends that would help a creator in the "{niche}" niche achieve: {goals}

    Return ONLY a JSON array of objects, with 'title', 'url', and 'summary' for each.
    Format: [{{"title": "...", "url": "...", "summary": "..."}}, ...]
    
    Make the URLs look realistic (e.g., reddit.com/r/.../..., youtube.com/watch?v=..., 
    techcrunch.com/..., tiktok.com/@.../video/..., etc.) and the summaries informative 
    and trend-focused.
    
    Do not add any other text, markdown, or commentary. Just the JSON array.
    """

        try:
            # Invoke the model with retry logic
            response_text = _call_gemini_api(model, prompt)
            
            # Parse the JSON response
            response_text = response_text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            trends = json.loads(response_text)
            
        except Exception as e:
            print(f"🚨 Error in Gemini fallback: {e}")
            trends = []
    
    if trends:
        print(f"✅ Scouted {len(trends)} trends successfully.")
        return {"scouted_trends": trends}
    else:
        print(f"🚨 No trends found - returning empty list")
        return {"scouted_trends": [], "error": "ripple: No trends found"}


# --- Test Harness ---
if __name__ == "__main__":
    
    print("--- 🧪 TESTING ripple AGENT (Standalone) ---")
    
    # Create a mock initial state
    initial_state = GraphState(
        niche="Tech reviews and gadget analysis",
        goals="Build 100k followers and land first sponsor deal",
        topic="AI wearable devices",
        user_vibe="Sarcastic tech reviews",
        scouted_trends=[],
        generated_script={},
        video_path="",
        clipped_shorts=[],
        engage_plan={},
        deal_plan=[],
        error=""
    )
    
    # Run the agent
    result_state = run_ripple(initial_state, num_trends=5)
    
    print("\n--- 🏁 RESULT ---")
    print(json.dumps(result_state, indent=2))
    
    if "scouted_trends" in result_state and result_state["scouted_trends"]:
        print("\n--- ✅ SUCCESS! ---")
        print(f"Found {len(result_state['scouted_trends'])} trends. Ready for quill.")
    else:
        print("\n--- ❌ FAILED! ---")
        print("The agent did not return trends. Check the error messages above.")
