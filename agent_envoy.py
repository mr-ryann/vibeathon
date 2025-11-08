"""
envoy Agent - Brand Partnership & Sponsor Pitching (formerly DealHunter)

Architecture: Updated to include script samples and short previews in pitches
Input: Generated scripts, clipped shorts metadata
Output: Brand matches with personalized pitches that reference actual content
Name: envoy - a diplomatic messenger, forging brand partnerships
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


# --- envoy Agent Node ---
def run_envoy(state: GraphState) -> GraphState:
    """
    Runs the envoy agent to find brand partnerships.
    
    Architecture: Updated to reference actual content in pitches
    Input: Topic, vibe, generated_script, clipped_shorts
    Output: Brand matches with personalized pitches including script samples
    
    Args:
        state: Current GraphState
    
    Returns:
        Updated state with deal_plan populated
    """
    print("--- 🤝 AGENT: envoy ---")
    
    # Get inputs from state
    topic = state.get('topic', '')
    niche = state.get('niche', '')
    user_vibe = state.get('user_vibe', '')
    generated_script = state.get('generated_script', {})
    clipped_shorts = state.get('clipped_shorts', [])
    
    print(f"🎯 Finding brand deals for: {topic}")
    print(f"✍️  Creator vibe: {user_vibe}")
    print(f"📝 Script available: {'Yes' if generated_script else 'No'}")
    print(f"🎬 Shorts created: {len(clipped_shorts)}")

    # Initialize the Gemini model
    model = genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        generation_config={
            "temperature": 0.7,
            "response_mime_type": "application/json"
        }
    )

    # Extract script sample for pitch context
    script_sample = ""
    if generated_script:
        full_script = generated_script.get('full_script', '')
        if full_script:
            # Use first 150 chars as sample
            script_sample = full_script[:150] + "..."
    
    # Count shorts for pitch
    shorts_count = len([s for s in clipped_shorts if not s.get('is_mock', False)])
    has_real_shorts = shorts_count > 0

    # Create enhanced prompt with content references
    master_prompt = f"""You are the 'envoy' agent, an expert in brand-creator partnerships and cold email outreach.

For the topic '{topic}' in the niche '{niche}', find the Top 3 specific companies that would be perfect sponsors for a creator with this vibe: "{user_vibe}".

**IMPORTANT CONTEXT - Creator's Actual Content:**
- Script Sample: "{script_sample}"
- Short-form videos created: {shorts_count} clips
- Content vibe: {user_vibe}

Consider:
- Companies that actively sponsor creators and influencers
- Brands with products/services directly relevant to '{topic}' and '{niche}'
- Companies known for influencer marketing partnerships
- Both direct-to-consumer brands and B2B companies if relevant

For EACH company, generate a personalized 200-word cold-email pitch template.

The pitch MUST:
- Be written FROM the creator (with vibe: "{user_vibe}") TO the company
- **REFERENCE THE ACTUAL SCRIPT SAMPLE** showing the creator's content quality
- Mention the {shorts_count} short-form videos already created (if > 0)
- Reference specific products/campaigns from that company
- Explain why the creator's audience is a perfect fit
- Include a clear value proposition (reach, engagement, content quality)
- End with a specific call-to-action (e.g., "Let's schedule a 15-min call")
- Sound natural and conversational, not corporate or generic
- Be approximately 200 words (±20 words)

**CRITICAL:** Include a line like: "Here's a sample from my latest script: '[insert script_sample here]' - this is the authentic voice my audience loves."

Return ONLY a JSON list of objects. Each object must have exactly these fields:
- company_name: The exact company/brand name
- website: The company's main website URL (just domain, e.g., "example.com")
- reason_for_sponsorship: Detailed explanation of why this company is perfect for '{topic}' content (mention specific products, audience alignment, partnership history)
- pitch_template: A 200-word personalized cold-email pitch that INCLUDES the script sample
- partnership_type: Type of partnership (e.g., "sponsored video", "affiliate", "brand ambassador", "product review")

