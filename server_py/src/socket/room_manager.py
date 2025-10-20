"""
Room Manager
Manages discussion rooms and participants
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from ..models import RoomStatus, CreateRoomModel, CreateParticipantModel, Room, Participant
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

        # Get role as string
        role = user_data.get("role", "listener")
        if isinstance(role, str):
            # Map role string to standardized values
            role_map = {
                "host": "host",
                "speaker": "speaker",
                "listener": "listener"
            }
            role = role_map.get(role.lower(), "listener")

        # Create participant dictionary for the room
        participant_dict = {
            "id": user_data.get("id"),
            "socketId": user_data.get("socketId"),
            "anonymousName": user_data.get("anonymousName"),
            "name": user_data.get("name"),
            "campus": user_data.get("campus"),
            "location": user_data.get("location"),
            "role": role,
            "isReady": user_data.get("isReady", False),
            "joinedAt": user_data.get("joinedAt", datetime.now().isoformat())
        }

        # Add participant (handles reconnection)
        room.add_participant(participant_dict)

        print(
            f"Added {participant_dict['anonymousName']} to room {room_id}. Total: {len(room.participants)}")
        return participant_dict

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
            room.remove_participant(participant.get("socketId"))
            print(
                f"Removed user {user_id} from room {room_id}. Remaining: {len(room.participants)}")

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
            # Update participant dictionary directly
            for key, value in updates.items():
                participant[key] = value

            print(f"Updated user {user_id} in room {room_id}: {updates}")

    def get_room_participants(self, room_id: str) -> List[Dict[str, Any]]:
        """
        Get room participants
        Args:
            room_id: Room identifier
        Returns: Array of participants
        """
        room = self.get_room(room_id)
        return room.participants  # Already dictionaries, no need to convert

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
            "currentSpeaker": current_speaker if current_speaker else None,
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
            old_role = participant.get("role", "listener")
            # Update role in dictionary
            participant["role"] = new_role.lower()
            print(
                f"Changed {participant.get('anonymousName', 'Unknown')} role from {old_role} to {new_role} in room {room_id}")
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
        speakers = [p for p in room.participants if p.get("role") == "speaker"]
        listeners = [p for p in room.participants if p.get("role") == "listener"]

        return {
            "totalParticipants": len(room.participants),
            "speakers": len(speakers),
            "listeners": len(listeners),
            "speakerList": speakers,  # Already dictionaries
            "listenerList": listeners  # Already dictionaries
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

    def get_host(self, room_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current host of a room
        Args:
            room_id: Room identifier
        Returns: Host participant or None
        """
        room = self.get_room(room_id)
        if not room.participants:
            return None
        
        # First check for explicit host role
        host = next((p for p in room.participants if p.get("role") == "host"), None)
        if host:
            return host
        
        # Fallback to first participant
        return room.participants[0] if room.participants else None

    def assign_new_host(self, room_id: str) -> Optional[Dict[str, Any]]:
        """
        Assign a new host when the current host leaves
        Args:
            room_id: Room identifier
        Returns: New host participant or None
        """
        room = self.get_room(room_id)
        if not room.participants:
            return None
        
        # Find the first available participant to become host
        new_host = None
        for participant in room.participants:
            if participant.get("role") != "host":  # Don't reassign if already host
                new_host = participant
                break
        
        if new_host:
            # Update the participant's role to host
            new_host["role"] = "host"
            print(f"Assigned new host: {new_host.get('anonymousName', 'Unknown')} in room {room_id}")
            return new_host
        
        return None

    def is_host(self, room_id: str, user_id: str) -> bool:
        """
        Check if a user is the host of a room
        Args:
            room_id: Room identifier
            user_id: User identifier
        Returns: True if user is host
        """
        host = self.get_host(room_id)
        return host and host.get("id") == user_id

    def preserve_host_state(self, room_id: str, user_id: str) -> Dict[str, Any]:
        """
        Preserve host state when host disconnects
        Args:
            room_id: Room identifier
            user_id: User identifier
        Returns: Preserved host state
        """
        room = self.get_room(room_id)
        participant = room.get_participant_by_id(user_id)
        
        if participant and participant.get("role") == "host":
            # Store host state for potential restoration
            host_state = {
                "id": participant.get("id"),
                "anonymousName": participant.get("anonymousName"),
                "name": participant.get("name"),
                "campus": participant.get("campus"),
                "location": participant.get("location"),
                "role": "host",
                "isReady": participant.get("isReady", False),
                "wasHost": True,
                "disconnectedAt": datetime.now().isoformat()
            }
            
            # Store in room metadata for restoration
            if not hasattr(room, 'metadata'):
                room.metadata = {}
            room.metadata['previous_host'] = host_state
            
            print(f"Preserved host state for {participant.get('anonymousName', 'Unknown')} in room {room_id}")
            return host_state
        
        return {}

    def restore_host_privileges(self, room_id: str, user_id: str) -> bool:
        """
        Restore host privileges if user was previously the host
        Args:
            room_id: Room identifier
            user_id: User identifier
        Returns: True if host privileges were restored
        """
        room = self.get_room(room_id)
        participant = room.get_participant_by_id(user_id)
        
        if not participant:
            return False
        
        # Check if this user was the previous host
        if hasattr(room, 'metadata') and room.metadata.get('previous_host'):
            prev_host = room.metadata['previous_host']
            if prev_host.get('id') == user_id:
                # Restore host role
                participant["role"] = "host"
                participant["isReady"] = prev_host.get("isReady", False)
                
                # Clear previous host metadata
                del room.metadata['previous_host']
                
                print(f"Restored host privileges for {participant.get('anonymousName', 'Unknown')} in room {room_id}")
                return True
        
        return False


# Singleton instance
room_manager = RoomManager()
