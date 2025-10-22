import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.models.agent_pydantic_models import AgentType

async def test_agent_type_conversion():
    print("Testing AgentType enum conversion...")
    
    # Test string to enum conversion
    agent_type_str = "facilitator"
    try:
        agent_type_enum = AgentType(agent_type_str)
        print(f"String '{agent_type_str}' converted to enum: {agent_type_enum}")
        print(f"Enum value: {agent_type_enum.value}")
        print(f"Comparison: {agent_type_enum.value == agent_type_str}")
    except ValueError as e:
        print(f"Error converting '{agent_type_str}' to AgentType: {e}")
    
    # Test all possible values
    for agent_type in AgentType:
        print(f"AgentType.{agent_type.name} = '{agent_type.value}'")

if __name__ == "__main__":
    asyncio.run(test_agent_type_conversion())
