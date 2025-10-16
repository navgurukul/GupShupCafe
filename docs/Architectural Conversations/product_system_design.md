# Gup-Shup Café - MVP System Architecture & 3-Day Hackathon Plan

**Project**: Gup-Shup Café - AI-Powered English Speaking Skills Platform  
**Hackathon**: AWS AI Agent Hackathon 2025  
**Timeline**: 3 Days  
**Repository**: https://github.com/navgurukul/GupShupCafe  
**Date**: October 2025  

---

## Executive Summary

Gup-Shup Café is a gamified, peer-to-peer discussion platform that provides instant AI-driven feedback on English speaking skills using the CEFR framework. This document defines the MVP architecture, prioritizes features for a 3-day hackathon sprint, and provides actionable tasks for a 5-member team.

**Core MVP Loop**: User joins room → Speaks in structured discussion → Receives real-time AI feedback → Tracks progress on CEFR scale

---

## 1. MVP Feature Prioritization

### 1.1 Must-Have Features (Core Loop - Days 1-3)

**Priority 1: Basic Room Operations**
- ✅ User authentication (simple login)
- ✅ Create/join discussion room (max 4-6 participants for MVP)
- ✅ Lobby system with ready-check mechanism
- ✅ Room state management (waiting, active, completed)

**Priority 2: Real-Time Audio Discussion**
- ✅ WebRTC peer-to-peer audio streaming
- ✅ Turn-based speaking system (60-second timers)
- ✅ Visual speaker indicators
- ✅ Microphone mute/unmute controls
- ✅ Basic audio level indicators

**Priority 3: AI Feedback Engine (Core Innovation)**
- ✅ Speech-to-Text (STT) using Web Speech Recognition API (MVP)
- ✅ **AWS Strands Multi-Agent System** for orchestrated AI feedback:
  - **EnglishFeedbackAgent**: Real-time grammar, vocabulary, and fluency analysis
  - **Debate Facilitator Agent**: Manages turn-taking and discussion flow
  - **Multi-Agent Orchestrator**: Coordinates agents and feedback delivery
- ✅ LLM-based feedback on English quality (grammar, vocabulary, fluency)
- ✅ CEFR level estimation (A1-C2 scale)
- ✅ Real-time English Feedback Modal (separate from SpeechToText tab)
  - Instant feedback (2-3 seconds) during speaking
  - Comprehensive analysis at end of discussion
  - Private feedback visible only to speaker
- ✅ Text-to-Speech (TTS) for AI agent responses
- ✅ Real-time feedback display to users
- ✅ **AWS AgentCore** wrapper for production deployment (runtime, identity, internet access)

**Priority 4: Minimal Persistence**
- ✅ Store session data (participants, transcripts, feedback)
- ✅ Track basic CEFR progress per user
- ✅ Save discussion history (last 24 hours for MVP)

### 1.2 Should-Have Features (Post-MVP / Nice-to-Have)

- ⚠️ Advanced topic generation (AI-curated topics)
- ⚠️ Detailed analytics dashboard
- ⚠️ User profiles with historical progress
- ⚠️ Multi-language support
- ⚠️ Mobile app version
- ⚠️ Gamification badges/achievements

### 1.3 Won't-Have for MVP

- ❌ User authentication with social login (OAuth)
- ❌ Payment/subscription systems
- ❌ Advanced moderation features
- ❌ Video streaming
- ❌ Recording and playback
- ❌ Export transcripts/reports

---

## 2. High-Level System Architecture

### 2.1 Component Overview

