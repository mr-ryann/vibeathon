"""
VibeOS - LangGraph Workflow
Orchestrates the complete autonomous content creation → monetization workflow
"""

import os
from typing import Dict, List, Any, TypedDict, Annotated
from datetime import datetime
import operator

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage

from agents import (
    agent_vibe,
    agent_script,
    agent_sponsor,
    agent_reply,
    agent_strategy,
    agent_dealhunter
)
from tools import (
    TrendHunter,
    SocialMediaPoster,
    AutoReplyEngine,
    SponsorFinder,
    EmailSender,
    AnalyticsTracker
)
from utils import VibeDatabase, generate_sample_user_id


# ==================== STATE DEFINITION ====================

class VibeOSState(TypedDict):
    """
    Shared state across all nodes in the workflow graph
    """
    # User inputs
    user_id: str
    content_samples: List[str]
    niche: str
    goal: str
    platforms: List[str]
    
    # Vibe profile
    vibe_profile: Dict[str, Any]
    
    # Trend data
    trends: List[Dict[str, Any]]
    selected_trend: Dict[str, Any]
    
    # Generated content
    generated_content: Dict[str, Any]
    
    # Publishing results
    post_results: List[Dict[str, Any]]
    
    # Sponsor outreach
    sponsors: List[Dict[str, Any]]
    pitch_results: List[Dict[str, Any]]
    deal_plan: List[Dict[str, Any]]  # DealHunter results
    
    # Analytics
    analytics: Dict[str, Any]
    
    # Status messages
    messages: Annotated[List[str], operator.add]
    status: str


# ==================== WORKFLOW NODES ====================

def analyze_vibe_node(state: VibeOSState) -> Dict:
    """
    Node 1: Analyze user's content samples to extract vibe profile
    """
    print("📊 Analyzing your vibe...")
    
    analyzer = agent_vibe()
    vibe_profile = analyzer.analyze_vibe(state['content_samples'])
    
    # Save to database
    db = VibeDatabase()
    db.save_user_profile(
        user_id=state['user_id'],
        niche=state['niche'],
        goal=state['goal'],
        vibe_profile=vibe_profile
    )
    
    return {
        "vibe_profile": vibe_profile,
        "messages": [f"✅ Vibe analyzed: {vibe_profile.get('tone', 'unique')} tone, {vibe_profile.get('humor_style', 'authentic')} humor"],
        "status": "vibe_analyzed"
    }


def hunt_trends_node(state: VibeOSState) -> Dict:
    """
    Node 2: Hunt for viral trends in user's niche
    """
    print("🔍 Hunting viral trends...")
    
    hunter = TrendHunter()
    trends = hunter.get_best_trends(state['niche'])
    
    if not trends:
        # Fallback if no trends found
        trends = [{
            "title": f"Popular {state['niche']} content",
            "snippet": f"Create engaging {state['niche']} content",
            "relevance_score": 7.0,
            "source": "Fallback"
        }]
    
    # Select top trend
    selected_trend = trends[0] if trends else {}
    
    return {
        "trends": trends,
        "selected_trend": selected_trend,
        "messages": [f"🎯 Found {len(trends)} trending topics. Top: '{selected_trend.get('title', 'N/A')[:50]}...'"],
        "status": "trends_found"
    }


def generate_content_node(state: VibeOSState) -> Dict:
    """
    Node 3: Generate viral content in user's voice
    """
    print("✨ Generating content in your voice...")
    
    generator = agent_script(state['vibe_profile'])
    
    # Generate for primary platform (or first in list)
    primary_platform = state['platforms'][0] if state['platforms'] else "tiktok"
    content = generator.generate_content(state['selected_trend'], platform=primary_platform)
    
    # Convert to dict for state
    content_dict = {
        "script": content.script,
        "caption": content.caption,
        "hashtags": content.hashtags,
        "thumbnail_prompt": content.thumbnail_prompt,
        "hook": content.hook,
        "platform": primary_platform,
        "trend_source": state['selected_trend'].get('title', 'Trending topic')
    }
    
    # Save to database
    db = VibeDatabase()
    db.save_generated_content(state['user_id'], primary_platform, content_dict)
    
    return {
        "generated_content": content_dict,
        "messages": [f"📝 Content created! Hook: '{content.hook[:60]}...'"],
        "status": "content_generated"
    }


