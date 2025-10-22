import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.database import db
from src.services.agent_service import agent_service
from src.models.agent_pydantic_models import AgentType

async def debug_agents():
    room_id = "37423ccd79b548588825581e9a700c48"
    
    print("=== Debugging Agent Retrieval ===")
    
    # Initialize database
    await db.initialize()
    
    # Test database query directly
    print("1. Testing database query...")
    agents_data = await db.get_agents_by_room(room_id)
    print(f"Raw agents data: {agents_data}")
    
    # Test agent service
    print("\n2. Testing agent service...")
    agents_response = await agent_service.get_agents_by_room(room_id)
    print(f"Agent service response: {agents_response}")
    
    # Test get_agents_by_type
    print("\n3. Testing get_agents_by_type...")
    facilitator_agents = await agent_service.get_agents_by_type(room_id, AgentType.FACILITATOR)
    print(f"Facilitator agents: {facilitator_agents}")
    
    # Test the specific endpoint logic
    print("\n4. Testing endpoint logic...")
    all_agents_response = await agent_service.get_agents_by_room(room_id)
    if all_agents_response.status == "success":
        print(f"All agents: {all_agents_response.data}")
        for agent in all_agents_response.data:
            print(f"Agent type: {agent.agent_type}, Expected: {AgentType.FACILITATOR.value}")
            print(f"Match: {agent.agent_type == AgentType.FACILITATOR.value}")

if __name__ == "__main__":
    asyncio.run(debug_agents())
