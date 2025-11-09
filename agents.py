"""
VibeOS - AI Agents
Specialized AI agents powered by LangChain + Groq for content generation and decision-making
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from pydantic import BaseModel, Field
import google.generativeai as genai

from utils import build_vibe_prompt, extract_vibe_markers, get_api_key


# ==================== PYDANTIC MODELS ====================

class ContentOutput(BaseModel):
    """Structured output for generated content"""
    script: str = Field(description="15-30 second content script")
    caption: str = Field(description="Social media caption (100-150 chars)")
    hashtags: List[str] = Field(description="List of 10 relevant hashtags")
    thumbnail_prompt: str = Field(description="Prompt for AI image generation")
    hook: str = Field(description="Attention-grabbing first line")


class SponsorPitch(BaseModel):
    """Structured output for sponsor pitch emails"""
    subject: str = Field(description="Email subject line")
    body: str = Field(description="Full email body")
    cta: str = Field(description="Call-to-action closing")


# ==================== BASE AGENT CLASS ====================

class BaseAgent:
    """Base class for all AI agents"""
    
    def __init__(self, model_name: str = "gemini-pro", temperature: float = 0.7):
        # Configure Gemini instead of Groq
        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key:
            raise ValueError("Missing GEMINI_API_KEY in environment variables")
        genai.configure(api_key=gemini_key)
        self.model = genai.GenerativeModel(model_name)
        self.temperature = temperature
    
    def invoke(self, messages: List) -> str:
        """Invoke LLM with messages"""
        # Convert messages to Gemini format
        prompt_parts = []
        for msg in messages:
            if hasattr(msg, 'content'):
                prompt_parts.append(msg.content)
            else:
                prompt_parts.append(str(msg))
        
        prompt = "\n\n".join(prompt_parts)
        response = self.model.generate_content(prompt)
        return response.text


# ==================== RIPPLE AGENT ====================

class VibeAnalyzerAgent(BaseAgent):
    """
    ripple: Analyzes user's content samples to extract their unique voice/style
    Uses Claude for high-quality analysis
    Name: ripple - like ripples spreading outward, detecting the unique patterns in content
    """
    
    def __init__(self):
        # Use Groq for vibe analysis
        super().__init__(temperature=0.3)  # Lower temp for consistent analysis
    
    def analyze_vibe(self, content_samples: List[str]) -> Dict[str, Any]:
        """
        Deep analysis of user's content to extract vibe profile
        """
        
        # First, use utility function for quantitative analysis
        quantitative_vibe = extract_vibe_markers(content_samples)
        
        # Then, use LLM for qualitative analysis
        analysis_prompt = f"""You are an expert content analyst specializing in creator voice identification.

Analyze these {len(content_samples)} content samples and identify the creator's UNIQUE voice characteristics:

CONTENT SAMPLES:
{chr(10).join([f'{i+1}. "{sample}"' for i, sample in enumerate(content_samples)])}

Provide a comprehensive vibe analysis covering:

1. **Tone & Personality**: What's their dominant emotional tone? (sarcastic, wholesome, edgy, professional, etc.)
2. **Humor Style**: How do they make people laugh? (self-deprecating, observational, absurdist, dry, etc.)
3. **Language Patterns**: What makes their writing unique? (slang usage, sentence structure, punctuation quirks)
4. **Audience Connection**: How do they relate to their audience? (relatable friend, expert teacher, provocateur, etc.)
5. **Signature Elements**: What would make someone say "that's definitely them"?

