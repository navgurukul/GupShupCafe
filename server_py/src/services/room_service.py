from src.database.db_connection import conn, cursor
from src.services.participant_service import participant_service
from src.services.agent_service import AgentService, agent_service
from src.models.participant_pydantic_models import ParticipantModel
from src.models.room_pydantic_models import (
    CreateRoomModel, RoomModel, CreateRoomResponseModel,
    UpdateRoomResponseModel, ListRoomsResponseModel, 
    UpdateRoomModel, DeleteRoomResponseModel,
    RoomStatus
)
from src.models.enums import CEFRLevel
import uuid
import sys
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add the project root directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))


class Room_service:
    def __init__(self):
        self.conn = conn
        self.cursor = cursor

    def create_room(self, room_model: CreateRoomModel) -> CreateRoomResponseModel:
        """Service to handle room creation"""
        try:
            from datetime import datetime
            room_id = uuid.uuid4().hex
            created_at = datetime.now()

            self.cursor.execute(
                """INSERT INTO rooms (
                    room_id, room_name, topic_title, topic_category, 
                    max_participants, speaking_time_per_turn, num_rounds, cefr_level,
                    status, current_round, current_speaker_index,
                    participant_count, created_at, started_at, ended_at, 
                    duration_seconds, facilitator_agent_id, english_agent_id, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    room_id,
                    room_model.room_name,
                    room_model.topic_title,
                    room_model.topic_category,
                    room_model.max_participants,
                    room_model.speaking_time_per_turn,
                    room_model.num_rounds,
                    room_model.cefr_level.value,
                    room_model.status.value,
                    room_model.current_round,
                    room_model.current_speaker_index,
                    room_model.participant_count,
                    created_at,
                    room_model.started_at,
                    room_model.ended_at,
                    room_model.duration_seconds,
                    room_model.facilitator_agent_id,
                    room_model.english_agent_id,
                    room_model.created_by
                )
            )
            self.conn.commit()

            # Fetch the created room to return complete data
            created_room = RoomModel(
                room_id=room_id,
                room_name=room_model.room_name,
                topic_title=room_model.topic_title,
                topic_category=room_model.topic_category,
                max_participants=room_model.max_participants,
                speaking_time_per_turn=room_model.speaking_time_per_turn,
                num_rounds=room_model.num_rounds,
                cefr_level=room_model.cefr_level,
                status=room_model.status,
                current_round=room_model.current_round,
                current_speaker_index=room_model.current_speaker_index,
                participant_count=room_model.participant_count,
                started_at=room_model.started_at,
                ended_at=room_model.ended_at,
                duration_seconds=room_model.duration_seconds,
                facilitator_agent_id=room_model.facilitator_agent_id,
                english_agent_id=room_model.english_agent_id,
                created_by=room_model.created_by,
                created_at=created_at
            )

            return CreateRoomResponseModel(
                status="success",
                data=created_room,
                message="Room created successfully"
            )
        except Exception as e:
            print(f"Error during room creation: {e}")
            return CreateRoomResponseModel(
                status="failure",
                data=None,
                message=f"Room creation failed: {e}"
            )

    def get_room(self, room_id: str) -> CreateRoomResponseModel:
        try:
            self.cursor.execute(
                "SELECT * FROM rooms WHERE room_id=?", (room_id,))
            row = self.cursor.fetchone()
            if not row:
                return CreateRoomResponseModel(
                    status="failure",
                    data=None,
                    message="Room not found"
                )
            cols = [d[0] for d in self.cursor.description]
            room_dict = dict(zip(cols, row))
            
            # Convert CEFR level string to enum
            if 'cefr_level' in room_dict and room_dict['cefr_level']:
                room_dict['cefr_level'] = CEFRLevel(room_dict['cefr_level'])
            
            # Convert status string to enum
            if 'status' in room_dict and room_dict['status']:
                room_dict['status'] = RoomStatus(room_dict['status'])
            
            room_data = RoomModel(**room_dict)
            return CreateRoomResponseModel(
                status="success",
                data=room_data,
                message="Room found"
            )
        except Exception as e:
            print(f"Error getting room: {e}")
            return CreateRoomResponseModel(
                status="failure",
                data=None,
                message="Failed to get room"
            )

    def list_rooms(self) -> ListRoomsResponseModel:
        try:
            self.cursor.execute("SELECT * FROM rooms ORDER BY created_at DESC")
            rows = self.cursor.fetchall()
            cols = [d[0] for d in self.cursor.description]
            rooms_data = []
            for r in rows:
                room_dict = dict(zip(cols, r))
                # Convert CEFR level string to enum
                if 'cefr_level' in room_dict and room_dict['cefr_level']:
                    room_dict['cefr_level'] = CEFRLevel(room_dict['cefr_level'])
                # Convert status string to enum
                if 'status' in room_dict and room_dict['status']:
                    room_dict['status'] = RoomStatus(room_dict['status'])
                rooms_data.append(RoomModel(**room_dict))
            
            return ListRoomsResponseModel(
                status="success",
                data=rooms_data,
                message="Rooms listed"
            )
        except Exception as e:
            print(f"Error listing rooms: {e}")
            return ListRoomsResponseModel(
                status="failure",
                data=[],
                message="Failed to list rooms"
            )

    def list_rooms_by_status(self, status: str) -> ListRoomsResponseModel:
        """List rooms filtered by status"""
        try:
            self.cursor.execute(
                "SELECT * FROM rooms WHERE status=? ORDER BY created_at DESC",
                (status,)
            )
            rows = self.cursor.fetchall()
            cols = [d[0] for d in self.cursor.description]
            rooms_data = []
            for r in rows:
                room_dict = dict(zip(cols, r))
                # Convert CEFR level string to enum
                if 'cefr_level' in room_dict and room_dict['cefr_level']:
                    room_dict['cefr_level'] = CEFRLevel(room_dict['cefr_level'])
                # Convert status string to enum
                if 'status' in room_dict and room_dict['status']:
                    room_dict['status'] = RoomStatus(room_dict['status'])
                rooms_data.append(RoomModel(**room_dict))
            
            return ListRoomsResponseModel(
                status="success",
                data=rooms_data,
                message=f"Rooms listed for status='{status}'"
            )
        except Exception as e:
            print(f"Error listing rooms by status: {e}")
            return ListRoomsResponseModel(
                status="failure",
                data=[],
                message="Failed to list rooms by status"
            )

    def update_room(self, room_id: str, update_model: UpdateRoomModel) -> UpdateRoomResponseModel:
        try:
            # Build update fields from the model
            fields = []
            values = []
            
            for k, v in update_model.items():
                if v is not None:
                    fields.append(f"{k}=?")
                    # Handle enum values
                    if hasattr(v, 'value'):
                        values.append(v.value)
                    else:
                        values.append(v)
            
            if not fields:
                return UpdateRoomResponseModel(
                    status="failure", 
                    data=None, 
                    message="No fields to update"
                )
            
            values.append(room_id)
            sql = f"UPDATE rooms SET {', '.join(fields)} WHERE room_id=?"
            self.cursor.execute(sql, tuple(values))
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                # Return the updated room data
                updated_room = self.get_room(room_id)
                if updated_room.status == "success":
                    return UpdateRoomResponseModel(
                        status="success", 
                        data=update_model, 
                        message="Room updated successfully"
                    )
            
            return UpdateRoomResponseModel(
                status="failure", 
                data=None, 
                message="Room not found or no changes made"
            )
        except Exception as e:
            print(f"Error updating room: {e}")
            self.conn.rollback()
            return UpdateRoomResponseModel(
                status="failure", 
                data=None, 
                message=f"Failed to update room: {e}"
            )

    def delete_room(self, room_id: str) -> DeleteRoomResponseModel:
        try:
            self.cursor.execute(
                "DELETE FROM rooms WHERE room_id=?", (room_id,))
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                return DeleteRoomResponseModel(
                    status="success", 
                    data=room_id, 
                    message="Room deleted successfully"
                )
            else:
                return DeleteRoomResponseModel(
                    status="failure", 
                    data=room_id, 
                    message="Room not found"
                )
        except Exception as e:
            print(f"Error deleting room: {e}")
            self.conn.rollback()
            return DeleteRoomResponseModel(
                status="failure", 
                data=room_id, 
                message=f"Failed to delete room: {e}"
            )



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
            room.remove_participant(participant.get("participant"))
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
        listeners = [p for p in room.participants if p.get(
            "role") == "listener"]

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
                "roomId": room.room_id,
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
        host = next(
            (p for p in room.participants if p.get("role") == "host"), None)
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
            print(
                f"Assigned new host: {new_host.get('anonymousName', 'Unknown')} in room {room_id}")
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

            print(
                f"Preserved host state for {participant.get('anonymousName', 'Unknown')} in room {room_id}")
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

                print(
                    f"Restored host privileges for {participant.get('anonymousName', 'Unknown')} in room {room_id}")
                return True

        return False

    async def start_discussion(self, room_id: str, payload: dict) -> UpdateRoomResponseModel:
        """Start the discussion in a room"""
        # Call agent.create_room_agents
        facilitator_id, english_id = await AgentService.create_room_agents(room_id, payload.get("topic_category", None))
        if facilitator_id is None or english_id is None:
            return UpdateRoomResponseModel(
                status="failure", 
                data=None, 
                message="Failed to create room agents"
            )

        try:
            self.cursor.execute(
                "UPDATE rooms SET status=?, started_at=?, facilitator_agent_id=?, english_agent_id=? WHERE room_id=?",
                (RoomStatus.IN_PROGRESS.value, datetime.now(), facilitator_id, english_id, room_id)
            )
            self.conn.commit()
            if self.cursor.rowcount > 0:
                # Create an update model for the response
                update_model = UpdateRoomModel(
                    room_id=room_id,
                    status=RoomStatus.IN_PROGRESS,
                    started_at=datetime.now(),
                    facilitator_agent_id=facilitator_id,
                    english_agent_id=english_id
                )
                return UpdateRoomResponseModel(
                    status="success", 
                    data=update_model, 
                    message="Discussion started"
                )
            return UpdateRoomResponseModel(
                status="failure", 
                data=None, 
                message="Room not found"
            )
        except Exception as e:
            print(f"Error starting discussion: {e}")
            self.conn.rollback()
            return UpdateRoomResponseModel(
                status="failure", 
                data=None, 
                message=f"Failed to start discussion: {e}"
            )


# Singleton instance
room_service = Room_service()
