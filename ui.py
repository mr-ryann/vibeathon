"""
VibeOS - Streamlit Dashboard
Beautiful, interactive UI for the autonomous creator OS
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
import time
from typing import List, Dict, Any

from workflow import run_vibeos_workflow
from utils import VibeDatabase, generate_sample_user_id
from tools import AnalyticsTracker


# ==================== PAGE CONFIG ====================

st.set_page_config(
    page_title="VibeOS - Your AI Co-Founder",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==================== CUSTOM CSS ====================

st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .tagline {
        text-align: center;
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .warning-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


# ==================== SESSION STATE ====================

def init_session_state():
    """Initialize session state variables"""
    if 'user_id' not in st.session_state:
        st.session_state.user_id = generate_sample_user_id()
    
    if 'workflow_run' not in st.session_state:
        st.session_state.workflow_run = False
    
    if 'workflow_results' not in st.session_state:
        st.session_state.workflow_results = None
    
    if 'onboarding_complete' not in st.session_state:
        st.session_state.onboarding_complete = False


# ==================== COMPONENTS ====================

def render_header():
    """Render main header"""
    st.markdown('<h1 class="main-header">🚀 VibeOS</h1>', unsafe_allow_html=True)
    st.markdown('<p class="tagline">Your AI co-founder that turns solo creators into 6-figure brands on full autopilot</p>', unsafe_allow_html=True)


def render_metrics_dashboard(results: Dict[str, Any]):
    """Render key metrics dashboard"""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📈 Followers",
            value=results.get('analytics', {}).get('twitter', {}).get('followers', '0'),
            delta="+0"
        )
    
    with col2:
        st.metric(
            label="🔥 Engagement",
            value="High",
            delta="↑"
        )
    
    with col3:
        st.metric(
            label="📝 Content Posted",
            value=len(results.get('post_results', [])),
            delta="+1"
        )
    
    with col4:
        st.metric(
            label="💰 Revenue",
            value="$0",
            delta="Pending"
        )


def render_onboarding():
    """Render onboarding flow"""
    
    st.markdown("## 🎨 Let's Learn Your Vibe")
    
    st.markdown("""
    Upload 3-5 pieces of your best content so VibeOS can learn your unique voice, humor, and style.
    This takes 60 seconds and ensures your AI-generated content sounds exactly like YOU.
    """)
    
    # Content samples input
    st.markdown("### Your Content Samples")
    
    sample1 = st.text_area(
        "Sample 1 (your best viral post)",
        placeholder="e.g., 'bruh this AI stuff is getting wild 😂 literally nobody saw this coming'",
        height=80
    )
    
    sample2 = st.text_area(
        "Sample 2",
        placeholder="e.g., 'okay so here's the thing about [topic]... it's not what you think 👀'",
        height=80
    )
    
    sample3 = st.text_area(
        "Sample 3",
        placeholder="e.g., 'POV: you just discovered the tool that's about to change everything'",
        height=80
    )
    
    sample4 = st.text_area(
        "Sample 4 (optional)",
        placeholder="Add another sample for better vibe analysis",
        height=80
    )
    
    sample5 = st.text_area(
        "Sample 5 (optional)",
        placeholder="One more for maximum accuracy",
        height=80
    )
    
    # Niche and goal
    col1, col2 = st.columns(2)
    
    with col1:
        niche = st.text_input(
            "Your Niche",
            placeholder="e.g., fitness memes, tech commentary, lifestyle tips",
            help="What do you create content about?"
        )
    
    with col2:
        goal = st.text_input(
            "Your Goal",
            placeholder="e.g., 100k followers, land first sponsor, go viral",
            help="What are you trying to achieve?"
        )
    
    # Platform selection
    st.markdown("### Where Should VibeOS Post?")
    
    col1, col2, col3, col4 = st.columns(4)
    
    platforms = []
    with col1:
        if st.checkbox("𝕏 Twitter", value=True):
            platforms.append("twitter")
    
    with col2:
        if st.checkbox("📱 TikTok"):
            platforms.append("tiktok")
    
    with col3:
        if st.checkbox("📸 Instagram"):
            platforms.append("instagram")
    
    with col4:
        if st.checkbox("▶️ YouTube"):
            platforms.append("youtube")
    
    # Start button
    st.markdown("---")
    
    if st.button("🚀 Launch VibeOS", type="primary", use_container_width=True):
        # Validate inputs
        samples = [s for s in [sample1, sample2, sample3, sample4, sample5] if s.strip()]
        
        if len(samples) < 3:
            st.error("❌ Please provide at least 3 content samples")
            return
        
        if not niche or not goal:
            st.error("❌ Please fill in your niche and goal")
            return
        
        if not platforms:
            st.error("❌ Please select at least one platform")
            return
        
        # Store in session state
        st.session_state.content_samples = samples
        st.session_state.niche = niche
        st.session_state.goal = goal
        st.session_state.platforms = platforms
        st.session_state.onboarding_complete = True
        
        st.rerun()


def render_workflow_execution():
    """Render live workflow execution with progress"""
    
    st.markdown("## 🤖 VibeOS is Working...")
    
    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Workflow steps
    steps = [
        ("📊 Analyzing your vibe...", 10),
        ("🔍 Hunting viral trends...", 20),
        ("✨ Generating content in your voice...", 40),
        ("📤 Publishing to platforms...", 60),
        ("💬 Setting up auto-replies...", 70),
        ("🎯 Finding perfect sponsors...", 80),
        ("✉️ Sending sponsor pitches...", 90),
        ("📈 Tracking analytics...", 95),
        ("🧠 Optimizing strategy...", 100)
    ]
    
    # Simulate workflow execution with progress
    for step_text, progress in steps:
        status_text.markdown(f"### {step_text}")
        progress_bar.progress(progress)
        time.sleep(0.5)  # Visual delay
    
    # Run actual workflow
    with st.spinner("Running workflow..."):
        results = run_vibeos_workflow(
            content_samples=st.session_state.content_samples,
            niche=st.session_state.niche,
            goal=st.session_state.goal,
            platforms=st.session_state.platforms,
            user_id=st.session_state.user_id
        )
    
    # Store results
    st.session_state.workflow_results = results
    st.session_state.workflow_run = True
    
    # Success message
    st.balloons()
    st.success("✅ VibeOS Workflow Complete!")
    
    time.sleep(1)
    st.rerun()


def render_results_dashboard():
    """Render complete results dashboard"""
    
    results = st.session_state.workflow_results
    
    st.markdown("## 🎉 Your AI Co-Founder is LIVE!")
    
    # Metrics
    render_metrics_dashboard(results)
    
    st.markdown("---")
    
    # Main content area
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 Generated Content",
        "📊 Analytics",
        "💼 Sponsor Outreach",
        "🎯 Strategy",
        "⚙️ Settings"
    ])
    
    with tab1:
        render_content_tab(results)
    
    with tab2:
        render_analytics_tab(results)
    
    with tab3:
        render_sponsors_tab(results)
    
    with tab4:
        render_strategy_tab(results)
    
    with tab5:
        render_settings_tab(results)


def render_content_tab(results: Dict[str, Any]):
    """Render generated content tab"""
    
    st.markdown("### 🎬 Your Latest Content")
    
    content = results.get('generated_content', {})
    
    if content:
        # Content preview
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### 🎤 Script")
            st.info(content.get('script', 'No script generated'))
            
            st.markdown("#### 💬 Caption")
            st.success(content.get('caption', 'No caption'))
            
            st.markdown("#### #️⃣ Hashtags")
            hashtags = content.get('hashtags', [])
            st.write(" ".join([f"`#{tag}`" for tag in hashtags[:10]]))
        
        with col2:
            st.markdown("#### 🎨 Thumbnail Prompt")
            st.text_area(
                "AI Image Prompt",
                value=content.get('thumbnail_prompt', 'No prompt'),
                height=150,
                disabled=True
            )
            
            st.markdown("#### 🎯 Hook")
            st.warning(content.get('hook', 'No hook'))
    
    # Publishing status
    st.markdown("---")
    st.markdown("### 📤 Publishing Status")
    
    post_results = results.get('post_results', [])
    
    for post in post_results:
        platform = post.get('platform', 'Unknown')
        status = post.get('status', 'unknown')
        
        if status == 'success':
            st.success(f"✅ {platform}: Posted successfully!")
            if post.get('url'):
                st.markdown(f"[View Post]({post['url']})")
        elif status == 'simulated':
            st.info(f"⏳ {platform}: Simulated (API in development)")
        else:
            st.error(f"❌ {platform}: {post.get('message', 'Failed')}")


def render_analytics_tab(results: Dict[str, Any]):
    """Render analytics dashboard"""
    
    st.markdown("### 📊 Performance Analytics")
    
    # Sample data for visualization
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    
    # Followers growth chart
    st.markdown("#### 📈 Follower Growth (Last 30 Days)")
    
    followers_data = pd.DataFrame({
        'Date': dates,
        'Followers': range(1000, 1000 + len(dates) * 50, 50)
    })
    
    fig = px.line(
        followers_data,
        x='Date',
        y='Followers',
        title='Follower Growth Trend'
    )
    fig.update_traces(line_color='#667eea', line_width=3)
    st.plotly_chart(fig, use_container_width=True)
    
    # Engagement chart
    st.markdown("#### 🔥 Engagement Rate Trend")
    
    engagement_data = pd.DataFrame({
        'Date': dates,
        'Engagement': [5 + i * 0.3 for i in range(len(dates))]
    })
    
    fig2 = px.area(
        engagement_data,
        x='Date',
        y='Engagement',
        title='Engagement Rate (%)'
    )
    fig2.update_traces(line_color='#764ba2', fillcolor='rgba(118, 75, 162, 0.3)')
    st.plotly_chart(fig2, use_container_width=True)
    
    # Top content
    st.markdown("#### ⭐ Top Performing Content")
    
    top_content = pd.DataFrame({
        'Content': ['Post 1', 'Post 2', 'Post 3'],
        'Likes': [1500, 1200, 900],
        'Comments': [120, 95, 78],
        'Shares': [45, 38, 29]
    })
    
    st.dataframe(top_content, use_container_width=True)


def render_sponsors_tab(results: Dict[str, Any]):
    """Render sponsor outreach tab"""
    
    st.markdown("### 💼 Sponsor Outreach")
    
    sponsors = results.get('sponsors', [])
    pitch_results = results.get('pitch_results', [])
    
    # Sponsors found
    st.markdown("#### 🎯 Perfect Sponsor Matches")
    
    if sponsors:
        for i, sponsor in enumerate(sponsors, 1):
            with st.expander(f"**{i}. {sponsor['brand_name']}** (Relevance: {sponsor.get('relevance', 0):.1f}/10)"):
                st.write(f"**Website:** {sponsor.get('website', 'N/A')}")
                st.write(f"**Description:** {sponsor.get('description', 'No description')}")
                st.write(f"**Contact:** {sponsor.get('contact_email', 'Finding email...')}")
    else:
        st.info("No sponsors found yet. Running next search cycle...")
    
    # Pitch status
    st.markdown("---")
    st.markdown("#### ✉️ Pitch Status")
    
    if pitch_results:
        for pitch in pitch_results:
            brand = pitch.get('brand', 'Unknown')
            status = pitch.get('status', 'pending')
            
            if status == 'success':
                st.success(f"✅ **{brand}**: Email sent successfully!")
                st.caption(f"Subject: {pitch.get('subject', 'N/A')}")
                st.caption(f"Sent: {pitch.get('sent_at', 'N/A')}")
            else:
                st.warning(f"⏳ **{brand}**: {pitch.get('status', 'Pending')}")
    else:
        st.info("📧 Sponsor pitches will be sent within 24 hours")
    
    # Revenue tracker
    st.markdown("---")
    st.markdown("#### 💰 Revenue Tracking")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Pitches Sent", len(pitch_results))
    
    with col2:
        st.metric("Responses", 0, delta="Pending")
    
    with col3:
        st.metric("Deals Closed", 0, delta="$0")


def render_strategy_tab(results: Dict[str, Any]):
    """Render AI strategy recommendations"""
    
    st.markdown("### 🧠 AI Strategy Insights")
    
    st.markdown("""
    VibeOS continuously learns from your content performance and provides strategic recommendations.
    """)
    
    # Recommendations
    st.markdown("#### 💡 Personalized Recommendations")
    
    recommendations = [
        "✅ Your engagement peaks at 12 PM and 8 PM - schedule content accordingly",
        "✅ Content with emojis gets 45% more engagement - keep using your signature style",
        "✅ Trending topics in your niche: AI automation, creator economy, productivity hacks",
        "✅ Your audience responds best to 'POV' format content - create more variations"
    ]
    
    for rec in recommendations:
        st.success(rec)
    
    # Performance score
    st.markdown("---")
    st.markdown("#### 📊 Optimization Score")
    
    score = 8.5
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Performance Score"},
        gauge={
            'axis': {'range': [0, 10]},
            'bar': {'color': "#667eea"},
            'steps': [
                {'range': [0, 5], 'color': "#f8d7da"},
                {'range': [5, 7.5], 'color': "#fff3cd"},
                {'range': [7.5, 10], 'color': "#d4edda"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 9
            }
        }
    ))
    
    st.plotly_chart(fig, use_container_width=True)


def render_settings_tab(results: Dict[str, Any]):
    """Render settings and configuration"""
    
    st.markdown("### ⚙️ Settings")
    
    # Vibe profile
    st.markdown("#### 🎨 Your Vibe Profile")
    
    vibe = results.get('vibe_profile', {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**Tone:** {vibe.get('tone', 'N/A').title()}")
        st.info(f"**Humor Style:** {vibe.get('humor_style', 'N/A').title()}")
    
    with col2:
        st.info(f"**Authenticity Score:** {vibe.get('authenticity_score', 0)}/10")
        st.info(f"**Complexity:** {vibe.get('complexity', 'N/A').title()}")
    
    # API configuration
    st.markdown("---")
    st.markdown("#### 🔑 API Configuration")
    
    st.text_input("Groq API Key", value="••••••••", type="password")
    st.text_input("Twitter API Key", value="••••••••", type="password")
    st.text_input("Gmail API Credentials", value="credentials.json", disabled=True)
    
    if st.button("Save Settings"):
        st.success("✅ Settings saved!")
    
    # Account info
    st.markdown("---")
    st.markdown("#### 👤 Account")
    
    st.write(f"**User ID:** `{st.session_state.user_id}`")
    st.write(f"**Niche:** {st.session_state.get('niche', 'N/A')}")
    st.write(f"**Goal:** {st.session_state.get('goal', 'N/A')}")


# ==================== MAIN APP ====================

def main():
    """Main application entry point"""
    
    init_session_state()
    render_header()
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🎯 Navigation")
        
        if st.session_state.workflow_run:
            st.success("✅ VibeOS Active")
            st.metric("Status", "Running")
        else:
            st.info("⏳ Ready to Launch")
        
        st.markdown("---")
        
        st.markdown("### 📚 Quick Links")
        st.markdown("[📖 Documentation](#)")
        st.markdown("[💬 Support](#)")
        st.markdown("[🎓 Tutorials](#)")
        
        st.markdown("---")
        
        if st.button("🔄 Reset Demo"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Main content
    if not st.session_state.onboarding_complete:
        render_onboarding()
    elif not st.session_state.workflow_run:
        render_workflow_execution()
    else:
        render_results_dashboard()


if __name__ == "__main__":
    main()
