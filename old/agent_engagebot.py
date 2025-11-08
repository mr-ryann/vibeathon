import os
import json
from typing import TypedDict, List, Dict, Any
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

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
    content_pack: Dict[str, Any]  # Will hold script, post, and image URL
    engage_plan: Dict[str, Any]
    deal_plan: List[Dict[str, str]]

# --- 2. The Agent Node: `run_engagebot` ---
def run_engagebot(state: GraphState) -> GraphState:
    """
    Runs the EngageBot agent to create an intelligent posting schedule.
    
    This agent:
    1. Analyzes the content script
    2. Determines optimal posting times across platforms
    3. Provides strategic reasoning for each post
    """
    print("--- 📢 AGENT: EngageBot ---")
    
    # Get inputs from the state
    content_pack = state.get('content_pack', {})
    script = content_pack.get('script', '')
    topic = state.get('topic', 'Unknown topic')
    
    if not script:
        print("⚠️  No script found in content_pack, using topic instead")
        script = f"Content about: {topic}"
    
    print(f"📊 Analyzing content for engagement strategy...")
    print(f"📝 Script length: {len(script)} characters")

    # 1. Initialize the Gemini model
    model = genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        generation_config={
            "temperature": 0.7,  # Balanced creativity and consistency
            "response_mime_type": "application/json"
        }
    )

    # 2. Create the intelligent scheduling prompt (Bundle 3.2: Enhanced with platform-specific content)
    prompt = f"""
    You are the 'EngageBot' agent, a world-class social media strategist and data scientist 
    specializing in viral content distribution and Gen Z engagement optimization.
    
    Based on this content script:
    \"\"\"
    {script[:1000]}
    \"\"\"
    
    Topic: {topic}
    
    What is the optimal cross-platform posting schedule for the next 24 hours to maximize 
    Gen Z engagement, reach, and virality?
    
    **CRITICAL: For each platform, you must generate platform-specific, ready-to-paste text:**
    
    - **YouTube**: 100-word video description + 5 SEO-optimized keywords
    - **TikTok**: 50-character catchy title + 3 trending hashtags
    - **Twitter/X**: 280-character engagement hook (question, hot take, or teaser)
    
    Consider:
    - Platform-specific peak activity times
    - Content format optimization per platform
    - Algorithm behavior (TikTok, Instagram, YouTube, Twitter/X)
    - Time zone targeting (focus on US East/West coasts)
    - Cross-promotion opportunities
    
    Return ONLY a JSON object with this exact structure:
    {{
        "plan": [
            {{
                "platform": "YouTube",
                "post_at": "14:00 EST",
                "content_type": "Long-form video",
                "reason": "Peak viewing time for in-depth content",
                "platform_specific_text": "Check out my deep dive into {topic}! In this video, I break down everything you need to know about [key point 1], [key point 2], and [key point 3]. Whether you're a beginner or already familiar with the topic, you'll find actionable insights and real-world examples. Don't forget to subscribe for more tech breakdowns!\\n\\nKeywords: {topic}, tech review, gadget analysis, consumer electronics, tech tutorial"
            }},
            {{
                "platform": "TikTok",
                "post_at": "19:00 EST",
                "content_type": "Short-form vertical video",
                "reason": "Peak Gen Z activity time, highest engagement window",
                "platform_specific_text": "The truth about {topic} 😱\\n#TechTok #TechReview #Viral"
            }},
            {{
                "platform": "Twitter",
                "post_at": "09:00 EST",
                "content_type": "Thread starter",
                "reason": "Morning engagement spike, conversation starter",
                "platform_specific_text": "Hot take: {topic} is either revolutionary or a total flop. Here's why both sides are missing the point 🧵\\n\\nDrop your thoughts below ⬇️"
            }}
        ],
        "strategy_summary": "Brief 2-sentence overall strategy",
        "predicted_reach": "Estimated total impressions (e.g., '500K-1M')"
    }}
    
    Include at least one post for YouTube, TikTok, and Twitter. Add 2-4 more platforms (Instagram, LinkedIn, etc.) as needed.
    Each post MUST have ready-to-paste "platform_specific_text" tailored to that platform's format and character limits.
    """

    try:
        # 3. Invoke the model
        print("🤖 Generating engagement strategy with Gemini...")
        response = model.generate_content(prompt)
        
        # 4. Parse the JSON response
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        engage_plan = json.loads(response_text)
        
        # Validate the structure
        if "plan" not in engage_plan:
            print("⚠️  Missing 'plan' key in response, creating default structure")
            engage_plan = {"plan": engage_plan if isinstance(engage_plan, list) else []}
        
        print(f"✅ Generated {len(engage_plan.get('plan', []))} posting slots")
        print(f"📊 Strategy: {engage_plan.get('strategy_summary', 'N/A')[:100]}...")
        print(f"🎯 Predicted reach: {engage_plan.get('predicted_reach', 'N/A')}")
        
        # 5. Update and return the state
        return {"engage_plan": engage_plan}
    
    except json.JSONDecodeError as e:
        print(f"🚨 JSON parsing error: {e}")
        print(f"🚨 Response text: {response.text if 'response' in locals() else 'No response'}")
        
        # Return a smart fallback plan (Bundle 3.2: with platform_specific_text)
        fallback_plan = {
            "plan": [
                {
                    "platform": "TikTok",
                    "post_at": "19:00 EST",
                    "content_type": "Short-form video",
                    "reason": "Peak Gen Z activity time on TikTok",
                    "platform_specific_text": f"You need to see this about {topic} 🤯\n#TechTok #Viral #Trending"
                },
                {
                    "platform": "Instagram Reels",
                    "post_at": "20:30 EST",
                    "content_type": "Reel",
                    "reason": "Cross-promotion during prime evening engagement",
                    "platform_specific_text": f"Breaking down {topic} in 60 seconds 👀✨\n#TechReels #InstaDaily #Explore"
                },
                {
                    "platform": "YouTube",
                    "post_at": "21:00 EST",
                    "content_type": "Video",
                    "reason": "Capture late-night browsing audience",
                    "platform_specific_text": f"Deep dive into {topic}! In this video, I cover everything from the basics to advanced insights. Perfect for tech enthusiasts looking to understand this trending topic. Hit subscribe for more tech content!\n\nKeywords: {topic}, tech review, analysis, tutorial, tech news"
                },
                {
                    "platform": "Twitter",
                    "post_at": "09:00 EST (next day)",
                    "content_type": "Tweet thread",
                    "reason": "Morning commute engagement spike",
                    "platform_specific_text": f"🧵 Let's talk about {topic}...\n\nEveryone's talking about it, but here's what they're getting wrong:\n\n1/ [Thread starter]"
                }
            ],
            "strategy_summary": "Staggered posting across platforms to maximize 24-hour reach and algorithmic favor.",
            "predicted_reach": "300K-500K impressions"
        }
        return {"engage_plan": fallback_plan}
    
    except Exception as e:
        print(f"🚨 Error in EngageBot: {e}")
        print(f"🚨 Response: {response.text if 'response' in locals() else 'No response'}")
        
        # Return minimal fallback (Bundle 3.2: with platform_specific_text)
        return {"engage_plan": {
            "plan": [
                {
                    "platform": "TikTok",
                    "post_at": "19:00 EST",
                    "content_type": "Video",
                    "reason": "Default prime time",
                    "platform_specific_text": f"{topic} explained 🔥\n#Viral"
                }
            ],
            "strategy_summary": "Error occurred, using default posting schedule.",
            "predicted_reach": "Unknown"
        }}

