"""
NexusCore - The Brain of CreatorForge Nexus

This is the main LangGraph orchestrator that connects all agents together
in a cohesive workflow. It manages the state flow and agent execution order.
"""

import os
from typing import TypedDict, List, Dict, Any
from dotenv import load_dotenv

# LangGraph imports
from langgraph.graph import StateGraph, END

# Import all agent functions
from agent_trendscout import run_trendscout, GraphState
from agent_forgemaster import run_forgemaster
from agent_engagebot import run_engagebot
from agent_dealhunter import run_dealhunter

# Load environment variables
load_dotenv()

# --- Bundle 1.3: API Key Validation ---
def validate_api_keys():
    """
    Validates that all required API keys are present on startup.
    Raises EnvironmentError if any keys are missing.
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    if not gemini_key:
        raise EnvironmentError(
            "🚨 GEMINI_API_KEY not found in environment.\n"
            "Please create a .env file with: GEMINI_API_KEY=your_key_here"
        )
    
    if len(gemini_key.strip()) < 10:  # Basic sanity check
        raise EnvironmentError(
            "🚨 GEMINI_API_KEY appears to be invalid (too short).\n"
            "Please check your .env file."
        )
    
    print("✅ API keys validated successfully")

# Validate on module import
validate_api_keys()

# --- Bundle 1.2: Error Handler Node ---
def error_handler(state: GraphState) -> GraphState:
    """
    Handles workflow errors by setting error state and stopping execution.
    Called when agents fail to produce required outputs.
    """
    error_msg = "⚠️ Pipeline failed: One or more agents did not produce valid output"
    
    # Set error in state (you can access this in UI to show warnings)
    state['error'] = error_msg
    
    print(f"\n{error_msg}")
    print("Workflow will terminate early.\n")
    
    return state

def check_for_trends(state: GraphState) -> str:
    """
    Conditional routing function after TrendScout.
    Checks if scouted_trends is empty and routes accordingly.
    
    Returns:
        "error_handler" if no trends found, "forgemaster" if trends exist
    """
    scouted_trends = state.get('scouted_trends', [])
    
    if not scouted_trends or len(scouted_trends) == 0:
        print("⚠️ No trends found by TrendScout - routing to error handler")
        return "error_handler"
    
    print(f"✅ Found {len(scouted_trends)} trends - proceeding to ForgeMaster")
    return "forgemaster"

# --- 1. Create the NexusCore Workflow ---
def create_nexus_workflow():
    """
    Creates and compiles the complete multi-agent workflow.
    
    Returns:
        Compiled LangGraph application ready to invoke
    """
    
    # Initialize the StateGraph with our GraphState
    workflow = StateGraph(GraphState)
    
    # --- 2. Add Agent Nodes ---
    # Each node is an agent function that processes the state
    workflow.add_node("trendscout", run_trendscout)
    workflow.add_node("forgemaster", run_forgemaster)
    workflow.add_node("engagebot", run_engagebot)
    workflow.add_node("dealhunter", run_dealhunter)
    workflow.add_node("error_handler", error_handler)  # Bundle 1.2: Error handling node
    
    # --- 3. Define the Execution Flow ---
    # Conditional flow: TrendScout results determine next step
    
    # Start with TrendScout (the research phase)
    workflow.set_entry_point("trendscout")
    
    # TrendScout → conditional routing (check for trends before proceeding)
    workflow.add_conditional_edges(
        "trendscout",
        check_for_trends,  # This function returns "error_handler" or "forgemaster"
        {
            "error_handler": "error_handler",
            "forgemaster": "forgemaster"
        }
    )
    
    # Error handler goes straight to END
    workflow.add_edge("error_handler", END)
    
    # ForgeMaster → EngageBot (content → distribution strategy)
    workflow.add_edge("forgemaster", "engagebot")
    
    # EngageBot → DealHunter (distribution → monetization)
    workflow.add_edge("engagebot", "dealhunter")
    
    # DealHunter → END (monetization → complete)
    workflow.add_edge("dealhunter", END)
    
    # --- 4. Compile the Graph ---
    # This creates the executable application
    app = workflow.compile()
    
    return app

# --- 5. Create the Compiled App ---
# This is the main application that your API/UI will use
nexus_app = create_nexus_workflow()

# --- 6. Helper Function for Running the Complete Pipeline ---
def run_nexus(topic: str, user_vibe: str) -> Dict[str, Any]:
    """
    Runs the complete CreatorForge Nexus pipeline (non-streaming version).
    
    Args:
        topic: The content topic to research (e.g., "AI Pin review")
        user_vibe: The creator's style (e.g., "Sarcastic tech reviews")
    
    Returns:
        Complete state with all agent outputs
    """
    
    print("=" * 80)
    print("🚀 NEXUSCORE - Starting Multi-Agent Pipeline")
    print("=" * 80)
    
    # Initialize the input state
    inputs = GraphState(
        topic=topic,
        user_vibe=user_vibe,
        scouted_trends=[],
        content_pack={},
        engage_plan={},
        deal_plan=[],
        error=""  # Bundle 1.2: Initialize error field
    )
    
    print(f"\n📋 Configuration:")
    print(f"   Topic: {topic}")
    print(f"   Vibe: {user_vibe}")
    print(f"\n🔄 Executing agent pipeline...")
    print("-" * 80)
    
    # Invoke the complete workflow
    # This will run all agents in sequence
    final_state = nexus_app.invoke(inputs)
    
    print("-" * 80)
    
    # Bundle 1.2: Check for workflow errors
    if final_state.get('error'):
        print(f"\n❌ Pipeline stopped with error: {final_state['error']}")
    else:
        print("\n✅ Pipeline Complete!")
    
    print("=" * 80)
    
    return final_state


# --- Bundle 4.1: Streaming Version with Real-Time Progress ---
def run_nexus_streaming(topic: str, user_vibe: str):
    """
    Generator version of run_nexus that yields progress updates for Streamlit.
    
    Yields progress messages like:
    - "🔍 Running TrendScout..."
    - "🔨 Running ForgeMaster..."
    - etc.
    
    Final yield is the complete state dict.
    
    Usage in Streamlit:
        with st.status("Running pipeline...") as status:
            for update in run_nexus_streaming(topic, vibe):
                if isinstance(update, str):
                    status.update(label=update)
                else:
                    final_state = update
    """
    
    # Initialize the input state
    inputs = GraphState(
        topic=topic,
        user_vibe=user_vibe,
        scouted_trends=[],
        content_pack={},
        engage_plan={},
        deal_plan=[],
        error=""
    )
    
    # Yield initial status
    yield "🚀 Initializing pipeline..."
    
    # Run agents with progress updates
    # Note: LangGraph doesn't expose intermediate states by default,
    # so we'll simulate the progress based on expected flow
    
    yield "🔍 Running TrendScout - Researching viral trends..."
    
    # Stream through the graph
    # LangGraph's streaming returns intermediate states
    for chunk in nexus_app.stream(inputs):
        # chunk is a dict like {'trendscout': {...state...}}
        if 'trendscout' in chunk:
            trends_count = len(chunk['trendscout'].get('scouted_trends', []))
            yield f"✅ TrendScout complete - Found {trends_count} trends"
            
            # Check for errors
            if chunk['trendscout'].get('error'):
                yield "❌ Pipeline stopped - No trends found"
                yield chunk['trendscout']  # Return final state
                return
            
            yield "🔨 Running ForgeMaster - Creating content..."
        
        elif 'forgemaster' in chunk:
            yield "✅ ForgeMaster complete - Script and thumbnail ready"
            yield "📢 Running EngageBot - Planning distribution..."
        
        elif 'engagebot' in chunk:
            plan_count = len(chunk['engagebot'].get('engage_plan', {}).get('plan', []))
            yield f"✅ EngageBot complete - {plan_count} posts scheduled"
            yield "💰 Running DealHunter - Finding sponsors..."
        
        elif 'dealhunter' in chunk:
            deal_count = len(chunk['dealhunter'].get('deal_plan', []))
            yield f"✅ DealHunter complete - {deal_count} sponsors found"
            yield "🎉 Pipeline complete!"
            yield chunk['dealhunter']  # Return final state
            return
        
        elif 'error_handler' in chunk:
            yield "❌ Pipeline stopped with error"
            yield chunk['error_handler']
            return
    
    # Fallback: if streaming doesn't work as expected, run normal version
    yield "⚠️ Streaming unavailable, running standard pipeline..."
    final_state = nexus_app.invoke(inputs)
    yield "✅ Pipeline complete!"
    yield final_state

# --- 7. Display Helper Function ---
def display_results(state: Dict[str, Any]):
    """
    Pretty-print the complete pipeline results.
    
    Args:
        state: The final GraphState after all agents have run
    """
    
    print("\n" + "=" * 80)
    print("📊 FINAL RESULTS - COMPLETE CONTENT PACKAGE")
    print("=" * 80)
    
    # Display Scouted Trends
    if state.get('scouted_trends'):
        print("\n🕵️ SCOUTED TRENDS:")
        print("-" * 80)
        for i, trend in enumerate(state['scouted_trends'], 1):
            print(f"\n#{i} - {trend.get('title', 'N/A')}")
            print(f"   URL: {trend.get('url', 'N/A')}")
            print(f"   Summary: {trend.get('summary', 'N/A')[:150]}...")
    
    # Display Content Pack
    if state.get('content_pack'):
        content = state['content_pack']
        print("\n\n🔨 CONTENT PACKAGE:")
        print("-" * 80)
        
        print("\n📝 SCRIPT:")
        print(content.get('script', 'N/A')[:500] + "...")
        
        print("\n\n🐦 SOCIAL POST:")
        print(content.get('social_post', 'N/A'))
        
        print("\n\n🖼️ THUMBNAIL:")
        print(f"   Prompt: {content.get('thumbnail_prompt', 'N/A')}")
        print(f"   URL: {content.get('thumbnail_url', 'N/A')[:80]}...")
    
    # Display Engagement Plan
    if state.get('engage_plan'):
        plan = state['engage_plan']
        print("\n\n📢 ENGAGEMENT STRATEGY:")
        print("-" * 80)
        
        if 'strategy_summary' in plan:
            print(f"\n🎯 Strategy: {plan['strategy_summary']}")
        
        if 'predicted_reach' in plan:
            print(f"📈 Predicted Reach: {plan['predicted_reach']}")
        
        if 'plan' in plan:
            print(f"\n📅 POSTING SCHEDULE ({len(plan['plan'])} posts):")
            for i, post in enumerate(plan['plan'][:3], 1):  # Show first 3
                print(f"\n   #{i} - {post.get('platform', 'N/A')}")
                print(f"      Time: {post.get('post_at', 'N/A')}")
                print(f"      Reason: {post.get('reason', 'N/A')[:80]}...")
            if len(plan['plan']) > 3:
                print(f"\n   ... and {len(plan['plan']) - 3} more posts")
    
    # Display Deal Plan
    if state.get('deal_plan'):
        print("\n\n💰 BRAND SPONSORSHIP OPPORTUNITIES:")
        print("-" * 80)
        for i, deal in enumerate(state['deal_plan'], 1):
            print(f"\n#{i} - 🏢 {deal.get('company_name', 'N/A')}")
            print(f"   🌐 {deal.get('website', 'N/A')}")
            print(f"   💡 {deal.get('reason_for_sponsorship', 'N/A')[:150]}...")
    
    print("\n" + "=" * 80)
    print("🎉 All content is ready for deployment!")
    print("=" * 80)

# --- 8. Main Execution (Test Harness) ---
if __name__ == "__main__":
    
    print("\n" + "=" * 80)
    print("🧪 TESTING NEXUSCORE - Complete Multi-Agent System")
    print("=" * 80)
    
    # Example configuration
    test_topic = "Rabbit R1 vs Humane AI Pin"
    test_vibe = "Sarcastic tech reviews with dark humor"
    
    # Run the complete pipeline
    final_state = run_nexus(
        topic=test_topic,
        user_vibe=test_vibe
    )
    
    # Display the results
    display_results(final_state)
    
    # Show what the API would return
    print("\n\n" + "=" * 80)
    print("📦 API RESPONSE STRUCTURE")
    print("=" * 80)
    print(f"""
This is what your API endpoint would return:

{{
    "topic": "{final_state.get('topic', 'N/A')}",
    "user_vibe": "{final_state.get('user_vibe', 'N/A')}",
    "scouted_trends": [...{len(final_state.get('scouted_trends', []))} trends...],
    "content_pack": {{
        "script": "...",
        "social_post": "...",
        "thumbnail_url": "...",
        "thumbnail_prompt": "..."
    }},
    "engage_plan": {{
        "plan": [...{len(final_state.get('engage_plan', {}).get('plan', []))} posts...],
        "strategy_summary": "...",
        "predicted_reach": "{final_state.get('engage_plan', {}).get('predicted_reach', 'N/A')}"
    }},
    "deal_plan": [...{len(final_state.get('deal_plan', []))} brand opportunities...]
}}
    """)
    
    print("\n✅ NexusCore test complete!")
    print("=" * 80)
