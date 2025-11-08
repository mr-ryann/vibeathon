"""
Streamlit UI for Nexus - Your AI Content Co-Founder

Intuitive workflow for hybrid human-AI content creation:
1. Generate viral scripts from trending topics
2. Shoot your video
3. Auto-clip and distribute shorts to platforms
"""

import streamlit as st
import json
from pathlib import Path
import time
from typing import Dict, Any
import os

# Import the Nexus core architecture
from nexus_core import run_nexus_phase1, run_nexus_phase2, db
from agent_ripple import fetch_viral_trends_serper


# ==================== PAGE CONFIG ====================

st.set_page_config(
    page_title="Nexus - AI Content Co-Founder",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ==================== CUSTOM CSS ====================

st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    
    .tagline {
        text-align: center;
        font-size: 1.4rem;
        color: #666;
        margin-bottom: 3rem;
        font-weight: 500;
    }
    
    .workflow-step {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        border: 2px solid #e0e0e0;
        margin: 1.5rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .workflow-step.active {
        border: 2px solid #667eea;
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
    }
    
    .workflow-step.completed {
        border: 2px solid #28a745;
        background: #f0fff4;
    }
    
    .step-number {
        display: inline-block;
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 50%;
        text-align: center;
        line-height: 40px;
        font-weight: bold;
        font-size: 1.2rem;
        margin-right: 1rem;
    }
    
    .step-number.completed {
        background: #28a745;
    }
    
    .script-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 5px solid #667eea;
    }
    
    .trend-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .trend-card:hover {
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
        transform: translateX(5px);
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        border: 2px solid #e0e0e0;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #667eea;
    }
    
    .metric-label {
        color: #666;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)


# ==================== SESSION STATE ====================

def init_session_state():
    """Initialize session state variables"""
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 'trends'  # trends, script, shoot, shorts
    
    if 'trends_data' not in st.session_state:
        st.session_state.trends_data = None
    
    if 'script_state' not in st.session_state:
        st.session_state.script_state = None
    
    if 'shorts_state' not in st.session_state:
        st.session_state.shorts_state = None
    
    if 'auto_fetch_trends' not in st.session_state:
        st.session_state.auto_fetch_trends = True
    
    if 'selected_trend' not in st.session_state:
        st.session_state.selected_trend = None
    
    if 'user_niche' not in st.session_state:
        st.session_state.user_niche = ''
    
    if 'user_vibe' not in st.session_state:
        st.session_state.user_vibe = ''
    
    if 'user_growth_goal' not in st.session_state:
        st.session_state.user_growth_goal = ''
    
    if 'trends_fetched' not in st.session_state:
        st.session_state.trends_fetched = False
    
    if 'promotions_data' not in st.session_state:
        st.session_state.promotions_data = []


# ==================== HEADER ====================

def render_header():
    """Render the main header"""
    st.markdown('<h1 class="main-header">🌊 Nexus</h1>', unsafe_allow_html=True)
    st.markdown('<p class="tagline">Your AI Content Co-Founder</p>', unsafe_allow_html=True)
    
    # Progress indicator
    steps = ['📊 Trends', '✍️ Script', '🎬 Shoot', '🚀 Shorts']
    step_keys = ['trends', 'script', 'shoot', 'shorts']
    current_idx = step_keys.index(st.session_state.current_step)
    
    cols = st.columns(4)
    for idx, (col, step_name) in enumerate(zip(cols, steps)):
        with col:
            if idx < current_idx:
                st.markdown(f"<div style='text-align: center; color: #28a745; font-weight: bold;'>{step_name} ✓</div>", unsafe_allow_html=True)
            elif idx == current_idx:
                st.markdown(f"<div style='text-align: center; color: #667eea; font-weight: bold; font-size: 1.2rem;'>{step_name}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='text-align: center; color: #ccc;'>{step_name}</div>", unsafe_allow_html=True)
    
    st.markdown("---")


# ==================== STEP 1: VIRAL TRENDS ====================

def render_trends_step():
    """Render the viral trends discovery step"""
    st.markdown('<div class="workflow-step active">', unsafe_allow_html=True)
    st.markdown('<span class="step-number">1</span> **Discover Viral Trends**', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # User inputs: Mandatory niche/vibe + Optional growth goal
    st.markdown("### 🎯 Tell us about your content")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        niche_input = st.text_input(
            "Your Content Niche/Vibe (Required)",
            placeholder="e.g., Tech reviews, AI news, Fitness tips, Finance",
            help="What kind of content do you create? This is your niche or style.",
            key="niche_input",
            value=st.session_state.get('user_niche', '')
        )
        
        if niche_input and niche_input != st.session_state.get('user_niche', ''):
            st.session_state.user_niche = niche_input
    
    with col2:
        growth_goal = st.text_input(
            "Growth Goal (Optional)",
            placeholder="e.g., 2k likes in 1 day",
            help="Any specific engagement or growth targets?",
            key="growth_goal",
            value=st.session_state.get('user_growth_goal', '')
        )
        
        if growth_goal:
            st.session_state.user_growth_goal = growth_goal
    
    # Auto-fetch toggle and manual button
    col1, col2 = st.columns([1, 1])
    
    with col1:
        auto_fetch = st.toggle(
            "🔄 Auto-fetch trends",
            value=st.session_state.auto_fetch_trends,
            help="Automatically fetch trends when you enter your niche"
        )
        st.session_state.auto_fetch_trends = auto_fetch
    
    with col2:
        fetch_manually = st.button(
            "🔍 Fetch Viral Trends Now",
            use_container_width=True,
            type="primary",
            disabled=not niche_input
        )
    
    # Fetch trends logic - Reload on every button click!
    should_fetch = False
    
    if fetch_manually and niche_input:
        should_fetch = True
        # Always reload when button is clicked (removed trends_fetched flag)
    elif auto_fetch and niche_input and not st.session_state.get('trends_fetched', False):
        should_fetch = True
        st.session_state.trends_fetched = True
    
    if should_fetch:
        with st.spinner("🌊 Scanning the internet for viral trends in your niche..."):
            # Build search query from niche + growth goal
            search_query = niche_input
            if growth_goal:
                search_query = f"{niche_input} viral trending {growth_goal}"
            
            # Try Serper first, fallback to Gemini simulation
            trends = fetch_viral_trends_serper(search_query, num_results=10)
            
            if not trends:
                st.info("💡 Using AI to simulate trending content (Google Serper API not configured)")
                # Fallback will happen in agent_ripple
            
            st.session_state.trends_data = {
                'niche': niche_input,
                'growth_goal': growth_goal,
                'trends': trends if trends else []
            }
    
    # Display trends
    if st.session_state.trends_data and st.session_state.trends_data.get('trends'):
        st.success(f"✅ Found {len(st.session_state.trends_data['trends'])} viral trends!")
        
        st.markdown("---")
        st.markdown("### 📊 Trending Topics in Your Niche")
        st.caption("Click 'Use This' to generate a script based on a trend")
        
        for idx, trend in enumerate(st.session_state.trends_data['trends']):
            with st.container():
                st.markdown(f'<div class="trend-card">', unsafe_allow_html=True)
                
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    st.markdown(f"**{trend.get('title', 'No title')}**")
                    st.caption(trend.get('summary', 'No summary')[:200] + "...")
                    if trend.get('url'):
                        st.caption(f"🔗 {trend.get('url')}")
                
                with col2:
                    if st.button("Use This", key=f"trend_{idx}", type="secondary"):
                        st.session_state.selected_trend = trend
                        st.session_state.current_step = 'script'
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    elif st.session_state.trends_data and not st.session_state.trends_data.get('trends'):
        st.warning("⚠️ No trends found. Try a different niche or check your API configuration.")
    elif niche_input and not st.session_state.get('trends_fetched', False):
        st.info("👆 Click 'Fetch Viral Trends Now' or enable auto-fetch to discover trending topics")


# ==================== STEP 2: GENERATE SCRIPT ====================

def render_script_step():
    """Render the script generation step"""
    st.markdown('<div class="workflow-step completed">', unsafe_allow_html=True)
    st.markdown('<span class="step-number completed">1</span> **Viral Trends** ✓', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="workflow-step active">', unsafe_allow_html=True)
    st.markdown('<span class="step-number">2</span> **Generate Your Script**', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Navigation: Back to trends
    if st.button("⬅️ Back to Trends", key="nav_back_to_trends"):
        st.session_state.current_step = 'trends'
        st.session_state.selected_trend = None
        st.rerun()
    
    st.markdown("---")
    
    # Show selected trend
    if st.session_state.selected_trend:
        st.markdown("### 📊 Selected Viral Trend")
        st.info(f"**{st.session_state.selected_trend.get('title')}**")
        if st.session_state.selected_trend.get('summary'):
            st.caption(st.session_state.selected_trend.get('summary')[:300] + "...")
    
    # Get niche and growth goal from session state (set in step 1)
    niche = st.session_state.get('user_niche', '')
    growth_goal = st.session_state.get('user_growth_goal', '')
    topic = st.session_state.selected_trend.get('title', '') if st.session_state.selected_trend else ''
    
    st.markdown("---")
    st.markdown("### 🎨 Your Content Style")
    st.caption(f"**Niche:** {niche}")
    if growth_goal:
        st.caption(f"**Growth Goal:** {growth_goal}")
    
    # Only ask for vibe/style - everything else comes from step 1
    vibe = st.text_input(
        "Your Vibe/Style (Required)",
        placeholder="e.g., Sarcastic and honest, Energetic and motivational, Calm and educational",
        help="Describe your unique voice and presentation style",
        key="user_vibe_input"
    )
    
    st.markdown("---")
    
    # Generate button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate = st.button(
            "🤖 Generate Script with AI",
            use_container_width=True,
            type="primary",
            disabled=not vibe
        )
    
    if generate:
        if not vibe:
            st.error("⚠️ Please describe your vibe/style")
        else:
            with st.spinner("🌊 ripple is analyzing viral patterns..."):
                time.sleep(0.5)
            
            with st.spinner("✍️ quill is crafting your script..."):
                try:
                    # Build goals from growth_goal if provided
                    goals = f"Growth Goal: {growth_goal}" if growth_goal else ""
                    
                    # Run script generation with data from step 1
                    state = run_nexus_phase1(
                        topic=topic,
                        niche=niche,
                        user_vibe=vibe,
                        goals=goals
                    )
                    
                    if state.get('error'):
                        st.error(f"❌ Error: {state['error']}")
                    elif state.get('generated_script'):
                        st.session_state.script_state = state
                        st.session_state.user_vibe = vibe  # Save for later
                        
                        # Generate promotions immediately after script
                        with st.spinner("🤝 envoy is finding sponsor opportunities for your script..."):
                            try:
                                from agent_envoy import run_envoy
                                promo_state = run_envoy(state)
                                st.session_state.promotions_data = promo_state.get('deal_plan', [])
                            except Exception as e:
                                st.warning(f"⚠️ Could not fetch promotions: {str(e)}")
                                st.session_state.promotions_data = []
                        
                        st.success("✅ Script generated!")
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Failed to generate script")
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    # Display generated script
    if st.session_state.script_state:
        script = st.session_state.script_state.get('generated_script', {})
        
        st.markdown("---")
        st.markdown("### 📜 Your AI-Generated Script")
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{script.get("estimated_duration", "15s")}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Duration</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{script.get("shot_count", 1)}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Shots</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{script.get("difficulty", "Easy").title()}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Difficulty</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            props_count = len(script.get('props_needed', []))
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{props_count}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Props</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Script content
        st.markdown('<div class="script-card">', unsafe_allow_html=True)
        
        st.markdown("#### 🎬 Full Script")
        st.markdown(f"```\n{script.get('full_script', '')}\n```")
        
        # Expandable breakdown
        with st.expander("📋 See Scene Breakdown"):
            st.markdown(f"**🎯 Intro (0-3s):**\n{script.get('intro', '')}")
            st.markdown(f"**📖 Body (3-12s):**\n{script.get('body', '')}")
            st.markdown(f"**✨ Outro (12-15s):**\n{script.get('outro', '')}")
        
        # Props
        if script.get('props_needed'):
            with st.expander("🎒 Props Checklist"):
                for prop in script.get('props_needed', []):
                    st.checkbox(prop, key=f"prop_{prop}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Download button
        script_text = f"""NEXUS SCRIPT
====================
Topic: {st.session_state.script_state.get('topic', 'Untitled')}
Niche: {st.session_state.script_state.get('niche', '')}
Vibe: {st.session_state.script_state.get('user_vibe', '')}

FULL SCRIPT:
{script.get('full_script', '')}

BREAKDOWN:
----------
INTRO (0-3s):
{script.get('intro', '')}

BODY (3-12s):
{script.get('body', '')}

OUTRO (12-15s):
{script.get('outro', '')}

PRODUCTION INFO:
----------------
Duration: {script.get('estimated_duration', '15 seconds')}
Difficulty: {script.get('difficulty', 'Easy')}
Shots: {script.get('shot_count', 1)}
Props: {', '.join(script.get('props_needed', []))}

---
Generated by Nexus AI
"""
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="📥 Download Script",
                data=script_text,
                file_name=f"nexus_script_{st.session_state.script_state.get('topic', 'untitled').replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col2:
            if st.button("🎬 I've Shot the Video - Upload It", use_container_width=True, type="primary"):
                st.session_state.current_step = 'shoot'
                st.rerun()
        
        # Display available promotions
        if st.session_state.get('promotions_data'):
            st.markdown("---")
            st.markdown("### 🤝 Available Sponsor Opportunities")
            st.caption("Based on your script, here are potential sponsors you can reach out to:")
            
            promotions = st.session_state.promotions_data
            
            for idx, promo in enumerate(promotions):
                with st.expander(f"💼 {promo.get('company_name', 'Sponsor')} - {promo.get('fit_score', 'N/A')} Match", expanded=(idx == 0)):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**Company:** {promo.get('company_name', 'N/A')}")
                        st.markdown(f"**Website:** {promo.get('website', 'N/A')}")
                        st.markdown(f"**Why They Fit:** {promo.get('why_good_fit', 'N/A')}")
                    
                    with col2:
                        st.markdown(f"**Match Score:** {promo.get('fit_score', 'N/A')}")
                        st.markdown(f"**Contact:** {promo.get('contact_email', 'Research needed')}")
                    
                    st.markdown("---")
                    st.markdown("**📧 Custom Pitch Email (Ready to Send):**")
                    
                    email_body = promo.get('pitch_template', '').replace('\\n', '\n')
                    st.text_area(
                        "Email content",
                        value=email_body,
                        height=300,
                        key=f"promo_email_{idx}",
                        help="Copy this email and send to the sponsor"
                    )
                    
                    # Copy button
                    if st.button(f"📋 Copy Email for {promo.get('company_name', 'Sponsor')}", key=f"copy_promo_{idx}"):
                        st.code(email_body, language=None)
                        st.success("✅ Email text displayed above - you can now copy it!")
        
        st.markdown("---")


# ==================== STEP 3: UPLOAD VIDEO ====================

def render_shoot_step():
    """Render the video upload step"""
    # Navigation: Back to script
    if st.button("⬅️ Back to Script", key="nav_back_to_script"):
        st.session_state.current_step = 'script'
        st.rerun()
    
    st.markdown("---")
    
    # Previous steps completed
    st.markdown('<div class="workflow-step completed">', unsafe_allow_html=True)
    st.markdown('<span class="step-number completed">1</span> **Viral Trends** ✓', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="workflow-step completed">', unsafe_allow_html=True)
    st.markdown('<span class="step-number completed">2</span> **Script Generated** ✓', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="workflow-step active">', unsafe_allow_html=True)
    st.markdown('<span class="step-number">3</span> **Upload Your Video**', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Shooting tips
    st.info("""
    📱 **Shooting Tips:**
    - Use your smartphone camera (portrait mode)
    - Good lighting (natural light works best)
    - Clear audio (quiet environment or use lapel mic)
    - Follow the script naturally - be yourself!
    - Multiple takes are fine - upload your best one
    """)
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Upload your video",
        type=['mp4', 'mov', 'avi', 'mkv'],
        help="Upload the video you shot using the script",
        key="video_upload"
    )
    
    if uploaded_file is not None:
        # Save uploaded file
        video_path = Path("uploads") / uploaded_file.name
        video_path.parent.mkdir(exist_ok=True)
        
        with open(video_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Show video preview
        st.video(str(video_path))
        
        file_size_mb = uploaded_file.size / (1024 * 1024)
        st.success(f"✅ Video uploaded: **{uploaded_file.name}** ({file_size_mb:.1f} MB)")
        
        st.markdown("---")
        
        if st.button("🚀 Clip Shorts & Automate Distribution", use_container_width=True, type="primary"):
            with st.spinner("💓 pulse is clipping your video into shorts..."):
                time.sleep(1)
            
            with st.spinner("🤝 envoy is finding sponsor opportunities..."):
                try:
                    # Run video processing
                    state = run_nexus_phase2(
                        state=st.session_state.script_state,
                        video_path=str(video_path)
                    )
                    
                    if state.get('error'):
                        st.error(f"❌ Error: {state['error']}")
                    else:
                        st.session_state.shorts_state = state
                        st.session_state.current_step = 'shorts'
                        st.success("✅ Shorts created!")
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")


# ==================== STEP 4: SHORTS & DISTRIBUTION ====================

def render_shorts_step():
    """Render the final results step"""
    # All previous steps completed
    for i, label in enumerate(['Viral Trends', 'Script Generated', 'Video Uploaded'], 1):
        st.markdown('<div class="workflow-step completed">', unsafe_allow_html=True)
        st.markdown(f'<span class="step-number completed">{i}</span> **{label}** ✓', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="workflow-step completed">', unsafe_allow_html=True)
    st.markdown('<span class="step-number completed">4</span> **Shorts Ready!** ✓', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("# 🎉 Your Content is Ready!")
    
    state = st.session_state.shorts_state
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        clips = [c for c in state.get('clipped_shorts', []) if not c.get('is_mock')]
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{len(clips)}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Shorts Created</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        posted = sum(1 for c in state.get('clipped_shorts', []) if c.get('posted'))
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{posted}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Auto-Posted</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        sponsors = state.get('deal_plan', [])
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{len(sponsors)}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Sponsors Found</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tabs for organized results
    tab1, tab2, tab3 = st.tabs(["🎬 Shorts", "💰 Sponsors", "📊 Analytics"])
    
    with tab1:
        st.markdown("### Your Clipped Shorts")
        
        for i, clip in enumerate(state.get('clipped_shorts', []), 1):
            if clip.get('is_mock'):
                continue
            
            with st.expander(f"📹 Short #{i}: {clip.get('filename', 'N/A')}", expanded=True):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Duration", f"{clip.get('duration', 0):.1f}s")
                
                with col2:
                    st.metric("Start", f"{clip.get('start_time', 0):.1f}s")
                
                with col3:
                    status = "Posted ✅" if clip.get('posted') else "Ready to post"
                    st.metric("Status", status)
                
                # Show platform-specific upload status
                if clip.get('youtube_upload'):
                    youtube_result = clip['youtube_upload']
                    if youtube_result.get('success'):
                        st.success(f"✅ Uploaded to YouTube: [{youtube_result.get('title')}]({youtube_result.get('url')})")
                    else:
                        st.info(f"💡 YouTube upload failed: {youtube_result.get('error', 'Unknown error')}")
                
                if clip.get('posted_twitter'):
                    st.success("✅ Posted to Twitter/X")
                elif 'posted_twitter' in clip:
                    st.info("💡 Twitter posting skipped (no API keys configured)")
                
                if os.path.exists(clip.get('path', '')):
                    st.video(clip.get('path'))
                    
                    # Download button
                    with open(clip.get('path'), 'rb') as f:
                        st.download_button(
                            label=f"📥 Download Short #{i}",
                            data=f.read(),
                            file_name=clip.get('filename'),
                            mime="video/mp4",
                            use_container_width=True
                        )
    
    with tab2:
        st.markdown("### Sponsor Opportunities")
        
        for i, deal in enumerate(state.get('deal_plan', []), 1):
            with st.expander(f"🏢 {i}. {deal.get('company_name', 'N/A')} - {deal.get('partnership_type', 'N/A')}", expanded=False):
                st.markdown(f"**🌐 Website:** [{deal.get('website', 'N/A')}](https://{deal.get('website', '')})")
                st.markdown(f"**💡 Why Sponsor:** {deal.get('reason_for_sponsorship', 'N/A')}")
                
                st.markdown("---")
                st.markdown("**📧 Pitch Email (Ready to Send):**")
                
                email_body = deal.get('pitch_template', '').replace('\\n', '\n')
                st.text_area(
                    "Email content",
                    value=email_body,
                    height=300,
                    key=f"email_{i}",
                    help="Copy this email and send to the sponsor"
                )
                
                # Copy to clipboard button (simulated)
                st.code(email_body, language=None)
    
    with tab3:
        st.markdown("### Engagement Plan")
        
        plan = state.get('engage_plan', {})
        
        st.markdown(f"**Strategy:** {plan.get('strategy', 'N/A')}")
        st.markdown(f"**Platforms:** {', '.join(plan.get('platforms', []))}")
        
        st.markdown("#### Next Steps:")
        for step in plan.get('next_steps', []):
            st.markdown(f"- {step}")
    
    # Action buttons
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Create New Content", use_container_width=True, type="primary"):
            # Reset everything
            st.session_state.current_step = 'trends'
            st.session_state.trends_data = None
            st.session_state.script_state = None
            st.session_state.shorts_state = None
            st.session_state.selected_trend = None
            st.rerun()
    
    with col2:
        if st.button("📊 View All Projects", use_container_width=True):
            st.info("Project history coming soon!")


# ==================== SIDEBAR ====================

def render_sidebar():
    """Render sidebar with settings and recent projects"""
    with st.sidebar:
        st.markdown("## ⚙️ Settings")
        
        # Serper API status
        serper_key = os.getenv("GOOGLE_SERPER_API_KEY")
        if serper_key:
            st.success("✅ Google Serper connected")
        else:
            st.warning("⚠️ Google Serper not configured")
            st.caption("Using AI-simulated trends instead")
        
        st.markdown("---")
        st.markdown("## 📚 Recent Scripts")
        
        try:
            recent_scripts = db.get_recent_scripts(limit=5)
            
            if recent_scripts:
                for script in recent_scripts:
                    with st.expander(f"{script['topic'][:25]}...", expanded=False):
                        st.caption(f"**Niche:** {script['niche']}")
                        st.caption(f"**Created:** {script['created_at'][:16]}")
            else:
                st.info("No scripts yet!")
        
        except Exception:
            st.caption("Database not initialized")


# ==================== MAIN APP ====================

def main():
    """Main application router"""
    init_session_state()
    render_header()
    
    # Route to current step
    if st.session_state.current_step == 'trends':
        render_trends_step()
    elif st.session_state.current_step == 'script':
        render_script_step()
    elif st.session_state.current_step == 'shoot':
        render_shoot_step()
    elif st.session_state.current_step == 'shorts':
        render_shorts_step()
    
    # Sidebar
    render_sidebar()


if __name__ == "__main__":
    main()
