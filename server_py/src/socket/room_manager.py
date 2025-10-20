"""
Room Manager
Manages discussion rooms and participants
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from ..models import RoomStatus, CreateRoomModel, CreateParticipantModel, Room
from ..models.participant_pydantic_models import Participant
from ..models.enums import CEFRLevel, ParticipantRole


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
                room_id=room_id,
                room_name="General",
                topic={"title": "General Discussion", "category": "general"},
                max_participants=6,
                speaking_time=60,
                num_rounds=3,
                cefr_level="A1",
                status=RoomStatus.WAITING,
                current_round=0,
                current_speaker_index=0,
                participants=[],
                started_at=None,
                ended_at=None,
                time_remaining=60,
                created_by="system"
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

        # Get role as string and map to enum
        role_str = user_data.get("role", "listener").lower()
        role_map = {
            "host": ParticipantRole.HOST,
            "speaker": ParticipantRole.PARTICIPANT,
            "listener": ParticipantRole.LISTENER
        }
        role = role_map.get(role_str, ParticipantRole.LISTENER)

        # Create participant object
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

        print(
            f"➕ Added {participant.anonymous_name} to room {room_id}. Total: {len(room.participants)}")
        return participant.to_dict()

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
            print(
                f"➖ Removed user {user_id} from room {room_id}. Remaining: {len(room.participants)}")

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
            # The participant is now a Pydantic model, so we can update it directly.
            # The `update_participant` method on the Room model handles this.
            room.update_participant(user_id, updates)

            print(f"🔄 Updated user {user_id} in room {room_id}: {updates}")

    def get_room_participants(self, room_id: str) -> List[Dict[str, Any]]:
        """
        Get room participants
        Args:
            room_id: Room identifier
        Returns: Array of participants as dictionaries
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
            old_role = participant.role
            participant.change_role(new_role)
            print(
                f"🔄 Changed {participant.anonymous_name} role from {old_role} to {new_role} in room {room_id}")
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
        speakers = [p for p in room.participants if p.role == "speaker"]
        listeners = [p for p in room.participants if p.role == "listener"]

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
        total_participants = sum(len(room.participants)
                                 for room in self.rooms.values())
        active_discussions = sum(
            1 for room in self.rooms.values() if room.status == RoomStatus.IN_PROGRESS)

        return {
            "totalRooms": len(self.rooms),
            "totalParticipants": total_participants,
            "activeDiscussions": active_discussions,
            "timestamp": datetime.now().isoformat()
        }


# Singleton instance
room_manager = RoomManager()
