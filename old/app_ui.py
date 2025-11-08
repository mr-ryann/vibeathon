"""
CreatorForge Nexus - Minimal UI
A Streamlit interface to visualize the TrendScout agent in action
"""

import streamlit as st
import json
from typing import Dict, Any
from agent_trendscout import run_trendscout, GraphState

# Page configuration
import streamlit as st
import json
from agent_trendscout import run_trendscout, GraphState
from agent_forgemaster import run_forgemaster

st.set_page_config(
    page_title="CreatorForge Nexus - Multi-Agent Demo",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS for better styling
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
    .agent-card {
        background-color: #1e1e1e;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .trend-card {
        background-color: #2d2d2d;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #764ba2;
    }
    .success-box {
        background-color: #1e3a1e;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #4caf50;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🧠 CreatorForge Nexus</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #888; font-size: 1.2rem;">Multi-Agent Content Creation System</p>', unsafe_allow_html=True)

st.markdown("---")

# Sidebar for agent info
with st.sidebar:
    st.markdown("### 🤖 Active Agents")
    st.markdown("""
    #### 🕵️ TrendScout
    **Status:** ✅ Active  
    **Role:** The "Eyes"  
    **Function:** Discovers viral trends, discussions, and content ideas
    
    ---
    
    #### 📝 ContentForge
    **Status:** 🔜 Coming Soon  
    **Role:** The "Creator"
    
    #### 🎨 VisualSmith
    **Status:** 🔜 Coming Soon  
    **Role:** The "Artist"
    
    #### 📢 EngageHub
    **Status:** 🔜 Coming Soon  
    **Role:** The "Promoter"
    
    #### 💼 DealMaker
    **Status:** 🔜 Coming Soon  
    **Role:** The "Negotiator"
    """)

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### ⚙️ Agent Configuration")
    
    # Input fields
    topic = st.text_input(
        "🎯 Enter Topic to Scout",
        value="Rabbit R1 vs Humane AI Pin",
        help="What topic should the agent research?"
    )
    
    user_vibe = st.text_input(
        "✨ Creator Vibe/Style",
        value="Sarcastic tech reviews",
        help="What's your content creation style?"
    )
    
    run_button = st.button("🚀 Launch TrendScout Agent", type="primary", use_container_width=True)

with col2:
    st.markdown("### 📊 Agent Status")
    status_placeholder = st.empty()
    
    with status_placeholder.container():
        st.info("⏸️ Waiting for launch command...")

# Results area (full width)
st.markdown("---")
st.markdown("### 📡 Agent Output")

output_container = st.container()

# Run the agent when button is clicked
if run_button:
    with st.spinner("🧠 TrendScout is searching the web..."):
        # Show status
        with status_placeholder.container():
            st.warning("🔄 Agent is running...")
        
        # Create initial state
        initial_state = GraphState(
            topic=topic,
            user_vibe=user_vibe,
            scouted_trends=[],
            content_pack={},
            engage_plan={},
            deal_plan=[]
        )
        
        # Run the agent
        result_state = run_trendscout(initial_state)
        
        # Update status
        with status_placeholder.container():
            if result_state.get("scouted_trends"):
                st.success(f"✅ Agent completed successfully! Found {len(result_state['scouted_trends'])} trends.")
            else:
                st.error("❌ Agent failed to find trends. Check console for errors.")
    
    # Display results
    with output_container:
        if result_state.get("scouted_trends"):
            trends = result_state["scouted_trends"]
            
            # Create tabs for different views
            tab1, tab2 = st.tabs(["📋 Formatted View", "🔧 Raw JSON"])
            
            with tab1:
                st.markdown(f"#### 🎯 Topic: **{topic}**")
                st.markdown(f"#### ✨ Style: **{user_vibe}**")
                st.markdown("---")
                
                for idx, trend in enumerate(trends, 1):
                    with st.expander(f"🔥 Trend #{idx}: {trend.get('title', 'No title')}", expanded=True):
                        col_a, col_b = st.columns([3, 1])
                        
                        with col_a:
                            st.markdown(f"**📰 Title:** {trend.get('title', 'N/A')}")
                            st.markdown(f"**🔗 URL:** [{trend.get('url', 'N/A')}]({trend.get('url', '#')})")
                            st.markdown(f"**📝 Summary:**")
                            st.write(trend.get('summary', 'N/A'))
                        
                        with col_b:
                            st.metric("Trend #", idx)
                
                st.markdown("---")
                st.markdown('<div class="success-box">✨ <b>Next Step:</b> This data will be passed to ContentForge agent to create viral content!</div>', unsafe_allow_html=True)
            
            with tab2:
                st.json(result_state)
                
                # Download button
                st.download_button(
                    label="📥 Download JSON",
                    data=json.dumps(result_state, indent=2),
                    file_name=f"trendscout_output_{topic.replace(' ', '_')}.json",
                    mime="application/json"
                )
        else:
            st.error("No trends found. Please check the console for error messages.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>🤖 Powered by <b>LangGraph</b> & <b>Gemini 2.5 Flash</b></p>
    <p style="font-size: 0.9rem;">Multi-Agent Architecture | Real-time Trend Discovery</p>
</div>
""", unsafe_allow_html=True)