Example format for reference:
[
  {{
    "company_name": "dbrand",
    "website": "dbrand.com",
    "reason_for_sponsorship": "Specializes in tech skins and accessories, perfect for tech content creators. Known for sponsoring YouTube tech reviewers like MKBHD.",
    "pitch_template": "Hey dbrand team,\\n\\nI'm [creator name], creating {user_vibe} content about {topic} for my growing audience. I just wrapped a script that goes: '{script_sample}' - this authentic, no-BS approach is what my viewers love.\\n\\nI've created {shorts_count} short-form videos on this topic that are getting strong engagement. My audience are tech enthusiasts who appreciate honest reviews and quality products like your skins.\\n\\nI've been following your partnerships with MKBHD and Linus Tech Tips, and I think we'd be a great fit. My content style matches your brand's irreverent, quality-focused vibe.\\n\\nI'd love to explore a partnership - whether it's a dedicated review, integration into my {topic} series, or a custom discount code for my community. My recent videos average [X] views with [Y]% engagement.\\n\\nInterested in a 15-minute call next week to discuss? I can share detailed analytics and content samples.\\n\\nCheers,\\n[Your Name]",
    "partnership_type": "sponsored video + affiliate"
  }}
]

Return ONLY the JSON array with exactly 3 companies. No other text or explanation."""

    try:
        # Call Gemini API
        print("🔍 Searching for brand partnerships...")
        print("✍️  Generating personalized pitches with script samples...")
        response = model.generate_content(master_prompt)
        
        # Parse the JSON response
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        deal_plan = json.loads(response_text)
        
        # Validate structure
        if not isinstance(deal_plan, list):
            raise ValueError("Response is not a list")
        
        # Ensure we have exactly 3 deals
        deal_plan = deal_plan[:3]
        
        # Validate each deal has required fields
        validated_deals = []
        for deal in deal_plan:
            required_fields = ['company_name', 'website', 'reason_for_sponsorship', 'pitch_template']
            if all(key in deal for key in required_fields):
                validated_deals.append({
                    'company_name': deal['company_name'],
                    'website': deal['website'],
                    'reason_for_sponsorship': deal['reason_for_sponsorship'],
                    'pitch_template': deal['pitch_template'],
                    'partnership_type': deal.get('partnership_type', 'sponsored content'),
                    'script_included': script_sample in deal['pitch_template'] if script_sample else False
                })
            else:
                print(f"⚠️  Skipping invalid deal (missing fields): {deal.get('company_name', 'Unknown')}")
        
        if not validated_deals:
            raise ValueError("No valid deals found in response")
        
        deal_plan = validated_deals
        
        # Display results
        print(f"✅ Found {len(deal_plan)} brand partnership opportunities:")
        for i, deal in enumerate(deal_plan, 1):
            print(f"\n{i}. 🏢 {deal['company_name']}")
            print(f"   🌐 {deal['website']}")
            print(f"   🤝 {deal['partnership_type']}")
            print(f"   💡 {deal['reason_for_sponsorship'][:80]}...")
            print(f"   📧 Script in pitch: {'✅ Yes' if deal.get('script_included') else '⚠️  No'}")
            print(f"   📧 Pitch preview: {deal['pitch_template'][:80]}...")
        
    except Exception as e:
        print(f"⚠️  Error calling Gemini API: {e}")
        print("📦 Using fallback sponsor recommendations...")
        
        # Fallback with script-enhanced pitches
        deal_plan = [
            {
                "company_name": "Skillshare",
                "website": "skillshare.com",
                "reason_for_sponsorship": f"Offers educational courses relevant to creators in the {niche} space, perfect for audience upskilling. Actively sponsors content creators across YouTube and social media.",
                "pitch_template": f"Hey Skillshare team,\\n\\nI create {user_vibe} content about {topic}. Here's a sample from my latest script: '{script_sample}' - this authentic approach is what my audience loves.\\n\\nI've created {shorts_count} short-form videos that are resonating strongly with viewers who love learning new skills. Your platform is a perfect fit for my community.\\n\\nMy content reaches engaged viewers who are always looking to level up. I'd love to partner with Skillshare to offer my community a special discount while creating a dedicated integration in my {topic} series.\\n\\nI've seen great results from your partnerships with Ali Abdaal and Thomas Frank. Let's create something equally impactful for my audience.\\n\\nInterested in a quick call this week?\\n\\nBest,\\n[Your Name]",
                "partnership_type": "sponsored video + affiliate",
                "script_included": bool(script_sample)
            },
            {
                "company_name": "Squarespace",
                "website": "squarespace.com",
                "reason_for_sponsorship": f"Website builder commonly sponsored by creators, helps audience build their own {topic} presence online. Known for influencer partnerships and creator-friendly programs.",
                "pitch_template": f"Hi Squarespace partnerships team,\\n\\nI create {user_vibe} content about {topic}. Check out this line from my recent script: '{script_sample}' - this is the authentic voice my {shorts_count} short videos deliver.\\n\\nMy audience is passionate about building their online presence. Many are aspiring creators and entrepreneurs who need professional websites to showcase their {topic} projects.\\n\\nMy channel averages strong engagement rates and my community trusts my recommendations. I'd love to showcase how Squarespace can help them launch with a custom discount code.\\n\\nYour partnerships with Marques Brownlee and Sara Dietschy have been excellent—I think we could create similar authentic value for my audience.\\n\\nCan we schedule a brief call?\\n\\nCheers,\\n[Your Name]",
                "partnership_type": "sponsored integration",
                "script_included": bool(script_sample)
            },
            {
                "company_name": "NordVPN",
                "website": "nordvpn.com",
                "reason_for_sponsorship": f"Privacy and security tool that appeals to tech-savvy audiences interested in {topic}. One of the most active sponsors in the creator economy.",
                "pitch_template": f"Hello NordVPN team,\\n\\nI cover {topic} with a {user_vibe} style. Here's my latest script sample: '{script_sample}' - this honest, direct approach drives my {shorts_count} short-form videos.\\n\\nMy audience is tech-savvy and privacy-conscious—exactly your target demographic. They trust my recommendations because I keep it real.\\n\\nI'd love to integrate NordVPN into my content with a dedicated segment explaining why online privacy matters for {topic} enthusiasts, plus a custom promo code. My recent videos hit strong view counts with high click-through rates on links.\\n\\nI've admired your creator partnerships and think we'd be a natural fit for an ongoing collaboration.\\n\\nWould you be open to a 15-minute intro call?\\n\\nThanks,\\n[Your Name]",
                "partnership_type": "sponsored segment + promo code",
                "script_included": bool(script_sample)
            }
        ]
        
        print(f"✅ Using {len(deal_plan)} fallback sponsors with script-enhanced pitches")
        for i, deal in enumerate(deal_plan, 1):
            print(f"{i}. {deal['company_name']} - {deal['website']}")

    print(f"\n💼 envoy complete! Found {len(deal_plan)} potential sponsors with script samples.")
    
    return {"deal_plan": deal_plan}


# --- Test Harness ---
if __name__ == "__main__":
    
    print("--- 🧪 TESTING envoy AGENT (Standalone) ---")
    
    # Create a mock initial state with script and shorts
    initial_state = GraphState(
        niche="Tech reviews and gadget analysis",
        goals="Build 100k followers and land first sponsor deal",
        topic="AI Wearable Devices",
        user_vibe="Sarcastic and brutally honest tech reviews",
        scouted_trends=[],
        generated_script={
            "intro": "Wait, I spent $500 on THIS?!",
            "body": "Let me show you why everyone's returning the AI Pin. [Hold up device] It's slower than my grandma's flip phone and half the features don't even work.",
            "outro": "Drop a 💀 if you also got scammed. Follow for more honest tech reviews.",
            "full_script": "Wait, I spent $500 on THIS?! Let me show you why everyone's returning the AI Pin. [Hold up device] It's slower than my grandma's flip phone and half the features don't even work. Drop a 💀 if you also got scammed. Follow for more honest tech reviews."
        },
        video_path="test_video.mp4",
        clipped_shorts=[
            {"clip_id": 1, "duration": 15, "posted": True},
            {"clip_id": 2, "duration": 30, "posted": True},
            {"clip_id": 3, "duration": 20, "posted": False}
        ],
        engage_plan={},
        deal_plan=[],
        error=""
    )
    
    # Run the agent
    result_state = run_envoy(initial_state)
    
    print("\n--- 🏁 RESULT ---")
    print("=" * 80)
    
    if "deal_plan" in result_state and result_state['deal_plan']:
        print(f"\n💰 BRAND PARTNERSHIP OPPORTUNITIES: {len(result_state['deal_plan'])} sponsors")
        print("=" * 80)
        
        for i, deal in enumerate(result_state['deal_plan'], 1):
            print(f"\n#{i} - 🏢 {deal['company_name']}")
            print(f"   🌐 Website: {deal['website']}")
            print(f"   🤝 Partnership Type: {deal['partnership_type']}")
            print(f"   💡 Why Sponsor: {deal['reason_for_sponsorship']}")
            print(f"   📧 Script Included: {'Yes ✅' if deal.get('script_included') else 'No ⚠️'}")
            print(f"\n   📧 PITCH EMAIL:")
            print("   " + "-" * 76)
            # Print pitch with indentation
            for line in deal['pitch_template'].split('\\n'):
                print(f"   {line}")
            print("   " + "-" * 76)
    
    print("\n" + "=" * 80)
    print("\n--- ✅ SUCCESS! ---")
    print("envoy has created sponsor pitches with actual script samples.")
    print("Ready to send personalized emails to brands!")
