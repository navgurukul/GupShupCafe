#!/usr/bin/env python3
"""
Test script to demonstrate dict-like functionality of Pydantic models
"""

import sys
import os
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models import CreateRoomModel, RoomStatus, CEFRLevel, CreateParticipantModel

def test_dict_functionality():
    """Test all dict-like operations on models"""
    
    print("🧪 Testing Dict-like Functionality on Pydantic Models")
    print("=" * 60)
    
    # Create a room model instance
    room = CreateRoomModel(
        topic_title="Technology Discussion",
        topic_category="Technology",
        cefr_level=CEFRLevel.B1,
        status=RoomStatus.WAITING,
        created_by="user123"
    )
    
    print("1. 📝 Created Room Model:")
    print(f"   {room}")
    print()
    
    # Test dict-style access
    print("2. 🔍 Dict-style Access:")
    print(f"   room['topic_title'] = {room['topic_title']}")
    print(f"   room['cefr_level'] = {room['cefr_level']}")
    print()
    
    # Test dict-style assignment
    print("3. ✏️  Dict-style Assignment:")
    room['topic_title'] = "AI and Machine Learning"
    room['max_participants'] = 8
    print(f"   Updated topic_title: {room['topic_title']}")
    print(f"   Updated max_participants: {room['max_participants']}")
    print()
    
    # Test 'in' operator
    print("4. 🔎 'in' Operator:")
    print(f"   'topic_title' in room: {'topic_title' in room}")
    print(f"   'nonexistent_field' in room: {'nonexistent_field' in room}")
    print()
    
    # Test iteration
    print("5. 🔄 Iteration over fields:")
    print("   Field names:", list(room.keys())[:5], "...")  # Show first 5
    print()
    
    # Test dict methods
    print("6. 📚 Dict Methods:")
    print(f"   len(room): {len(room)}")
    print(f"   room.get('topic_title'): {room.get('topic_title')}")
    print(f"   room.get('nonexistent', 'default'): {room.get('nonexistent', 'default')}")
    print()
    
    # Test update method
    print("7. 🔄 Update Method:")
    room.update({
        'speaking_time_per_turn': 90,
        'num_rounds': 5
    })
    print(f"   Updated speaking_time_per_turn: {room['speaking_time_per_turn']}")
    print(f"   Updated num_rounds: {room['num_rounds']}")
    print()
    
    # Test items() method
    print("8. 📋 Items Method (first 3):")
    for key, value in list(room.items())[:3]:
        print(f"   {key}: {value}")
    print()
    
    # Test copy method
    print("9. 📄 Copy Method:")
    room_copy = room.copy()
    room_copy['topic_title'] = "Modified Copy"
    print(f"   Original: {room['topic_title']}")
    print(f"   Copy: {room_copy['topic_title']}")
    print()
    
    # Test to_dict method
    print("10. 🗂️  To Dict Method:")
    room_dict = room.to_dict()
    print(f"    Type: {type(room_dict)}")
    print(f"    Keys: {list(room_dict.keys())[:3]}...")
    print()
    
    # Test with participant model
    print("11. 👤 Testing with Participant Model:")
    participant = CreateParticipantModel(
        room_id="room123",
        user_id="user456",
        anonymous_name="Blue Panda",
        starting_cefr_level="B1",
        joined_at=datetime.now()
    )
    
    # Use dict-like operations
    participant['is_ready'] = True
    participant['role'] = "host"
    
    print(f"    participant['anonymous_name']: {participant['anonymous_name']}")
    print(f"    participant['is_ready']: {participant['is_ready']}")
    print(f"    'socket_id' in participant: {'socket_id' in participant}")
    print()
    
    print("✅ All dict-like functionality tests passed!")
    print("🎉 Models are now scriptable like dictionaries!")

if __name__ == "__main__":
    test_dict_functionality()