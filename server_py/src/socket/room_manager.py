"""
Room Manager
Manages discussion rooms and participants
"""

from typing import Dict, List, Any, Optional
from datetime import datetime


class RoomManager:
    """Manages discussion rooms and participants"""
    
    def __init__(self):
        self.rooms: Dict[str, Dict[str, Any]] = {}
        self._skip_cleanup = False

    def get_room(self, room_id: str) -> Dict[str, Any]:
        """
        Get or create a room
        Args:
            room_id: Room identifier
        Returns: Room object
        """
        if room_id not in self.rooms:
            self.rooms[room_id] = {
                "id": room_id,
                "participants": [],
                "discussion": {
                    "active": False,
                    "topic": None,
                    "currentSpeakerIndex": 0,
                    "speakingTime": 60,
                    "timeRemaining": 0,
                    "round": 1,
                    "timer": None,
                    "startedAt": None,
                    "endedAt": None
                },
                "createdAt": datetime.now().isoformat()
            }
        return self.rooms[room_id]

    def add_user_to_room(self, room_id: str, user_data: Dict[str, Any]):
        """
        Add user to room
        Args:
            room_id: Room identifier
            user_data: User data
        """
        room = self.get_room(room_id)
        
        # Remove user if already in room (reconnection)
        self._skip_cleanup = True
        self.remove_user_from_room(room_id, user_data.get("id"))
        self._skip_cleanup = False
        
        # Add user to room
        room["participants"].append({
            "id": user_data.get("id"),
            "socketId": user_data.get("socketId"),
            "anonymousName": user_data.get("anonymousName"),
            "name": user_data.get("name"),
            "campus": user_data.get("campus"),
            "location": user_data.get("location"),
            "role": user_data.get("role", "listener"),
            "isReady": user_data.get("isReady", False),
            "joinedAt": user_data.get("joinedAt", datetime.now().isoformat())
        })
        
        print(f"➕ Added {user_data.get('anonymousName')} to room {room_id}. Total: {len(room['participants'])}")

    def remove_user_from_room(self, room_id: str, user_id: str):
        """
        Remove user from room
        Args:
            room_id: Room identifier
            user_id: User identifier
        """
        room = self.get_room(room_id)
        initial_count = len(room["participants"])
        
        room["participants"] = [p for p in room["participants"] if p["id"] != user_id]
        
        if len(room["participants"]) != initial_count:
            print(f"➖ Removed user {user_id} from room {room_id}. Remaining: {len(room['participants'])}")
        
        # Clean up empty rooms
        if len(room["participants"]) == 0 and not self._skip_cleanup:
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
        
        for participant in room["participants"]:
            if participant["id"] == user_id:
                participant.update(updates)
                print(f"🔄 Updated user {user_id} in room {room_id}: {updates}")
                break

    def get_room_participants(self, room_id: str) -> List[Dict[str, Any]]:
        """
        Get room participants
        Args:
            room_id: Room identifier
        Returns: Array of participants
        """
        room = self.get_room(room_id)
        return [
            {
                "id": p["id"],
                "anonymousName": p["anonymousName"],
                "isReady": p["isReady"],
                "joinedAt": p["joinedAt"],
                "socketId": p["socketId"],
                "role": p.get("role", "listener")
            }
            for p in room["participants"]
        ]

    def get_discussion_state(self, room_id: str) -> Dict[str, Any]:
        """
        Get room discussion state
        Args:
            room_id: Room identifier
        Returns: Discussion state
        """
        room = self.get_room(room_id)
        discussion = room["discussion"]
        
        current_speaker = None
        if discussion["active"] and room["participants"]:
            idx = discussion["currentSpeakerIndex"]
            if 0 <= idx < len(room["participants"]):
                current_speaker = room["participants"][idx]
        
        return {
            "active": discussion["active"],
            "topic": discussion["topic"],
            "currentSpeaker": current_speaker,
            "timeRemaining": discussion["timeRemaining"],
            "round": discussion["round"],
            "participantCount": len(room["participants"])
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
        if new_role not in ["speaker", "listener"]:
            return False

        room = self.get_room(room_id)
        
        for participant in room["participants"]:
            if participant["id"] == user_id:
                old_role = participant.get("role", "listener")
                participant["role"] = new_role
                print(f"🔄 Changed {participant['anonymousName']} role from {old_role} to {new_role} in room {room_id}")
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
        speakers = [p for p in room["participants"] if p.get("role") == "speaker"]
        listeners = [p for p in room["participants"] if p.get("role") == "listener"]
        
        return {
            "totalParticipants": len(room["participants"]),
            "speakers": len(speakers),
            "listeners": len(listeners),
            "speakerList": speakers,
            "listenerList": listeners
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
            if room["discussion"].get("timer"):
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
                "id": room_id,
                "participantCount": len(room["participants"]),
                "discussionActive": room["discussion"]["active"],
                "round": room["discussion"]["round"],
                "createdAt": room["createdAt"]
            }
            for room_id, room in self.rooms.items()
        ]

    def get_stats(self) -> Dict[str, Any]:
        """
        Get server statistics
        Returns: Server stats
        """
        total_participants = sum(len(room["participants"]) for room in self.rooms.values())
        active_discussions = sum(1 for room in self.rooms.values() if room["discussion"]["active"])
        
        return {
            "totalRooms": len(self.rooms),
            "totalParticipants": total_participants,
            "activeDiscussions": active_discussions,
            "timestamp": datetime.now().isoformat()
        }


# Singleton instance
room_manager = RoomManager()
