"""
Enums
Enumeration types used across the application
"""

from enum import Enum


class RoomStatus(str, Enum):
    """Room status enumeration"""
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ParticipantRole(str, Enum):
    """Participant role enumeration"""
    HOST = "host"
    PARTICIPANT = "speaker"  
    LISTENER = "listener"


class CEFRLevel(str, Enum):
    """CEFR language proficiency level enumeration"""
    A0 = "A0"  # Beginner
    A1 = "A1"  # Elementary
    A2 = "A2"  # Pre-intermediate
    B1 = "B1"  # Intermediate
    B2 = "B2"  # Upper-intermediate
    C1 = "C1"  # Advanced
    C2 = "C2"  # Proficiency