Return your analysis in JSON format with these keys:
{{
    "tone": "primary tone descriptor",
    "humor_style": "type of humor",
    "language_quirks": ["quirk1", "quirk2"],
    "audience_relationship": "how they connect",
    "signature_phrases": ["phrase1", "phrase2"],
    "content_formula": "their typical structure (hook → body → payoff)",
    "authenticity_score": 0-10
}}"""

        messages = [
            SystemMessage(content="You are an expert content analyst with deep understanding of creator psychology and voice."),
            HumanMessage(content=analysis_prompt)
        ]
        
        response = self.invoke(messages)
        
        # Parse JSON response
        try:
            import json
            qualitative_vibe = json.loads(response)
        except:
            qualitative_vibe = {
                "tone": quantitative_vibe.get('tone', 'casual'),
                "humor_style": "observational",
                "language_quirks": quantitative_vibe.get('signature_words', [])[:5],
                "audience_relationship": "relatable friend",
                "signature_phrases": [],
                "content_formula": "hook → value → CTA",
                "authenticity_score": 7.5
            }
        
        # Combine quantitative and qualitative analysis
        full_vibe = {
            **quantitative_vibe,
            **qualitative_vibe,
            "analyzed_at": datetime.now().isoformat(),
            "sample_count": len(content_samples)
        }
        
        return full_vibe


# ==================== QUILL AGENT ====================

class ContentGeneratorAgent(BaseAgent):
    """
    quill: Generates viral content (scripts, captions, hooks) in user's exact voice
    Name: quill - the writer's tool, crafting stories from raw trends
    """
    
    def __init__(self, vibe_profile: Dict[str, Any]):
        super().__init__(temperature=0.9)  # Higher temp for creativity
        self.vibe_profile = vibe_profile
        self.vibe_prompt = build_vibe_prompt(vibe_profile)
    
    def generate_content(self, trend: Dict[str, Any], platform: str = "tiktok") -> ContentOutput:
        """
        Generate complete content package based on trending topic
        """
        
        # Platform-specific requirements
        platform_specs = {
            "tiktok": {"length": "15-30 seconds", "style": "fast-paced, hook in first 3 seconds"},
            "instagram": {"length": "30-60 seconds", "style": "visually stunning, aesthetic"},
            "twitter": {"length": "1 tweet (280 chars)", "style": "punchy, quotable"},
            "youtube": {"length": "60 seconds", "style": "informative + entertaining"}
        }
        
        spec = platform_specs.get(platform, platform_specs["tiktok"])
        
        generation_prompt = f"""You are creating viral {platform} content based on this trending topic:

TRENDING TOPIC:
Title: {trend.get('title', '')}
Context: {trend.get('snippet', '') or trend.get('text', '')}
Relevance Score: {trend.get('relevance_score', 0)}/10

YOUR VIBE PROFILE:
{self.vibe_prompt}

PLATFORM REQUIREMENTS:
- Length: {spec['length']}
- Style: {spec['style']}

CREATE A COMPLETE CONTENT PACKAGE:

1. **SCRIPT** ({spec['length']}):
   - Hook (first 3 seconds) - must stop scrolling
   - Body (deliver value/entertainment)
   - Payoff (satisfying ending + CTA)
   - Written in YOUR voice (not generic creator voice)

2. **CAPTION** (100-150 characters):
   - Complements video, doesn't repeat it
   - Includes call-to-action
   - Your signature style

3. **HASHTAGS** (10 total):
   - 3 viral/broad (1M+ posts)
   - 7 niche-specific (10k-500k posts)
   - Mix trending + evergreen

4. **THUMBNAIL PROMPT** (for AI image generation):
   - Describe the perfect thumbnail image
   - Include colors, composition, text overlay
   - Must be scroll-stopping

5. **HOOK VARIATIONS** (provide 3 alternatives):
   - Give me 3 different first-line hooks to A/B test

Return ONLY valid JSON matching this structure:
{{
    "script": "full script here",
    "caption": "caption here",
    "hashtags": ["hashtag1", "hashtag2", ...],
    "thumbnail_prompt": "detailed prompt",
    "hook": "strongest hook option"
}}

CRITICAL: This must sound like YOU, not generic AI. Use your tone, humor, and style."""

        messages = [
            SystemMessage(content=self.vibe_prompt),
            HumanMessage(content=generation_prompt)
        ]
        
        response = self.invoke(messages)
        
        # Parse JSON response
        try:
            import json
            # Extract JSON from response (in case there's extra text)
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            json_str = response[json_start:json_end]
            content_data = json.loads(json_str)
            
            return ContentOutput(**content_data)
        
        except Exception as e:
            print(f"Error parsing content output: {e}")
            # Return fallback content
            return ContentOutput(
                script=f"Check out this {trend.get('title', 'trend')} - it's wild! [Your take here]",
                caption="New video dropping 🔥 #viral",
                hashtags=["fyp", "viral", "trending", "foryou", "explore"],
                thumbnail_prompt="Bold text overlay on gradient background",
                hook="Wait, this is actually insane..."
            )


# ==================== PULSE AGENT ====================

class SponsorPitchAgent(BaseAgent):
    """
    pulse: Writes personalized sponsor pitch emails in user's voice
    Name: pulse - the steady heartbeat of engagement and outreach
    """
    
    def __init__(self, vibe_profile: Dict[str, Any], user_stats: Dict[str, Any]):
        super().__init__(temperature=0.7)
        self.vibe_profile = vibe_profile
        self.user_stats = user_stats
    
    def generate_pitch(self, brand: Dict[str, Any]) -> SponsorPitch:
        """
        Generate personalized sponsor pitch email
        """
        
        pitch_prompt = f"""You are writing a sponsor pitch email to {brand['brand_name']}.

