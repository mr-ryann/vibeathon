"""
CreatorForge Nexus - LangGraph-Powered Multi-Agent UI

This Streamlit interface now uses the official NexusCore LangGraph workflow
instead of calling agents directly. This demonstrates the full LangGraph implementation.
"""

import streamlit as st
import json
from typing import Dict, Any
from urllib.parse import quote_plus

# Import the NexusCore LangGraph application
from nexus_core import run_nexus, run_nexus_streaming, GraphState

# --- Actionable Agents Helper Functions ---

def create_mailto_link(pitch_template: str, company_name: str) -> str:
    """
    Creates a mailto: link that opens the user's native email client
    with pre-filled sponsor pitch email.
    
    Args:
        pitch_template: The personalized pitch email body
        company_name: The sponsor company name
    
    Returns:
        Complete mailto: URL with encoded subject and body
    """
    # Generate mock sponsor email
    clean_company = company_name.lower().replace(' ', '').replace(',', '')
    sponsor_email = f"partnerships@{clean_company}.com"
    
    # Create subject line
    subject = f"Creator Collab Opportunity: AI Content x {company_name}"
    
    # URL-encode subject and body for mailto link
    encoded_subject = quote_plus(subject)
    encoded_body = quote_plus(pitch_template)
    
    # Construct mailto link
    mailto_link = f"mailto:{sponsor_email}?subject={encoded_subject}&body={encoded_body}"
    
    return mailto_link

