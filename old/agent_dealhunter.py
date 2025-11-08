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

# --- 2. The Agent Node: `run_dealhunter` ---
def run_dealhunter(state: GraphState) -> GraphState:
    """
    Agent 4: DealHunter - The "Wallet" (Intelligent Mock)
    
    Purpose (Hackathon): To simulate finding relevant brand deals, proving the "Empire" vision.
    
    This agent:
    1. Takes the topic and user_vibe from state
    2. Uses Gemini Pro API with search/reasoning capabilities
    3. Finds Top 3 specific companies that would be perfect sponsors
    4. **Bundle 3.1:** Generates ready-to-send pitch email templates for each sponsor
    5. Returns structured JSON with company_name, website, reason_for_sponsorship, and pitch_template
    """
    print("--- 💰 AGENT: DealHunter ---")
    
    # Get the topic and user_vibe from the state
    topic = state['topic']
    user_vibe = state['user_vibe']
    print(f"🎯 Finding brand deals for: {topic}")
    print(f"✍️  Creator vibe: {user_vibe}")

    # Initialize the Gemini model
    model = genai.GenerativeModel(
        model_name='gemini-2.5-flash',  # Using 2.5-flash (available model)
        generation_config={
            "temperature": 0.7,  # Balanced for creative yet relevant suggestions
            "response_mime_type": "application/json"
        }
    )

    # --- Master Prompt (Bundle 3.1: Enhanced with pitch template generation) ---
    master_prompt = f"""You are the 'DealHunter' agent, an expert in brand-creator partnerships and cold email outreach.

For the topic '{topic}', use your search tool to find the Top 3 specific companies that would be perfect sponsors for a creator with this vibe: "{user_vibe}".

Consider:
- Companies that actively sponsor creators and influencers
- Brands with products/services directly relevant to '{topic}'
- Companies known for influencer marketing partnerships
- Both direct-to-consumer brands and B2B companies if relevant

For EACH company, you must also generate a personalized 150-word cold-email pitch template.

The pitch must:
- Be written FROM the creator (with vibe: "{user_vibe}") TO the company
- Reference specific products/campaigns from that company
- Explain why the creator's audience is a perfect fit
- Include a clear value proposition (reach, engagement, content quality)
- End with a specific call-to-action (e.g., "Let's schedule a 15-min call")
- Sound natural and conversational, not corporate or generic
- Be exactly 150 words (±10 words)

Return ONLY a JSON list of objects. Each object must have exactly these fields:
- company_name: The exact company/brand name
- website: The company's main website URL (just the domain, e.g., "example.com")
- reason_for_sponsorship: A specific, detailed explanation of why this company is a perfect fit for '{topic}' content creators (mention specific products, audience alignment, and partnership history if known)
- pitch_template: A 150-word personalized cold-email pitch from the creator to this specific company

Example format for reference:
[
  {{
    "company_name": "dbrand",
    "website": "dbrand.com",
    "reason_for_sponsorship": "Specializes in tech skins and accessories, a perfect fit for tech content creators covering devices and gadgets. Known for sponsoring YouTube tech reviewers.",
    "pitch_template": "Hey dbrand team,\\n\\nI'm [creator name], and I create {user_vibe} content about {topic} for my audience of [X] tech enthusiasts. I've been following your campaigns with MKBHD and Linus Tech Tips, and I think we'd be a great fit.\\n\\nMy recent video on the {topic} hit [X] views in 48 hours, with a 12% engagement rate. My audience loves detailed product breakdowns, and your skins would be a natural fit for my upcoming {topic} series.\\n\\nI'd love to explore a partnership—whether it's a dedicated review, integration into my monthly tech roundups, or a custom discount code for my community.\\n\\nInterested in a quick 15-min call next week? Let me know what works for your team.\\n\\nCheers,\\n[Your Name]"
  }}
]

Return ONLY the JSON array with exactly 3 companies, no other text or explanation."""

    try:
        # Call Gemini API
        print("🔍 Searching for brand partnerships...")
        print("✍️  Generating personalized pitch templates...")
        response = model.generate_content(master_prompt)
        
        # Parse the JSON response
        deal_plan = json.loads(response.text)
        
        # Validate the structure
        if not isinstance(deal_plan, list):
            raise ValueError("Response is not a list")
        
        # Ensure we have exactly 3 deals
        deal_plan = deal_plan[:3]
        
        # Validate each deal has required fields (Bundle 3.1: now includes pitch_template)
        validated_deals = []
        for deal in deal_plan:
            required_fields = ['company_name', 'website', 'reason_for_sponsorship', 'pitch_template']
            if all(key in deal for key in required_fields):
                validated_deals.append({
                    'company_name': deal['company_name'],
                    'website': deal['website'],
                    'reason_for_sponsorship': deal['reason_for_sponsorship'],
                    'pitch_template': deal['pitch_template']
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
            print(f"   💡 {deal['reason_for_sponsorship'][:80]}...")
            print(f"   📧 Pitch preview: {deal['pitch_template'][:60]}...")
        
    except Exception as e:
        print(f"⚠️  Error calling Gemini API: {e}")
        print("📦 Using fallback sponsor recommendations...")
        
        # Fallback: Provide topic-relevant default sponsors with pitch templates (Bundle 3.1)
        deal_plan = [
            {
                "company_name": "Skillshare",
                "website": "skillshare.com",
                "reason_for_sponsorship": f"Offers educational courses relevant to creators in the {topic} space, perfect for audience upskilling. Actively sponsors content creators across YouTube and social media.",
                "pitch_template": f"Hey Skillshare team,\n\nI'm a creator making {user_vibe} content about {topic}. My audience is always looking to level up their skills, and your platform is a perfect fit.\n\nMy last video on {topic} reached 50K+ engaged viewers who love learning new techniques. I'd love to partner with Skillshare to offer my community a special discount while creating a dedicated integration in my upcoming series.\n\nI've seen great results from your partnerships with creators like Ali Abdaal and Thomas Frank. Let's explore how we can create something equally impactful for my audience.\n\nInterested in a quick call this week?\n\nBest,\n[Your Name]"
            },
            {
                "company_name": "Squarespace",
                "website": "squarespace.com",
                "reason_for_sponsorship": f"Website builder commonly sponsored by creators, helps audience build their own {topic} presence online. Known for influencer partnerships and creator-friendly affiliate programs.",
                "pitch_template": f"Hi Squarespace partnerships team,\n\nI create {user_vibe} content about {topic} for an audience that's passionate about building their online presence. Many of them are aspiring creators and entrepreneurs who need professional websites.\n\nMy channel averages 40K views per video with a highly engaged community (8% avg engagement rate). I'd love to showcase how Squarespace can help my audience launch their {topic} projects with a custom discount code.\n\nYour partnerships with Marques Brownlee and Sara Dietschy have been excellent—I think we could create similar authentic value.\n\nCan we schedule a brief call?\n\nCheers,\n[Your Name]"
            },
            {
                "company_name": "NordVPN",
                "website": "nordvpn.com",
                "reason_for_sponsorship": f"Privacy and security tool that appeals to tech-savvy audiences interested in {topic}. One of the most active sponsors in the creator economy.",
                "pitch_template": f"Hello NordVPN team,\n\nI'm a content creator covering {topic} with a {user_vibe} style. My audience is tech-savvy and privacy-conscious—exactly your target demographic.\n\nMy recent {topic} video hit 60K views with a 10% click-through rate on links. I'd love to integrate NordVPN into my content with a dedicated segment explaining why online privacy matters for {topic} enthusiasts, plus a custom promo code.\n\nI've admired your creator partnerships and think we'd be a natural fit for an ongoing collaboration.\n\nWould you be open to a 15-minute intro call?\n\nThanks,\n[Your Name]"
            }
        ]
        
        print(f"✅ Using {len(deal_plan)} fallback sponsors with pitch templates")
        for i, deal in enumerate(deal_plan, 1):
            print(f"{i}. {deal['company_name']} - {deal['website']}")

    # Update the state with the deal plan
    print(f"\n💼 DealHunter complete! Found {len(deal_plan)} potential sponsors.")
    
    return {"deal_plan": deal_plan}


# --- 3. Testing the Agent (Standalone) ---
if __name__ == "__main__":
    print("\n🧪 TESTING: DealHunter Agent\n")
    print("=" * 60)
    
    # Create a test state
    test_state = {
        "user_vibe": "Tech-savvy, informative, slightly humorous",
        "topic": "AI Pin wearable technology",
        "scouted_trends": [],
        "content_pack": {},
        "engage_plan": {},
        "deal_plan": []
    }
    
    print(f"📋 Input State:")
    print(f"   Topic: {test_state['topic']}")
    print(f"   User Vibe: {test_state['user_vibe']}\n")
    
    # Run the agent
    result = run_dealhunter(test_state)
    
    # Display the result
    print("\n" + "=" * 60)
    print("📊 RESULT:")
    print("=" * 60)
    print("\nDeal Plan (JSON):")
    print(json.dumps(result['deal_plan'], indent=2))
    
    print("\n" + "=" * 60)
    print("✅ DealHunter Test Complete!")
    print("=" * 60 + "\n")