```
┌────────────────────────────────────────────────────────────────────────┐
│                            CLIENT LAYER                                 │
│  ┌──────────────────────────────────────────────────────────────┐     │
│  │                    React 18 + Vite                            │     │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐            │     │
│  │  │  Pages     │  │  Contexts  │  │ Components │            │     │
│  │  │ - Login    │  │ - Auth     │  │ - Table    │            │     │
│  │  │ - Lobby    │  │ - Socket   │  │ - Timer    │            │     │
│  │  │ - Room     │  │ - Audio    │  │ - Feedback │            │     │
│  │  └────────────┘  └────────────┘  └────────────┘            │     │
│  │                                                               │     │
│  │  ┌─────────────────────────────────────────────┐            │     │
│  │  │           User Data (Stored & Cached)        │            │     │
│  │  │  - CEFR Level: A0, A1, A2, B1, B2, C1, C2   │            │     │
│  │  │  - Topic Interests: Technology, Sports, etc.│            │     │
│  │  │  - Progress History: Session scores & trends│            │     │
│  │  │  (Used for lobby matching in future versions)│            │     │
│  │  └─────────────────────────────────────────────┘            │     │
│  │                                                               │     │
│  │  ┌─────────────────────────────────────────────┐            │     │
│  │  │    WebRTC (Peer-to-Peer Audio Mesh)         │            │     │
│  │  │    - Local/Remote Stream Management          │            │     │
│  │  │    - STUN/TURN for NAT Traversal            │            │     │
│  │  └─────────────────────────────────────────────┘            │     │
│  └──────────────────────────────────────────────────────────────┘     │
│           │                    │                    │                  │
│      REST API          WebSocket (Socket.io)    WebRTC Signaling      │
│           │                    │                    │                  │
└───────────┼────────────────────┼────────────────────┼──────────────────┘
            │                    │                    │
            ▼                    ▼                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                           SERVER LAYER (AWS EC2)                        │
│  ┌──────────────────────────────────────────────────────────────┐     │
│  │              FastAPI + python-socketio                        │     │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │     │
│  │  │ REST API │  │ Socket.io│  │  WebRTC  │  │   CORS   │    │     │
│  │  │ Routes   │  │ Handlers │  │ Signaling│  │Middleware│    │     │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────────┘    │     │
│  └───────┼─────────────┼─────────────┼──────────────────────────┘     │
│          │             │             │                                 │
│  ┌───────▼─────┐  ┌────▼────┐  ┌────▼─────┐                          │
│  │ Room Manager│  │ Session │  │ WebRTC   │                          │
│  │  Service    │  │ Manager │  │ Relay    │                          │
│  └─────┬───────┘  └────┬────┘  └──────────┘                          │
│        │               │                                               │
└────────┼───────────────┼───────────────────────────────────────────────┘
         │               │
         │               ▼
         │    ┌─────────────────┐
         │    │   MongoDB/SQLite │
         │    │   - Users        │
         │    │   - Sessions     │
         │    │   - Participants │
         │    │   - Transcripts  │
         │    │   - Feedback     │
         │    │   - Progress     │
         │    └─────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────────────────────┐
│                  AWS STRANDS MULTI-AGENT SYSTEM                         │
│                     (Wrapped in AWS AgentCore)                          │
│  ┌──────────────────────────────────────────────────────────────┐     │
│  │              Multi-Agent Orchestrator                         │     │
│  │  - Coordinates agents for real-time and comprehensive feedback     │
│  │  - Manages instant (2-3s) vs detailed analysis                │     │
│  │  - Routes feedback to appropriate UI components               │     │
│  └────────────┬─────────────────────────┬──────────────────────┘     │
│               │                         │                             │
│  ┌────────────▼───────────┐  ┌─────────▼──────────────┐              │
│  │ EnglishFeedbackAgent   │  │ Debate Facilitator     │              │
│  │                        │  │      Agent             │              │
│  │ - Grammar analysis     │  │ - Turn management      │              │
│  │ - Vocabulary scoring   │  │ - Topic guidance       │              │
│  │ - Fluency assessment   │  │ - Discussion flow      │              │
│  │ - CEFR level (A1-C2)   │  │ - Participant support  │              │
│  │ - Instant feedback     │  │ - Moderation           │              │
│  └────────────────────────┘  └────────────────────────┘              │
│                                                                        │
│  Powered by:                                                           │
│  - AWS Bedrock (Claude 3 for production)                               │
│  - Gemini API (for development)                                        │
│  - AWS AgentCore (runtime, identity, internet access)                  │
└────────────────────────────────────────────────────────────────────────┘
         │
         │  ⬆ DIRECT CONNECTION TO SERVER LAYER
         │  • FastAPI calls orchestrator.get_english_feedback()
         │  • Server passes transcripts and context to agents
         │  • Agents return feedback via standardized interfaces
         │
         ▼
┌────────────────────────────────────────────────────────────────────────┐
│                    PLUGGABLE AI SERVICE LAYER                           │
│  ┌──────────────────────────────────────────────────────────────┐     │
│  │                  AI Service Abstraction                       │     │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │     │
│  │  │ STT Module  │  │ LLM Module  │  │ TTS Module  │          │     │
│  │  │ (Interface) │  │ (Interface) │  │ (Interface) │          │     │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘          │     │
│  └─────────┼─────────────────┼─────────────────┼─────────────────┘     │
│            │                 │                 │                       │
│  ┌─────────▼───────┐ ┌───────▼───────┐ ┌──────▼──────┐              │
│  │ STT Providers   │ │ LLM Providers │ │TTS Providers│              │
│  │ ┌─────────────┐ │ │ ┌───────────┐ │ │ ┌─────────┐ │              │
│  │ │Web Speech   │ │ │ │  Gemini   │ │ │ │ Browser │ │              │
│  │ │ Recognition │ │ │ │  (Dev)    │ │ │ │   TTS   │ │              │
│  │ └─────────────┘ │ │ └───────────┘ │ │ └─────────┘ │              │
│  │ ┌─────────────┐ │ │ ┌───────────┐ │ │ ┌─────────┐ │              │
│  │ │ AWS         │ │ │ │  Bedrock  │ │ │ │ AWS     │ │              │
│  │ │ Transcribe  │ │ │ │  Claude   │ │ │ │ Polly   │ │              │
│  │ └─────────────┘ │ │ └───────────┘ │ │ └─────────┘ │              │
│  └─────────────────┘ └───────────────┘ └─────────────┘              │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow Sequence (with AWS Strands Multi-Agent System)

```
┌──────────┐          ┌──────────┐          ┌─────────────────┐          ┌──────────────────┐
│  User A  │          │  Server  │          │ AWS Strands     │          │ EnglishFeedback  │
│ (Alice)  │          │ (FastAPI)│          │ Orchestrator    │          │     Agent        │
└────┬─────┘          └────┬─────┘          └────────┬────────┘          └────────┬─────────┘
     │                     │                          │                            │
     │ 1. Join Room        │                          │                            │
     │ ───────────────────>│                          │                            │
     │                     │                          │                            │
     │ 2. Room State       │                          │                            │
     │ <───────────────────│                          │                            │
     │                     │                          │                            │
     │ 3. Speak (Turn)     │                          │                            │
     │ "I thinks AI will   │                          │                            │
     │  replace many jobs" │                          │                            │
     │ ───────────────────>│                          │                            │
     │    (WebRTC Audio)   │                          │                            │
     │                     │                          │                            │
     │                     │ 4. STT Transcript        │                            │
     │                     │ ────────────────────────>│                            │
     │                     │                          │                            │
     │                     │                          │ 5. Quick Analysis Request  │
     │                     │                          │ ─────────────────────────>│
     │                     │                          │    (instant=True, 2-3s)    │
     │                     │                          │                            │
     │                     │                          │ 6. Grammar Feedback        │
     │                     │                          │ <─────────────────────────│
     │                     │                          │    "I thinks" → "I think"  │
     │                     │                          │    CEFR: B1, Score: 7/10   │
     │                     │                          │                            │
     │ 7. English Feedback │ <────────────────────────│                            │
     │    Modal (Private)  │   (Socket: "english-feedback")                        │
     │ ┌──────────────────┐│                          │                            │
     │ │ 📝 Grammar:      ││                          │                            │
     │ │ ⚠ "I thinks"→    ││                          │                            │
     │ │   "I think"      ││                          │                            │
     │ │ ✓ Rest is clear  ││                          │                            │
     │ └──────────────────┘│                          │                            │
     │                     │                          │                            │
     │ 8. Agent mentions   │ <────────────────────────│                            │
     │    feedback gently  │   (TTS: "Alice, great point!                          │
     │    in conversation  │    Quick tip: 'I think' instead of 'I thinks'")       │
     │                     │                          │                            │
     │ [Continue discussion...]                       │                            │
     │                     │                          │                            │
     │ 9. End of Round     │                          │                            │
     │ ───────────────────>│                          │                            │
     │                     │                          │                            │
     │                     │ 10. Comprehensive Analysis│                           │
     │                     │ ────────────────────────>│ ─────────────────────────>│
     │                     │    (instant=False)       │  (All statements, context) │
     │                     │                          │                            │
     │                     │                          │ 11. Detailed Feedback      │
     │                     │                          │ <─────────────────────────│
     │                     │                          │    - Progress tracking     │
     │                     │                          │    - Improvement areas     │
     │                     │                          │    - CEFR trajectory       │
     │                     │                          │                            │
     │ 12. Summary Report  │ <────────────────────────│                            │
     │     Dashboard       │                          │                            │
     │                     │                          │                            │

Example Code (from comment):
```python
# Quick analysis during speaking (2-3 seconds)
english_feedback = orchestrator.get_english_feedback(
    recent_statements, 
    instant=True  # Fast response for real-time UI
)

# Comprehensive analysis at end of discussion
summary = orchestrator.get_english_feedback(
    all_statements,
    instant=False  # Detailed with progress tracking
)
```

Example Output:
```
[Alice]: I thinks AI will replace many jobs.

📝 Grammar Feedback (Private English Feedback Modal):
⚠ Suggestion: "I thinks" should be "I think" (subject-verb agreement).
The rest of your statement is clear and well-structured. (Instant feedbacks are subjective and verbal only)
```

---

## 2.3 Data Models for the Application

### 2.3.1 Core Data Entities

The application uses the following data models to persist user progress, session information, and feedback:

#### User Model

```python
# server_py/src/database/models/user.py
from datetime import datetime
from typing import Optional, List

class User:
    """
    User model tracking individual progress and preferences.
    """
    id: str  # UUID
    email: Optional[str]  # For registered users
    
    # CEFR Progress Tracking (MVP Core Feature)
    current_cefr_level: str  # "A0", "A1", "A2", "B1", "B2", "C1", "C2"
    # A0 = Not yet reached A1, used for complete beginners
    
    cefr_history: List[dict]  # Historical CEFR levels with timestamps
    # Example: [
    #   {"level": "A0", "date": "2025-01-01", "session_id": "abc123"},
    #   {"level": "A1", "date": "2025-01-15", "session_id": "def456"}
    # ]
    
    # Topic Interests (For Future Lobby Matching)
    topic_interests: List[str]  # ["Technology", "Sports", "Politics", "Science", etc.]
    # Note: Lobby matching by CEFR level and topics is a FUTURE FEATURE (not MVP)
    
    # Statistics - not in MVP
    total_sessions: int
    total_speaking_time: int  # seconds
    total_words_spoken: int
    
    # Average Scores (Calculated from feedback - not in MVP)
    avg_grammar_score: float  # 0-10
    avg_vocabulary_score: float  # 0-10
    avg_fluency_score: float  # 0-10
    avg_overall_score: float  # 0-10
    
    # Metadata
    created_at: datetime
    last_active: datetime
    
    # Settings
    notification_preferences: dict
```

#### Session Model

```python
# server_py/src/database/models/session.py
from datetime import datetime
from typing import List, Optional

class Session:
    """
    Discussion session model.
    """
    id: str  # UUID
    room_code: str  # Human-readable room code
    
    # Session Configuration
    topic: str  # Discussion topic
    topic_category: str  # "Technology", "Current Events", etc.
    max_participants: int  # Default: 6
    speaking_time_per_turn: int  # seconds, default: 60
    num_rounds: int  # Default: 3
    
    # Session State
    status: str  # "waiting", "in_progress", "completed", "cancelled"
    current_round: int
    current_speaker_index: int
    
    # Participants
    participant_ids: List[str]  # User IDs
    participant_count: int
    
    # Timing
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    duration_seconds: int
    
    # Facilitator Agent
    facilitator_agent_id: str  # AWS Strands agent instance ID
    
    # Metadata
    created_at: datetime
    created_by: str  # User ID who created the room
```

#### Participant Model

```python
# server_py/src/database/models/participant.py
from datetime import datetime
from typing import List, Optional

class Participant:
    """
    Individual participant in a session.
    """
    id: str  # UUID
    session_id: str
    user_id: str
    
    # Identity
    anonymous_name: str  # Anonymous name like "Blue Panda", "Red Dragon"
    avatar_color: str  # Hex color code
    
    # Session Role
    role: str  # "participant", "host", "listener"
    is_ready: bool  # Ready to start discussion
    
    # Speaking Data
    total_speaking_time: int  # seconds in this session
    total_words_spoken: int
    number_of_turns: int
    
    # Real-Time State
    is_speaking: bool
    is_muted: bool
    socket_id: str  # Socket.io connection ID
    
    # CEFR Level at Session Start (for progress tracking)
    starting_cefr_level: str
    ending_cefr_level: Optional[str]  # Updated at session end
    
    # Connection
    joined_at: datetime
    left_at: Optional[datetime]
    connection_quality: str  # "excellent", "good", "fair", "poor"
```

#### Transcript Model

```python
# server_py/src/database/models/transcript.py
from datetime import datetime
from typing import Optional

class Transcript:
    """
    Individual speech transcript from a participant.
    """
    id: str  # UUID
    session_id: str
    participant_id: str
    user_id: str
    
    # Content
    text: str  # Transcribed speech
    language: str  # "en" for MVP
    confidence: float  # STT confidence (0.0-1.0)
    
    # Context
    round_number: int
    turn_number: int
    speaker_order: int  # Order in this round
    
    # Timing
    started_at: datetime
    ended_at: datetime
    duration_seconds: int
    
    # Audio Metadata
    word_count: int
    speech_rate: float  # words per minute
    
    # Processing Status
    is_processed: bool  # Has feedback been generated?
    processed_at: Optional[datetime]
    
    # Raw Audio Reference (optional, for future features)
    audio_file_url: Optional[str]
```

#### Feedback Model

```python
# server_py/src/database/models/feedback.py
from datetime import datetime
from typing import List, Dict, Optional

class Feedback:
    """
    AI-generated English feedback for a transcript.
    """
    id: str  # UUID
    session_id: str
    participant_id: str
    user_id: str
    transcript_id: str
    
    # Feedback Type
    feedback_type: str  # "instant" (2-3s) or "comprehensive"
    
    # CEFR Assessment
    cefr_level: str  # A0, A1, A2, B1, B2, C1, C2
    cefr_confidence: float  # 0.0-1.0
    
    # Detailed Scores (0-10 scale)
    grammar_score: float
    vocabulary_score: float
    fluency_score: float
    pronunciation_score: Optional[float]  # Future feature
    coherence_score: Optional[float]  # Future feature
    overall_score: float  # Average of available scores
    
    # Grammar Feedback
    grammar_issues: List[Dict]  # [{
    #   "original": "I thinks",
    #   "corrected": "I think",
    #   "reason": "subject-verb agreement",
    #   "severity": "high"  # high, medium, low
    # }]
    
    # Vocabulary Feedback
    vocabulary_level: str  # "basic", "intermediate", "advanced"
    vocabulary_suggestions: List[Dict]  # [{
    #   "word_used": "good",
    #   "alternatives": ["excellent", "remarkable", "outstanding"],
    #   "context": "when praising ideas"
    # }]
    
    # Fluency Feedback
    fluency_issues: List[str]  # ["Long pauses", "Repetitive phrases"]
    fluency_comments: str  # Detailed comments
    
    # Improvement Suggestions
    suggestions: List[str]  # Top 3-5 actionable suggestions
    
    # Positive Feedback
    strengths: List[str]  # What the user did well
    
    # Display Message (For UI)
    display_message: str  # Formatted feedback for modal
    agent_mention: str  # Gentle mention for AI conversation
    
    # AI Agent Info
    agent_id: str  # EnglishFeedbackAgent instance
    agent_model: str  # "gemini-1.5-flash" or "bedrock-claude-3"
    
    # Processing
    generation_time_ms: int  # Time to generate feedback
    created_at: datetime
```

#### Progress Model

```python
# server_py/src/database/models/progress.py
from datetime import datetime
from typing import List, Dict

class Progress:
    """
    User progress tracking over time.
    Aggregates feedback from multiple sessions.
    """
    id: str  # UUID
    user_id: str
    
    # CEFR Trajectory
    cefr_progression: List[Dict]  # [{
    #   "date": "2025-01-15",
    #   "level": "A1",
    #   "session_id": "abc123",
    #   "confidence": 0.85
    # }]
    
    # Score Trends (Last 30 days)
    grammar_trend: List[Dict]  # [{"date": "2025-01-15", "score": 7.5}]
    vocabulary_trend: List[Dict]
    fluency_trend: List[Dict]
    overall_trend: List[Dict]
    
    # Improvement Areas (Identified by AI)
    current_improvement_areas: List[str]  # ["Subject-verb agreement", "Article usage"]
    resolved_improvement_areas: List[Dict]  # [{
    #   "area": "Past tense usage",
    #   "resolved_date": "2025-01-10",
    #   "sessions_to_resolve": 5
    # }]
    
    # Strengths
    identified_strengths: List[str]  # ["Good vocabulary", "Clear pronunciation"]
    
    # Topic Performance
    topic_performance: Dict[str, float]  # {
    #   "Technology": 8.2,
    #   "Sports": 7.5,
    #   "Politics": 6.8
    # }
    
    # Milestones
    milestones_achieved: List[Dict]  # [{
    #   "milestone": "Reached B1 level",
    #   "date": "2025-01-15",
    #   "badge_id": "b1-achiever"
    # }]
    
    # Statistics
    total_sessions: int
    total_speaking_time: int
    total_words_spoken: int
    total_feedback_received: int
    
    # Metadata
    last_calculated: datetime
    next_goal: str  # "Reach B2 level"
```

### 2.3.2 Database Schema Diagram

```
┌─────────────┐
│    User     │
│─────────────│
│ id (PK)     │
│             │
│ email       │◄───────────┐
│ cefr_level  │            │
│ topics[]    │            │
│ stats       │            │
└─────────────┘            │
       │                   │
       │ 1:N               │ 1:1
       ▼                   │
┌─────────────┐            │
│ Participant │            │
│─────────────│            │
│ id (PK)     │            │
│ session_id  │────┐       │
│ user_id (FK)│    │       │
│ display_name│    │       │
│ cefr_level  │    │       │
└─────────────┘    │       │
       │           │       │
       │ 1:N       │ N:1   │
       ▼           ▼       │
┌─────────────┐ ┌─────────────┐
│ Transcript  │ │   Session   │
│─────────────│ │─────────────│
│ id (PK)     │ │ id (PK)     │
│ participant │ │ room_name   │
│ text        │ │ topic       │
│ timestamp   │ │ status      │
└─────────────┘ │ config      │
       │        └─────────────┘
       │ 1:N
       ▼
┌─────────────┐
│  Feedback   │
│─────────────│
│ id (PK)     │
│ transcript  │
│ cefr_level  │
│ scores      │
│ suggestions │
└─────────────┘
       │
       │ N:1
       ▼
┌─────────────┐
│  Progress   │
│─────────────│
│ id (PK)     │────────────────┘
│ user_id (FK)│
│ trends[]    │
│ milestones[]│
└─────────────┘
```

### 2.3.3 Data Flow for User Progress

```
1. User joins session
   └─> Create/Update Participant record

2. User speaks during turn
   └─> Create Transcript record
   └─> Trigger EnglishFeedbackAgent (instant mode, 2-3s)
   └─> Create Feedback record (instant)
   └─> Emit feedback to user's English Feedback Modal (private)

3. Turn ends
   └─> Update Participant stats (speaking_time, word_count)

4. Session ends
   └─> Trigger comprehensive feedback for all transcripts
   └─> Create Feedback records (comprehensive)
   └─> Update Participant ending_cefr_level
   └─> Update Session status to "completed"

5. Background job (post-session)
   └─> Aggregate all session feedback
   └─> Update User current_cefr_level (if changed)
   └─> Update Progress record with trends and milestones
   └─> Update User topic_interests based on session topics
   
6. Future: Lobby Matching (not MVP)
   └─> Query Users by cefr_level range (±1 level)
   └─> Filter by topic_interests
   └─> Suggest matched lobbies
```

### 2.3.4 CEFR Level Definitions (For MVP)

| Level | Name | Description | Expected Scores |
|-------|------|-------------|-----------------|
| **A0** | Pre-A1 | Not yet reached A1, complete beginner | Overall < 3.0 |
| **A1** | Beginner | Basic phrases, simple interactions | Overall 3.0-4.5 |
| **A2** | Elementary | Simple sentences, common topics | Overall 4.5-5.5 |
| **B1** | Intermediate | Express opinions, handle common situations | Overall 5.5-7.0 |
| **B2** | Upper Intermediate | Fluent discussion, complex ideas | Overall 7.0-8.5 |
| **C1** | Advanced | Precise language, subtle meanings | Overall 8.5-9.5 |
| **C2** | Proficient | Native-like fluency and accuracy | Overall 9.5-10.0 |

**Note**: CEFR level and topic interests are stored for **all users in MVP**. However, **lobby matching by these fields is a FUTURE FEATURE** and not part of the 3-day MVP scope.

---

## 3. Pluggable AI Service Layer Design

### 3.1 Design Principles

1. **AWS Strands Multi-Agent Orchestration**: Coordinate multiple specialized agents (EnglishFeedbackAgent, Debate Facilitator)
2. **AWS AgentCore Deployment**: Wrap agents in AgentCore for production runtime, identity management, and internet access
3. **Abstraction**: Each AI service (STT, LLM, TTS) is behind an interface
4. **OpenAI Compatibility**: LLM interface uses standard OpenAI message format
5. **Easy Switching**: Toggle between Gemini (dev) and Bedrock (prod) with config
6. **Fallback Support**: Graceful degradation if AI services fail
7. **Real-Time Feedback**: Instant (2-3s) feedback during speaking + comprehensive analysis post-discussion

### 3.2 Architecture (with AWS Strands)

```
┌────────────────────────────────────────────────────────────────────────┐
│                        AWS AgentCore Runtime                            │
│  ┌──────────────────────────────────────────────────────────────┐     │
│  │           AWS Strands Multi-Agent Orchestrator                │     │
│  │                                                               │     │
│  │  ┌──────────────────────┐    ┌─────────────────────────┐    │     │
│  │  │ EnglishFeedbackAgent │    │ Debate Facilitator Agent │    │     │
│  │  │                      │    │                          │    │     │
│  │  │ - Grammar Analysis   │    │ - Turn Management        │    │     │
│  │  │ - Vocabulary Scoring │    │ - Topic Guidance         │    │     │
│  │  │ - Fluency Assessment │    │ - Discussion Flow        │    │     │
│  │  │ - CEFR Leveling      │    │ - Moderation             │    │     │
│  │  │ - Instant (2-3s)     │    │ - Participant Support    │    │     │
│  │  │ - Comprehensive Mode │    │                          │    │     │
│  │  └──────────────────────┘    └─────────────────────────┘    │     │
│  │                                                               │     │
│  │  orchestrator.get_english_feedback(statements, instant=True) │     │
│  │  orchestrator.get_english_feedback(statements, instant=False)│     │
│  └──────────────────────────────────────────────────────────────┘     │
│                                                                        │
│  AgentCore provides:                                                   │
│  - Runtime environment                                                 │
│  - Identity & permissions                                              │
│  - Internet access for LLM APIs                                        │
│  - Logging & monitoring                                                │
└────────────────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌────────────────────────────────────────────────────────────────┐
│                  AI Service Manager (ai_services.py)            │
│                                                                 │
│  config = {                                                     │
│    "stt_provider": "web_speech_api",    # or "aws_transcribe" │
│    "llm_provider": "gemini",            # or "bedrock"          │
│    "tts_provider": "browser_tts",       # or "aws_polly"       │
│    "agent_orchestrator": "aws_strands"  # Multi-agent system   │
│  }                                                              │
└────────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  STTInterface   │  │  LLMInterface   │  │  TTSInterface   │
│  (Abstract)     │  │  (Abstract)     │  │  (Abstract)     │
└─────────────────┘  └─────────────────┘  └─────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ WebSpeechSTT    │  │  GeminiLLM      │  │  BrowserTTS     │
│ AWSTranscribeSTT│  │  BedrockLLM     │  │  AWSPollyTTS    │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### 3.3 Interface Definitions

#### STTInterface
```python
# server_py/src/ai/stt_interface.py
from abc import ABC, abstractmethod
from typing import Optional

class STTInterface(ABC):
    """Abstract interface for Speech-to-Text providers."""
    
    @abstractmethod
    async def transcribe(self, audio_data: bytes, language: str = "en") -> dict:
        """
        Transcribe audio to text.
        
        Args:
            audio_data: Raw audio bytes (WAV/PCM format)
            language: Language code (default: "en")
            
        Returns:
            {
                "success": bool,
                "text": str,
                "confidence": float,  # 0.0-1.0
                "language": str,
                "provider": str
            }
        """
        pass
    
    @abstractmethod
    def get_supported_languages(self) -> list[str]:
        """Return list of supported language codes."""
        pass
```

#### LLMInterface (OpenAI-Compatible)
```python
# server_py/src/ai/llm_interface.py
from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class LLMInterface(ABC):
    """
    Abstract interface for Language Model providers.
    Uses OpenAI message format for compatibility.
    """
    
    @abstractmethod
    async def chat(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> dict:
        """
        Generate chat completion.
        
        Args:
            messages: OpenAI-style messages
                [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello!"},
                    {"role": "assistant", "content": "Hi there!"}
                ]
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            {
                "success": bool,
                "message": {
                    "role": "assistant",
                    "content": str
                },
                "usage": {
                    "prompt_tokens": int,
                    "completion_tokens": int,
                    "total_tokens": int
                },
                "provider": str
            }
        """
        pass
    
    @abstractmethod
    async def analyze_english(self, transcript: str, context: dict) -> dict:
        """
        Analyze English speaking quality based on CEFR.
        
        Args:
            transcript: User's spoken text
            context: {
                "previous_feedback": List[dict],
                "topic": str,
                "participant_name": str
            }
            
        Returns:
            {
                "success": bool,
                "cefr_level": str,  # A1, A2, B1, B2, C1, C2
                "score": float,     # 0.0-10.0
                "feedback": {
                    "grammar": {"score": float, "issues": List[str]},
                    "vocabulary": {"score": float, "level": str},
                    "fluency": {"score": float, "comments": str},
                    "pronunciation": {"score": float, "notes": str}
                },
                "suggestions": List[str],
                "provider": str
            }
        """
        pass
```

#### TTSInterface
```python
# server_py/src/ai/tts_interface.py
from abc import ABC, abstractmethod

class TTSInterface(ABC):
    """Abstract interface for Text-to-Speech providers."""
    
    @abstractmethod
    async def synthesize(
        self, 
        text: str, 
        voice: str = "default",
        language: str = "en"
    ) -> dict:
        """
        Synthesize speech from text.
        
        Args:
            text: Text to speak
            voice: Voice ID/name
            language: Language code
            
        Returns:
            {
                "success": bool,
                "audio_url": str,  # URL or base64 data URI
                "audio_format": str,  # "mp3", "wav", etc.
                "duration": float,  # seconds
                "provider": str
            }
        """
        pass
    
    @abstractmethod
    def get_available_voices(self, language: str = "en") -> list[dict]:
        """Return list of available voices for language."""
        pass
```

### 3.4 Concrete Implementations (MVP)

#### Gemini LLM (Development)
```python
# server_py/src/ai/gemini_llm.py
import google.generativeai as genai
from .llm_interface import LLMInterface

class GeminiLLM(LLMInterface):
    """Gemini API implementation for development."""
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
    
    async def chat(self, messages, temperature=0.7, max_tokens=500):
        # Convert OpenAI format to Gemini format
        prompt = self._convert_messages(messages)
        
        response = await self.model.generate_content_async(
            prompt,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens
            }
        )
        
        return {
            "success": True,
            "message": {
                "role": "assistant",
                "content": response.text
            },
            "usage": {
                "prompt_tokens": 0,  # Gemini doesn't provide this
                "completion_tokens": 0,
                "total_tokens": 0
            },
            "provider": "gemini"
        }
    
    async def analyze_english(self, transcript, context):
        prompt = f"""
        Analyze this English transcript based on CEFR standards (A1-C2).
        
        Transcript: "{transcript}"
        Topic: {context.get('topic', 'General conversation')}
        
        Provide:
        1. CEFR Level (A1/A2/B1/B2/C1/C2)
        2. Grammar score (0-10)
        3. Vocabulary score (0-10)
        4. Fluency score (0-10)
        5. Top 3 improvement suggestions
        
        Format as JSON.
        """
        
        response = await self.chat([
            {"role": "system", "content": "You are an English language expert."},
            {"role": "user", "content": prompt}
        ])
        
        # Parse and structure response
        # (Implementation details...)
        
        return {
            "success": True,
            "cefr_level": "B1",
            "score": 7.5,
            "feedback": {...},
            "suggestions": [...],
            "provider": "gemini"
        }
```

#### Bedrock LLM (Production)
```python
# server_py/src/ai/bedrock_llm.py
import boto3
import json
from .llm_interface import LLMInterface

class BedrockLLM(LLMInterface):
    """AWS Bedrock (Claude) implementation for production."""
    
    def __init__(self, region: str = "us-east-1", model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"):
        self.client = boto3.client("bedrock-runtime", region_name=region)
        self.model_id = model_id
    
    async def chat(self, messages, temperature=0.7, max_tokens=500):
        # Convert OpenAI format to Claude format
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages
        }
        
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body)
        )
        
        result = json.loads(response['body'].read())
        
        return {
            "success": True,
            "message": {
                "role": "assistant",
                "content": result['content'][0]['text']
            },
            "usage": {
                "prompt_tokens": result['usage']['input_tokens'],
                "completion_tokens": result['usage']['output_tokens'],
                "total_tokens": result['usage']['input_tokens'] + result['usage']['output_tokens']
            },
            "provider": "bedrock"
        }
    
    async def analyze_english(self, transcript, context):
        # Similar to Gemini but using Bedrock
        # (Implementation details...)
        pass