def publish_content_node(state: VibeOSState) -> Dict:
    """
    Node 4: Publish content to social platforms
    """
    print("📤 Publishing to platforms...")
    
    poster = SocialMediaPoster()
    results = []
    
    # Publish to each platform
    for platform in state['platforms']:
        if platform.lower() == "twitter":
            # Post to Twitter
            full_post = f"{state['generated_content']['caption']}\n\n#{' #'.join(state['generated_content']['hashtags'][:3])}"
            result = poster.post_to_twitter(full_post)
            results.append(result)
        
        elif platform.lower() == "tiktok":
            # TikTok posting (simulated for MVP)
            result = poster.post_to_tiktok("", state['generated_content']['caption'], state['generated_content']['hashtags'])
            results.append(result)
        
        elif platform.lower() == "instagram":
            # Instagram posting (simulated for MVP)
            result = poster.post_to_instagram("", state['generated_content']['caption'])
            results.append(result)
    
    success_count = sum(1 for r in results if r.get('status') in ['success', 'simulated'])
    
    return {
        "post_results": results,
        "messages": [f"🚀 Published to {success_count}/{len(state['platforms'])} platforms"],
        "status": "content_published"
    }


def auto_reply_node(state: VibeOSState) -> Dict:
    """
    Node 5: Auto-reply to first 10 comments
    """
    print("💬 Setting up auto-replies...")
    
    # Get the first successful post
    successful_post = next((p for p in state['post_results'] if p.get('status') == 'success'), None)
    
    if successful_post:
        reply_engine = AutoReplyEngine(state['vibe_profile'])
        post_id = successful_post.get('post_id')
        platform = successful_post.get('platform')
        
        if post_id:
            # Auto-reply to comments
            replies_sent = reply_engine.auto_reply_to_post(post_id, platform, max_replies=10)
            message = f"✅ Auto-reply activated for first {replies_sent} comments"
        else:
            message = "⏳ Auto-reply queued (waiting for comments)"
    else:
        message = "⏭️ Auto-reply skipped (no live posts)"
    
    return {
        "messages": [message],
        "status": "auto_reply_set"
    }


def find_sponsors_node(state: VibeOSState) -> Dict:
    """
    Node 6: Find relevant sponsors
    """
    print("🎯 Finding perfect sponsors...")
    
    finder = SponsorFinder()
    sponsors = finder.find_sponsors(state['niche'], num_sponsors=3)
    
    # Enrich with contact emails
    for sponsor in sponsors:
        if sponsor.get('website'):
            sponsor['contact_email'] = finder.find_contact_email(sponsor['website'])
    
    return {
        "sponsors": sponsors,
        "messages": [f"💼 Found {len(sponsors)} potential sponsors: {', '.join([s['brand_name'] for s in sponsors[:2]])}..."],
        "status": "sponsors_found"
    }


def run_dealhunter(state: VibeOSState) -> Dict:
    """
    Node: DealHunter - Find relevant brand deals using Gemini Pro API
    Uses AI-powered search to find Top 3 specific companies for sponsorship
    """
    print("💰 DealHunter: Finding perfect brand partnerships...")
    
    # Initialize DealHunter agent
    deal_hunter = agent_dealhunter()
    
    # Get the topic from state - use selected trend or niche
    topic = state.get('selected_trend', {}).get('title') or state.get('niche', 'content creation')
    
    # Find brand deals
    deal_plan = deal_hunter.find_deals(topic)
    
    # Format message with deal summary
    if deal_plan:
        companies = ', '.join([deal['company_name'] for deal in deal_plan[:2]])
        message = f"🤝 DealHunter found {len(deal_plan)} brand opportunities: {companies}..."
    else:
        message = "⚠️ DealHunter: No deals found, using fallback sponsors"
    
    return {
        "deal_plan": deal_plan,
        "messages": [message],
        "status": "deals_found"
    }