YOUR CREATOR PROFILE:
- Niche: {self.user_stats.get('niche', 'content creator')}
- Followers: {self.user_stats.get('followers', 'growing audience')}
- Engagement Rate: {self.user_stats.get('engagement_rate', 'high engagement')}
- Tone: {self.vibe_profile.get('tone', 'authentic')}

BRAND INFO:
- Brand: {brand['brand_name']}
- Description: {brand.get('description', '')}
- Website: {brand.get('website', '')}

WRITE A PITCH EMAIL THAT:
1. **Subject Line**: Grab attention (under 60 chars)
2. **Opening**: Quick intro that shows you researched them
3. **Value Prop**: What's in it for THEM (not you)
4. **Proof**: Your best stats/content examples
5. **CTA**: Specific next step (call/media kit review)

VOICE REQUIREMENTS:
- Write like a HUMAN, not a corporate template
- Match this tone: {self.vibe_profile.get('tone', 'professional but personable')}
- Keep it under 150 words (busy people)
- No cringe phrases like "excited to partner" or "perfect fit"
- Be confident but not arrogant

Return ONLY valid JSON:
{{
    "subject": "subject line here",
    "body": "full email body here",
    "cta": "specific call-to-action"
}}"""

        messages = [
            SystemMessage(content="You are an expert at writing high-converting sponsor pitch emails for creators."),
            HumanMessage(content=pitch_prompt)
        ]
        
        response = self.invoke(messages)
        
        try:
            import json
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            json_str = response[json_start:json_end]
            pitch_data = json.loads(json_str)
            
            return SponsorPitch(**pitch_data)
        
        except Exception as e:
            print(f"Error parsing pitch output: {e}")
            # Return fallback pitch
            return SponsorPitch(
                subject=f"Quick partnership idea for {brand['brand_name']}",
                body=f"Hi {brand['brand_name']} team,\n\nI create {self.user_stats.get('niche', 'content')} for {self.user_stats.get('followers', 'an engaged audience')}. My audience loves brands that [relevant value prop].\n\nWould love to discuss a partnership. Available for a quick call this week?\n\nBest,\n[Your name]",
                cta="Are you free for a 15-min call this week?"
            )


# ==================== PULSE REPLY AGENT ====================

class ReplyGeneratorAgent(BaseAgent):
    """
    pulse: Generates authentic replies to comments in user's voice
    Name: pulse - maintaining the rhythm of audience engagement
    """
    
    def __init__(self, vibe_profile: Dict[str, Any]):
        super().__init__(temperature=0.8)
        self.vibe_profile = vibe_profile
    
    def generate_reply(self, comment: str, context: str = "") -> str:
        """
        Generate contextual reply to a comment
        """
        
        reply_prompt = f"""Generate a SHORT reply to this comment on your content.

COMMENT: "{comment}"
CONTEXT: {context if context else "General content post"}

YOUR VIBE: {self.vibe_profile.get('tone', 'friendly')} tone, {self.vibe_profile.get('humor_style', 'authentic')} humor

REQUIREMENTS:
- Under 100 characters
- Sound like a real human (not "Thanks for watching!")
- Match your vibe/personality
- Encourage engagement (but naturally)
- No corporate speak