```

### 3.5 Configuration & Factory Pattern

```python
# server_py/src/ai/ai_service_manager.py
from .stt_interface import STTInterface
from .llm_interface import LLMInterface
from .tts_interface import TTSInterface
from .web_speech_stt import WebSpeechSTT
from .gemini_llm import GeminiLLM
from .bedrock_llm import BedrockLLM
from .browser_tts import BrowserTTS

class AIServiceManager:
    """Factory for creating and managing AI services."""
    
    def __init__(self, config: dict):
        self.config = config
        self._stt = None
        self._llm = None
        self._tts = None
    
    def get_stt(self) -> STTInterface:
        if not self._stt:
            provider = self.config.get("stt_provider", "web_speech_api")
            if provider == "web_speech_api":
                self._stt = WebSpeechSTT()
            elif provider == "aws_transcribe":
                # self._stt = AWSTranscribeSTT()
                pass
        return self._stt
    
    def get_llm(self) -> LLMInterface:
        if not self._llm:
            provider = self.config.get("llm_provider", "gemini")
            if provider == "gemini":
                api_key = self.config.get("gemini_api_key")
                self._llm = GeminiLLM(api_key)
            elif provider == "bedrock":
                self._llm = BedrockLLM()
        return self._llm
    
    def get_tts(self) -> TTSInterface:
        if not self._tts:
            provider = self.config.get("tts_provider", "browser_tts")
            if provider == "browser_tts":
                self._tts = BrowserTTS()
            elif provider == "aws_polly":
                # self._tts = AWSPollyTTS()
                pass
        return self._tts

