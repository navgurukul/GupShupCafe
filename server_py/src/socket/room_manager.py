"""
Room Manager
Manages discussion rooms and participants
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from ..models import Room, Participant, RoomStatus, ParticipantRole


class RoomManager:
    """Manages discussion rooms and participants"""
    
    def __init__(self):
        self.rooms: Dict[str, Room] = {}
        self._skip_cleanup = False

    def get_room(self, room_id: str) -> Room:
        """
        Get or create a room
        Args:
            room_id: Room identifier
        Returns: Room object
        """
        if room_id not in self.rooms:
            self.rooms[room_id] = Room(
                room_code=room_id,
                status=RoomStatus.WAITING,
                speaking_time=60,
                max_rounds=3
            )
        return self.rooms[room_id]

    def add_user_to_room(self, room_id: str, user_data: Dict[str, Any]):
        """
        Add user to room
        Args:
            room_id: Room identifier
            user_data: User data
        """
        room = self.get_room(room_id)
        
        # Create Participant object
        role = user_data.get("role", "listener")
        if isinstance(role, str):
            # Map role string to enum
            role_map = {
                "host": ParticipantRole.HOST,
                "speaker": ParticipantRole.PARTICIPANT,
                "listener": ParticipantRole.LISTENER
            }
            role = role_map.get(role.lower(), ParticipantRole.LISTENER)
        
        participant = Participant(
            id=user_data.get("id"),
            socket_id=user_data.get("socketId"),
            anonymous_name=user_data.get("anonymousName"),
            name=user_data.get("name"),
            campus=user_data.get("campus"),
            location=user_data.get("location"),
            role=role,
            is_ready=user_data.get("isReady", False),
            joined_at=user_data.get("joinedAt", datetime.now().isoformat())
        )
        
        # Add participant (handles reconnection)
        room.add_participant(participant)
        
        print(f"➕ Added {participant.anonymous_name} to room {room_id}. Total: {len(room.participants)}")

    def remove_user_from_room(self, room_id: str, user_id: str):
        """
        Remove user from room
        Args:
            room_id: Room identifier
            user_id: User identifier
        """
        room = self.get_room(room_id)
        initial_count = len(room.participants)
        
        # Remove participant by user ID
        participant = room.get_participant_by_id(user_id)
        if participant:
            room.remove_participant(participant.socket_id)
            print(f"➖ Removed user {user_id} from room {room_id}. Remaining: {len(room.participants)}")
        
        # Clean up empty rooms
        if len(room.participants) == 0 and not self._skip_cleanup:
            self.cleanup_room(room_id)

    def update_user(self, room_id: str, user_id: str, updates: Dict[str, Any]):
        """
        Update user data in room
        Args:
            room_id: Room identifier
            user_id: User identifier
            updates: Data to update
        """
        room = self.get_room(room_id)
        participant = room.get_participant_by_id(user_id)
        
        if participant:
            # Update participant attributes
            for key, value in updates.items():
                # Convert camelCase to snake_case
                attr_name = key
                if key == "isReady":
                    attr_name = "is_ready"
                elif key == "isSpeaking":
                    attr_name = "is_speaking"
                elif key == "isMuted":
                    attr_name = "is_muted"
                elif key == "cefrLevel":
                    attr_name = "cefr_level"
                elif key == "socketId":
                    attr_name = "socket_id"
                elif key == "anonymousName":
                    attr_name = "anonymous_name"
                elif key == "avatarColor":
                    attr_name = "avatar_color"
                    
                if hasattr(participant, attr_name):
                    setattr(participant, attr_name, value)
            
            print(f"🔄 Updated user {user_id} in room {room_id}: {updates}")

    def get_room_participants(self, room_id: str) -> List[Dict[str, Any]]:
        """
        Get room participants
        Args:
            room_id: Room identifier
        Returns: Array of participants
        """
        room = self.get_room(room_id)
        return [p.to_dict() for p in room.participants]

    def get_discussion_state(self, room_id: str) -> Dict[str, Any]:
        """
        Get room discussion state
        Args:
            room_id: Room identifier
        Returns: Discussion state
        """
        room = self.get_room(room_id)
        current_speaker = room.get_current_speaker()
        
        return {
            "active": room.status == RoomStatus.IN_PROGRESS,
            "topic": room.topic,
            "currentSpeaker": current_speaker.to_dict() if current_speaker else None,
            "timeRemaining": room.time_remaining,
            "round": room.current_round,
            "participantCount": len(room.participants)
        }

    def change_user_role(self, room_id: str, user_id: str, new_role: str) -> bool:
        """
        Change user role in room
        Args:
            room_id: Room identifier
            user_id: User identifier
            new_role: New role ('speaker' or 'listener')
        Returns: Success status
        """
        if new_role not in ["speaker", "listener", "host"]:
            return False

        room = self.get_room(room_id)
        participant = room.get_participant_by_id(user_id)
        
        if participant:
            old_role = participant.role.value
            # Map role string to enum
            role_map = {
                "host": ParticipantRole.HOST,
                "speaker": ParticipantRole.PARTICIPANT,
                "listener": ParticipantRole.LISTENER
            }
            participant.role = role_map.get(new_role.lower(), ParticipantRole.LISTENER)
            print(f"🔄 Changed {participant.anonymous_name} role from {old_role} to {new_role} in room {room_id}")
            return True
        
        return False

    def get_role_stats(self, room_id: str) -> Dict[str, Any]:
        """
        Get role statistics for a room
        Args:
            room_id: Room identifier
        Returns: Role statistics
        """
        room = self.get_room(room_id)
        speakers = [p for p in room.participants if p.role == ParticipantRole.PARTICIPANT]
        listeners = [p for p in room.participants if p.role == ParticipantRole.LISTENER]
        
        return {
            "totalParticipants": len(room.participants),
            "speakers": len(speakers),
            "listeners": len(listeners),
            "speakerList": [p.to_dict() for p in speakers],
            "listenerList": [p.to_dict() for p in listeners]
        }

    def can_become_speaker(self, room_id: str, max_speakers: int = 6) -> bool:
        """
        Check if user can become speaker (based on room limits)
        Args:
            room_id: Room identifier
            max_speakers: Maximum allowed speakers (default: 6)
        Returns: Can become speaker
        """
        stats = self.get_role_stats(room_id)
        return stats["speakers"] < max_speakers

    def cleanup_room(self, room_id: str):
        """
        Clean up room resources
        Args:
            room_id: Room identifier
        """
        if room_id in self.rooms:
            room = self.rooms[room_id]
            
            # Clear any active timers (would need async handling in real implementation)
            if room.timer:
                # In Python with asyncio, we'd cancel the task here
                pass
            
            # Remove the room
            del self.rooms[room_id]
            print(f"🧹 Cleaned up empty room: {room_id}")

    def get_all_rooms(self) -> List[Dict[str, Any]]:
        """
        Get all rooms (for debugging/monitoring)
        Returns: Array of room summaries
        """
        return [
            {
                "id": room.room_code,
                "participantCount": len(room.participants),
                "discussionActive": room.status == RoomStatus.IN_PROGRESS,
                "round": room.current_round,
                "createdAt": room.created_at
            }
            for room in self.rooms.values()
        ]

    def get_stats(self) -> Dict[str, Any]:
        """
        Get server statistics
        Returns: Server stats
        """
        total_participants = sum(len(room.participants) for room in self.rooms.values())
        active_discussions = sum(1 for room in self.rooms.values() if room.status == RoomStatus.IN_PROGRESS)
        
        return {
            "totalRooms": len(self.rooms),
            "totalParticipants": total_participants,
            "activeDiscussions": active_discussions,
            "timestamp": datetime.now().isoformat()
        }


# Singleton instance
room_manager = RoomManager()