# Page configuration
st.set_page_config(
    page_title="CreatorForge Nexus - LangGraph System",
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
    .langgraph-badge {
        background-color: #667eea;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 0.5rem 0;
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
    }
    .pitch-button {
        display: inline-block;
        padding: 0.75rem 1.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-decoration: none;
        border-radius: 8px;
        font-weight: bold;
        text-align: center;
        transition: transform 0.2s;
    }
    .pitch-button:hover {
        transform: scale(1.05);
        text-decoration: none;
        color: white;
    }
    .copy-button {
        background-color: #4caf50;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        border: none;
        cursor: pointer;
        font-weight: bold;
    }
        border-left: 4px solid #764ba2;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🤖 CreatorForge Nexus</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #888; font-size: 1.2rem;">LangGraph-Powered Multi-Agent Content Creation System</p>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center;"><span class="langgraph-badge">⚡ Powered by LangGraph</span></div>', unsafe_allow_html=True)
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
    st.markdown("### 🧠 NexusCore Pipeline")
    st.info("Using LangGraph StateGraph to orchestrate all agents")
    
    st.markdown("**Agent Flow:**")
    st.markdown("""
    ```
    TrendScout
        ↓
    ForgeMaster
        ↓
    EngageBot
        ↓
    DealHunter
        ↓
    Complete!
    ```
    """)
    
    st.markdown("---")
    
    run_button = st.button("🚀 Run NexusCore", type="primary", use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 📊 System Info")
    st.markdown("""
    **Architecture:** LangGraph StateGraph  
    **Agents:** 4 active  
    **Processing:** Sequential  
    **State Management:** GraphState TypedDict
    """)

# Main content
if run_button:
    # Bundle 4.2: Input validation
    if len(topic.strip()) < 3:
        st.warning("⚠️ Please enter a topic with at least 3 characters")
        st.stop()
    
    if len(user_vibe.strip()) < 3:
        st.warning("⚠️ Please enter a creator vibe with at least 3 characters")
        st.stop()
    
    # Bundle 4.1: Real-time progress with st.status()
    with st.status("🚀 Running NexusCore Pipeline...", expanded=True) as status:
        final_state = None
        
        try:
            # Stream progress updates
            for update in run_nexus_streaming(topic=topic, user_vibe=user_vibe):
                if isinstance(update, str):
                    # Progress message
                    status.update(label=update)
                    st.write(update)
                else:
                    # Final state received
                    final_state = update
            
            status.update(label="✅ Pipeline Complete!", state="complete")
            
            # Check for errors
            if final_state and final_state.get('error'):
                st.error(f"❌ Pipeline Error: {final_state['error']}")
                st.stop()
            
            # Display results in expandable sections
            st.success("🎉 LangGraph pipeline executed successfully!")
            
            # Agent 1 Results: TrendScout
            with st.expander("🕵️ **Agent 1: TrendScout** - Research Results", expanded=True):
                st.markdown("**State Update:** `scouted_trends` added to GraphState")
                
                trends = final_state.get('scouted_trends', [])
                st.metric("Trends Found", len(trends))
                
                for i, trend in enumerate(trends, 1):
                    st.markdown(f"""
                    <div class="trend-card">
                        <h4>📌 Trend #{i}: {trend.get('title', 'N/A')}</h4>
                        <p><strong>🔗 Source:</strong> <a href="{trend.get('url', '#')}" target="_blank">{trend.get('url', 'N/A')}</a></p>
                        <p><strong>📝 Summary:</strong> {trend.get('summary', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Agent 2 Results: ForgeMaster
            with st.expander("🔨 **Agent 2: ForgeMaster** - Content Package", expanded=True):
                st.markdown("**State Update:** `content_pack` added to GraphState")
                
                content = final_state.get('content_pack', {})
                
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
            
            # Agent 3 Results: EngageBot
            with st.expander("📢 **Agent 3: EngageBot** - Distribution Strategy", expanded=True):
                st.markdown("**State Update:** `engage_plan` added to GraphState")
                
                plan = final_state.get('engage_plan', {})
                
                # Strategy Summary
                if 'strategy_summary' in plan:
                    st.markdown("### 🎯 Overall Strategy")
                    st.info(plan['strategy_summary'])
                
                # Predicted Reach
                col1, col2 = st.columns(2)
                with col1:
                    if 'predicted_reach' in plan:
                        st.metric("Predicted Reach", plan['predicted_reach'])
                with col2:
                    schedule_data = plan.get('plan', [])
                    st.metric("Posting Slots", len(schedule_data))
                
                # Special Instagram Preview Section
                st.markdown("### 📸 Instagram Post Preview")
                instagram_post = None
                for post in schedule_data:
                    if 'instagram' in post.get('platform', '').lower():
                        instagram_post = post
                        break
                
                if instagram_post:
                    # Show thumbnail image
                    thumbnail_url = final_state.get('content_pack', {}).get('thumbnail_url', '')
                    if thumbnail_url:
                        st.image(thumbnail_url, caption="Your Video Thumbnail", use_container_width=True)
                    
                    # Show Instagram caption in text area for easy copying
                    if 'platform_specific_text' in instagram_post:
                        caption = instagram_post['platform_specific_text']
                        st.text_area(
                            "📱 Instagram Caption (Ready to Copy):",
                            value=caption,
                            height=150,
                            key="instagram_caption"
                        )
                        
                        # Action buttons
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.download_button(
                                label="📋 Download Caption",
                                data=caption,
                                file_name="instagram_caption.txt",
                                mime="text/plain",
                                key="instagram_download"
                            )
                        with col_b:
                            # Show posting time
                            st.info(f"⏰ Best time to post: {instagram_post.get('post_at', 'N/A')}")
                    
                    st.markdown("---")
                
                # Full Posting Schedule
                st.markdown("### 📅 Complete Posting Schedule")
                
                for i, post in enumerate(schedule_data, 1):
                    platform_emoji = {
                        'YouTube': '🎥',
                        'TikTok': '🎵',
                        'Twitter': '🐦',
                        'Instagram': '📸'
                    }.get(post.get('platform', ''), '📱')
                    
                    st.markdown(f"""
                    <div class="content-section">
                        <h4>#{i} - {platform_emoji} {post.get('platform', 'Unknown')}</h4>
                        <p><strong>⏰ Time:</strong> {post.get('post_at', 'N/A')}</p>
                        <p><strong>📹 Content Type:</strong> {post.get('content_type', 'N/A')}</p>
                        <p><strong>💡 Strategy:</strong> {post.get('reason', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Bundle 3.2: Display platform-specific ready-to-paste content
                    if 'platform_specific_text' in post:
                        st.markdown("**✍️ Ready-to-Paste Content:**")
                        st.text_area(
                            f"{post.get('platform', 'Platform')} Post:",
                            value=post['platform_specific_text'],
                            height=120,
                            key=f"platform_text_{i}"
                        )
                        
                        # Download button for easy copying
                        st.download_button(
                            label=f"📋 Download {post.get('platform', 'Platform')} Post",
                            data=post['platform_specific_text'],
                            file_name=f"{post.get('platform', 'post').replace(' ', '_').lower()}_post.txt",
                            mime="text/plain",
                            key=f"platform_post_{i}"
                        )
                    
                    if i < len(schedule_data):
                        st.markdown("---")
            
            # Agent 4 Results: DealHunter
            with st.expander("💰 **Agent 4: DealHunter** - Brand Sponsorship Opportunities", expanded=True):
                st.markdown("**State Update:** `deal_plan` added to GraphState (with pitch templates)")
                
                deals = final_state.get('deal_plan', [])
                
                if deals:
                    st.metric("Potential Sponsors Found", len(deals))
                    
                    st.markdown("### 🤝 Brand Partnership Opportunities")
                    
                    for i, deal in enumerate(deals, 1):
                        with st.container():
                            st.markdown(f"""
                            <div class="content-section">
                                <h4>#{i} - 🏢 {deal.get('company_name', 'N/A')}</h4>
                                <p><strong>🌐 Website:</strong> <a href="https://{deal.get('website', '#')}" target="_blank">{deal.get('website', 'N/A')}</a></p>
                                <p><strong>💡 Why This Sponsor:</strong> {deal.get('reason_for_sponsorship', 'N/A')}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Bundle 3.1: Display ready-to-send pitch template
                            if 'pitch_template' in deal:
                                st.markdown("**📧 Ready-to-Send Pitch Email:**")
                                st.text_area(
                                    "Pitch Preview:",
                                    value=deal['pitch_template'],
                                    height=200,
                                    key=f"pitch_text_{i}"
                                )
                                
                                # Create mailto link for instant email opening
                                mailto_link = create_mailto_link(
                                    pitch_template=deal['pitch_template'],
                                    company_name=deal.get('company_name', 'Sponsor')
                                )
                                
                                # Actionable button - opens email client
                                st.markdown(
                                    f'<a href="{mailto_link}" class="pitch-button" target="_blank">📧 Pitch {deal.get("company_name", "Sponsor")} Now</a>',
                                    unsafe_allow_html=True
                                )
                                
                                st.markdown("")  # Spacing
                            
                            st.markdown("---")
                else:
                    st.warning("No sponsorship opportunities found")
            
            # Final GraphState
            with st.expander("🧬 **Complete GraphState** - LangGraph Output"):
                st.markdown("This is the final state object returned by the LangGraph workflow:")
                st.json({
                    "topic": final_state.get('topic'),
                    "user_vibe": final_state.get('user_vibe'),
                    "scouted_trends": f"{len(final_state.get('scouted_trends', []))} trends",
                    "content_pack": "✅ Generated",
                    "engage_plan": "✅ Generated",
                    "deal_plan": f"{len(final_state.get('deal_plan', []))} sponsors",
                    "total_fields": len(final_state)
                })
            
            # Download results
            st.markdown("---")
            st.markdown("### 💾 Export GraphState")
            
            export_data = dict(final_state)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    label="📥 Download Complete GraphState (JSON)",
                    data=json.dumps(export_data, indent=2),
                    file_name=f"nexus_state_{topic.replace(' ', '_')}.json",
                    mime="application/json"
                )
            
            with col2:
                st.metric("Total Processing Time", "~40 seconds")
        
        except Exception as e:
            st.error(f"❌ Error running NexusCore: {str(e)}")
            st.exception(e)

else:
    # Welcome screen
    st.markdown("""
    ## 👋 Welcome to CreatorForge Nexus
    
    This is a **LangGraph-powered multi-agent system** that creates viral content automatically.
    
    ### 🏗️ Architecture:
    
    Built with **LangGraph StateGraph**, this system uses a proper graph-based workflow instead of 
    simple sequential calls. The `NexusCore` orchestrates all agents through a compiled StateGraph.
    
    ### 📊 The Workflow:
    
    ```python
    workflow = StateGraph(GraphState)
    workflow.add_node("trendscout", run_trendscout)
    workflow.add_node("forgemaster", run_forgemaster)
    workflow.add_node("engagebot", run_engagebot)
    workflow.add_node("dealhunter", run_dealhunter)
    
    workflow.set_entry_point("trendscout")
    workflow.add_edge("trendscout", "forgemaster")
    workflow.add_edge("forgemaster", "engagebot")
    workflow.add_edge("engagebot", "dealhunter")
    workflow.add_edge("dealhunter", END)
    
    app = workflow.compile()
    ```
    
    ### 🚀 How it works:
    
    1. **🕵️ TrendScout** - Searches for viral trends → Updates `scouted_trends` in GraphState
    2. **🔨 ForgeMaster** - Creates content package → Updates `content_pack` in GraphState
    3. **📢 EngageBot** - Optimizes posting schedule → Updates `engage_plan` in GraphState
    4. **💰 DealHunter** - Finds brand sponsors → Updates `deal_plan` in GraphState
    
    All agents share the same `GraphState` object, making this a true multi-agent system!
    
    ### ✨ Key Features:
    
    - ✅ **Real LangGraph Implementation** (not just sequential calls)
    - ✅ **Stateful Workflow** (GraphState shared across agents)
    - ✅ **Compiled Graph** (optimized execution)
    - ✅ **Production-Ready** (proper error handling)
    - ✅ **100% Free** (Gemini + Pollinations APIs)
    
    ---
    
    **💡 Get Started:** Enter your topic and vibe in the sidebar, then click "🚀 Run NexusCore"!
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
        st.markdown("### 🔧 Tech Stack")
        st.markdown("""
        - **LangGraph** StateGraph
        - **Gemini 2.5** Flash
        - **Pollinations.ai**
        - **Python 3.13+**
        """)