# Usage in main application
ai_manager = AIServiceManager({
    "stt_provider": "web_speech_api",
    "llm_provider": "gemini",  # Switch to "bedrock" for production
    "tts_provider": "browser_tts",
    "gemini_api_key": os.getenv("GEMINI_API_KEY")
})

llm = ai_manager.get_llm()
feedback = await llm.analyze_english(transcript, context)
```

### 3.6 AWS Strands Multi-Agent Orchestrator (Core Innovation)

The AWS Strands Multi-Agent Orchestrator coordinates specialized agents to provide real-time English feedback and facilitate discussions. This is the key innovation for the MVP.

#### 3.6.1 Orchestrator Implementation

```python
# server_py/src/ai/aws_strands_orchestrator.py
from aws_agentcore import AgentCore
from typing import List, Dict, Optional

class AWSStrandsOrchestrator:
    """
    Multi-agent orchestrator using AWS Strands.
    Coordinates EnglishFeedbackAgent and Debate Facilitator Agent.
    """
    
    def __init__(self, agentcore_config: dict):
        """
        Initialize with AWS AgentCore for runtime, identity, and internet access.
        
        Args:
            agentcore_config: Configuration for AWS AgentCore deployment
        """
        self.agentcore = AgentCore(agentcore_config)
        self.english_agent = None
        self.facilitator_agent = None
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize specialized agents."""
        # EnglishFeedbackAgent for grammar, vocabulary, fluency analysis
        self.english_agent = self.agentcore.create_agent(
            name="EnglishFeedbackAgent",
            capabilities=["grammar_analysis", "cefr_leveling", "instant_feedback"]
        )
        
        # Debate Facilitator Agent for turn management and discussion flow
        self.facilitator_agent = self.agentcore.create_agent(
            name="DebateFacilitatorAgent",
            capabilities=["turn_management", "topic_guidance", "moderation"]
        )
    
    async def get_english_feedback(
        self,
        statements: List[Dict[str, str]],
        instant: bool = True,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Get English feedback from the multi-agent system.
        
        Args:
            statements: List of recent statements with format:
                [
                    {"speaker": "Alice", "text": "I thinks AI will replace jobs"},
                    {"speaker": "Bob", "text": "That's an interesting point"}
                ]
            instant: If True, return quick analysis (2-3 seconds).
                    If False, return comprehensive analysis with progress tracking.
            context: Optional context including previous feedback, topic, etc.
        
        Returns:
            Feedback dictionary with grammar, vocabulary, fluency scores and suggestions
        
        Example Usage:
            # Quick analysis during speaking (2-3 seconds)
            english_feedback = orchestrator.get_english_feedback(
                recent_statements, 
                instant=True  # Fast response for real-time UI
            )
            
            # Comprehensive analysis at end of discussion
            summary = orchestrator.get_english_feedback(
                all_statements,
                instant=False  # Detailed with progress tracking
            )
        """
        context = context or {}
        
        if instant:
            # Fast analysis for real-time feedback modal
            return await self._instant_feedback(statements, context)
        else:
            # Comprehensive analysis with progress tracking
            return await self._comprehensive_feedback(statements, context)
    
    async def _instant_feedback(self, statements: List[Dict], context: Dict) -> Dict:
        """
        Provide instant feedback (2-3 seconds) for real-time display.
        Focuses on most recent statement.
        """
        if not statements:
            return {"success": False, "error": "No statements provided"}
        
        latest = statements[-1]
        
        # Quick analysis by EnglishFeedbackAgent
        result = await self.english_agent.analyze({
            "text": latest["text"],
            "mode": "instant",
            "previous_feedback": context.get("previous_feedback", [])
        })
        
        # Format for English Feedback Modal
        return {
            "success": True,
            "speaker": latest["speaker"],
            "feedback_type": "instant",
            "response_time": "2-3s",
            "grammar": {
                "score": result.get("grammar_score", 0),
                "issues": result.get("grammar_issues", []),
                "suggestions": result.get("grammar_suggestions", [])
            },
            "vocabulary": {
                "score": result.get("vocabulary_score", 0),
                "level": result.get("vocabulary_level", "intermediate")
            },
            "fluency": {
                "score": result.get("fluency_score", 0),
                "comments": result.get("fluency_comments", "")
            },
            "cefr_level": result.get("cefr_level", "B1"),
            "overall_score": result.get("overall_score", 7.0),
            "display_message": self._format_feedback_message(result),
            "agent_mention": self._format_gentle_mention(latest["speaker"], result)
        }
    
    async def _comprehensive_feedback(self, statements: List[Dict], context: Dict) -> Dict:
        """
        Provide comprehensive feedback at end of discussion.
        Analyzes all statements and tracks progress.
        """
        # Detailed analysis by EnglishFeedbackAgent
        result = await self.english_agent.analyze({
            "statements": statements,
            "mode": "comprehensive",
            "context": context
        })
        
        return {
            "success": True,
            "feedback_type": "comprehensive",
            "participants": self._analyze_per_participant(statements, result),
            "progress_tracking": {
                "cefr_trajectory": result.get("cefr_progression", []),
                "improvement_areas": result.get("improvement_areas", []),
                "strengths": result.get("strengths", [])
            },
            "session_summary": result.get("summary", ""),
            "recommendations": result.get("recommendations", [])
        }
    
    def _format_feedback_message(self, result: Dict) -> str:
        """
        Format feedback for English Feedback Modal display.
        
        Example Output:
        [Alice]: I thinks AI will replace many jobs.
        
        📝 Grammar Feedback:
        ⚠ Suggestion: "I thinks" should be "I think" (subject-verb agreement).
        The rest of your statement is clear and well-structured.
        """
        issues = result.get("grammar_issues", [])
        if not issues:
            return "✓ Your grammar is clear and correct!"
        
        message = "📝 Grammar Feedback:\n"
        for issue in issues:
            message += f"⚠ Suggestion: {issue['original']} → {issue['corrected']} ({issue['reason']})\n"
        
        if result.get("positive_note"):
            message += f"\n{result['positive_note']}"
        
        return message
    
    def _format_gentle_mention(self, speaker: str, result: Dict) -> str:
        """
        Format gentle feedback mention for agent's conversation.
        Agent mentions feedback subtly during discussion.
        """
        issues = result.get("grammar_issues", [])
        if not issues:
            return f"{speaker}, great point!"
        
        main_issue = issues[0]
        return (
            f"{speaker}, great point! "
            f"Quick tip: '{main_issue['corrected']}' instead of '{main_issue['original']}'"
        )
    
    def _analyze_per_participant(self, statements: List[Dict], result: Dict) -> Dict:
        """Analyze feedback per participant for summary."""
        participants = {}
        for stmt in statements:
            speaker = stmt["speaker"]
            if speaker not in participants:
                participants[speaker] = {
                    "statements_count": 0,
                    "cefr_levels": [],
                    "grammar_scores": [],
                    "vocabulary_scores": []
                }
            participants[speaker]["statements_count"] += 1
        
        # Add detailed analysis from result
        for speaker, data in result.get("per_participant", {}).items():
            if speaker in participants:
                participants[speaker].update(data)
        
        return participants


