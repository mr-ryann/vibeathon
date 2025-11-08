import os
import json
from typing import TypedDict, List, Dict, Any
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

# --- Google GenAI SDK (direct) ---
import google.generativeai as genai

# --- Load API Key ---
# This loads the .env file so os.environ.get() can find the key
load_dotenv()
if "GEMINI_API_KEY" not in os.environ:
    raise EnvironmentError("🚨 GEMINI_API_KEY not found. Please create a .env file with your API key.")

# Configure the Google GenAI SDK
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# --- 1. Define the GraphState ---
# This is the "bloodstream" of our app.
# We'll define the full state, even though this agent only uses a part of it.
class GraphState(TypedDict):
    """
    The shared state of the CreatorForge Nexus.
    """
    user_vibe: str
    topic: str
    scouted_trends: List[Dict[str, str]]
    content_pack: Dict[str, Any]  # Will hold script, post, and image URL
    engage_plan: Dict[str, Any]
    deal_plan: List[Dict[str, str]]
    error: str  # Bundle 1.2: Error message for workflow failures

# --- 2. The Agent Node: `run_trendscout` ---
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
def _call_gemini_api(model, prompt: str) -> str:
    """Call Gemini API with retry logic"""
    response = model.generate_content(prompt)
    return response.text

def run_trendscout(state: GraphState, num_trends: int = 5) -> GraphState:
    """
    Runs the TrendScout agent to find real-time trends for the given topic.
    
    Args:
        state: Current GraphState
        num_trends: Number of trends to find (default: 5, configurable for better variety)
    """
    print("--- 🧠 AGENT: TrendScout ---")
    
    # Get the initial topic from the state
    topic = state['topic']
    print(f"🕵️‍♂️ Scouting for {num_trends} trends on topic: {topic}")

    # 1. Initialize the Gemini model
    # Note: We'll use the model's knowledge to simulate trend scouting
    # For real-time search, you would need to integrate with a search API
    model = genai.GenerativeModel(
        model_name='gemini-2.0-flash-exp',  # Using latest model
        generation_config={
            "temperature": 0.7,  # Slightly higher for creative trend finding
            "response_mime_type": "application/json"
        }
    )

    # 2. Create the prompt (NOW CONFIGURABLE with num_trends)
    prompt = f"""
    You are the 'TrendScout' agent. Your job is to find the TOP {num_trends} most recent,
    relevant, and viral articles, Reddit threads, or social media discussions
    about the topic: {topic}.

    Based on your knowledge of current tech trends and viral discussions, simulate
    what the most likely trending articles and discussions would be about this topic.
    Create realistic-looking trend data with plausible titles, URLs, and summaries.

    Return ONLY a JSON array of objects, with 'title', 'url', and 'summary' for each.
    Format: [{{"title": "...", "url": "...", "summary": "..."}}, ...]
    
    Make the URLs look realistic (e.g., reddit.com/r/technology/..., youtube.com/watch?v=..., 
    techcrunch.com/..., etc.) and the summaries informative and trend-focused.
    
    Do not add any other text, markdown, or commentary. Just the JSON array.
    """

    try:
        # 3. Invoke the model WITH RETRY LOGIC
        response_text = _call_gemini_api(model, prompt)
        
        # 4. Parse the JSON response
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
        
        print(f"✅ Scouted {len(trends)} trends successfully.")
        
        # 5. Update and return the state
        return {"scouted_trends": trends}
    
    except Exception as e:
        print(f"🚨 Error in TrendScout after retries: {e}")
        print(f"🚨 Falling back to empty trends")
        return {"scouted_trends": []}  # Return an empty list on failure

# --- 3. Test Harness ---
# This block runs ONLY when you execute this file directly (e.g., `python agent_trendscout.py`)
if __name__ == "__main__":
    
    print("--- 🧪 TESTING TrendScout AGENT (Standalone) ---")
    
    # Create a mock initial state to feed the agent
    initial_state = GraphState(
        topic="Rabbit R1 vs Humane AI Pin",
        user_vibe="Sarcastic tech reviews",
        scouted_trends=[],
        content_pack={},
        engage_plan={},
        deal_plan=[]
    )
    
    # Run the agent function just like LangGraph would
    result_state = run_trendscout(initial_state)
    
    print("\n--- 🏁 RESULT ---")
    # Pretty-print the JSON output
    print(json.dumps(result_state, indent=2))
    
    if "scouted_trends" in result_state and result_state["scouted_trends"]:
        print("\n--- ✅ SUCCESS! ---")
        print("The agent ran and found trends. We are ready for Agent 2.")
    else:
        print("\n--- ❌ FAILED! ---")
        print("The agent did not return trends. Check the error messages above.")