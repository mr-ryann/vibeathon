"""
CreatorForge Nexus - Multi-Agent UI
A Streamlit interface to visualize the multi-agent system in action
"""

import streamlit as st
import json
from typing import Dict, Any
from agent_trendscout import run_trendscout, GraphState
from agent_forgemaster import run_forgemaster
from agent_engagebot import run_engagebot
from agent_dealhunter import run_dealhunter

# Page configuration
st.set_page_config(
    page_title="CreatorForge Nexus - Multi-Agent System",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .agent-status {
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: bold;
        display: inline-block;
        margin: 0.5rem 0;
    }
    .agent-running {
        background-color: #ffa500;
        color: #000;
    }
    .agent-complete {
        background-color: #4caf50;
        color: #fff;
    }
    .trend-card {
        background-color: #2d2d2d;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    .content-section {
        background-color: #1e1e1e;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #764ba2;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🤖 CreatorForge Nexus</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #888; font-size: 1.2rem;">Multi-Agent Content Creation System Powered by LangGraph</p>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.markdown("### 🎮 Control Panel")
    
    topic = st.text_input(
        "🎯 Topic to Research",
        value="Rabbit R1 vs Humane AI Pin",
        help="What topic should the agents research?"
    )
    
    user_vibe = st.text_area(
        "🎭 Creator Vibe",
        value="Sarcastic tech reviews with dark humor",
        help="Describe your content style/personality",
        height=80
    )
    
    st.markdown("---")
    st.markdown("### 🤖 Agent Pipeline")
    
    run_trendscout_enabled = st.checkbox("🕵️ TrendScout", value=True)
    run_forgemaster_enabled = st.checkbox("🔨 ForgeMaster", value=True)
    run_engagebot_enabled = st.checkbox("📢 EngageBot", value=True)
    run_dealhunter_enabled = st.checkbox("💰 DealHunter", value=True)
    
    st.markdown("---")
    
    run_button = st.button("🚀 Run Agent Pipeline", type="primary", use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 📊 Agent Status")
    st.markdown("""
    **🕵️ TrendScout** - The Eyes  
    Discovers viral trends
    
    **🔨 ForgeMaster** - The Hands  
    Creates content packs
    
    **📢 EngageBot** - The Mouth  
    Optimizes posting schedule
    
    **💰 DealHunter** - The Wallet  
    Finds brand sponsors
    """)

# Main content
if run_button:
    # Initialize state
    state = GraphState(
        topic=topic,
        user_vibe=user_vibe,
        scouted_trends=[],
        content_pack={},
        engage_plan={},
        deal_plan=[]
    )
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Agent 1: TrendScout
    if run_trendscout_enabled:
        status_text.markdown('<div class="agent-status agent-running">🕵️ TrendScout: Running...</div>', unsafe_allow_html=True)
        progress_bar.progress(25)
        
        with st.expander("🕵️ **TrendScout Agent** - Finding Trends...", expanded=True):
            with st.spinner("Searching the internet for viral trends..."):
                result = run_trendscout(state)
                state['scouted_trends'] = result['scouted_trends']
            
            st.success(f"✅ Found {len(state['scouted_trends'])} trending topics!")
            
            # Display trends
            for i, trend in enumerate(state['scouted_trends'], 1):
                st.markdown(f"""
                <div class="trend-card">
                    <h4>📌 Trend #{i}: {trend.get('title', 'N/A')}</h4>
                    <p><strong>🔗 Source:</strong> <a href="{trend.get('url', '#')}" target="_blank">{trend.get('url', 'N/A')}</a></p>
                    <p><strong>📝 Summary:</strong> {trend.get('summary', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
        
        progress_bar.progress(50)
    
    # Agent 2: ForgeMaster
    if run_forgemaster_enabled and state['scouted_trends']:
        status_text.markdown('<div class="agent-status agent-running">🔨 ForgeMaster: Running...</div>', unsafe_allow_html=True)
        progress_bar.progress(75)
        
        with st.expander("🔨 **ForgeMaster Agent** - Creating Content...", expanded=True):
            with st.spinner("Generating content pack..."):
                result = run_forgemaster(state)
                state['content_pack'] = result['content_pack']
            
            st.success("✅ Content pack generated successfully!")
            
            # Display content pack
            content = state['content_pack']
            
            # Script
            st.markdown("### 📝 Generated Script")
            st.markdown(f"""
            <div class="content-section">
                <pre style="white-space: pre-wrap; font-family: 'Courier New', monospace;">{content.get('script', 'N/A')}</pre>
            </div>
            """, unsafe_allow_html=True)
            
            # Social Post
            st.markdown("### 🐦 Social Media Post")
            st.markdown(f"""
            <div class="content-section">
                <p style="font-size: 1.1rem; line-height: 1.6;">{content.get('social_post', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Thumbnail
            st.markdown("### 🖼️ Generated Thumbnail")
            col1, col2 = st.columns([2, 1])
            
            with col1:
                try:
                    st.image(content.get('thumbnail_url', ''), caption="AI-Generated Thumbnail", width="stretch")
                except:
                    st.warning("⚠️ Thumbnail image failed to load")
            
            with col2:
                st.markdown("**Thumbnail Prompt:**")
                st.info(content.get('thumbnail_prompt', 'N/A'))
                st.markdown("**Image URL:**")
                st.code(content.get('thumbnail_url', 'N/A'), language=None)
        
        progress_bar.progress(75)
    
    # Agent 3: EngageBot
    if run_engagebot_enabled and state['content_pack']:
        status_text.markdown('<div class="agent-status agent-running">📢 EngageBot: Running...</div>', unsafe_allow_html=True)
        progress_bar.progress(85)
        
        with st.expander("📢 **EngageBot Agent** - Optimizing Schedule...", expanded=True):
            with st.spinner("Analyzing content and generating posting strategy..."):
                result = run_engagebot(state)
                state['engage_plan'] = result['engage_plan']
            
            st.success("✅ Posting schedule optimized!")
            
            # Display engagement plan
            plan = state['engage_plan']
            
            # Strategy Summary
            if 'strategy_summary' in plan:
                st.markdown("### 🎯 Overall Strategy")
                st.info(plan['strategy_summary'])
            
            # Predicted Reach
            if 'predicted_reach' in plan:
                st.markdown("### 📈 Predicted Reach")
                st.metric("Total Impressions", plan['predicted_reach'])
            
            # Posting Schedule
            st.markdown("### 📅 Posting Schedule")
            
            schedule_data = plan.get('plan', [])
            
            # Display as cards
            for i, post in enumerate(schedule_data, 1):
                st.markdown(f"""
                <div class="content-section">
                    <h4>#{i} - {post.get('platform', 'Unknown')} 📱</h4>
                    <p><strong>⏰ Time:</strong> {post.get('post_at', 'N/A')}</p>
                    <p><strong>📹 Content Type:</strong> {post.get('content_type', 'N/A')}</p>
                    <p><strong>💡 Strategy:</strong> {post.get('reason', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
        
        progress_bar.progress(100)
    
    # Agent 4: DealHunter
    if run_dealhunter_enabled:
        status_text.markdown('<div class="agent-status agent-running">💰 DealHunter: Running...</div>', unsafe_allow_html=True)
        progress_bar.progress(90)
        
        with st.expander("💰 **DealHunter Agent** - Finding Sponsors...", expanded=True):
            with st.spinner("Searching for brand partnership opportunities..."):
                result = run_dealhunter(state)
                state['deal_plan'] = result['deal_plan']
            
            st.success(f"✅ Found {len(state['deal_plan'])} potential sponsors!")
            
            # Display sponsorship opportunities
            st.markdown("### 🤝 Brand Sponsorship Opportunities")
            
            for i, deal in enumerate(state['deal_plan'], 1):
                st.markdown(f"""
                <div class="content-section">
                    <h4>#{i} - 🏢 {deal.get('company_name', 'N/A')}</h4>
                    <p><strong>🌐 Website:</strong> <a href="https://{deal.get('website', '#')}" target="_blank">{deal.get('website', 'N/A')}</a></p>
                    <p><strong>💡 Why This Sponsor:</strong> {deal.get('reason_for_sponsorship', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
        
        progress_bar.progress(100)
    
    # Final status
    status_text.markdown('<div class="agent-status agent-complete">✅ All Agents Complete!</div>', unsafe_allow_html=True)
    
    # Download results
    st.markdown("---")
    st.markdown("### 💾 Export Results")
    
    export_data = {
        "topic": state['topic'],
        "user_vibe": state['user_vibe'],
        "scouted_trends": state['scouted_trends'],
        "content_pack": state['content_pack'],
        "engage_plan": state['engage_plan'],
        "deal_plan": state['deal_plan']
    }
    
    st.download_button(
        label="📥 Download Complete Results (JSON)",
        data=json.dumps(export_data, indent=2),
        file_name=f"creator_nexus_{topic.replace(' ', '_')}.json",
        mime="application/json"
    )

else:
    # Welcome screen
    st.markdown("""
    ## 👋 Welcome to CreatorForge Nexus
    
    This is a **multi-agent system** built with LangGraph that creates viral content automatically.
    
    ### How it works:
    
    1. **🕵️ TrendScout** - Searches the internet for trending discussions and viral content
    2. **🔨 ForgeMaster** - Synthesizes trends into a complete content package
        - 📝 60-second script
        - 🐦 Social media post
        - 🖼️ AI-generated thumbnail
    3. **📢 EngageBot** - Creates intelligent posting schedule
        - 📅 Multi-platform timing
        - 🎯 Strategic reasoning
        - 📊 Reach predictions
    4. **💰 DealHunter** - Finds brand sponsorship opportunities
        - 🏢 Top 3 relevant companies
        - 🌐 Company websites
        - 💡 Detailed partnership reasoning
    
    ### Get Started:
    
    1. Enter your topic in the sidebar
    2. Define your creator vibe/style
    3. Click "🚀 Run Agent Pipeline"
    4. Watch the agents work their magic!
    
    ---
    
    **💡 Pro Tip:** Try different topics and vibes to see how the agents adapt!
    """)
    
    # Example showcase
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🎯 Example Topics")
        st.markdown("""
        - AI gadgets review
        - Gaming industry drama
        - Tech startup failures
        - Viral TikTok trends
        """)
    
    with col2:
        st.markdown("### 🎭 Example Vibes")
        st.markdown("""
        - Sarcastic tech reviewer
        - Wholesome motivational
        - Dramatic storytelling
        - Educational but fun
        """)
    
    with col3:
        st.markdown("### 🚀 Coming Soon")
        st.markdown("""
        -  DealMaker
        - 📊 Analytics Dashboard
        - 🎨 Visual Editor
        """)
