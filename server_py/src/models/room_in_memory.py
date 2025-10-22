"""
In-Memory Room and Participant Classes
Simple classes for managing room state in memory
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from .enums import CEFRLevel, ParticipantRole
from .room_pydantic_models import RoomStatus


@dataclass
class Participant:
    """In-memory participant representation"""
    participant_id: str
    user_id: str
    room_id: str
    anonymous_name: str
    avatar_color: Optional[str] = None
    role: str = "participant"
    is_ready: bool = False
    turn_order: int = 0
    is_speaking: bool = False
    is_muted: bool = False
    socket_id: Optional[str] = None
    starting_cefr_level: str = "A0"
    ending_cefr_level: Optional[str] = None
    joined_at: datetime = field(default_factory=datetime.now)
    left_at: Optional[datetime] = None
    campusOrLocation: Optional[str] = None
    speaking_time_seconds: int = 0


@dataclass
class Room:
    """In-memory room representation"""
    room_id: str
    room_name: Optional[str] = None
    topic_title: str = "General Discussion"
    topic_category: str = "general"
    max_participants: int = 6
    speaking_time_per_turn: int = 60
    num_rounds: int = 3
    cefr_level: CEFRLevel = CEFRLevel.A1
    status: RoomStatus = RoomStatus.WAITING
    current_round: int = 0
    current_speaker_index: int = 0
    rounds_completed: int = 0
    participant_count: int = 0
    participants: List[Participant] = field(default_factory=list)
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_seconds: int = 0
    facilitator_agent_id: Optional[str] = None
    english_agent_id: Optional[str] = None
    created_by: str = "system"
    created_at: datetime = field(default_factory=datetime.now)
    time_remaining: int = 60  # For real-time countdown
    
    # Additional fields for real-time management
    topic: Dict[str, str] = field(default_factory=lambda: {"title": "General Discussion", "category": "general"})
    speaking_time: int = 60  # Alias for speaking_time_per_turn
    
    def get_participant_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get participant by user ID"""
        for participant in self.participants:
            if participant.user_id == user_id:
                return {
                    "id": participant.user_id,
                    "socketId": participant.socket_id,
                    "anonymousName": participant.anonymous_name,
                    "name": participant.anonymous_name,  # Use anonymous_name as name
                    "campus": None,
                    "location": None,
                    "role": participant.role,
                    "isReady": participant.is_ready,
                    "joinedAt": participant.joined_at.isoformat() if participant.joined_at else None
                }
        return None
    
    def get_participant_by_socket(self, socket_id: str) -> Optional[Dict[str, Any]]:
        """Get participant by socket ID"""
        for participant in self.participants:
            if participant.socket_id == socket_id:
                return {
                    "id": participant.user_id,
                    "socketId": participant.socket_id,
                    "anonymousName": participant.anonymous_name,
                    "name": participant.anonymous_name,  # Use anonymous_name as name
                    "campus": None,
                    "location": None,
                    "role": participant.role,
                    "isReady": participant.is_ready,
                    "joinedAt": participant.joined_at.isoformat() if participant.joined_at else None
                }
        return None
    
    def add_participant(self, participant_data: Dict[str, Any]):
        """Add participant to room"""
        # Check if participant already exists
        existing = self.get_participant_by_id(participant_data.get("id"))
        if existing:
            # Update existing participant
            for p in self.participants:
                if p.user_id == participant_data.get("id"):
                    p.socket_id = participant_data.get("socketId")
                    p.anonymous_name = participant_data.get("anonymousName")
                    p.role = participant_data.get("role", "listener")
                    p.is_ready = participant_data.get("isReady", False)
                    break
        else:
            # Add new participant
            participant = Participant(
                participant_id=participant_data.get("id", ""),
                user_id=participant_data.get("id", ""),
                room_id=self.room_id,
                anonymous_name=participant_data.get("anonymousName", ""),
                socket_id=participant_data.get("socketId"),
                role=participant_data.get("role", "listener"),
                is_ready=participant_data.get("isReady", False)
            )
            self.participants.append(participant)
    
    def remove_participant(self, socket_id: str):
        """Remove participant by socket ID"""
        self.participants = [p for p in self.participants if p.socket_id != socket_id]
    
    def get_current_speaker(self) -> Optional[Dict[str, Any]]:
        """Get current speaker"""
        if not self.participants or self.current_speaker_index >= len(self.participants):
            return None
        
        speaker = self.participants[self.current_speaker_index]
        return {
            "id": speaker.user_id,
            "socketId": speaker.socket_id,
            "anonymousName": speaker.anonymous_name,
            "name": speaker.anonymous_name,
            "role": speaker.role,
            "isReady": speaker.is_ready
        }
    
    def advance_turn(self) -> Optional[Dict[str, Any]]:
        """Advance to next speaker"""
        if not self.participants:
            return None
        
        self.current_speaker_index = (self.current_speaker_index + 1) % len(self.participants)
        return self.get_current_speaker()
    
    def is_current_speaker(self, user_id: str) -> bool:
        """Check if user is current speaker"""
        current_speaker = self.get_current_speaker()
        return current_speaker and current_speaker.get("id") == user_id