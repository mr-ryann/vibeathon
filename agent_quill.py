"""
quill Agent - Script Generation (formerly ForgeMaster)

Architecture: Shift to script-only output
Output: Structured script {"intro": "...", "body": "...", "outro": "..."}
Focus: Human-shootable 15-sec Reel scripts that remix trends in user's vibe
Name: quill - the writer's tool, crafting stories from raw trends
"""

import os
import json
from typing import TypedDict, List, Dict, Any
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
import google.generativeai as genai

# Load API keys
load_dotenv()
if "GEMINI_API_KEY" not in os.environ:
    raise EnvironmentError("🚨 GEMINI_API_KEY not found. Please create a .env file with your API key.")

# Configure Google GenAI SDK
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))


# --- GraphState Definition ---
class GraphState(TypedDict):
    """
    The shared state of the Nexus.
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


# --- quill Agent Node ---
def run_quill(state: GraphState) -> GraphState:
    """
    Runs the quill agent to create a human-shootable script.
    
    Architecture: Script-only generation (no thumbnail/images)
    Output: Structured script with intro, body, outro
    Focus: 15-second Reel scripts that can be shot by humans
    
    Args:
        state: Current GraphState
    
    Returns:
        Updated state with generated_script populated
    """
    print("--- ✍️  AGENT: quill ---")
    
    # Get inputs from the state
    user_vibe = state.get('user_vibe', 'Casual and engaging')
    scouted_trends = state.get('scouted_trends', [])
    topic = state.get('topic', '')
    niche = state.get('niche', '')
    
    print(f"🎨 Forging script with vibe: {user_vibe}")
    print(f"📊 Using {len(scouted_trends)} scouted trends")

    # Initialize the Gemini model
    model = genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        generation_config={
            "temperature": 0.8,  # Higher creativity for content generation
            "response_mime_type": "application/json"
        }
    )

    # Create the structured prompt for script generation
    trends_text = json.dumps(scouted_trends, indent=2) if scouted_trends else "No specific trends available"
    
    prompt = f"""
    You are the 'quill' agent, a world-class script writer for viral short-form content.
    
    Create a 15-SECOND REEL SCRIPT that can be shot by a human creator with just a smartphone.
    
    Context:
    - Topic: {topic}
    - Niche: {niche}
    - Creator Vibe: {user_vibe}
    - Trends to remix: {trends_text}
    
    CRITICAL REQUIREMENTS:
    1. The script must be EXACTLY 15 seconds when spoken at normal pace
    2. It must be HUMAN-SHOOTABLE (no special effects, just a person talking to camera)
    3. Remix the trends into the creator's vibe: "{user_vibe}"
    4. Make it punchy, engaging, and optimized for virality
    5. Include natural camera direction hints (e.g., "Look directly at camera", "Hold up phone")
    
    STRUCTURE YOUR SCRIPT IN 3 PARTS:
    
    [INTRO] (0-3 seconds): A shocking hook or question that stops the scroll
    - Must grab attention IMMEDIATELY
    - Can be a question, bold statement, or pattern interrupt
    - Example: "Wait, THIS is what everyone's been buying?!"
    
    [BODY] (3-12 seconds): The core message remixing the trend
    - Deliver the main insight or entertainment
    - Stay in the creator's vibe
    - Include 1-2 camera direction hints
    - Example: "Hold up the product. I spent $500 on this AI gadget and it can't even..."
    
    [OUTRO] (12-15 seconds): Strong call-to-action or punchline
    - End with engagement prompt or memorable line
    - Example: "Drop a 💀 if you also wasted money on tech hype. Follow for more honest reviews."
    
    Return ONLY a JSON object with this exact structure:
    {{
        "intro": "The hook line with [camera direction if needed]",
        "body": "The main content with [camera directions]. Multiple sentences allowed.",
        "outro": "The CTA or punchline",
        "full_script": "Complete 15-second script as one paragraph",
        "shot_count": 1,
        "difficulty": "easy",
        "props_needed": ["list", "of", "any", "props"],
        "estimated_duration": "15 seconds"
    }}
    
    Make it HUMAN and AUTHENTIC - this person is shooting with their phone, not a Hollywood crew.
    No other text. Just the JSON object.
    """

    try:
        # Invoke the model with retry logic
        print("🤖 Generating script with Gemini...")
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
        
        script_data = json.loads(response_text)
        
        # Validate required fields
        required_fields = ['intro', 'body', 'outro', 'full_script']
        if not all(key in script_data for key in required_fields):
            raise ValueError(f"Missing required fields in script. Got: {script_data.keys()}")
        
        # Add metadata
        script_data['created_at'] = str(os.environ.get('TIMESTAMP', 'unknown'))
        script_data['topic'] = topic
        script_data['vibe'] = user_vibe
        
        print("✅ Script generated successfully!")
        print(f"📝 Script length: {len(script_data['full_script'])} characters")
        print(f"🎬 Shot count: {script_data.get('shot_count', 1)}")
        print(f"⚡ Difficulty: {script_data.get('difficulty', 'unknown')}")
        
        # Return updated state
        return {"generated_script": script_data}
    
    except json.JSONDecodeError as e:
        print(f"🚨 JSON parsing error: {e}")
        print(f"🚨 Response may be malformed")
        
        # Fallback script
        fallback_script = {
            "intro": f"Let's talk about {topic}...",
            "body": f"Everyone in {niche} is talking about this, but here's what they're missing. [Hold up phone to camera] The real story is way more interesting.",
            "outro": "Drop a comment if you want more on this. Follow for daily insights.",
            "full_script": f"Let's talk about {topic}... Everyone in {niche} is talking about this, but here's what they're missing. [Hold up phone to camera] The real story is way more interesting. Drop a comment if you want more on this. Follow for daily insights.",
            "shot_count": 1,
            "difficulty": "easy",
            "props_needed": ["smartphone"],
            "estimated_duration": "15 seconds",
            "created_at": "unknown",
            "topic": topic,
            "vibe": user_vibe
        }
        
        return {
            "generated_script": fallback_script,
            "error": f"quill JSON parsing failed: {str(e)}"
        }
    
    except Exception as e:
        print(f"🚨 Error in quill: {e}")
        
        # Fallback script
        fallback_script = {
            "intro": "Here's something you need to know...",
            "body": f"About {topic}. [Look directly at camera] This is important.",
            "outro": "Follow for more.",
            "full_script": f"Here's something you need to know... About {topic}. [Look directly at camera] This is important. Follow for more.",
            "shot_count": 1,
            "difficulty": "easy",
            "props_needed": [],
            "estimated_duration": "15 seconds",
            "created_at": "unknown",
            "topic": topic,
            "vibe": user_vibe
        }
        
        return {
            "generated_script": fallback_script,
            "error": f"quill failed: {str(e)}"
        }


# --- Test Harness ---
if __name__ == "__main__":
    
    print("--- 🧪 TESTING quill AGENT (Standalone) ---")
    
    # Create a mock initial state with some scouted trends
    initial_state = GraphState(
        niche="Tech reviews and gadget analysis",
        goals="Build 100k followers",
        topic="Rabbit R1 vs Humane AI Pin",
        user_vibe="Sarcastic tech reviews with dark humor",
        scouted_trends=[
            {
                "title": "AI's First Fumble? Why the Rabbit R1 and Humane AI Pin Both Miss",
                "url": "https://www.theverge.com/2024/4/25/rabbit-r1-humane-ai-pin-review",
                "summary": "Analysis of core failures: slow performance, lack of use cases."
            },
            {
                "title": "I Wasted My Money: The TRUTH About the Rabbit R1 & Humane AI Pin",
                "url": "https://www.youtube.com/watch?v=ai_pin_truth",
                "summary": "Viral review sharing disappointing hands-on experience."
            },
            {
                "title": "Reddit: AI Hardware Hype is Dead",
                "url": "https://www.reddit.com/r/technology/ai_hardware",
                "summary": "Community frustrations with buggy software."
            }
        ],
        generated_script={},
        video_path="",
        clipped_shorts=[],
        engage_plan={},
        deal_plan=[],
        error=""
    )
    
    # Run the agent
    result_state = run_quill(initial_state)
    
    print("\n--- 🏁 RESULT ---")
    
    if "generated_script" in result_state and result_state["generated_script"]:
        script = result_state["generated_script"]
        
        print("\n" + "=" * 80)
        print("📝 GENERATED SCRIPT (15-SECOND REEL)")
        print("=" * 80)
        
        print(f"\n🎬 INTRO (0-3s):")
        print(f"   {script.get('intro', 'N/A')}")
        
        print(f"\n📖 BODY (3-12s):")
        print(f"   {script.get('body', 'N/A')}")
        
        print(f"\n🎯 OUTRO (12-15s):")
        print(f"   {script.get('outro', 'N/A')}")
        
        print(f"\n📄 FULL SCRIPT:")
        print(f"   {script.get('full_script', 'N/A')}")
        
        print(f"\n📊 METADATA:")
        print(f"   Shot Count: {script.get('shot_count', 'N/A')}")
        print(f"   Difficulty: {script.get('difficulty', 'N/A')}")
        print(f"   Props: {', '.join(script.get('props_needed', []))}")
        print(f"   Duration: {script.get('estimated_duration', 'N/A')}")
        
        print("\n" + "=" * 80)
        print("\n--- ✅ SUCCESS! ---")
        print("Script is ready for human shooting. Next: User shoots video and uploads.")
    else:
        print("\n--- ❌ FAILED! ---")
        print("The agent did not return a script. Check the error messages above.")
