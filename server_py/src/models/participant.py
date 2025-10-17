"""
Participant Model
Represents a participant in a discussion room
"""

from typing import List, Optional
from datetime import datetime
from .enums import ParticipantRole


class Participant:
    """Participant in a roundtable discussion"""
    
    def __init__(
        self,
        id: str,
        socket_id: str,
        anonymous_name: str,
        avatar_color: str = "#3B82F6",
        role: ParticipantRole = ParticipantRole.LISTENER,
        is_ready: bool = False,
        is_speaking: bool = False,
        is_muted: bool = False,
        cefr_level: str = "A1",
        transcripts: Optional[List[str]] = None,
        name: Optional[str] = None,
        campus: Optional[str] = None,
        location: Optional[str] = None,
        joined_at: Optional[str] = None
    ):
        self.id = id
        self.socket_id = socket_id
        self.anonymous_name = anonymous_name
        self.avatar_color = avatar_color
        self.role = role if isinstance(role, ParticipantRole) else ParticipantRole(role)
        self.is_ready = is_ready
        self.is_speaking = is_speaking
        self.is_muted = is_muted
        self.cefr_level = cefr_level
        self.transcripts = transcripts or []
        self.name = name
        self.campus = campus
        self.location = location
        self.joined_at = joined_at or datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        """Convert participant to dictionary"""
        return {
            "id": self.id,
            "socketId": self.socket_id,
            "anonymousName": self.anonymous_name,
            "avatarColor": self.avatar_color,
            "role": self.role.value,
            "isReady": self.is_ready,
            "isSpeaking": self.is_speaking,
            "isMuted": self.is_muted,
            "cefrLevel": self.cefr_level,
            "transcripts": self.transcripts,
            "name": self.name,
            "campus": self.campus,
            "location": self.location,
            "joinedAt": self.joined_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Participant':
        """Create participant from dictionary"""
        return cls(
            id=data.get("id"),
            socket_id=data.get("socketId"),
            anonymous_name=data.get("anonymousName"),
            avatar_color=data.get("avatarColor", "#3B82F6"),
            role=data.get("role", ParticipantRole.LISTENER),
            is_ready=data.get("isReady", False),
            is_speaking=data.get("isSpeaking", False),
            is_muted=data.get("isMuted", False),
            cefr_level=data.get("cefrLevel", "A1"),
            transcripts=data.get("transcripts", []),
            name=data.get("name"),
            campus=data.get("campus"),
            location=data.get("location"),
            joined_at=data.get("joinedAt")
        )
    
    def __repr__(self) -> str:
        return f"Participant(id={self.id}, name={self.anonymous_name}, role={self.role.value})"