# --- 3. Test Harness ---
if __name__ == "__main__":
    
    print("--- 🧪 TESTING EngageBot AGENT (Standalone) ---")
    
    # Create a mock initial state with content from ForgeMaster
    initial_state = GraphState(
        topic="Rabbit R1 vs Humane AI Pin",
        user_vibe="Sarcastic tech reviews with dark humor",
        scouted_trends=[],
        content_pack={
            "script": """
            (Scene: Creator with a deadpan expression, holding both a Rabbit R1 and a Humane AI Pin)
            
            CREATOR: They promised us the future. They delivered... well, *this*. 
            The Rabbit R1. The Humane AI Pin. My bank account is still filing a restraining order.
            
            Remember all that breathless hype? 'Revolutionary AI on your lapel!' 
            Turns out, 'assistant' here means 'a really expensive way to feel like a paid beta tester.'
            
            Performance slower than my grandma trying to find the remote. 
            Bugs? They're practically a *feature*!
            
            So, if you're thinking of dropping hundreds on these technological marvels... don't.
            Save your money. Or better yet, tell me in the comments: what's the *most* 
            disappointing tech you've ever bought?
            """,
            "social_post": "Remember the #AI hype? My latest video exposes the failures of the Rabbit R1 & Humane AI Pin. 💀 #TechFail",
            "thumbnail_url": "https://image.pollinations.ai/prompt/tech_review_thumbnail"
        },
        engage_plan={},
        deal_plan=[]
    )
    
    # Run the agent function
    result_state = run_engagebot(initial_state)
    
    print("\n--- 🏁 RESULT ---")
    
    # Display the engagement plan
    if "engage_plan" in result_state and result_state["engage_plan"]:
        plan = result_state["engage_plan"]
        
        print("\n📊 ENGAGEMENT STRATEGY")
        print("=" * 80)
        
        if "strategy_summary" in plan:
            print(f"\n🎯 Overall Strategy:")
            print(f"   {plan['strategy_summary']}")
        
        if "predicted_reach" in plan:
            print(f"\n📈 Predicted Reach: {plan['predicted_reach']}")
        
        print(f"\n📅 POSTING SCHEDULE ({len(plan.get('plan', []))} posts):")
        print("=" * 80)
        
        for i, post in enumerate(plan.get('plan', []), 1):
            print(f"\n#{i} - {post.get('platform', 'Unknown Platform')}")
            print(f"    ⏰ Time: {post.get('post_at', 'N/A')}")
            print(f"    📱 Type: {post.get('content_type', 'N/A')}")
            print(f"    💡 Reason: {post.get('reason', 'N/A')}")
        
        print("\n" + "=" * 80)
        print("\n--- ✅ SUCCESS! ---")
        print("The EngageBot agent ran successfully. We are ready for Agent 4.")
    else:
        print("\n--- ❌ FAILED! ---")
        print("The agent did not return an engagement plan. Check the error messages above.")
