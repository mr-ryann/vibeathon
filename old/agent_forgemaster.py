import os
import json
import urllib.parse
from typing import TypedDict, List, Dict, Any
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
import requests

# --- Google GenAI SDK (direct) ---
import google.generativeai as genai

# --- Load API Key ---
load_dotenv()
if "GEMINI_API_KEY" not in os.environ:
    raise EnvironmentError("🚨 GEMINI_API_KEY not found. Please create a .env file with your API key.")

# Configure the Google GenAI SDK
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# --- 1. Define the GraphState ---
class GraphState(TypedDict):
    """
    The shared state of the CreatorForge Nexus.
    """
    user_vibe: str
    topic: str
    scouted_trends: List[Dict[str, str]]
    engage_plan: Dict[str, Any]
    deal_plan: List[Dict[str, str]]

# --- Helper Functions ---
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
def _call_gemini_api(model, prompt: str) -> str:
    """Call Gemini API with retry logic"""
    response = model.generate_content(prompt)
    return response.text

def get_thumbnail_url(prompt: str) -> str:
    """
    Generate thumbnail URL with fallback for reliability.
    
    Bundle 2.1: Tries Pollinations first, falls back to reliable placeholder
    """
    import hashlib
    
    # Try Pollinations first
    encoded_prompt = urllib.parse.quote(prompt)
    pollinations_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&nologo=true"
    
    try:
        # Test if URL is accessible (with timeout for hackathon speed)
        response = requests.head(pollinations_url, timeout=5)
        if response.status_code == 200:
            print(f"✅ Pollinations thumbnail generated")
            return pollinations_url
    except Exception as e:
        print(f"⚠️  Pollinations failed: {e}")
    
    # Fallback to Lorem Picsum (100% reliable placeholder)
    # Make it unique by hashing the prompt
    prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:8]
    fallback_url = f"https://picsum.photos/seed/{prompt_hash}/1280/720"
    print(f"✅ Using fallback thumbnail (reliable)")
    return fallback_url

# --- 2. The Agent Node: `run_forgemaster` ---
def run_forgemaster(state: GraphState) -> GraphState:
    """
    Runs the ForgeMaster agent to create a complete content pack.
    
    This agent:
    1. Takes the scouted trends and user vibe
    2. Generates a script, social post, and thumbnail prompt
    3. Creates a thumbnail image URL using Pollinations.ai
    """
    print("--- 🔨 AGENT: ForgeMaster ---")
    
    # Get inputs from the state
    user_vibe = state['user_vibe']
    scouted_trends = state['scouted_trends']
    
    print(f"🎨 Forging content with vibe: {user_vibe}")
    print(f"📊 Using {len(scouted_trends)} scouted trends")

    # --- STEP A: Text Generation ---
    
    # 1. Initialize the Gemini model
    model = genai.GenerativeModel(
        model_name='gemini-2.0-flash-exp',  # Latest model
        generation_config={
            "temperature": 0.8,  # Higher creativity for content generation
            "response_mime_type": "application/json"
        }
    )

    # 2. Create the IMPROVED STRUCTURED prompt (Bundle 2.2)
    trends_text = json.dumps(scouted_trends, indent=2)
    topic = state.get('topic', 'trending topic')
    
    prompt = f"""
    You are the 'ForgeMaster' agent, a world-class content strategist and viral content creator.
    
    Create a 150-word video script following this EXACT structure:
    
    [HOOK] (0-10s): A shocking question or statement about {topic}.
    [PROBLEM] (10-30s): Why this topic matters to the audience.
    [SOLUTION] (30-90s): The core info, based on these trends:
    {trends_text}
    [CTA] (90-120s): A clear call to action.
    
    The VIBE must be: {user_vibe}
    Make it punchy, engaging, and optimized for virality.
    
    Return ONLY a JSON object with these three keys:
    
    1. "script": The full script following the structure above
    2. "social_post": A 280-char Twitter post to promote the video with hashtags
    3. "thumbnail_prompt": A 15-word DALL-E prompt for a high-CTR thumbnail
       (e.g., "shocked tech reviewer holding AI pin, dramatic red lighting, arrows, YouTube style")
    
    No other text. Just the JSON object.
    """

    try:
        # 3. Invoke the model WITH RETRY LOGIC
        print("🤖 Generating content with Gemini...")
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
        
        content_data = json.loads(response_text)
        
        print("✅ Content generated successfully!")
        
        # --- STEP B: Image Generation ---
        
        # 5. Extract the thumbnail prompt
        thumbnail_prompt = content_data.get("thumbnail_prompt", "")
        
        if not thumbnail_prompt:
            print("⚠️  No thumbnail prompt found, using default")
            thumbnail_prompt = "viral tech video thumbnail, dramatic lighting, high quality"
        
        # 6. URL-encode the prompt for Pollinations.ai
        encoded_prompt = urllib.parse.quote(thumbnail_prompt)
        
        # 7. Use the RELIABLE thumbnail function (Bundle 2.1)
        thumbnail_url = get_thumbnail_url(thumbnail_prompt)
        
        print(f"🖼️  Thumbnail URL: {thumbnail_url[:80]}...")
        
        # 8. Build the complete content pack
        content_pack = {
            "script": content_data.get("script", ""),
            "social_post": content_data.get("social_post", ""),
            "thumbnail_url": thumbnail_url,
            "thumbnail_prompt": thumbnail_prompt  # Include for reference
        }
        
        print(f"✅ ForgeMaster completed! Generated {len(content_pack['script'])} char script")
        
        # 9. Update and return the state
        return {"content_pack": content_pack}
    
    except json.JSONDecodeError as e:
        print(f"🚨 JSON parsing error: {e}")
        print(f"🚨 Response text may be malformed")
        return {"content_pack": {
            "script": "Error generating content",
            "social_post": "Error generating content",
            "thumbnail_url": "https://picsum.photos/1280/720",
            "thumbnail_prompt": "error"
        }}
    
    except Exception as e:
        print(f"🚨 Error in ForgeMaster: {e}")
        return {"content_pack": {
            "script": "Error generating content",
            "social_post": "Error generating content",
            "thumbnail_url": "https://picsum.photos/1280/720",
            "thumbnail_prompt": "error"
        }}

