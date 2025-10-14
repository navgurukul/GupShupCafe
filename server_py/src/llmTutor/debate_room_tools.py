"""
MCP Server for Debate Room Tools

This module provides tools for facilitating debate/discussion rooms including:
- Topic selection
- Turn management
- Fact checking capabilities
"""

from mcp.server import FastMCP
from typing import List, Dict, Optional, Any
import random

# Create MCP server for debate room tools
mcp = FastMCP("Debate Room Tools Server")


# Predefined topics for debates/discussions
TOPICS = [
    "The impact of artificial intelligence on job markets",
    "Should social media platforms be regulated more strictly?",
    "Climate change: Individual responsibility vs. corporate accountability",
    "The future of remote work",
    "Privacy vs. security in the digital age",
    "Universal basic income: pros and cons",
    "Space exploration: priority or luxury?",
    "Education system reform needs",
    "Renewable energy transition challenges",
    "The role of government in healthcare"
]


@mcp.tool(description="Select a random topic for debate or discussion")
def topic_selector(category: Optional[str] = None) -> str:
    """
    Select a debate/discussion topic randomly or from a category.
    
    Args:
        category: Optional category filter (not implemented yet, returns random topic)
    
    Returns:
        A topic string for the debate/discussion
    """
    return random.choice(TOPICS)


@mcp.tool(description="Get the next speaker in the turn sequence")
def get_next_speaker(
    current_speaker: str,
    participants: List[str],
    turn_order: Optional[List[str]] = None
) -> Dict[str, str]:
    """
    Determine the next speaker in the debate/discussion room.
    
    Args:
        current_speaker: Name of the current speaker
        participants: List of all participant names
        turn_order: Optional custom turn order (if None, uses participant list order)
    
    Returns:
        Dictionary with next_speaker name and position
    """
    if not participants:
        return {"next_speaker": "agent", "message": "No participants in the room"}
    
    order = turn_order if turn_order else participants
    
    if current_speaker not in order:
        # Start with the first participant
        return {"next_speaker": order[0], "position": "1"}
    
    current_index = order.index(current_speaker)
    next_index = (current_index + 1) % len(order)
    
    return {
        "next_speaker": order[next_index],
        "position": str(next_index + 1)
    }


@mcp.tool(description="Track speaking turns and ensure proper sequencing")
def validate_turn(
    speaker: str,
    expected_speaker: str,
    participants: List[str]
) -> Dict[str, str]:
    """
    Validate if a speaker is speaking in their correct turn.
    
    Args:
        speaker: Name of the person trying to speak
        expected_speaker: Name of the person whose turn it is
        participants: List of all participants
    
    Returns:
        Dictionary with validation result and message
    """
    if speaker not in participants:
        return {
            "valid": "False",
            "message": f"{speaker} is not in the participant list",
            "action": "reject"
        }
    
    if speaker == expected_speaker:
        return {
            "valid": "True",
            "message": f"It is {speaker}'s turn to speak",
            "action": "allow"
        }
    else:
        return {
            "valid": "False",
            "message": f"Please wait for your turn. Currently, it is {expected_speaker}'s turn",
            "action": "defer"
        }


@mcp.tool(description="Initialize the debate/discussion room with participants")
def initialize_room(
    participant_names: List[str],
    room_type: str = "discussion"
) -> Dict[str, str]:
    """
    Initialize a debate or discussion room with participants.
    
    Args:
        participant_names: List of participant names (1-6 people)
        room_type: Type of room - 'debate' or 'discussion'
    
    Returns:
        Dictionary with room configuration and first speaker
    """
    if not participant_names or len(participant_names) < 1:
        return {
            "success": "False",
            "message": "At least 1 participant is required"
        }
    
    if len(participant_names) > 6:
        return {
            "success": "False",
            "message": "Maximum 6 participants allowed"
        }
    
    return {
        "success": "True",
        "room_type": room_type,
        "participants": str(participant_names),
        "participant_count": str(len(participant_names)),
        "first_speaker": participant_names[0],
        "turn_order": str(participant_names),
        "message": f"Room initialized with {len(participant_names)} participant(s)"
    }


@mcp.tool(description="Track discussion progress and identify common/diverging points")
def analyze_discussion_pulse(
    statements: List[Dict[str, str]],
    room_type: str = "discussion"
) -> Dict[str, str]:
    """
    Analyze the pulse of the discussion/debate to identify convergence and divergence.
    
    Args:
        statements: List of dictionaries with 'speaker' and 'content' keys
        room_type: 'discussion' or 'debate'
    
    Returns:
        Dictionary with analysis of common points and diverging viewpoints
    """
    if not statements:
        return {
            "common_points": "[]",
            "diverging_points": "[]",
            "pulse": "just_started",
            "message": "Not enough data to analyze yet"
        }
    
    # Basic analysis based on keywords (simplified for MVP)
    speaker_count = len(set(s.get("speaker", "") for s in statements))
    
    return {
        "total_statements": str(len(statements)),
        "unique_speakers": str(speaker_count),
        "pulse": "active" if len(statements) > 3 else "warming_up",
        "participation_level": "high" if speaker_count > len(statements) * 0.6 else "moderate",
        "message": "Discussion is progressing",
        "suggestion": "Good participation" if speaker_count > 1 else "Encourage more participation"
    }


def start_debate_tools_server():
    """Start the debate room tools MCP server."""
    print("Starting Debate Room Tools Server on http://localhost:8000")
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    start_debate_tools_server()