# Usage in FastAPI endpoint
@app.post("/api/ai/instant-feedback")
async def get_instant_feedback(request: FeedbackRequest):
    """
    Endpoint for real-time English feedback during speaking.
    Returns feedback in 2-3 seconds for English Feedback Modal.
    """
    orchestrator = get_strands_orchestrator()
    
    feedback = await orchestrator.get_english_feedback(
        statements=request.recent_statements,
        instant=True,
        context={
            "previous_feedback": request.previous_feedback,
            "topic": request.topic,
            "participant_name": request.speaker
        }
    )
    
    # Emit to specific participant only (private feedback)
    await socketio.emit(
        "english-feedback",
        feedback,
        room=request.participant_socket_id
    )
    
    return {"success": True, "feedback_sent": True}


@app.post("/api/ai/comprehensive-feedback")
async def get_comprehensive_feedback(request: ComprehensiveFeedbackRequest):
    """
    Endpoint for detailed feedback at end of discussion.
    Includes progress tracking and recommendations.
    """
    orchestrator = get_strands_orchestrator()
    
    summary = await orchestrator.get_english_feedback(
        statements=request.all_statements,
        instant=False,
        context={
            "session_id": request.session_id,
            "topic": request.topic,
            "duration": request.duration
        }
    )
    
    return summary
```

#### 3.6.2 English Feedback Modal (Frontend)

The English Feedback Modal is a separate UI component from the SpeechToText tab. It displays private, real-time feedback visible only to the speaker.

```javascript
// client/src/components/EnglishFeedbackModal.jsx
import React, { useState, useEffect } from 'react';
import { useSocket } from '../contexts/SocketContext';