Just return the reply text, nothing else."""

        messages = [
            SystemMessage(content=f"You reply to comments in a {self.vibe_profile.get('tone', 'friendly')} and authentic way."),
            HumanMessage(content=reply_prompt)
        ]
        
        response = self.invoke(messages)
        
        # Clean up response
        reply = response.strip().strip('"').strip("'")
        
        # Ensure it's not too long
        if len(reply) > 200:
            reply = reply[:197] + "..."
        
        return reply


# ==================== CORE STRATEGY AGENT ====================

class StrategyAgent(BaseAgent):
    """
    core: Makes high-level decisions about content strategy and optimization
    Name: core - the central brain, making strategic decisions
    """
    
    def __init__(self):
        super().__init__(temperature=0.5)  # Lower temp for strategic thinking
    
    def analyze_performance(self, content_history: List[Dict]) -> Dict[str, Any]:
        """
        Analyze past content performance and provide strategic recommendations
        """
        
        if not content_history:
            return {
                "recommendations": ["Post more content to gather data"],
                "best_posting_time": "12:00",
                "best_content_type": "trending topics",
                "optimization_score": 0
            }
        
        # Build performance summary
        performance_summary = self._summarize_performance(content_history)
        
        analysis_prompt = f"""You are a data-driven content strategist analyzing creator performance.

PERFORMANCE DATA:
{performance_summary}

PROVIDE STRATEGIC RECOMMENDATIONS:

1. What's working? (top 3 patterns)
2. What's not working? (top 3 issues)
3. Optimization opportunities (specific actions)
4. Best posting times based on engagement
5. Content type focus (what to double down on)

Return JSON:
{{
    "recommendations": ["rec1", "rec2", "rec3"],
    "best_posting_time": "HH:MM",
    "best_content_type": "description",
    "optimization_score": 0-10,
    "key_insights": ["insight1", "insight2"]
}}"""

        messages = [
            SystemMessage(content="You are an expert content strategist with deep analytics expertise."),
            HumanMessage(content=analysis_prompt)
        ]
        
        response = self.invoke(messages)
        
        try:
            import json
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            json_str = response[json_start:json_end]
            strategy_data = json.loads(json_str)
            return strategy_data
        
        except:
            return {
                "recommendations": ["Continue posting consistently", "Engage with comments", "Test different content formats"],
                "best_posting_time": "12:00",
                "best_content_type": "trending topics",
                "optimization_score": 7
            }
    
    def _summarize_performance(self, content_history: List[Dict]) -> str:
        """Summarize content performance for analysis"""
        
        total_posts = len(content_history)
        avg_engagement = sum(c.get('engagement_rate', 0) for c in content_history) / max(total_posts, 1)
        total_likes = sum(c.get('likes', 0) for c in content_history)
        
        summary = f"""
Total Posts: {total_posts}
Average Engagement Rate: {avg_engagement:.2f}%
Total Likes: {total_likes}
Date Range: {content_history[0].get('created_at', 'N/A')} to {content_history[-1].get('created_at', 'N/A')}
        """
        
        return summary


# ==================== ENVOY AGENT ====================

class DealHunterAgent:
    """
    envoy: Finds relevant brand deals using Gemini Pro API with search
    Simulates finding brand partnerships for the "Empire" vision
    Name: envoy - the ambassador, forging partnerships and deals
    """
    
    def __init__(self):
        # Configure Gemini API
        gemini_api_key = get_api_key('gemini')
        genai.configure(api_key=gemini_api_key)
        
        # Use Gemini Pro model with grounding/search capabilities
        self.model = genai.GenerativeModel('gemini-pro')
    
    def find_deals(self, topic: str) -> List[Dict[str, Any]]:
        """
        Find top 3 brand sponsorship opportunities for a given topic
        
        Args:
            topic: The content topic/niche to find sponsors for
            
        Returns:
            List of sponsor opportunities with company_name, website, and reason_for_sponsorship
        """
        
        # Master Prompt for envoy
        prompt = f"""You are the 'envoy' agent, an expert in brand-creator partnerships. 

For the topic '{topic}', identify the Top 3 specific companies that would be perfect sponsors for a creator making content about this topic.

Consider:
- Companies that actively sponsor creators and influencers
- Brands with products/services relevant to this niche
- Companies known for marketing partnerships
- Both direct-to-consumer brands and B2B companies if relevant

Return ONLY a valid JSON list of objects. Each object must have exactly these fields:
- company_name: The exact company/brand name
- website: The company's main website URL
- reason_for_sponsorship: A specific explanation of why this company is a perfect fit for '{topic}' content (be specific about product fit, audience alignment, etc.)

