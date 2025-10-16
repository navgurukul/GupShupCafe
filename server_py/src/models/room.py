"""
Room Model
Represents a discussion room with participants
"""

from typing import List, Optional
from datetime import datetime
from .participant import Participant
from .enums import RoomStatus


class Room:
    """Discussion room managing participants and turn-based speaking"""
    
    def __init__(
        self,
        room_code: str,
        topic: Optional[str] = None,
        participants: Optional[List[Participant]] = None,
        status: RoomStatus = RoomStatus.WAITING,
        current_speaker_index: int = 0,
        current_round: int = 1,
        max_rounds: int = 3,
        speaking_time: int = 60,
        created_at: Optional[str] = None,
        started_at: Optional[str] = None,
        ended_at: Optional[str] = None,
        time_remaining: int = 0
    ):
        self.room_code = room_code
        self.topic = topic
        self.participants = participants or []
        self.status = status if isinstance(status, RoomStatus) else RoomStatus(status)
        self.current_speaker_index = current_speaker_index
        self.current_round = current_round
        self.max_rounds = max_rounds
        self.speaking_time = speaking_time
        self.created_at = created_at or datetime.now().isoformat()
        self.started_at = started_at
        self.ended_at = ended_at
        self.time_remaining = time_remaining
        self.timer = None  # For async timer management
    
    def add_participant(self, participant: Participant) -> None:
        """Add a participant to the room"""
        # Remove if already exists (reconnection)
        self.remove_participant(participant.socket_id)
        self.participants.append(participant)
    
    def remove_participant(self, sid: str) -> Optional[Participant]:
        """Remove a participant by socket ID"""
        for i, p in enumerate(self.participants):
            if p.socket_id == sid:
                return self.participants.pop(i)
        return None
    
    def get_participant_by_id(self, user_id: str) -> Optional[Participant]:
        """Get participant by user ID"""
        for p in self.participants:
            if p.id == user_id:
                return p
        return None
    
    def get_participant_by_socket(self, socket_id: str) -> Optional[Participant]:
        """Get participant by socket ID"""
        for p in self.participants:
            if p.socket_id == socket_id:
                return p
        return None
    
    def set_participant_ready(self, sid: str, ready: bool = True) -> bool:
        """Set participant ready status"""
        participant = self.get_participant_by_socket(sid)
        if participant:
            participant.is_ready = ready
            return True
        return False
    
    def all_ready(self) -> bool:
        """Check if all participants are ready"""
        if not self.participants:
            return False
        return all(p.is_ready for p in self.participants)
    
    def get_current_speaker(self) -> Optional[Participant]:
        """Get the current speaker"""
        if not self.participants or self.current_speaker_index >= len(self.participants):
            return None
        return self.participants[self.current_speaker_index]
    
    def advance_turn(self) -> Optional[Participant]:
        """Advance to the next speaker"""
        if not self.participants:
            return None
        
        self.current_speaker_index += 1
        
        # Check if we've completed a round
        if self.current_speaker_index >= len(self.participants):
            self.current_speaker_index = 0
            self.current_round += 1
            
            # Check if we've completed all rounds
            if self.current_round > self.max_rounds:
                self.status = RoomStatus.COMPLETED
                self.ended_at = datetime.now().isoformat()
                return None
        
        return self.get_current_speaker()
    
    def to_dict(self) -> dict:
        """Convert room to dictionary"""
        current_speaker = self.get_current_speaker()
        
        return {
            "id": self.room_code,
            "roomCode": self.room_code,
            "topic": self.topic,
            "participants": [p.to_dict() for p in self.participants],
            "status": self.status.value,
            "discussion": {
                "active": self.status == RoomStatus.IN_PROGRESS,
                "topic": self.topic,
                "currentSpeakerIndex": self.current_speaker_index,
                "currentSpeaker": current_speaker.to_dict() if current_speaker else None,
                "speakingTime": self.speaking_time,
                "timeRemaining": self.time_remaining,
                "round": self.current_round,
                "startedAt": self.started_at,
                "endedAt": self.ended_at
            },
            "participantCount": len(self.participants),
            "createdAt": self.created_at,
            "startedAt": self.started_at,
            "endedAt": self.ended_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Room':
        """Create room from dictionary"""
        participants = [
            Participant.from_dict(p) if isinstance(p, dict) else p
            for p in data.get("participants", [])
        ]
        
        return cls(
            room_code=data.get("roomCode") or data.get("id"),
            topic=data.get("topic"),
            participants=participants,
            status=data.get("status", RoomStatus.WAITING),
            current_speaker_index=data.get("currentSpeakerIndex", 0),
            current_round=data.get("currentRound", 1),
            max_rounds=data.get("maxRounds", 3),
            speaking_time=data.get("speakingTime", 60),
            created_at=data.get("createdAt"),
            started_at=data.get("startedAt"),
            ended_at=data.get("endedAt"),
            time_remaining=data.get("timeRemaining", 0)
        )
    
    def __repr__(self) -> str:
        return f"Room(code={self.room_code}, status={self.status.value}, participants={len(self.participants)})"