const EnglishFeedbackModal = ({ isOpen, onClose }) => {
  const [feedback, setFeedback] = useState(null);
  const socket = useSocket();
  
  useEffect(() => {
    if (!socket) return;
    
    // Listen for private English feedback
    socket.on('english-feedback', (data) => {
      setFeedback(data);
    });
    
    return () => {
      socket.off('english-feedback');
    };
  }, [socket]);
  
  if (!isOpen || !feedback) return null;
  
  return (
    <div className="fixed bottom-20 right-4 w-96 bg-white rounded-lg shadow-xl p-4 z-50">
      <div className="flex justify-between items-start mb-3">
        <h3 className="text-lg font-semibold text-gray-800">
          📝 English Feedback
        </h3>
        <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
          ✕
        </button>
      </div>
      
      <div className="space-y-3">
        {/* CEFR Level Badge */}
        <div className="flex items-center gap-2">
          <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
            CEFR: {feedback.cefr_level}
          </span>
          <span className="text-sm text-gray-600">
            Score: {feedback.overall_score}/10
          </span>
        </div>
        
        {/* Grammar Feedback */}
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-3 rounded">
          <p className="text-sm font-medium text-yellow-800 mb-1">Grammar</p>
          {feedback.grammar.issues.map((issue, idx) => (
            <p key={idx} className="text-sm text-gray-700">
              ⚠ {issue.original} → {issue.corrected}
              <span className="text-gray-500 ml-1">({issue.reason})</span>
            </p>
          ))}
          {feedback.grammar.issues.length === 0 && (
            <p className="text-sm text-green-700">✓ Clear and correct!</p>
          )}
        </div>
        
        {/* Vocabulary & Fluency Scores */}
        <div className="grid grid-cols-2 gap-2">
          <div className="bg-gray-50 p-2 rounded">
            <p className="text-xs text-gray-600">Vocabulary</p>
            <p className="text-lg font-semibold">{feedback.vocabulary.score}/10</p>
          </div>
          <div className="bg-gray-50 p-2 rounded">
            <p className="text-xs text-gray-600">Fluency</p>
            <p className="text-lg font-semibold">{feedback.fluency.score}/10</p>
          </div>
        </div>
        
        {/* Display Message */}
        <div className="text-sm text-gray-700 whitespace-pre-line">
          {feedback.display_message}
        </div>
      </div>
    </div>
  );
};

export default EnglishFeedbackModal;
```

#### 3.6.3 Integration with AWS AgentCore

```python
# server_py/src/deployment/agentcore_config.py
import os
from aws_agentcore import AgentCoreConfig

def get_agentcore_config():
    """
    Configure AWS AgentCore for production deployment.
    Provides runtime, identity, and internet access for agents.
    """
    return AgentCoreConfig(
        runtime_environment={
            "python_version": "3.11",
            "memory_mb": 2048,
            "timeout_seconds": 30
        },
        identity={
            "iam_role": os.getenv("AGENTCORE_IAM_ROLE"),
            "permissions": [
                "bedrock:InvokeModel",
                "transcribe:StartStreamTranscription",
                "polly:SynthesizeSpeech"
            ]
        },
        internet_access={
            "enabled": True,
            "allowed_domains": [
                "generativelanguage.googleapis.com",  # Gemini API
                "bedrock-runtime.us-east-1.amazonaws.com"  # Bedrock
            ]
        },
        logging={
            "cloudwatch_log_group": "/aws/agentcore/gupshup-cafe",
            "log_level": "INFO"
        },
        monitoring={
            "metrics_enabled": True,
            "traces_enabled": True
        }
    )


# Initialize orchestrator with AgentCore
orchestrator = AWSStrandsOrchestrator(get_agentcore_config())
```

---

## 4. AWS Cloud Architecture

### 4.1 Infrastructure Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          AWS CLOUD (us-east-1)                           │
│                                                                          │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                    AWS AMPLIFY HOSTING                             │ │
│  │  ┌──────────────────────────────────────────────────────────────┐ │ │
│  │  │                  Frontend (React + Vite)                      │ │ │
│  │  │  - Static files (HTML, JS, CSS)                              │ │ │
│  │  │  - CloudFront CDN distribution                               │ │ │
│  │  │  - Auto SSL certificate (HTTPS)                              │ │ │
│  │  │  - CI/CD from GitHub                                         │ │ │
│  │  └──────────────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                    │                                    │
│                         HTTPS/WSS  │                                    │
│                                    ▼                                    │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                    VPC (Virtual Private Cloud)                     │ │
│  │                                                                    │ │
│  │  ┌─────────────────────────────────────────────────────────────┐ │ │
│  │  │               Public Subnet (10.0.1.0/24)                    │ │ │
│  │  │                                                              │ │ │
│  │  │  ┌──────────────────────────────────────────────────────┐  │ │ │
│  │  │  │      EC2 Instance (t2.small or t3.medium)            │  │ │ │
│  │  │  │                                                       │  │ │ │
│  │  │  │  - Ubuntu 22.04 LTS                                  │  │ │ │
│  │  │  │  - Python 3.11 + FastAPI                            │  │ │ │
│  │  │  │  - python-socketio                                   │  │ │ │
│  │  │  │  - Nginx (reverse proxy)                            │  │ │ │
│  │  │  │  - Systemd service management                        │  │ │ │
│  │  │  │                                                       │  │ │ │
│  │  │  │  Ports:                                              │  │ │ │
│  │  │  │  - 22 (SSH - restricted to admin IP)                │  │ │ │
│  │  │  │  - 80 (HTTP - redirects to 443)                     │  │ │ │
│  │  │  │  - 443 (HTTPS/WSS - public)                         │  │ │ │
│  │  │  │  - 3003 (Internal FastAPI - via Nginx)              │  │ │ │
│  │  │  └──────────────────────────────────────────────────────┘  │ │ │
│  │  │                           │                                 │ │ │
│  │  └───────────────────────────┼─────────────────────────────────┘ │ │
│  │                              │                                   │ │
│  └──────────────────────────────┼───────────────────────────────────┘ │
│                                 │                                     │
│  ┌──────────────────────────────▼───────────────────────────────────┐ │
│  │                    Security Group (sg-gupshup-api)                │ │
│  │                                                                   │ │
│  │  Inbound Rules:                                                  │ │
│  │  - SSH (22): Admin IP only                                       │ │
│  │  - HTTP (80): 0.0.0.0/0 (redirect to HTTPS)                     │ │
│  │  - HTTPS (443): 0.0.0.0/0                                        │ │
│  │                                                                   │ │
│  │  Outbound Rules:                                                 │ │
│  │  - All traffic: 0.0.0.0/0 (for API calls)                       │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                 │                                     │
│  ┌──────────────────────────────▼───────────────────────────────────┐ │
│  │                    EBS Volume (Elastic Block Storage)             │ │
│  │  - 20 GB gp3 (general purpose SSD)                               │ │
│  │  - Stores: Application code, MongoDB/SQLite DB, Logs             │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │          AWS Strands Multi-Agent System (AgentCore)              │   │
│  │  ┌────────────────────────────────────────────────────────────┐ │   │
│  │  │            Multi-Agent Orchestrator                         │ │   │
│  │  │  - Coordinates EnglishFeedbackAgent & Debate Facilitator    │ │   │
│  │  │  - Instant feedback (2-3s) + Comprehensive analysis         │ │   │
│  │  │  - Runtime, identity, internet access via AgentCore         │ │   │
│  │  └────────────────────────────────────────────────────────────┘ │   │
│  │                                                                  │   │
│  │  Powered by AWS Bedrock (Claude 3) + Gemini (dev)               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │              AWS Bedrock (AI/ML Services)                        │   │
│  │  ┌────────────────┐  ┌────────────────┐  ┌─────────────────┐   │   │
│  │  │ Claude 3       │  │ Amazon Polly   │  │ AWS Transcribe  │   │   │
│  │  │ (Anthropic)    │  │ (TTS)          │  │ (STT)           │   │   │
│  │  │ - LLM Analysis │  │ - Voice Synth  │  │ - Speech-to-Text│   │   │
│  │  │ - CEFR Feedback│  │                │  │                 │   │   │
│  │  └────────────────┘  └────────────────┘  └─────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                  CloudWatch (Monitoring)                         │   │
│  │  - EC2 metrics (CPU, memory, network)                           │   │
│  │  - Application logs                                              │   │
│  │  - Alarms for high CPU/memory                                    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                  Route 53 (DNS - Optional)                       │   │
│  │  - api.gupshup-cafe.com → EC2 Elastic IP                        │   │
│  │  - gupshup-cafe.com → Amplify                                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

                                    │
                                    │  Internet
                                    │
                        ┌───────────▼───────────┐
                        │   Users (Browsers)    │
                        │  - Chrome/Firefox     │
                        │  - WebRTC P2P Audio   │
                        └───────────────────────┘
```

### 4.2 Network Flow

```
┌───────────┐
│  User A   │ ─────────────────┐
└───────────┘                  │
                               ▼
┌───────────┐          ┌────────────────┐
│  User B   │ ────────►│ CloudFront CDN │
└───────────┘          │ (Amplify)      │
                       └────────┬───────┘
┌───────────┐                  │
│  User C   │ ─────────────────┘
└───────────┘
         │
         │ HTTPS/WSS (443)
         │
         ▼
┌─────────────────────┐
│ AWS EC2 Instance    │
│ (Nginx → FastAPI)   │
│                     │
│ • REST API          │
│ • WebSocket Events  │
│ • WebRTC Signaling  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  AWS Bedrock API    │
│  • Claude 3 (LLM)   │
│  • Amazon Polly     │
│  • AWS Transcribe   │
└─────────────────────┘

WebRTC Audio (P2P):
User A ◄──────────► User B  (Direct, no server relay)
User A ◄──────────► User C
User B ◄──────────► User C
```

### 4.3 Cost Estimation (MVP - 3 Months)

| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| **AWS Amplify** | Build minutes: 100 mins<br>Hosting: 5 GB storage, 15 GB data transfer | $5-10 |
| **EC2 (t3.medium)** | 1 instance, 2 vCPU, 4 GB RAM<br>730 hours/month | $30 |
| **EBS Storage** | 20 GB gp3 | $2 |
| **Data Transfer** | 50 GB/month (free tier covers first 100 GB) | $0-5 |
| **AWS Bedrock (Claude 3 Sonnet)** | ~10,000 requests/month<br>~1M input tokens, ~200K output tokens | $15-25 |
| **Amazon Polly** | 1M characters TTS | $4 |
| **AWS Transcribe** | 100 hours audio | $24 |
| **CloudWatch** | Basic monitoring + logs | $3 |
| **Route 53** (Optional) | Hosted zone + queries | $1 |
| **Total (Estimated)** | | **$84-104/month** |

**Note**: For MVP, you can reduce costs by:
- Using Gemini API (free tier) instead of Bedrock
- Using Web Speech API (browser STT/TTS) - **$0 cost**
- Using t2.micro (free tier) for first year
- **Estimated MVP cost with free services: $5-15/month**

---

## 5. Team Task Distribution & 3-Day Action Plan

### 5.1 Team Composition

| Role | Responsibilities | Key Skills |
|------|-----------------|------------|
| **Product Lead (Full-Stack + AI)** | Architecture, AI integration, coordination | FastAPI, React, LLMs, AWS |
| **Frontend Developer** | React UI, WebRTC, real-time features | React, Socket.io, WebRTC, Tailwind |
| **AI Engineer #1** | LLM integration, CEFR feedback, prompt engineering | Gemini/Bedrock, NLP, Python |
| **AI Engineer #2** | STT/TTS integration, audio processing | Speech APIs, Audio processing |
| **AWS DevOps Specialist** | Infrastructure, deployment, CI/CD | AWS (EC2, Amplify, Bedrock), Docker, Nginx |

### 5.2 Day 1: Foundation & Core Setup

#### Product Lead (Full-Stack + AI)
- [ ] **Hour 1-2**: Review existing codebase, document current state
- [ ] **Hour 3-4**: Set up project structure for AI service layer
  - Create `ai_services/` directory structure
  - Define interface classes (STTInterface, LLMInterface, TTSInterface)
  - Set up configuration management
- [ ] **Hour 5-6**: Implement basic AIServiceManager factory
- [ ] **Hour 7-8**: Integrate LLM basic chat endpoint with FastAPI
  - POST `/api/ai/analyze` endpoint
  - Test with sample transcript

#### Frontend Developer
- [ ] **Hour 1-2**: Audit existing React components (Login, Lobby, Roundtable)
- [ ] **Hour 3-4**: Set up feedback display components
  - Create `FeedbackPanel` component
  - Create `CEFRLevelIndicator` component
  - Create `SpeakingStatsCard` component
- [ ] **Hour 5-6**: Wire Socket.io events for AI feedback
  - Listen for `ai-feedback` event
  - Display real-time feedback in UI
- [ ] **Hour 7-8**: Test end-to-end flow (dummy data)

#### AI Engineer #1 (LLM)
- [ ] **Hour 1-2**: Research Gemini API for CEFR analysis
- [ ] **Hour 3-4**: Implement `GeminiLLM` class
  - Implement `chat()` method with OpenAI format conversion
  - Write unit tests
- [ ] **Hour 5-6**: Design CEFR analysis prompt
  - System prompt for English teacher role
  - JSON output format for structured feedback
- [ ] **Hour 7-8**: Implement `analyze_english()` method
  - Grammar scoring
  - Vocabulary assessment
  - Fluency evaluation
  - Test with sample transcripts

#### AI Engineer #2 (STT/TTS)
- [ ] **Hour 1-2**: Research Web Speech Recognition API
- [ ] **Hour 3-4**: Implement client-side STT integration
  - Hook into AudioContext
  - Send transcripts to server via Socket.io
- [ ] **Hour 5-6**: Implement `BrowserTTS` class
  - Text-to-speech for AI feedback
  - Voice selection logic
- [ ] **Hour 7-8**: Test STT/TTS integration
  - Record sample audio
  - Verify transcript accuracy

#### AWS DevOps Specialist
- [ ] **Hour 1-2**: Set up AWS account, configure IAM users
- [ ] **Hour 3-4**: Provision EC2 instance (t2.micro for testing)
  - Install Ubuntu 22.04
  - Configure security groups
  - Assign Elastic IP
- [ ] **Hour 5-6**: Install dependencies on EC2
  - Python 3.11, FastAPI, nginx
  - Clone repository
  - Set up virtual environment
- [ ] **Hour 7-8**: Deploy initial backend version
  - Configure systemd service
  - Test health check endpoint
  - Set up CloudWatch logging

**Day 1 Goal**: Core infrastructure is running; Basic AI chat endpoint works; Frontend displays feedback UI skeleton.

---

### 5.3 Day 2: Integration & AI Features

#### Product Lead (Full-Stack + AI)
- [ ] **Hour 1-2**: Implement feedback storage in database
  - Create `feedback` table schema
  - Store feedback per participant per session
- [ ] **Hour 3-4**: Implement CEFR progress tracking
  - Calculate average CEFR level over time
  - Store historical scores
- [ ] **Hour 5-6**: Create `/api/feedback/history/:userId` endpoint
- [ ] **Hour 7-8**: Integration testing with all AI services
  - Test full flow: Speak → STT → LLM → Feedback → DB
  - Debug issues

#### Frontend Developer
- [ ] **Hour 1-2**: Implement real-time feedback display
  - Show feedback panel when user finishes speaking
  - Display CEFR level, scores, suggestions
- [ ] **Hour 3-4**: Add progress tracking UI
  - Line chart for CEFR level over sessions
  - Display improvement metrics
- [ ] **Hour 5-6**: Implement TTS audio playback
  - Play AI agent feedback as audio
  - Sync text + audio
- [ ] **Hour 7-8**: Polish UI/UX
  - Animations for feedback appearance
  - Mobile responsiveness
  - Loading states

#### AI Engineer #1 (LLM)
- [ ] **Hour 1-2**: Refine CEFR analysis prompt
  - Add more detailed grammar rules
  - Improve vocabulary level detection
- [ ] **Hour 3-4**: Implement context-aware feedback
  - Use previous feedback to track improvement
  - Personalize suggestions
- [ ] **Hour 5-6**: Add topic-specific analysis
  - Adjust scoring based on topic difficulty
  - Provide topic-relevant vocabulary tips
- [ ] **Hour 7-8**: Prepare Bedrock LLM implementation
  - Set up AWS Bedrock access
  - Implement `BedrockLLM` class (for Day 3 production switch)

#### AI Engineer #2 (STT/TTS)
- [ ] **Hour 1-2**: Optimize STT accuracy
  - Add noise filtering
  - Handle silence detection
- [ ] **Hour 3-4**: Implement transcript post-processing
  - Remove filler words (um, uh, like)
  - Normalize punctuation
- [ ] **Hour 5-6**: Add language detection
  - Detect if user speaks in English vs other languages
  - Provide appropriate feedback
- [ ] **Hour 7-8**: Prepare AWS Transcribe integration (optional)
  - Research API usage
  - Implement basic wrapper (for future use)

#### AWS DevOps Specialist
- [ ] **Hour 1-2**: Set up AWS Amplify for frontend
  - Connect GitHub repository
  - Configure build settings
  - Deploy to staging environment
- [ ] **Hour 3-4**: Configure environment variables
  - Set `VITE_API_URL` to EC2 backend
  - Test frontend → backend connectivity
