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
    PARTICIPANT = "speaker"  # Maps to 'speaker' for backward compatibility
    LISTENER = "listener"
