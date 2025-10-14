"""
Test script for debate room tools to verify functionality.
This tests the MCP server tools without requiring full agent setup.
"""

import sys
import time
import threading

# Test the debate room tools MCP server
def test_debate_tools_server():
    """Test that the debate tools server can start and provide tools."""
    print("Testing Debate Room Tools Server...")
    
    # Start server in background thread
    from debate_room_tools import start_debate_tools_server
    server_thread = threading.Thread(target=start_debate_tools_server, daemon=True)
    server_thread.start()
    
    print("✓ Server thread started")
    time.sleep(2)  # Give server time to start
    print("✓ Server should be running on http://localhost:8000")
    
    # Test imports
    from debate_room_tools import (
        topic_selector, 
        get_next_speaker, 
        validate_turn,
        initialize_room,
        analyze_discussion_pulse
    )
    print("✓ All tool functions imported successfully")
    
    # Test topic_selector
    topic = topic_selector()
    print(f"✓ Topic selector: '{topic}'")
    assert isinstance(topic, str) and len(topic) > 0
    
    # Test initialize_room
    room_config = initialize_room(
        participant_names=["Alice", "Bob", "Carol"],
        room_type="discussion"
    )
    print(f"✓ Room initialization: {room_config}")
    assert room_config['success'] == "True"
    assert "Alice" in room_config['participants']
    
    # Test with too many participants
    room_config_fail = initialize_room(
        participant_names=["P1", "P2", "P3", "P4", "P5", "P6", "P7"],
        room_type="discussion"
    )
    print(f"✓ Room initialization (max participants check): {room_config_fail}")
    assert room_config_fail['success'] == "False"
    
    # Test get_next_speaker
    participants = ["Alice", "Bob", "Carol"]
    next_speaker = get_next_speaker(
        current_speaker="Alice",
        participants=participants
    )
    print(f"✓ Next speaker after Alice: {next_speaker}")
    assert next_speaker['next_speaker'] == "Bob"
    
    # Test wrap-around
    next_speaker = get_next_speaker(
        current_speaker="Carol",
        participants=participants
    )
    print(f"✓ Next speaker after Carol (wrap): {next_speaker}")
    assert next_speaker['next_speaker'] == "Alice"
    
    # Test validate_turn
    validation = validate_turn(
        speaker="Bob",
        expected_speaker="Bob",
        participants=participants
    )
    print(f"✓ Turn validation (correct turn): {validation}")
    assert validation['valid'] == "True"
    
    validation_fail = validate_turn(
        speaker="Bob",
        expected_speaker="Alice",
        participants=participants
    )
    print(f"✓ Turn validation (wrong turn): {validation_fail}")
    assert validation_fail['valid'] == "False"
    
    # Test analyze_discussion_pulse
    statements = [
        {"speaker": "Alice", "content": "I think AI is important"},
        {"speaker": "Bob", "content": "Yes, but we need regulations"},
        {"speaker": "Carol", "content": "We should focus on education"}
    ]
    pulse = analyze_discussion_pulse(statements, room_type="discussion")
    print(f"✓ Discussion pulse analysis: {pulse}")
    assert pulse['total_statements'] == "3"
    assert pulse['unique_speakers'] == "3"
    
    print("\n" + "="*60)
    print("ALL TESTS PASSED! ✓")
    print("="*60)
    return True


def test_facilitator_structure():
    """Test the facilitator class structure without requiring agent."""
    print("\nTesting Facilitator Structure...")
    
    try:
        # Import the facilitator
        from debate_room_facilitator import DebateRoomFacilitator
        print("✓ Facilitator class imported successfully")
        
        # Test initialization with default rounds
        facilitator = DebateRoomFacilitator(room_type="discussion")
        print("✓ Facilitator initialized with default rounds")
        
        assert facilitator.room_type == "discussion"
        assert facilitator.num_rounds == 3
        assert facilitator.participants == []
        assert facilitator.topic is None
        assert facilitator.english_feedback_history == {}
        print("✓ Facilitator attributes correct (default)")
        
        # Test initialization with custom rounds
        facilitator2 = DebateRoomFacilitator(room_type="debate", num_rounds=5)
        print("✓ Facilitator initialized with custom rounds")
        
        assert facilitator2.room_type == "debate"
        assert facilitator2.num_rounds == 5
        print("✓ Facilitator custom attributes correct")
        
        print("\n" + "="*60)
        print("FACILITATOR STRUCTURE TESTS PASSED! ✓")
        print("="*60)
        return True
    except ImportError as e:
        print(f"⚠ Facilitator structure test skipped: {e}")
        print("  (This is expected if Strands agents are not installed)")
        print("\n" + "="*60)
        print("FACILITATOR STRUCTURE TESTS SKIPPED")
        print("="*60)
        return True


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("DEBATE ROOM FACILITATOR - COMPONENT TESTS")
    print("="*60 + "\n")
    
    try:
        # Test 1: Debate tools server
        test_debate_tools_server()
        
        # Test 2: Facilitator structure
        test_facilitator_structure()
        
        print("\n" + "="*60)
        print("ALL COMPONENT TESTS COMPLETED SUCCESSFULLY! ✅")
        print("="*60)
        print("\nNote: Full integration test requires:")
        print("  - GEMINI_API_KEY in .env")
        print("  - Strands agents installation")
        print("  - Run: uv run debate_room_facilitator.py")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
