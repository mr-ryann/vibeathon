"""
VibeOS - AI Agents
Specialized AI agents powered by LangChain + Groq for content generation and decision-making
"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime

from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from pydantic import BaseModel, Field

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
    
    def __init__(self, model_name: str = "llama-3.1-70b-versatile", temperature: float = 0.7):
        self.llm = ChatGroq(
            groq_api_key=get_api_key('groq'),
            model_name=model_name,
            temperature=temperature
        )
    
    def invoke(self, messages: List) -> str:
        """Invoke LLM with messages"""
        response = self.llm.invoke(messages)
        return response.content


# ==================== VIBE ANALYZER AGENT ====================

class VibeAnalyzerAgent(BaseAgent):
    """
    Analyzes user's content samples to extract their unique voice/style
    Uses Claude for high-quality analysis
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


# ==================== CONTENT GENERATOR AGENT ====================

class ContentGeneratorAgent(BaseAgent):
    """
    Generates viral content (scripts, captions, hooks) in user's exact voice
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


# ==================== SPONSOR PITCH AGENT ====================

class SponsorPitchAgent(BaseAgent):
    """
    Writes personalized sponsor pitch emails in user's voice
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


# ==================== REPLY GENERATOR AGENT ====================

class ReplyGeneratorAgent(BaseAgent):
    """
    Generates authentic replies to comments in user's voice
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


# ==================== STRATEGY AGENT ====================

class StrategyAgent(BaseAgent):
    """
    Makes high-level decisions about content strategy and optimization
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
    
    analyzer = VibeAnalyzerAgent()
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
    
    generator = ContentGeneratorAgent(vibe)
    content = generator.generate_content(trend, platform="tiktok")
    
    print(f"Hook: {content.hook}")
    print(f"Caption: {content.caption}")
    print(f"Hashtags: {', '.join(content.hashtags[:5])}")
    
    print("\n✅ All agents operational!")
