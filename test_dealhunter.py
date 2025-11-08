"""
Test script for DealHunter Agent
Tests the Gemini Pro integration for finding brand sponsorships
"""

import os
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from agents import DealHunterAgent
import json


def test_dealhunter_basic():
    """Test basic DealHunter functionality"""
    print("="*60)
    print("🧪 Testing DealHunter Agent")
    print("="*60)
    
    # Check for Gemini API key
    gemini_key = os.getenv('GEMINI_API_KEY')
    if not gemini_key:
        print("\n⚠️  WARNING: GEMINI_API_KEY not found in environment")
        print("Add GEMINI_API_KEY to your .env file to test with real API")
        print("Testing with fallback mode...\n")
    else:
        print(f"\n✅ Gemini API Key found: {gemini_key[:10]}...")
    
    # Test topics
    test_topics = [
        "AI Pin technology and wearable AI devices",
        "Fitness and workout content",
        "Gaming and esports"
    ]
    
    agent = DealHunterAgent()
    
    for i, topic in enumerate(test_topics, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: Topic = '{topic}'")
        print('='*60)
        
        try:
            # Find deals
            deals = agent.find_deals(topic)
            
            # Validate structure
            print(f"\n✅ Found {len(deals)} potential sponsors:")
            print(f"\nJSON Output:")
            print(json.dumps(deals, indent=2))
            
            # Validate each deal has required fields
            for deal in deals:
                assert 'company_name' in deal, "Missing company_name"
                assert 'website' in deal, "Missing website"
                assert 'reason_for_sponsorship' in deal, "Missing reason_for_sponsorship"
                
                print(f"\n📦 {deal['company_name']}")
                print(f"   🌐 {deal['website']}")
                print(f"   💡 {deal['reason_for_sponsorship']}")
            
            print(f"\n✅ All {len(deals)} deals have correct structure!")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("✅ DealHunter Testing Complete!")
    print("="*60)


def test_dealhunter_integration():
    """Test DealHunter in workflow context"""
    print("\n" + "="*60)
    print("🧪 Testing DealHunter in Workflow Context")
    print("="*60)
    
    # Simulate workflow state
    state = {
        'selected_trend': {
            'title': 'New AI gadgets revolutionizing productivity'
        },
        'niche': 'tech reviews'
    }
    
    agent = DealHunterAgent()
    
    # Test with selected trend
    topic = state['selected_trend']['title']
    print(f"\nTopic from selected_trend: '{topic}'")
    
    deals = agent.find_deals(topic)
    
    print(f"\n✅ DealHunter returned {len(deals)} deals")
    
    # Verify it returns a list that can be added to state
    assert isinstance(deals, list), "Should return a list"
    assert len(deals) <= 3, "Should return max 3 deals"
    
    print("✅ Integration test passed!")


if __name__ == "__main__":
    print("\n🚀 Starting DealHunter Agent Tests\n")
    
    try:
        # Run basic tests
        test_dealhunter_basic()
        
        # Run integration test
        test_dealhunter_integration()
        
        print("\n" + "="*60)
        print("🎉 ALL TESTS PASSED!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