# --- 3. Test Harness ---
if __name__ == "__main__":
    
    print("--- 🧪 TESTING ForgeMaster AGENT (Standalone) ---")
    
    # Create a mock initial state with some scouted trends
    # (In a real LangGraph, this would come from TrendScout)
    initial_state = GraphState(
        topic="Rabbit R1 vs Humane AI Pin",
        user_vibe="Sarcastic tech reviews with dark humor",
        scouted_trends=[
            {
                "title": "AI's First Fumble? Why the Rabbit R1 and Humane AI Pin Both Miss the Mark",
                "url": "https://www.theverge.com/2024/4/25/rabbit-r1-humane-ai-pin-review",
                "summary": "Analysis dissects the core failures of both devices, highlighting slow performance and lack of compelling use cases."
            },
            {
                "title": "I Wasted My Money: The TRUTH About the Rabbit R1 & Humane AI Pin",
                "url": "https://www.youtube.com/watch?v=ai_pin_truth",
                "summary": "Viral YouTube review sharing disappointing hands-on experience with both devices."
            },
            {
                "title": "Reddit Discussion: AI Hardware Hype is Dead",
                "url": "https://www.reddit.com/r/technology/ai_hardware_discussion",
                "summary": "Community shares frustrations with buggy software and feeling like beta testers."
            }
        ],
        content_pack={},
        engage_plan={},
        deal_plan=[]
    )
    
    # Run the agent function
    result_state = run_forgemaster(initial_state)
    
    print("\n--- 🏁 RESULT ---")
    
    # Pretty-print the content pack
    if "content_pack" in result_state and result_state["content_pack"]:
        content = result_state["content_pack"]
        
        print("\n📝 SCRIPT:")
        print("=" * 80)
        print(content.get("script", "N/A"))
        
        print("\n\n🐦 SOCIAL POST:")
        print("=" * 80)
        print(content.get("social_post", "N/A"))
        
        print("\n\n🖼️  THUMBNAIL:")
        print("=" * 80)
        print(f"Prompt: {content.get('thumbnail_prompt', 'N/A')}")
        print(f"URL: {content.get('thumbnail_url', 'N/A')}")
        
        print("\n--- ✅ SUCCESS! ---")
        print("The ForgeMaster agent ran successfully. We are ready for Agent 3.")
    else:
        print("\n--- ❌ FAILED! ---")
        print("The agent did not return a content pack. Check the error messages above.")