Example format:
[
  {{
    "company_name": "Company Name",
    "website": "companyname.com",
    "reason_for_sponsorship": "Specific reason why they're perfect for this niche"
  }}
]

Return ONLY the JSON array, no other text."""

        try:
            # Call Gemini API
            response = self.model.generate_content(prompt)
            
            # Extract and parse the response
            response_text = response.text.strip()
            
            # Try to extract JSON from the response
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                deals = json.loads(json_str)
                
                # Validate the structure
                validated_deals = []
                for deal in deals[:3]:  # Ensure max 3
                    if all(key in deal for key in ['company_name', 'website', 'reason_for_sponsorship']):
                        validated_deals.append({
                            'company_name': deal['company_name'],
                            'website': deal['website'],
                            'reason_for_sponsorship': deal['reason_for_sponsorship']
                        })
                
                if validated_deals:
                    return validated_deals
            
            # If parsing fails, raise exception to trigger fallback
            raise ValueError("Failed to parse valid JSON from response")
            
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            print(f"Falling back to default sponsors for topic: {topic}")
            
            # Fallback: Return topic-relevant sponsors
            return self._get_fallback_sponsors(topic)
    
    def _get_fallback_sponsors(self, topic: str) -> List[Dict[str, Any]]:
        """
        Provide fallback sponsor suggestions if API fails
        """
        # Generic sponsors that work for most tech/creator content
        fallback_sponsors = [
            {
                "company_name": "Skillshare",
                "website": "skillshare.com",
                "reason_for_sponsorship": f"Offers educational courses relevant to creators in the {topic} space, perfect for audience upskilling."
            },
            {
                "company_name": "Squarespace",
                "website": "squarespace.com",
                "reason_for_sponsorship": f"Website builder commonly sponsored by creators, helps audience build their own {topic} presence online."
            },
            {
                "company_name": "NordVPN",
                "website": "nordvpn.com",
                "reason_for_sponsorship": f"Privacy and security tool that appeals to tech-savvy audiences interested in {topic}."
            }
        ]
        
        return fallback_sponsors


# ==================== PUBLIC API ALIASES ====================

# Expose agent entry points following agent_<name> convention while keeping
# the original class names available for compatibility with legacy imports.
agent_vibe = VibeAnalyzerAgent
agent_script = ContentGeneratorAgent
agent_sponsor = SponsorPitchAgent
agent_reply = ReplyGeneratorAgent
agent_strategy = StrategyAgent
agent_dealhunter = DealHunterAgent

__all__ = [
    "agent_vibe",
    "agent_script",
    "agent_sponsor",
    "agent_reply",
    "agent_strategy",
    "agent_dealhunter",
    "VibeAnalyzerAgent",
    "ContentGeneratorAgent",
    "SponsorPitchAgent",
    "ReplyGeneratorAgent",
    "StrategyAgent",
    "DealHunterAgent",
    "ContentOutput",
    "SponsorPitch"
]


# ==================== TESTING ====================

if __name__ == "__main__":
    print("Testing VibeOS Agents...\n")
    
    # Test Vibe Analyzer
    print("1. Testing Vibe Analyzer Agent")
    print("-" * 50)
    
    samples = [
        "bruh this is literally the funniest thing I've seen all week 💀",
        "okay but nobody talks about how actually insane this is...",
        "POV: you just discovered the life hack that changes everything 🤯"
    ]
    
    analyzer = agent_vibe()
    vibe = analyzer.analyze_vibe(samples)
    
    print(f"Detected Tone: {vibe.get('tone')}")
    print(f"Humor Style: {vibe.get('humor_style')}")
    print(f"Authenticity Score: {vibe.get('authenticity_score')}/10")
    
    # Test Content Generator
    print("\n2. Testing Content Generator Agent")
    print("-" * 50)
    
    trend = {
        "title": "AI tools replacing jobs in 2025",
        "snippet": "New AI automation tools are transforming creative industries",
        "relevance_score": 8.5
    }
    
    generator = agent_script(vibe)
    content = generator.generate_content(trend, platform="tiktok")
    
    print(f"Hook: {content.hook}")
    print(f"Caption: {content.caption}")
    print(f"Hashtags: {', '.join(content.hashtags[:5])}")
    
    print("\n✅ All agents operational!")