def pitch_sponsors_node(state: VibeOSState) -> Dict:
    """
    Node 7: Generate and send sponsor pitch emails
    """
    print("✉️ Sending sponsor pitches...")
    
    # Get user stats for pitch
    user_stats = {
        "niche": state['niche'],
        "followers": "growing audience",  # In production, fetch from analytics
        "engagement_rate": "high engagement"
    }
    
    pitch_agent = agent_sponsor(state['vibe_profile'], user_stats)
    email_sender = EmailSender()
    
    pitch_results = []
    
    for sponsor in state['sponsors'][:3]:  # Pitch top 3 sponsors
        # Generate pitch
        pitch = pitch_agent.generate_pitch(sponsor)
        
        # Send email (if Gmail configured)
        if sponsor.get('contact_email'):
            user_email = os.getenv('USER_EMAIL', 'creator@example.com')
            
            send_result = email_sender.send_pitch_email(
                to_email=sponsor['contact_email'],
                subject=pitch.subject,
                body=pitch.body,
                user_email=user_email
            )
            
            pitch_results.append({
                "brand": sponsor['brand_name'],
                "email": sponsor['contact_email'],
                "subject": pitch.subject,
                "status": send_result.get('status'),
                "sent_at": send_result.get('sent_at')
            })
    
    success_count = sum(1 for p in pitch_results if p.get('status') == 'success')
    
    return {
        "pitch_results": pitch_results,
        "messages": [f"📧 Sent {success_count}/{len(state['sponsors'][:3])} sponsor pitches"],
        "status": "sponsors_pitched"
    }


def track_analytics_node(state: VibeOSState) -> Dict:
    """
    Node 8: Track performance analytics
    """
    print("📈 Tracking analytics...")
    
    tracker = AnalyticsTracker()
    
    # Get analytics from platforms
    analytics_data = {
        "twitter": tracker.get_twitter_analytics() if "twitter" in [p.lower() for p in state['platforms']] else {},
        "followers_growth": "+0",  # In production, calculate delta
        "engagement_trend": "↑",
        "revenue": "$0",  # Track sponsor deals
        "content_posted": 1,
        "tracked_at": datetime.now().isoformat()
    }
    
    return {
        "analytics": analytics_data,
        "messages": ["📊 Analytics updated"],
        "status": "analytics_tracked"
    }


def optimize_strategy_node(state: VibeOSState) -> Dict:
    """
    Node 9: Analyze performance and optimize strategy
    """
    print("🧠 Optimizing strategy...")
    
    strategy_agent = agent_strategy()
    
    # Get historical content (from database)
    # For MVP, use current content as sample
    content_history = [state['generated_content']] if state.get('generated_content') else []
    
    recommendations = strategy_agent.analyze_performance(content_history)
    
    return {
        "messages": [f"💡 Strategy optimized: {recommendations.get('optimization_score', 7)}/10 performance score"],
        "status": "workflow_complete"
    }


# ==================== WORKFLOW GRAPH ====================