- [ ] **Hour 5-6**: Set up SSL certificate (Let's Encrypt or ACM)
  - Configure nginx for HTTPS
  - Update security groups
- [ ] **Hour 7-8**: Set up monitoring
  - Configure CloudWatch alarms
  - Set up log aggregation
  - Test error reporting

**Day 2 Goal**: Full AI feedback loop is working end-to-end; Frontend shows real-time CEFR analysis; AWS infrastructure is stable.

---

### 5.4 Day 3: Polish, Testing & Production Deployment

#### Product Lead (Full-Stack + AI)
- [ ] **Hour 1-2**: Switch from Gemini to AWS Bedrock (production)
  - Update `ai_service_manager.py` config
  - Test Bedrock LLM integration
  - Compare quality with Gemini
- [ ] **Hour 3-4**: Implement analytics endpoints
  - `/api/analytics/session/:sessionId`
  - `/api/analytics/user/:userId`
- [ ] **Hour 5-6**: Code review and bug fixes
  - Review all PRs
  - Fix critical bugs
- [ ] **Hour 7-8**: Prepare demo presentation
  - Create demo script
  - Prepare test scenarios

#### Frontend Developer
- [ ] **Hour 1-2**: Final UI polish
  - Fix CSS issues
  - Add loading spinners
  - Improve error messages
- [ ] **Hour 3-4**: Cross-browser testing
  - Test on Chrome, Firefox, Safari
  - Fix WebRTC compatibility issues
- [ ] **Hour 5-6**: Mobile responsiveness
  - Test on iOS and Android
  - Adjust layouts for small screens
- [ ] **Hour 7-8**: User acceptance testing
  - Run through full user journey
  - Create bug list and fix critical issues

#### AI Engineer #1 (LLM)
- [ ] **Hour 1-2**: Fine-tune CEFR accuracy
  - Test with diverse transcripts
  - Adjust scoring thresholds
- [ ] **Hour 3-4**: Implement fallback for AI failures
  - Handle API timeouts
  - Provide generic feedback if LLM fails
- [ ] **Hour 5-6**: Optimize prompt tokens
  - Reduce prompt length to lower costs
  - Maintain quality
- [ ] **Hour 7-8**: Document AI configuration
  - Write README for AI services
  - Document prompt templates

#### AI Engineer #2 (STT/TTS)
- [ ] **Hour 1-2**: Test STT with various accents
  - Indian, American, British accents
  - Adjust confidence thresholds
- [ ] **Hour 3-4**: Optimize TTS voice quality
  - Select best voice for AI agent
  - Adjust speaking rate
- [ ] **Hour 5-6**: Add audio recording debugging
  - Log audio quality metrics
  - Detect poor microphone issues
- [ ] **Hour 7-8**: Document STT/TTS usage
  - Write user guide for audio setup
  - Troubleshooting guide

#### AWS DevOps Specialist
- [ ] **Hour 1-2**: Production deployment to EC2
  - Deploy final backend version
  - Run database migrations
  - Verify all services are running
- [ ] **Hour 3-4**: Deploy frontend to Amplify (production)
  - Merge to main branch
  - Trigger production build
  - Verify deployment
- [ ] **Hour 5-6**: Load testing
  - Simulate 20-50 concurrent users
  - Monitor CPU/memory usage
  - Optimize if needed
- [ ] **Hour 7-8**: Backup and disaster recovery
  - Set up automated DB backups
  - Document recovery procedures
  - Create runbook for common issues

**Day 3 Goal**: Production system is live and stable; Demo is ready; All critical bugs are fixed.

---

### 5.5 Task Dependencies & Critical Path

```
DAY 1: Foundation
─────────────────────────────────────────────────────────────────
┌──────────────────┐
│ DevOps: EC2      │──┐
│ Setup            │  │
└──────────────────┘  │
                      ▼
┌──────────────────┐  ┌──────────────────┐
│ Product: AI      │─►│ AI#1: LLM        │
│ Service Layer    │  │ Implementation   │
└──────────────────┘  └──────────────────┘
         │                     │
         │                     ▼
         │            ┌──────────────────┐
         │            │ Backend: Deploy  │
         │            │ AI Endpoint      │
         │            └──────────────────┘
         ▼
┌──────────────────┐
│ Frontend: UI     │
│ Components       │
└──────────────────┘

DAY 2: Integration
─────────────────────────────────────────────────────────────────
┌──────────────────┐  ┌──────────────────┐
│ Product: DB      │─►│ Frontend: Real-  │
│ Feedback Storage │  │ time Feedback UI │
└──────────────────┘  └──────────────────┘
         │                     │
         ▼                     ▼
┌──────────────────┐  ┌──────────────────┐
│ AI#1: Context-   │  │ DevOps: Amplify  │
│ Aware Feedback   │  │ Deployment       │
└──────────────────┘  └──────────────────┘
         │
         ▼
┌──────────────────┐
│ AI#2: STT/TTS    │
│ Optimization     │
└──────────────────┘

DAY 3: Production
─────────────────────────────────────────────────────────────────
┌──────────────────┐  ┌──────────────────┐
│ Product: Bedrock │─►│ DevOps: Prod     │
│ Switch           │  │ Deployment       │
└──────────────────┘  └──────────────────┘
         │                     │
         ▼                     ▼
┌──────────────────┐  ┌──────────────────┐
│ Frontend: Polish │─►│ Team: Testing    │
│ & Testing        │  │ & Demo Prep      │
└──────────────────┘  └──────────────────┘
```

### 5.6 Communication & Standup Schedule

**Daily Standups (15 minutes at 9 AM)**
- What did I complete yesterday?
- What am I working on today?
- Any blockers?

**Mid-Day Sync (30 minutes at 2 PM)**
- Integration testing
- Resolve blockers
- Adjust priorities

**End-of-Day Review (30 minutes at 6 PM)**
- Demo progress
- Plan next day
- Update task board

**Communication Channels**
- Slack/Discord: Real-time questions
- GitHub: Code reviews, issues
- Zoom: Standups and demos

---

## 6. Risk Mitigation & Contingency Plans

### 6.1 Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **WebRTC Fails on Some Browsers** | High | Medium | Test early; Provide browser compatibility list; Use WebRTC polyfills |
| **AI API Rate Limits** | Medium | Medium | Implement caching; Add retry logic; Use fallback messages |
| **Database Performance Issues** | Medium | Low | Use SQLite for MVP (simpler); Optimize queries; Add indexes |
| **Deployment Issues** | High | Medium | DevOps starts Day 1; Use proven stack; Document setup steps |
| **Speech Recognition Inaccuracy** | Medium | High | Set user expectations; Allow manual transcript editing; Use noise filtering |

### 6.2 Timeline Risks

| Risk | Mitigation |
|------|------------|
| **Scope Creep** | Stick to Must-Have features only; Product Lead enforces priorities |
| **Blocking Dependencies** | Identify critical path early; Parallel work where possible |
| **Team Member Unavailable** | Document all work; Knowledge sharing in standups |

### 6.3 Demo Risks

| Risk | Mitigation |
|------|------------|
| **Live Demo Fails** | Record backup video demo; Have staging environment ready; Test demo script 3x |
| **Internet Connectivity Issues** | Use mobile hotspot backup; Test offline scenarios |

---

## 7. Success Metrics (MVP)

### 7.1 Technical Success Criteria

- [x] **Core Loop Works**: User can join room → speak → receive feedback
- [x] **Real-Time Communication**: WebRTC audio works for 4+ participants
- [x] **AI Feedback**: CEFR level is assigned with 80%+ accuracy
- [x] **Uptime**: Backend stays up for 24 hours without crashes
- [x] **Response Time**: AI feedback delivered within 5 seconds

### 7.2 Hackathon Demo Metrics

- [x] **Wow Factor**: Live demo of 3 users speaking and getting instant feedback
- [x] **CEFR Visualization**: Show progress chart with improving scores
- [x] **AWS Integration**: Demonstrate Bedrock usage (Claude 3)
- [x] **Scalability**: Explain how architecture scales to 100+ concurrent rooms

### 7.3 User Experience Metrics

- [x] **Onboarding**: User can join room in < 2 minutes
- [x] **Intuitive UI**: No training needed to use platform
- [x] **Feedback Quality**: Users understand feedback and can act on it
- [x] **Mobile-Friendly**: Works on phones (iOS/Android)

---

## 8. Post-Hackathon Roadmap

### Phase 2 (Week 1-2 Post-Hackathon)
- Advanced topic generation (AI-curated)
- User profiles with authentication (OAuth)
- Historical progress dashboard
- Advanced CEFR analytics (pronunciation, coherence)

### Phase 3 (Month 1-2)
- Multi-language support
- Gamification (badges, leaderboards)
- Teacher dashboard for classrooms
- Export transcripts and reports

### Phase 4 (Month 3+)
- Mobile app (React Native)
- Video support
- Recorded sessions playback
- AI-generated practice exercises

---

## 9. References & Resources

### Documentation Links
- **Main Repo**: https://github.com/navgurukul/GupShupCafe
- **Existing Docs**: https://github.com/navgurukul/GupShupCafe/tree/dev/docs
- **AWS Bedrock**: https://aws.amazon.com/bedrock/
- **Gemini API**: https://ai.google.dev/docs
- **Web Speech API**: https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API

### Technical Specs
- **CEFR Framework**: https://www.coe.int/en/web/common-european-framework-reference-languages
- **WebRTC Best Practices**: https://webrtc.org/getting-started/overview
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Socket.io Docs**: https://socket.io/docs/

### AWS Services
- **AWS Amplify Console**: https://console.aws.amazon.com/amplify/
- **EC2 Dashboard**: https://console.aws.amazon.com/ec2/
- **Bedrock Console**: https://console.aws.amazon.com/bedrock/

---

## 10. Conclusion

This MVP architecture prioritizes the **core feedback loop** that makes Gup-Shup Café unique: instant, AI-driven English speaking feedback in a gamified peer discussion. By using a pluggable AI service layer with OpenAI-compatible interfaces, we ensure flexibility to switch between Gemini (dev) and AWS Bedrock (production) seamlessly.

The 3-day plan balances ambition with realism, focusing on a working demo that showcases the innovation while ensuring the team can deliver on time. The AWS cloud architecture is cost-effective for MVP ($5-15/month with free tiers) and scalable for future growth.

**Key Takeaways:**
1. **Focus on Core Loop**: Don't get distracted by nice-to-have features
2. **Pluggable AI Design**: Flexibility to swap AI providers without code changes
3. **Clear Task Distribution**: Each team member knows their role and dependencies
4. **Risk-Aware Planning**: Contingencies for common hackathon pitfalls
5. **Demo-Ready by Day 3**: Live demo is the ultimate success metric

**Let's build something amazing! 🚀**

---

**Document Status**: ✅ Ready for Implementation  
**Last Updated**: October 2025  
**Version**: 1.0  
**Authors**: Product Team - AWS AI Agent Hackathon 2025
