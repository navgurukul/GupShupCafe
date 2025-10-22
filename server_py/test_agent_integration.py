#!/usr/bin/env python3
"""
Quick test script to verify agent integration
"""

import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.agent_service import AgentService
from models import CreateAgentModel, AgentType, AgentModelSource

async def test_agent_integration():
    """Test the agent integration with actual Strands agents."""
    
    print("🧪 Testing Agent Integration...")
    
    try:
        # Test creating agents
        print("\n1. Testing agent creation...")
        
        facilitator_data = CreateAgentModel(
            room_id="test-room-123",
            agent_model=AgentModelSource.GEMINI,
            agent_type=AgentType.FACILITATOR,
        )
        
        english_data = CreateAgentModel(
            room_id="test-room-123",
            agent_model=AgentModelSource.GEMINI,
            agent_type=AgentType.ENGLISH,
        )
        
        # Test agent instance creation (without database)
        print("\n2. Testing agent instance creation...")
        
        # Test getting agent core
        agent_core = AgentService._get_or_create_agent_core()
        print(f"✅ AgentCore created: {type(agent_core).__name__}")
        
        # Test creating agent instances
        english_instance = AgentService._get_agent_instance("test-english-1", AgentType.ENGLISH.value)
        facilitator_instance = AgentService._get_agent_instance("test-facilitator-1", AgentType.FACILITATOR.value)
        
        if english_instance:
            print(f"✅ English agent instance created: {type(english_instance).__name__}")
        else:
            print("❌ Failed to create English agent instance")
            
        if facilitator_instance:
            print(f"✅ Facilitator agent instance created: {type(facilitator_instance).__name__}")
        else:
            print("❌ Failed to create Facilitator agent instance")
        
        # Test agent functionality
        print("\n3. Testing agent functionality...")
        
        if english_instance:
            try:
                # Test English feedback
                test_data = {
                    "text": "I think this is a very interesting topic to discuss with everyone here today.",
                    "context": {
                        "topic": "technology in education",
                        "feedback_type": "instant"
                    }
                }
                
                result = await english_instance.analyze(test_data)
                print(f"✅ English agent analysis completed")
                print(f"   CEFR Level: {result.get('cefr_level', 'N/A')}")
                print(f"   Suggestions: {len(result.get('suggestions', []))} items")
                
            except Exception as e:
                print(f"❌ English agent test failed: {e}")
        
        if facilitator_instance:
            try:
                # Test Facilitator response
                context = {
                    "topic": "technology in education",
                    "current_speaker": {"anonymous_name": "Alice"},
                    "turn_number": 1,
                    "previous_statements": [],
                    "current_round": 1,
                    "total_rounds": 3
                }
                
                response = await facilitator_instance.facilitate_turn(context)
                print(f"✅ Facilitator agent response generated")
                print(f"   Response: {response[:100]}...")
                
            except Exception as e:
                print(f"❌ Facilitator agent test failed: {e}")
        
        print("\n🎉 Agent integration test completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_agent_integration())