def create_vibeos_workflow() -> StateGraph:
    """
    Create the complete VibeOS workflow graph
    """
    
    # Initialize graph
    workflow = StateGraph(VibeOSState)
    
    # Add all nodes
    workflow.add_node("analyze_vibe", analyze_vibe_node)
    workflow.add_node("hunt_trends", hunt_trends_node)
    workflow.add_node("generate_content", generate_content_node)
    workflow.add_node("publish_content", publish_content_node)
    workflow.add_node("auto_reply", auto_reply_node)
    workflow.add_node("find_sponsors", find_sponsors_node)
    workflow.add_node("run_dealhunter", run_dealhunter)
    workflow.add_node("pitch_sponsors", pitch_sponsors_node)
    workflow.add_node("track_analytics", track_analytics_node)
    workflow.add_node("optimize_strategy", optimize_strategy_node)
    
    # Define edges (workflow flow)
    workflow.set_entry_point("analyze_vibe")
    workflow.add_edge("analyze_vibe", "hunt_trends")
    workflow.add_edge("hunt_trends", "generate_content")
    workflow.add_edge("generate_content", "publish_content")
    workflow.add_edge("publish_content", "auto_reply")
    workflow.add_edge("auto_reply", "find_sponsors")
    workflow.add_edge("find_sponsors", "run_dealhunter")
    workflow.add_edge("run_dealhunter", "pitch_sponsors")
    workflow.add_edge("pitch_sponsors", "track_analytics")
    workflow.add_edge("track_analytics", "optimize_strategy")
    workflow.add_edge("optimize_strategy", END)
    
    return workflow.compile()


# ==================== WORKFLOW EXECUTION ====================

def run_vibeos_workflow(
    content_samples: List[str],
    niche: str,
    goal: str,
    platforms: List[str],
    user_id: str = None
) -> Dict[str, Any]:
    """
    Execute the complete VibeOS workflow
    
    Args:
        content_samples: 3-5 pieces of user's content
        niche: Creator's niche (e.g., "fitness memes")
        goal: Creator's goal (e.g., "100k followers")
        platforms: List of platforms to post to
        user_id: Optional user ID (generated if not provided)
    
    Returns:
        Complete workflow results
    """
    
    # Generate user ID if not provided
    if not user_id:
        user_id = generate_sample_user_id()
    
    # Initialize state
    initial_state = {
        "user_id": user_id,
        "content_samples": content_samples,
        "niche": niche,
        "goal": goal,
        "platforms": platforms,
        "vibe_profile": {},
        "trends": [],
        "selected_trend": {},
        "generated_content": {},
        "post_results": [],
        "sponsors": [],
        "deal_plan": [],
        "pitch_results": [],
        "analytics": {},
        "messages": [],
        "status": "initialized"
    }
    
    # Create and run workflow
    workflow = create_vibeos_workflow()
    
    print("\n" + "="*60)
    print("🚀 VIBEOS WORKFLOW STARTING")
    print("="*60 + "\n")
    
    # Execute workflow
    final_state = workflow.invoke(initial_state)
    
    print("\n" + "="*60)
    print("✅ WORKFLOW COMPLETE")
    print("="*60 + "\n")
    
    # Print summary
    print("📋 EXECUTION SUMMARY:")
    for message in final_state.get('messages', []):
        print(f"   {message}")
    
    return final_state


# ==================== TESTING ====================

if __name__ == "__main__":
    # Test complete workflow
    print("Testing VibeOS Complete Workflow\n")
    
    # Sample user data
    test_samples = [
        "bruh this AI stuff is getting wild 😂 literally nobody saw this coming",
        "okay so here's the thing about automation... it's not what you think 👀",
        "POV: you just discovered the tool that's about to change everything 🤯"
    ]
    
    test_niche = "AI & automation memes"
    test_goal = "Build 100k follower tech brand"
    test_platforms = ["twitter"]  # Start with Twitter only for testing
    
    # Run workflow
    result = run_vibeos_workflow(
        content_samples=test_samples,
        niche=test_niche,
        goal=test_goal,
        platforms=test_platforms
    )
    
    # Display results
    print("\n" + "="*60)
    print("📊 FINAL RESULTS")
    print("="*60)
    print(f"\nUser ID: {result['user_id']}")
    print(f"Status: {result['status']}")
    print(f"\nVibe Profile: {result['vibe_profile'].get('tone', 'N/A')} tone")
    print(f"Content Generated: {result['generated_content'].get('hook', 'N/A')[:80]}...")
    print(f"Sponsors Found: {len(result.get('sponsors', []))}")
    print(f"Pitches Sent: {len(result.get('pitch_results', []))}")
