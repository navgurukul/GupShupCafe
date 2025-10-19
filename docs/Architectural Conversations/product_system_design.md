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
- ✅ Store room data (participants, transcripts, feedback)
- ✅ Track basic CEFR progress per user
- ✅ User authentication (simple login)
- ✅ Save discussion history (last 24 hours for MVP)

---

## 2. High-Level System Architecture

### 2.1 Component Overview

```
┌────────────────────────────────────────────────────────────────────────┐
│                            CLIENT LAYER                                 │
│  ┌─────────────────────────────────────────────────────────────┐     │
│  │                    React 18 + Vite                         │     │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐            │     │
│  │  │  Pages     │  │  Contexts  │  │ Components │            │     │
│  │  │ - Login    │  │ - Auth     │  │ - Table    │            │     │
│  │  │ - Lobby    │  │ - Socket   │  │ - Timer    │            │     │
│  │  │ - Room     │  │ - Audio    │  │ - Feedback │            │     │
│  │  └────────────┘  └────────────┘  └────────────┘            │     │
│  │                                                            │     │
│  │  ┌─────────────────────────────────────────────┐            │     │
│  │  │           User Data (Stored & Cached)       │            │     │
│  │  │  - CEFR Level: A0, A1, A2, B1, B2, C1, C2   │            │     │
│  │  │  - Topic Interests: Technology, Sports, etc.│            │     │
│  │  │                                             │            │     │
│  │  │                                             │            │     │
│  │  └─────────────────────────────────────────────┘            │     │
│  │                                                             │     │
│  │  ┌─────────────────────────────────────────────┐            │     │
│  │  │    WebRTC (Peer-to-Peer Audio Mesh)         │            │     │
│  │  │    - Local/Remote Stream Management         │            │     │
│  │  │    - STUN/TURN for NAT Traversal            │            │     │
│  │  └─────────────────────────────────────────────┘            │     │
│  └─────────────────────────────────────────────────────────────┘     │
│           │                    │                    │                │
│      REST API          WebSocket (Socket.io)    WebRTC Signaling     │
│           │                    │                    │                │
└───────────┼────────────────────┼────────────────────┼────────────────┘
            │                    │                    │
            ▼                    ▼                    ▼
┌───────────────────────────────────────────────────────────────────────┐
│                        SERVER LAYER (AWS Fargate)                     │
│  ┌──────────────────────────────────────────────────────────────┐     │
│  │              FastAPI + python-socketio                       │     │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │     │
│  │  │ REST API │  │ Socket.io│  │  WebRTC  │  │   CORS   │      │     │
│  │  │ Routes   │  │ Handlers │  │ Signaling│  │Middleware│      │     │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────────┘      │     │
│  └───────┼─────────────┼─────────────┼──────────────────────────┘     │
│          │             │             │                                │
│  ┌───────▼─────┐  ┌────▼────┐  ┌────▼─────┐                           │
│  │ Room Manager│  │ Room │  │ WebRTC   │                           │
│  │  Service    │  │ Manager │  │ Relay    │                           │
│  └─────┬───────┘  └────┬────┘  └──────────┘                           │
│        │               │                                              │
└────────┼───────────────┼──────────────────────────────────────────────┘
         │               │
         │               ▼
         │    ┌─────────────────┐
         │    │   SQLite         │
         │    │   - Users        │
         │    │   - Rooms     │
         │    │   - Participants │
         │    │   - Feedback     │
         │    │                  │
         │    │                  │
         │    └─────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────────────────────┐
│                  AWS STRANDS MULTI-AGENT SYSTEM                        │
│                     (Wrapped in AWS AgentCore)                         │
│  ┌───────────────────────────────────────────────────────────────┐     │
│  │              Multi-Agent Orchestrator                         │     │
│  │  - Coordinates agents for real-time and comprehensive feedback|     │
│  │  - Manages instant (2-3s) vs detailed analysis                │     │
│  │  - Routes feedback to appropriate UI components               │     │
│  └────────────┬─────────────────────────┬────────────────────────┘     │
│               │                         │                              │
│  ┌────────────▼───────────┐  ┌─────────▼──────────────┐                │
│  │ EnglishFeedbackAgent   │  │ Debate Facilitator     │                │
│  │                        │  │      Agent             │                │
│  │ - Grammar analysis     │  │ - Turn management      │                │
│  │ - Vocabulary scoring   │  │ - Topic guidance       │                │
│  │ - Fluency assessment   │  │ - Discussion flow      │                │
│  │ - CEFR level (A1-C2)   │  │ - Participant support  │                │
│  │ - Instant feedback     │  │ - Moderation           │                │
│  └────────────────────────┘  └────────────────────────┘                │
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
│                    PLUGGABLE AI SERVICE LAYER                          │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │                  AI Service Abstraction                      │      │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │      │
│  │  │ STT Module  │  │ LLM Module  │  │ TTS Module  │           │      │
│  │  │ (Interface) │  │ (Interface) │  │ (Interface) │           │      │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘           │      │
│  └─────────┼─────────────────┼─────────────────┼────────────────┘      │
│            │                 │                 │                       │
│  ┌─────────▼───────┐ ┌───────▼───────┐ ┌──────▼──────┐                 │
│  │ STT Providers   │ │ LLM Providers │ │TTS Providers│                 │
│  │ ┌─────────────┐ │ │ ┌───────────┐ │ │ ┌─────────┐ │                 │
│  │ │Web Speech   │ │ │ │  Gemini   │ │ │ │ Browser │ │                 │
│  │ │ Recognition │ │ │ │  (Dev)    │ │ │ │   TTS   │ │                 │
│  │ └─────────────┘ │ │ └───────────┘ │ │ └─────────┘ │                 │
│  │ ┌─────────────┐ │ │ ┌───────────┐ │ │ ┌─────────┐ │                 │
│  │ │ AWS         │ │ │ │  Bedrock  │ │ │ │ AWS     │ │                 │
│  │ │ Transcribe  │ │ │ │  Claude   │ │ │ │ Polly   │ │                 │
│  │ └─────────────┘ │ │ └───────────┘ │ │ └─────────┘ │                 │
│  └─────────────────┘ └───────────────┘ └─────────────┘                 │
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

The application uses the following data models to persist user progress, room information, and feedback:

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
    
    # Topic Interests (For Future Lobby Matching)
    topic_categories: List[str]  # ["Technology", "Sports", "Politics", "Science", etc.]
    # Note: Lobby matching by CEFR level and topics is a FUTURE FEATURE (not MVP)
    # Metadata
    created_at: datetime
    last_active: datetime

================== NOT IN MVP ==============================
    # Statistics - not in MVP
    total_rooms: int
    total_speaking_time: int  # seconds
    total_words_spoken: int
    
    # Average Scores (Calculated from feedback - not in MVP)
    avg_grammar_score: float  # 0-10
    avg_vocabulary_score: float  # 0-10
    avg_fluency_score: float  # 0-10
    avg_overall_score: float  # 0-10
    
  
    
    # Settings
    notification_preferences: dict

================== NOT IN MVP ==============================
```

#### Room Model

```python
# server_py/src/database/models/room.py
from datetime import datetime
from typing import List, Optional

class Room:
    """
    Discussion room model.
    """
    id: str  # UUID
    room_name: str  # Human-readable room code
    
    # Room Configuration
    topic: str  # Discussion topic
    topic_category: str  # "Technology", "Current Events", etc.
    max_participants: int  # Default: 6
    cefr_level: str  # "A0", "A1", "A2", "B1", "B2", "C1", "C2"
    speaking_time_per_turn: int  # seconds, default: 60
    num_rounds: int  # Default: 3
    
    # Room State
    status: str  # "waiting", "in_progress", "completed", "cancelled"
    current_round: int
    current_speaker_index: int
    
    # Participants
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
    Individual participant in a room.
    """
    id: str  # UUID
    room_id: str # Foreign key
    user_id: str # Foreign key
    
    # Identity
    anonymous_name: str  # Anonymous name like "Blue Panda", "Red Dragon"
    avatar_color: str  # Hex color code
    turn_order: int  # Order in speaking turns
    
    # Room Role
    role: str  # "participant", "host", "listener"
    is_ready: bool  # Ready to start discussion

    # Real-Time State
    is_speaking: bool
    is_muted: bool
    socket_id: str  # Socket.io connection ID

    
    # CEFR Level at Room Start (for progress tracking)
    starting_cefr_level: str
    ending_cefr_level: Optional[str]  # Updated at room end

    # Connection
    joined_at: datetime
    left_at: Optional[datetime]

================== NOT IN MVP ==============================
    # Speaking Data
    total_speaking_time: int  # seconds in this room
    total_words_spoken: int
    number_of_turns: int
    
    
    # Connection
    connection_quality: str  # "excellent", "good", "fair", "poor"
```

#### Feedback Model

```python
# server_py/src/database/models/feedback.py
from datetime import datetime
from typing import List, Dict, Optional

class Feedback: # Received from EnglishFeedbackAgent; stored per transcript
    """
    AI-generated English feedback for a transcript.
    """
    id: str  # UUID, Primary Key
    room_id: str  # Foreign Key
    participant_id: str  # Foreign Key
    user_id: str  # Foreign Key (from {{User}})

    # Feedback Type
    feedback_type: str  # "instant" or "comprehensive"

    # --- Instant Feedback Fields ---
    # (Populated if feedback_type == "instant")
    # random insights from any5 points from the comprehensive fields below
    # Display Message (For UI)
    display_message: str  # Formatted feedback for modal

    # --- Comprehensive Feedback Fields ---
    # (Populated if feedback_type == "comprehensive")

    # CEFR Level Summary
    cefr_speaking: str  # e.g., "A1", "C2"
    cefr_listening: str  # e.g., "A1", "C2"

    # Listening & Responsiveness
    listening_activity: str # describe how actively they listen
    response_effectiveness: str # mention if they respond to others’ points effectively
    listening_positive_observation: str 
    listening_improvement_suggestion: str # specific suggestion, e.g., connecting your ideas more closely to others or acknowledging their points before speaking

    # Speaking Quality
    fluency: str  # e.g., "steady flow", "some pauses"
    sentence_complexity: str  # e.g., "simple", "medium", "complex"
    pace: str  # e.g., "smooth", "rushed", "hesitant"
    filler_examples: str  # Stored as JSON TEXT (e.g., ["um", "like"])
    grammar: str  # e.g., "mostly accurate", "needs improvement"

    # Vocabulary & Expression
    vocab_examples: str  # Stored as JSON TEXT (e.g., ["adequate", "perform"])
    vocab_analysis: str  # e.g., "range", "confidence", "basic usage"
    vocab_positive_observation: str # positive observation, e.g., tried new words or expressions
    vocab_improvement_suggestion: str # vocabulary improvement suggestion, e.g., try using more descriptive words or synonyms to make your points stronger.

    # Depth of Understanding & Content
    understanding_level: str  # e.g., "basic", "fair", "deep"
    explanation_quality: str  # e.g., "logical", "reflective", "opinion-based"
    interaction_style: str  # e.g., "compare, build on, or respond"
    depth_of_understanding_suggestion: str # e.g., suggestion: use examples, explanations, or comparisons

    # Comparative Reflection (Optional)
    comparative_performance: str # more fluent / more confident / less detailed / more reflective compared to others
    comparative_suggestion: str # specific suggestion: e.g., summarizing others’ points, asking questions, or elaborating more

    # Summary Feedback
    summary_strength: str # strength area, e.g., expressing your opinions clearly or staying engaged
    summary_improvement_area: str # specific improvement area, e.g., reducing fillers, using longer sentences, expanding vocabulary, or deepening reasoning
    target_cefr_level: str  # e.g., "B2"



    # AI Agent Info
    agent_id: str  # EnglishFeedbackAgent instance
    agent_model: str  # "gemini-1.5-flash" or "bedrock-claude-3"
    
    created_at: datetime

```

### Transcript Model

```python
# server_py/src/database/models/transcript.py
from datetime import datetime
from typing import Optional

class Transcript:
    """
    Individual speech transcript from a participant for a particular round.
    """
    id: str  # UUID
    session_id: str
    participant_id: str
    user_id: str
    
    # Context
    round_number: int # round number out of the total number of rounds for a room
    turn_order: int # turn order of the participant within the round

    # Content
    transcript_text: str  # Transcribed speech
    language: str  # "en"
    stt_confidence: float  # STT confidence (0.0-1.0)
    
    
    # Timing
    started_at: datetime
    ended_at: datetime
    duration_seconds: int
    
    # Audio Metadata
    word_count: int
    speech_rate: float  # words per minute
    
    # Processing Status
    is_processed: bool  # Has feedback been generated?
    processed_at: Optional[datetime] # Feedback's created_at time stored here 
    
    # Raw Audio Reference (optional, for future features)
    audio_file_url: Optional[str]
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
│ topic_categories[]       │
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
│ text        │ │ topic_category       
│ timestamp   │ │ status      │
└─────────────┘ │ topic       |
       │          max_participants: default = 3
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
```

### 2.3.3 Data Flow for User Login 
```
1. User sign up (for the first time)
   └─> Google Authentication.
   └─> Create a new User record
       └─> Email (get from the google sign in object)
       └─> CEFR_level (initially A0)
       └─> Save createdAt time (not in MVP)
       └─> Initialise lastActive (not in MVP)
       └─> Initialise stats variables to zeroes (not in MVP)
   └─> Find user's topics of interests: (not in MVP)
       └─> Provide a list of suggested topic categories (Education, Technology, etc.) that can be clicked and added to interested topics input
       └─> Save the topics of interest.
2. Lobby page displayed
   └─> List the online lobbies/rooms (filtered with user's topics of interest - not in MVP) as cards - Each lobby card shows the room_name, topic category, CEFR_level and # of participants
   └─> User can create a new room by clicking the 'Create new room' button.
       └─> Create new room button clicked
       └─> Room creation form opened - User becomes the host for the room - Enter room_name, max_participants and select the topic_category for the room. Host's CEFR level is assigned to the room
       └─> Host mentions his anonymous name for the room
       └─> Publish room for others to join
       └─> Other participants join and click 'I'm ready to start!' button.
       └─> When all participants are ready to start, the room starts.
   └─> User can join an online room published by another user by clicking the one of the available room cards on the screen.
       └─> User mentions his anonymous name for the room
       └─> User clicks 'I'm ready to start!' button when mic and network working fine and ready to start.
       └─> When all participants are ready to start, the room starts. 
```

### 2.3.4 Data Flow for Room

```
1. User joins room
   └─> Create/Update Participant record

2. User speaks during turn
   └─> Create Transcript record
   └─> Trigger EnglishFeedbackAgent (instant mode, 2-3s)
   └─> Create Feedback record (instant)
   └─> Emit feedback to user's English Feedback Modal (private)

3. Turn ends
   └─> Update Participant stats (speaking_time, word_count)

4. Room ends
   └─> Trigger comprehensive feedback for all transcripts
   └─> Create Feedback records (comprehensive)
   └─> Update Participant ending_cefr_level
   └─> Update Room status to "completed"

5. Background job (post-room)
   └─> Aggregate all room feedback
   └─> Update User current_cefr_level (if changed)
   └─> Update Progress record with trends and milestones
   └─> Update User topic_interests based on room topics
   
6. Future: Lobby Matching (not MVP)
   └─> Query Users by cefr_level range (±1 level)
   └─> Filter by topic_interests
   └─> Suggest matched lobbies
```

### 2.3.4 CEFR Level Definitions (For MVP)

| Level  | Name               | Description                                | Expected Scores  |
| ------ | ------------------ | ------------------------------------------ | ---------------- |
| **A0** | Pre-A1             | Not yet reached A1, complete beginner      | Overall < 3.0    |
| **A1** | Beginner           | Basic phrases, simple interactions         | Overall 3.0-4.5  |
| **A2** | Elementary         | Simple sentences, common topics            | Overall 4.5-5.5  |
| **B1** | Intermediate       | Express opinions, handle common situations | Overall 5.5-7.0  |
| **B2** | Upper Intermediate | Fluent discussion, complex ideas           | Overall 7.0-8.5  |
| **C1** | Advanced           | Precise language, subtle meanings          | Overall 8.5-9.5  |
| **C2** | Proficient         | Native-like fluency and accuracy           | Overall 9.5-10.0 |

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
┌───────────────────────────────────────────────────────────────────────┐
│                        AWS AgentCore Runtime                          │
│  ┌──────────────────────────────────────────────────────────────┐     │
│  │           AWS Strands Multi-Agent Orchestrator               │     │
│  │                                                              │     │
│  │  ┌──────────────────────┐    ┌─────────────────────────┐     │     │
│  │  │ EnglishFeedbackAgent │    │ Debate Facilitator Agent │    │     │
│  │  │                      │    │                          │    │     │
│  │  │ - Grammar Analysis   │    │ - Turn Management        │    │     │
│  │  │ - Vocabulary Feedback│    │ - Topic Guidance         │    │     │
│  │  │ - Fluency Feedback   │    │ - Discussion Flow        │    │     │
│  │  │ - CEFR Leveling      │    │ - Moderation             │    │     │
│  │  │ - Instant (2-3s)     │    │ - Participant Support    │    │     │
│  │  │ - Comprehensive Feedback│ │                          │    │     │
│  │  └──────────────────────┘    └─────────────────────────┘     │     │
│  │                                                              │     │
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
        max_output_tokens: int = 500
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
            max_output_tokens: Maximum tokens to generate
            
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
            "room_summary": result.get("summary", ""),
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
            "room_id": request.room_id,
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
│                          AWS CLOUD (ap-south-1)                           │
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
│  │  │  │      AWS Fargate Container                           │  │ │ │
│  │  │  │                                                       │  │ │ │
│  │  │  │  - Python 3.11 Docker container                     │  │ │ │
│  │  │  │  - FastAPI application                              │  │ │ │
│  │  │  │  - python-socketio                                   │  │ │ │
│  │  │  │  - Application Load Balancer                        │  │ │ │
│  │  │  │  - ECS Task Definition                              │  │ │ │
│  │  │  │                                                       │  │ │ │
│  │  │  │  Ports:                                              │  │ │ │
│  │  │  │  - 80 (HTTP - redirects to 443)                     │  │ │ │
│  │  │  │  - 443 (HTTPS/WSS - via ALB)                        │  │ │ │
│  │  │  │  - 3003 (Container port - internal)                 │  │ │ │
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
│  │  - HTTP (80): 0.0.0.0/0 (ALB only)                              │ │
│  │  - HTTPS (443): 0.0.0.0/0 (ALB only)                            │ │
│  │                                                                   │ │
│  │  Outbound Rules:                                                 │ │
│  │  - All traffic: 0.0.0.0/0 (for API calls)                       │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                 │                                     │
│  ┌──────────────────────────────▼───────────────────────────────────┐ │
│  │                    EFS Volume (Elastic File System)               │ │
│  │  - Shared persistent storage for Fargate tasks                   │ │
│  │  - Stores: SQLite DB, Room data, Logs                         │ │
│  │  - Auto-scaling, pay-per-use                                     │ │
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
│  │  - Fargate metrics (CPU, memory, network)                        │   │
│  │  - Application logs                                              │   │
│  │  - Alarms for high CPU/memory                                    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                  Route 53 (DNS - Optional)                       │   │
│  │  - api.gupshup-cafe.com → ALB DNS                                │   │
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
│ AWS Fargate Task    │
│ (ALB → FastAPI)     │
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

| Service                           | Usage                                                                     | Monthly Cost       |
| --------------------------------- | ------------------------------------------------------------------------- | ------------------ |
| **AWS Amplify**                   | Build minutes: 100 mins<br>Hosting: 5 GB storage, 15 GB data transfer     | $5-10              |
| **AWS Fargate**                   | 0.5 vCPU, 1 GB RAM, 730 hours/month<br>Serverless container orchestration | $15-20             |
| **Application Load Balancer**     | ALB hours + LCU usage                                                     | $18-22             |
| **Data Transfer**                 | 50 GB/month (free tier covers first 100 GB)                               | $0-5               |
| **AWS Bedrock (Claude 3 Sonnet)** | ~10,000 requests/month<br>~1M input tokens, ~200K output tokens           | $15-25             |
| **Amazon Polly**                  | 1M characters TTS                                                         | $4                 |
| **AWS Transcribe**                | 100 hours audio                                                           | $24                |
| **CloudWatch**                    | Basic monitoring + logs                                                   | $3                 |
| **Route 53** (Optional)           | Hosted zone + queries                                                     | $1                 |
| **Total (Estimated)**             |                                                                           | **$101-126/month** |

**Note**: For MVP, reducing costs during development by:
- Using Gemini API (free tier) instead of Bedrock
- Using Web Speech API (browser STT/TTS) - **$0 cost**
- Using minimal Fargate resources (0.25 vCPU, 0.5 GB RAM)
- **Estimated MVP cost with free services: $25-35/month**


---

### 5.5 Task Dependencies & Critical Path

```
DAY 1: Foundation
─────────────────────────────────────────────────────────────────
┌──────────────────┐
│ DevOps: Fargate  │──┐
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



## 6. Risk Mitigation & Contingency Plans

### 6.1 Technical Risks

| Risk                              | Impact | Probability | Mitigation                                                                  |
| --------------------------------- | ------ | ----------- | --------------------------------------------------------------------------- |
| **WebRTC Fails on Some Browsers** | High   | Medium      | Test early; Provide browser compatibility list; Use WebRTC polyfills        |
| **AI API Rate Limits**            | Medium | Medium      | Implement caching; Add retry logic; Use fallback messages                   |
| **Database Performance Issues**   | Medium | Low         | Use SQLite for MVP (simpler); Optimize queries; Add indexes                 |
| **Deployment Issues**             | High   | Medium      | DevOps starts Day 1; Use proven stack; Document setup steps                 |
| **Speech Recognition Inaccuracy** | Medium | High        | Set user expectations; Allow manual transcript editing; Use noise filtering |

### 6.2 Timeline Risks

| Risk                        | Mitigation                                                         |
| --------------------------- | ------------------------------------------------------------------ |
| **Scope Creep**             | Stick to Must-Have features only; Product Lead enforces priorities |
| **Blocking Dependencies**   | Identify critical path early; Parallel work where possible         |
| **Team Member Unavailable** | Document all work; Knowledge sharing in standups                   |

### 6.3 Demo Risks

| Risk                             | Mitigation                                                                    |
| -------------------------------- | ----------------------------------------------------------------------------- |
| **Live Demo Fails**              | Record backup video demo; Have staging environment ready; Test demo script 3x |
| **Internet Connectivity Issues** | Use mobile hotspot backup; Test offline scenarios                             |

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
- Recorded rooms playback
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
- **ECS/Fargate Console**: https://console.aws.amazon.com/ecs/
- **Application Load Balancer**: https://console.aws.amazon.com/ec2/v2/home#LoadBalancers:
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

## 11. Current WebRTC Architecture & Proposed API-First Flow

### 11.1 Current WebRTC Design and Sequence of Events

The current implementation uses a peer-to-peer (P2P) WebRTC architecture for real-time audio communication between participants in a roundtable discussion. The backend server acts as a signaling server to facilitate WebRTC connection establishment but does not relay audio data.

#### 11.1.1 WebRTC Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Current WebRTC Architecture                           │
│                                                                          │
│  ┌──────────────┐                                    ┌──────────────┐   │
│  │  User A      │◄──────────P2P Audio ──────────────►│  User B      │   │
│  │  (Browser)   │                                    │  (Browser)   │   │
│  └──────┬───────┘                                    └──────┬───────┘   │
│         │                                                   │            │
│         │          WebSocket (Socket.io)                   │            │
│         │          Signaling Only                          │            │
│         │                                                   │            │
│         └──────────────────┬──────────────────────────────┘            │
│                            │                                            │
│                            ▼                                            │
│                 ┌─────────────────────┐                                 │
│                 │  FastAPI Backend    │                                 │
│                 │  (Port 3003)        │                                 │
│                 │                     │                                 │
│                 │  - Socket.io Server │                                 │
│                 │  - WebRTC Signaling │                                 │
│                 │  - Room Management  │                                 │
│                 └─────────────────────┘                                 │
└─────────────────────────────────────────────────────────────────────────┘

Key Characteristics:
- Audio flows P2P between browsers (not through server)
- Server only relays WebRTC signaling messages
- Uses STUN servers for NAT traversal
- Opus codec prioritized for voice quality
```

#### 11.1.2 Detailed Sequence of Events for Peer-to-Peer WebRTC

**Reference Diagram**: See `/docs/diagrams/plan/uml/06-sequence-webrtc-audio.puml` and corresponding PNG for the complete visual sequence.

**Phase 1: Initial Setup and Room Join**

1. **User Authentication & Socket Connection**
   - User logs in via Google OAuth
   - Frontend establishes Socket.io connection with auth credentials
   - Backend assigns socket ID and stores auth data

2. **Room Join Flow**
   - User navigates to lobby and selects/creates a room
   - Frontend emits `join-room` event with:
     ```javascript
     {
       roomId: "room-123",
       userData: {
         userId: "user-uuid",
         name: "Alice",
         anonymousName: "Blue Panda",
         role: "speaker", // or "listener"
         isReady: false
       }
     }
     ```
   - Backend:
     - Adds user to `room_manager`
     - Emits `participant-joined` to other participants
     - Emits `participants-update` to all in room

**Phase 2: Audio Initialization**

3. **Microphone Permission Request**
   - Frontend (`AudioContext.jsx`) calls `requestMicrophoneAccess()`
   - Browser prompts user for microphone permission
   - On grant:
     ```javascript
     const audioConstraints = {
       audio: {
         echoCancellation: true,
         noiseSuppression: true,
         autoGainControl: true,
         sampleRate: 48000,
         channelCount: 1
       }
     }
     const localStream = await navigator.mediaDevices.getUserMedia(audioConstraints)
     ```
   - `localStream` stored in `AudioContext`

4. **WebRTC Readiness Signal**
   - After both `localStream` is obtained AND `participants-update` received:
     ```javascript
     socket.emit('ready-for-webrtc')
     ```
   - Backend receives event and broadcasts:
     ```javascript
     await sio.emit("peer-ready", {
       socketId: sid
     }, room=room_id, skip_sid=sid)
     ```

**Phase 3: WebRTC Peer Connection Establishment**

5. **Peer Connection Creation (Initiator)**
   - When `peer-ready` received, frontend creates `RTCPeerConnection`:
     ```javascript
     const config = {
       iceServers: [
         { urls: 'stun:stun.l.google.com:19302' },
         { urls: 'stun:stun1.l.google.com:19302' }
       ],
       iceCandidatePoolSize: 10,
       bundlePolicy: 'balanced',
       rtcpMuxPolicy: 'require'
     }
     const pc = new RTCPeerConnection(config)
     pc.addTrack(localStream.getAudioTracks()[0])
     ```

6. **SDP Offer Creation**
   - Initiator creates and sets local description:
     ```javascript
     const offer = await pc.createOffer()
     await pc.setLocalDescription(optimizeAudioSDP(offer))
     ```
   - Opus codec prioritization applied in SDP
   - Emit to backend:
     ```javascript
     socket.emit('webrtc-offer', {
       to: targetSocketId,
       sdp: pc.localDescription
     })
     ```

7. **Offer Relay**
   - Backend relays offer to target peer:
     ```javascript
     await sio.emit("webrtc-offer", {
       from: sourceSid,
       sdp: offerSdp
     }, room=targetSid)
     ```

8. **SDP Answer Creation**
   - Recipient receives offer and creates answer:
     ```javascript
     await pc.setRemoteDescription(offer)
     const answer = await pc.createAnswer()
     await pc.setLocalDescription(answer)
     socket.emit('webrtc-answer', {
       to: originatorSocketId,
       sdp: pc.localDescription
     })
     ```

9. **Answer Relay**
   - Backend relays answer back to initiator:
     ```javascript
     await sio.emit("webrtc-answer", {
       from: answererSid,
       sdp: answerSdp
     }, room=initiatorSid)
     ```

10. **ICE Candidate Exchange**
    - Both peers gather ICE candidates via STUN servers
    - Each candidate emitted:
      ```javascript
      pc.onicecandidate = (event) => {
        if (event.candidate) {
          socket.emit('webrtc-ice-candidate', {
            to: peerSocketId,
            candidate: event.candidate
          })
        }
      }
      ```
    - Backend relays candidates:
      ```javascript
      await sio.emit("webrtc-ice-candidate", {
        from: sourceSid,
        candidate: candidate
      }, room=targetSid)
      ```
    - Peers add candidates:
      ```javascript
      await pc.addIceCandidate(candidate)
      ```

**Phase 4: Connection Established**

11. **Audio Stream Ready**
    - `pc.ontrack` fired when remote stream received:
      ```javascript
      pc.ontrack = (event) => {
        const remoteStream = event.streams[0]
        setRemoteStreams(prev => ({
          ...prev,
          [peerSocketId]: remoteStream
        }))
        
        // Create hidden audio element for playback
        const audioElement = document.createElement('audio')
        audioElement.srcObject = remoteStream
        audioElement.autoplay = true
        audioElement.volume = 1.0
      }
      ```

12. **Connection State Monitoring**
    - Frontend monitors connection:
      ```javascript
      pc.onconnectionstatechange = () => {
        console.log(`Peer connection state: ${pc.connectionState}`)
        // States: new, connecting, connected, disconnected, failed, closed
      }
      ```

**Phase 5: Audio Control**

13. **Mute/Unmute**
    - User clicks mute button:
      ```javascript
      localStream.getAudioTracks()[0].enabled = false
      socket.emit('participant-muted')
      ```
    - Backend broadcasts state:
      ```javascript
      await sio.emit("participant-muted", {
        peerId: sid
      }, room=room_id)
      ```

14. **Audio Level Monitoring**
    - Frontend uses Web Audio API:
      ```javascript
      const audioContext = new AudioContext()
      const analyser = audioContext.createAnalyser()
      const microphone = audioContext.createMediaStreamSource(localStream)
      microphone.connect(analyser)
      
      // Sample audio levels at 100ms intervals
      analyser.getByteFrequencyData(dataArray)
      const average = dataArray.reduce((a, b) => a + b) / dataArray.length
      ```

**Phase 6: Cleanup**

15. **Leave Room**
    - User leaves:
      ```javascript
      socket.emit('leave-room')
      pc.close() // Close all peer connections
      localStream.getTracks().forEach(track => track.stop())
      ```
    - Backend removes from room:
      ```javascript
      room_manager.remove_user_from_room(room_id, user_id)
      await sio.emit("participant-left", {
        participantId: user_id
      }, room=room_id)
      ```

**Key Socket Events Summary:**

| Event Name | Direction | Purpose |
|------------|-----------|---------|
| `join-room` | Client → Server | User joins a room |
| `participants-update` | Server → Client | Room participant list updated |
| `ready-for-webrtc` | Client → Server | Client ready for WebRTC connections |
| `peer-ready` | Server → Client | Another peer is ready for WebRTC |
| `webrtc-offer` | Bidirectional (via Server) | SDP offer for connection |
| `webrtc-answer` | Bidirectional (via Server) | SDP answer for connection |
| `webrtc-ice-candidate` | Bidirectional (via Server) | ICE candidates for NAT traversal |
| `participant-muted` | Server → Clients | Participant muted their mic |
| `participant-unmuted` | Server → Clients | Participant unmuted their mic |
| `leave-room` | Client → Server | User leaves room |
| `participant-left` | Server → Clients | Participant left the room |

---

### 11.2 Proposed Action Plan: API-First Flow with Strategic Socket Usage

This section outlines a proposed architecture that prioritizes REST API calls for state management while strategically using Socket.io for real-time events and WebRTC signaling.

#### 11.2.1 Motivation for API-First Approach

**Current Challenges:**
1. **State Synchronization**: Socket events (`participants-update`) require careful state management on both client and server
2. **Debugging Complexity**: Real-time socket events harder to debug than REST API calls
3. **State Recovery**: If client disconnects, must reconstruct state from socket events
4. **Testing**: REST APIs easier to test than socket event sequences

**Proposed Benefits:**
1. **Single Source of Truth**: Database-backed REST APIs provide authoritative state
2. **Simpler Client Logic**: HTTP requests with clear request/response patterns
3. **Better Error Handling**: Standard HTTP status codes and error responses
4. **Easier State Recovery**: Client can fetch current state via API after reconnection
5. **Gradual Enhancement**: Can add socket events for real-time updates as needed

#### 11.2.2 Hybrid Architecture: REST APIs + Strategic Sockets

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   Proposed Hybrid Architecture                           │
│                                                                          │
│  User Management         Room Management        Real-Time Events        │
│  ─────────────────       ────────────────       ────────────────        │
│                                                                          │
│  ┌──────────────┐       ┌──────────────┐       ┌──────────────┐         │
│  │ REST APIs    │       │ REST APIs    │       │ Socket.io    │         │
│  │              │       │              │       │              │         │
│  │ POST /signup │       │ POST /rooms  │       │ webrtc-*     │         │
│  │ POST /login  │       │ GET  /rooms  │       │ turn-started │         │
│  │ GET  /users  │       │ GET  /rooms/:id      │ turn-ended   │         │
│  │ PATCH /users │       │ PATCH /rooms/:id     │ ai-speaking  │         │
│  └──────────────┘       │              │       │              │         │
│                         │ POST /rooms/:id/start│              │         │
│  Participant Mgmt       │ POST /rooms/:id/participants       │         │
│  ─────────────────      │ GET  /rooms/:id/participants       │         │
│                         │ PATCH /participants/:id            │         │
│  ┌──────────────┐       │ DELETE /participants/:id           │         │
│  │ REST APIs    │       └──────────────┘       └──────────────┘         │
│  │              │                                                        │
│  │ POST /participants                                                    │
│  │ GET  /participants/:id                                                │
│  │ PATCH /participants/:id/ready                                         │
│  └──────────────┘                                                        │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘

Database as Single Source of Truth:
┌─────────────────────────────────────────┐
│           SQLite Database               │
│                                         │
│  ┌──────┐  ┌──────┐  ┌──────────────┐  │
│  │Users │  │Rooms │  │Participants  │  │
│  └──────┘  └──────┘  └──────────────┘  │
│                                         │
│  All state persisted and queryable      │
└─────────────────────────────────────────┘
```

#### 11.2.3 Detailed Flow: Login to Room Start Using APIs

**Step 1: User Authentication (Existing)**

```
Frontend                          Backend
   │                                 │
   │  POST /api/auth/google-login    │
   │  { token, email, name }         │
   ├────────────────────────────────>│
   │                                 │──┐ Verify Google token
   │                                 │  │ Create/update user in DB
   │                                 │<─┘
   │  { userId, token, user }        │
   │<────────────────────────────────┤
   │                                 │
   │  Store token in localStorage    │
   │  Initialize Socket.io with auth │
```

**API Endpoint:** `POST /api/auth/google-login`
- **Input:** `{ googleToken, email, name }`
- **Output:** `{ userId, authToken, user: { id, email, name, cefr_level, topic_categories } }`
- **Database:** Creates/updates entry in `users` table

**Step 2: Browse and Create/Join Room**

```
Frontend                          Backend
   │                                 │
   │  GET /api/rooms?status=waiting  │
   ├────────────────────────────────>│
   │                                 │──┐ Query rooms table
   │  { rooms: [...] }               │<─┘
   │<────────────────────────────────┤
   │                                 │
   │  User clicks "Create Room"      │
   │                                 │
   │  POST /api/rooms                │
   │  {                              │
   │    room_name: "Tech Talk",      │
   │    topic_category: "Technology",│
   │    max_participants: 4,         │
   │    cefr_level: "B1"             │
   │  }                              │
   ├────────────────────────────────>│
   │                                 │──┐ Insert into rooms table
   │                                 │  │ status = "WAITING"
   │  { room: {...}, roomId }        │<─┘
   │<────────────────────────────────┤
```

**API Endpoints:**

1. **`GET /api/rooms`** (Existing: `server_py/src/api/room_routes.py`)
   - Query params: `status=waiting`, `cefr_level=B1`
   - **Output:** `{ success: true, data: [{ room_id, room_name, topic_category, participant_count, max_participants, cefr_level, status }] }`

2. **`POST /api/rooms`** (Existing)
   - **Input:** `{ room_name, topic_category?, max_participants?, cefr_level, created_by }`
   - **Output:** `{ success: true, data: { room_id, room_name, status: "WAITING", ... } }`
   - **Database:** 
     ```sql
     INSERT INTO rooms (room_id, room_name, topic_category, cefr_level, 
                        max_participants, status, created_by, created_at)
     VALUES (?, ?, ?, ?, ?, "WAITING", ?, NOW())
     ```

**Step 3: Join Room as Participant**

```
Frontend                          Backend
   │                                 │
   │  POST /api/participants         │
   │  {                              │
   │    room_id: "room-123",         │
   │    user_id: "user-456",         │
   │    anonymous_name: "Blue Panda",│
   │    role: "speaker"              │
   │  }                              │
   ├────────────────────────────────>│
   │                                 │──┐ Insert into participants
   │                                 │  │ Increment room.participant_count
   │  { participant: {...} }         │<─┘
   │<────────────────────────────────┤
   │                                 │
   │  Socket.io: join-room (optional)│
   │  Just for real-time notifications
   ├────────────────────────────────>│
   │                                 │
   │  GET /api/rooms/:id/participants│
   │  (fetch current participants)   │
   ├────────────────────────────────>│
   │  { participants: [...] }        │
   │<────────────────────────────────┤
```

**API Endpoints:**

1. **`POST /api/participants`** (Existing: `server_py/src/api/participant_routes.py`)
   - **Input:** `{ room_id, user_id, anonymous_name, role: "speaker"|"listener" }`
   - **Output:** `{ success: true, data: { participant_id, room_id, user_id, anonymous_name, role, is_ready: false, joined_at } }`
   - **Database:**
     ```sql
     INSERT INTO participants (participant_id, room_id, user_id, 
                               anonymous_name, role, is_ready, joined_at)
     VALUES (?, ?, ?, ?, ?, FALSE, NOW())
     ```

2. **`GET /api/rooms/:roomId/participants`** (Can be added to `room_routes.py`)
   - **Output:** `{ success: true, data: [{ participant_id, user_id, anonymous_name, role, is_ready }] }`

**Step 4: Mark Ready to Start**

```
Frontend                          Backend
   │                                 │
   │  User clicks "I'm Ready!"       │
   │                                 │
   │  PATCH /api/participants/:id    │
   │  { is_ready: true }             │
   ├────────────────────────────────>│
   │                                 │──┐ Update participant
   │  { participant: {...} }         │  │ Check if all ready
   │<────────────────────────────────┤<─┘
   │                                 │
   │  Optionally: Socket event       │
   │  "participant-ready"            │
   │<────────────────────────────────┤
```

**API Endpoint:**

**`PATCH /api/participants/:participantId`** (Existing)
- **Input:** `{ is_ready: true }`
- **Output:** `{ success: true, data: { participant_id, is_ready: true } }`
- **Database:**
  ```sql
  UPDATE participants 
  SET is_ready = TRUE 
  WHERE participant_id = ?
  ```

**Step 5: Start Room (Transition to IN_PROGRESS)**

```
Frontend (Host)                   Backend
   │                                 │
   │  All participants ready?        │
   │  POST /api/rooms/:id/start      │
   ├────────────────────────────────>│
   │                                 │──┐ Check all participants ready
   │                                 │  │ Generate AI topic if needed
   │                                 │  │ Assign AI agent to room
   │                                 │  │ UPDATE rooms SET
   │                                 │  │   status = "IN_PROGRESS"
   │                                 │  │   started_at = NOW()
   │                                 │  │   facilitator_agent_id = ?
   │  { room: {                      │<─┘
   │    status: "IN_PROGRESS",       │
   │    started_at: "...",           │
   │    topic: "...",                │
   │    facilitator_agent_id: "..."  │
   │  }}                             │
   │<────────────────────────────────┤
   │                                 │
   │  Socket: "room-started" event   │
   │  (notify all participants)      │
   │<════════════════════════════════│ (Socket.io broadcast)
   │                                 │
   │  Initialize WebRTC connections  │
   │  using existing socket flow     │
```

**API Endpoint:**

**`POST /api/rooms/:roomId/start`** (New endpoint to add to `room_routes.py`)
- **Validation:**
  - All participants must have `is_ready = true`
  - Minimum participants met (e.g., >= 2)
- **Actions:**
  1. Generate discussion topic (if not provided)
  2. Assign AWS Strands AI agent to room
  3. Update room status and started_at
- **Input:** `{ topic?: string }` (optional custom topic)
- **Output:** 
  ```json
  {
    "success": true,
    "data": {
      "room_id": "room-123",
      "status": "IN_PROGRESS",
      "started_at": "2025-10-19T10:30:00Z",
      "topic": "Impact of AI on Employment",
      "facilitator_agent_id": "agent-789",
      "current_round": 1,
      "current_speaker_index": 0
    }
  }
  ```
- **Database:**
  ```sql
  UPDATE rooms 
  SET status = "IN_PROGRESS", 
      started_at = NOW(),
      topic = ?,
      facilitator_agent_id = ?
  WHERE room_id = ? 
    AND status = "WAITING"
    AND (SELECT COUNT(*) FROM participants 
         WHERE room_id = ? AND is_ready = TRUE) >= min_participants
  ```
- **Socket Event:** After successful update, emit `room-started` to all participants in the room:
  ```javascript
  await sio.emit("room-started", {
    room_id: room_id,
    status: "IN_PROGRESS",
    topic: topic,
    started_at: started_at,
    first_speaker: first_speaker_participant
  }, room=room_id)
  ```

#### 11.2.4 Analysis: Socket Events vs API Calls

**Question:** Can `participants-update` socket event be replaced by API calls?

**Short Answer:** Partially yes, but socket events provide better UX for real-time updates.

**Detailed Comparison:**

| Aspect | Socket Events (`participants-update`) | REST API Polling | Hybrid Approach (Recommended) |
|--------|--------------------------------------|------------------|-------------------------------|
| **Real-time Updates** | ✅ Instant | ❌ Delayed (polling interval) | ✅ Instant via socket |
| **State Accuracy** | ⚠️ Can miss updates if disconnected | ✅ Always current from DB | ✅ Best of both |
| **Debugging** | ❌ Harder (event sequence) | ✅ Easy (HTTP logs) | ✅ Easy (API + events) |
| **Network Efficiency** | ✅ Only when changes occur | ❌ Constant polling overhead | ✅ Efficient |
| **Client Complexity** | ⚠️ Must manage event state | ✅ Simple fetch | ⚠️ Moderate |
| **Reconnection Recovery** | ⚠️ Must replay events | ✅ Fetch current state | ✅ Fetch + resume events |

**Implementation Strategy:**

1. **Primary: Use API calls for state management**
   - Fetching initial participant list: `GET /api/rooms/:roomId/participants`
   - Adding/removing participants: `POST/DELETE /api/participants/:id`
   - Updating participant status: `PATCH /api/participants/:id`

2. **Secondary: Use socket events for real-time notifications**
   - Emit `participant-joined` when someone joins (via socket)
   - Emit `participant-ready` when someone marks ready
   - Client can choose to:
     - **Option A:** Re-fetch full list via API on each event
     - **Option B:** Update local state based on event payload
   - On reconnection, always fetch via API to resync

**Code Example:**

```javascript
// Client-side approach
const [participants, setParticipants] = useState([])

// Initial fetch via API
useEffect(() => {
  async function fetchParticipants() {
    const response = await fetch(`/api/rooms/${roomId}/participants`)
    const data = await response.json()
    setParticipants(data.data)
  }
  fetchParticipants()
}, [roomId])

// Listen to socket events for real-time updates
useEffect(() => {
  if (!socket) return
  
  // Option A: Refetch on event (simpler, always correct)
  socket.on('participant-joined', () => {
    fetchParticipants() // Re-fetch from API
  })
  
  // Option B: Update local state (more efficient, but requires careful logic)
  socket.on('participant-joined', (data) => {
    setParticipants(prev => [...prev, data.participant])
  })
  
  // On reconnection, always refetch
  socket.on('connect', () => {
    fetchParticipants()
  })
}, [socket])
```

**Recommendation:**
- **Keep socket events** for `participant-joined`, `participant-left`, `participant-ready`
- **Add REST API endpoints** as source of truth
- **Client strategy:** Use socket events to **trigger** API refetch (Option A above)
- **Benefit:** Simple, correct, and efficient

#### 11.2.5 Challenges and Trade-offs

**Challenge 1: Increased API Calls**
- **Issue:** More HTTP requests vs socket events
- **Mitigation:** 
  - Cache responses with short TTL (5-10 seconds)
  - Use socket events to invalidate cache
  - Batch updates when possible

**Challenge 2: Race Conditions**
- **Issue:** Socket event arrives before API response
- **Mitigation:**
  - Always prioritize API response data
  - Use optimistic UI updates with rollback on error
  - Add request timestamps and discard stale responses

**Challenge 3: Socket Connection Loss**
- **Issue:** Missing real-time updates during disconnection
- **Mitigation:**
  - On reconnect, fetch full state via API
  - Show "reconnecting" UI indicator
  - Buffer missed updates on server (future enhancement)

**Challenge 4: Learning Curve**
- **Issue:** Team needs to understand both paradigms
- **Mitigation:**
  - Clear documentation (like this!)
  - Helper hooks: `useSyncedState(apiEndpoint, socketEvent)`
  - Code examples and patterns

**Ease of Implementation:**

| Approach | Implementation Effort | Maintenance Effort | Reliability |
|----------|----------------------|-------------------|-------------|
| Socket-Only (Current) | Low | High | Medium |
| API-Only (Pure REST) | Medium | Low | High |
| **Hybrid (Recommended)** | **Medium** | **Medium** | **Very High** |

**Verdict:** Hybrid approach is **recommended** because:
1. Provides reliable state recovery via APIs
2. Maintains real-time UX via sockets
3. Easier to debug and test than socket-only
4. More resilient to network issues

---

### 11.3 Audio Transmission During Speaking Turns

Once the room status changes to `IN_PROGRESS`, WebRTC audio connections are established using the existing socket-based flow.

#### 11.3.1 Speaking Turn Management

**Turn-Based Flow:**

```
Room Start
   │
   ├─ POST /api/rooms/:id/start succeeds
   │  └─ Backend emits "room-started" socket event
   │     └─ Payload: { first_speaker: { participant_id, anonymous_name } }
   │
   ├─ Frontend receives "room-started"
   │  └─ All participants establish WebRTC connections (if not already connected)
   │     └─ Use existing ready-for-webrtc → peer-ready → offer/answer flow
   │
   ├─ Frontend receives "turn-started"
   │  └─ Payload: { speaker_index, speaker: {...}, timer: 60 }
   │  └─ Speaking participant unmutes
   │  └─ Non-speaking participants listen
   │
   ├─ Speaker speaks (audio flows via WebRTC P2P)
   │  └─ All participants hear audio through WebRTC connections
   │  └─ Backend does NOT relay audio (P2P only)
   │  └─ STT happens on frontend: Web Speech Recognition API
   │     └─ Transcript sent via socket: emit('speech-transcript', { text })
   │
   ├─ Turn ends (timer expires or manual)
   │  └─ emit('end-turn')
   │  └─ Backend emits "turn-ended"
   │  └─ Backend emits "turn-started" for next speaker
   │
   └─ Repeat for all speakers × all rounds
```

#### 11.3.2 Audio Flow to AI Agent

**Challenge:** AI agent needs to receive audio for analysis, but WebRTC is P2P and doesn't route through server.

**Proposed Solution:** Transcripts sent to backend for AI analysis (not raw audio).

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Audio to AI Agent Flow                           │
│                                                                      │
│  1. Speaker speaks                                                   │
│     └─ Audio flows via WebRTC P2P to all participants               │
│                                                                      │
│  2. Frontend STT (Web Speech Recognition)                            │
│     └─ Converts audio to text in real-time                          │
│     └─ emit('speech-transcript', {                                  │
│           participant_id: "...",                                    │
│           text: "I think AI will...",                               │
│           timestamp: "..."                                          │
│        })                                                           │
│                                                                      │
│  3. Backend receives transcript                                      │
│     └─ Saves to database: transcripts table                         │
│     └─ Forwards to AWS Strands orchestrator                         │
│        └─ orchestrator.get_english_feedback(                        │
│              statements: [{ speaker, text }],                       │
│              instant: true                                          │
│           )                                                         │
│        └─ EnglishFeedbackAgent analyzes grammar/vocabulary          │
│                                                                      │
│  4. AI feedback returned                                             │
│     └─ emit('english-feedback', feedback, room=participant_sid)     │
│     └─ Private feedback modal shown to speaker only                 │
│                                                                      │
│  5. (Optional) For future: Server-side audio recording               │
│     └─ Could use MediaRecorder API to send audio chunks             │
│     └─ Backend stores in S3 and processes with AWS Transcribe       │
│     └─ NOT MVP - transcripts sufficient for MVP                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Key Point:** For MVP, the AI agent receives **transcripts** (text) via socket events, not raw audio. This is sufficient for:
- Grammar analysis
- Vocabulary assessment
- CEFR level estimation
- Instant feedback generation

**Future Enhancement:** If needed, implement server-side audio recording:
```javascript
// Future: Send audio chunks to backend for AWS Transcribe
const mediaRecorder = new MediaRecorder(localStream)
mediaRecorder.ondataavailable = (event) => {
  socket.emit('audio-chunk', {
    participant_id: userId,
    audio_data: event.data, // blob
    timestamp: Date.now()
  })
}
```

#### 11.3.3 Diagram: Audio Flow in Speaking Turn

```
┌──────────────┐
│ Speaker A    │
│ (Unmuted)    │
└───────┬──────┘
        │ Speaking
        │
        ├─────────────────────────────────────────────────┐
        │                                                 │
        │ WebRTC P2P Audio                                │
        │                                                 │
        ▼                                                 ▼
┌──────────────┐                                 ┌──────────────┐
│ Listener B   │                                 │ Listener C   │
│ (Muted)      │                                 │ (Muted)      │
└──────────────┘                                 └──────────────┘
        │                                                 │
        │ Web Speech Recognition (STT)                    │
        │                                                 │
        └─────────────────────┬───────────────────────────┘
                              │
                              │ socket.emit('speech-transcript')
                              │
                              ▼
                    ┌──────────────────┐
                    │  Backend Server  │
                    │                  │
                    │  1. Save to DB   │
                    │  2. Send to AI   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ AWS Strands      │
                    │ AI Orchestrator  │
                    │                  │
                    │ EnglishFeedback  │
                    │ Agent            │
                    └────────┬─────────┘
                             │
                             │ Instant feedback (2-3s)
                             │
                             ▼
                    ┌──────────────────┐
                    │  Backend Server  │
                    │                  │
                    │  emit to speaker │
                    └────────┬─────────┘
                             │
                             ▼
                      ┌──────────────┐
                      │ Speaker A    │
                      │              │
                      │ 📝 Feedback  │
                      │ Modal (Private)
                      └──────────────┘
```

---

### 11.4 AI Agent Speaking Turn with TTS

When it's the AI agent's turn to speak, the flow changes to accommodate Text-to-Speech (TTS) generation on the backend.

#### 11.4.1 AI Agent Turn Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    AI Agent Speaking Turn                            │
│                                                                      │
│  1. Turn rotation reaches AI agent                                   │
│     └─ Backend detects next speaker is AI facilitator agent         │
│     └─ emit('turn-started', {                                       │
│           speaker: {                                                │
│             participant_id: "ai-agent",                             │
│             anonymous_name: "AI Facilitator",                       │
│             role: "agent"                                           │
│           },                                                        │
│           timer: 60                                                 │
│        })                                                           │
│                                                                      │
│  2. AI generates speech content                                      │
│     └─ orchestrator.get_facilitator_response(                       │
│           room_context: { topic, transcripts, feedback },           │
│           task: "provide_feedback" | "ask_question" | "summarize"   │
│        )                                                            │
│     └─ Returns text: "Alice made a great point about..."           │
│                                                                      │
│  3. Backend generates audio via TTS                                  │
│     └─ Use AWS Polly (production) or Browser TTS (dev)              │
│     └─ tts_service.synthesize(                                     │
│           text: ai_response_text,                                   │
│           voice: "Matthew",  // AWS Polly voice                     │
│           language: "en-US"                                         │
│        )                                                            │
│     └─ Returns audio URL or base64 data                             │
│                                                                      │
│  4. Stream audio to all participants                                 │
│     └─ emit('ai-speaking', {                                        │
│           audio_url: "https://s3.../audio.mp3",                     │
│           text: "Alice made a great point...",  // for captions     │
│           duration: 8.5  // seconds                                 │
│        })                                                           │
│                                                                      │
│  5. Frontend plays AI audio                                          │
│     └─ All participants receive audio URL                           │
│     └─ Create <audio> element and play:                             │
│        const audio = new Audio(audio_url)                           │
│        audio.play()                                                 │
│     └─ Show captions/transcript in UI                               │
│     └─ Indicate "AI Facilitator is speaking"                        │
│                                                                      │
│  6. Audio playback completes                                         │
│     └─ Frontend emits 'ai-turn-complete'                            │
│     └─ Backend advances to next human speaker                       │
│     └─ emit('turn-started', { next_speaker })                       │
└─────────────────────────────────────────────────────────────────────┘
```

#### 11.4.2 TTS Implementation Details

**Backend Service (`server_py/src/services/tts_service.py`):**

```python
from abc import ABC, abstractmethod
import boto3
import os

class TTSInterface(ABC):
    @abstractmethod
    async def synthesize(self, text: str, voice: str, language: str) -> dict:
        pass

class AWSPollyTTS(TTSInterface):
    """Production TTS using AWS Polly"""
    
    def __init__(self):
        self.client = boto3.client('polly', region_name='ap-south-1')
    
    async def synthesize(self, text: str, voice: str = "Matthew", 
                         language: str = "en-US") -> dict:
        try:
            response = self.client.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId=voice,
                Engine='neural',  # Better quality
                LanguageCode=language
            )
            
            # Upload audio stream to S3 or return base64
            audio_stream = response['AudioStream'].read()
            
            # Option A: Save to S3 and return URL
            audio_url = await upload_to_s3(audio_stream, 
                                           f"ai-speech-{uuid.uuid4()}.mp3")
            
            return {
                "success": True,
                "audio_url": audio_url,
                "audio_format": "mp3",
                "duration": len(text) * 0.06,  # Rough estimate
                "provider": "aws-polly"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

class BrowserTTS(TTSInterface):
    """Development TTS using browser's SpeechSynthesis API"""
    
    async def synthesize(self, text: str, voice: str = "default", 
                         language: str = "en-US") -> dict:
        # For development, return text and let browser handle TTS
        return {
            "success": True,
            "text": text,
            "use_browser_tts": True,
            "language": language,
            "provider": "browser"
        }
```

**Socket Event Handler:**

```python
@sio.event
async def ai_agent_turn(sid, data):
    """Handle AI agent's speaking turn"""
    try:
        room_id = data.get("room_id")
        
        # Get room context
        room = room_manager.get_room(room_id)
        transcripts = await db.get_room_transcripts(room_id)
        
        # Generate AI response
        orchestrator = get_strands_orchestrator()
        ai_response = await orchestrator.get_facilitator_response(
            room_context={
                "topic": room.topic,
                "transcripts": transcripts,
                "current_round": room.current_round
            },
            task="provide_feedback"
        )
        
        # Generate audio via TTS
        tts_service = get_tts_service()
        audio_result = await tts_service.synthesize(
            text=ai_response["text"],
            voice="Matthew",
            language="en-US"
        )
        
        if audio_result["success"]:
            # Emit AI audio to all participants
            await sio.emit("ai-speaking", {
                "audio_url": audio_result.get("audio_url"),
                "text": ai_response["text"],
                "duration": audio_result.get("duration"),
                "use_browser_tts": audio_result.get("use_browser_tts", False)
            }, room=room_id)
            
            print(f"[Backend] AI agent speaking in room {room_id}")
        else:
            print(f"[Backend] TTS failed: {audio_result.get('error')}")
            
    except Exception as e:
        print(f"Error handling ai-agent-turn: {str(e)}")
```

**Frontend Handler (`AudioContext.jsx`):**

```javascript
useEffect(() => {
  if (!socket) return
  
  socket.on('ai-speaking', async (data) => {
    console.log('[Audio] AI agent is speaking:', data.text)
    
    if (data.use_browser_tts) {
      // Development: Use browser's SpeechSynthesis API
      const utterance = new SpeechSynthesisUtterance(data.text)
      utterance.lang = data.language || 'en-US'
      utterance.rate = 1.0
      window.speechSynthesis.speak(utterance)
      
      utterance.onend = () => {
        socket.emit('ai-turn-complete')
      }
    } else {
      // Production: Play audio from URL
      const audio = new Audio(data.audio_url)
      audio.play()
      
      audio.onended = () => {
        socket.emit('ai-turn-complete')
      }
    }
    
    // Update UI to show AI is speaking
    setAiSpeaking({
      isActive: true,
      text: data.text,
      duration: data.duration
    })
  })
  
  socket.on('ai-turn-complete', () => {
    setAiSpeaking({ isActive: false })
  })
  
  return () => {
    socket.off('ai-speaking')
    socket.off('ai-turn-complete')
  }
}, [socket])
```

#### 11.4.3 AI Agent Participant Entry

**Database Entry:**

When the room starts, the backend should create a special participant entry for the AI agent:

```python
async def create_ai_agent_participant(room_id: str) -> str:
    """Create AI agent as a participant in the room"""
    
    agent_participant = {
        "participant_id": f"ai-agent-{uuid.uuid4()}",
        "room_id": room_id,
        "user_id": "system-ai-facilitator",  # Special system user
        "anonymous_name": "AI Facilitator",
        "role": "agent",  # Special role
        "is_ready": True,  # Always ready
        "turn_order": -1,  # Will be assigned during turn setup
        "joined_at": datetime.now().isoformat()
    }
    
    await db.save_participant(agent_participant)
    
    return agent_participant["participant_id"]
```

**Turn Order with AI:**

```python
def assign_turn_order(participants):
    """Assign turn order including AI agent"""
    
    # Separate humans and AI
    human_participants = [p for p in participants if p.role != "agent"]
    ai_agents = [p for p in participants if p.role == "agent"]
    
    # Shuffle humans
    random.shuffle(human_participants)
    
    # Interleave AI agent(s) with humans
    # Example: Human1, Human2, AI, Human3, Human4, AI (repeat)
    turn_order = []
    ai_frequency = 2  # AI speaks every 2 human turns
    
    for i, human in enumerate(human_participants):
        turn_order.append(human)
        if (i + 1) % ai_frequency == 0 and ai_agents:
            turn_order.append(ai_agents[0])
    
    # Assign turn_order field
    for idx, participant in enumerate(turn_order):
        participant.turn_order = idx
    
    return turn_order
```

---

### 11.5 Summary: Complete Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────────┐
│                     Complete Room Flow: APIs + Sockets                    │
└──────────────────────────────────────────────────────────────────────────┘

Phase 1: Setup (REST APIs)
──────────────────────────────
1. POST /auth/google-login       → User authenticated
2. GET  /rooms?status=waiting    → Browse available rooms
3. POST /rooms                   → Create room (status: WAITING)
4. POST /participants            → Join room as participant
5. PATCH /participants/:id       → Mark ready (is_ready: true)
   └─ Socket: emit 'participant-ready' (optional notification)

Phase 2: Start Room (Hybrid)
──────────────────────────────
6. POST /rooms/:id/start         → Backend validates & starts room
   ├─ Check all participants ready
   ├─ Generate AI topic
   ├─ Create AI agent participant
   ├─ UPDATE rooms SET status = "IN_PROGRESS", started_at = NOW()
   └─ Socket: emit 'room-started' to all participants
      └─ Payload: { topic, first_speaker, facilitator_agent_id }

Phase 3: WebRTC Setup (Sockets)
──────────────────────────────
7. Frontend: Initialize WebRTC on 'room-started'
   ├─ requestMicrophoneAccess()
   ├─ emit 'ready-for-webrtc'
   └─ On 'peer-ready': establish peer connections
      ├─ Create RTCPeerConnection
      ├─ Exchange offers/answers (via webrtc-offer/answer)
      └─ Exchange ICE candidates (via webrtc-ice-candidate)

Phase 4: Speaking Turns (Sockets + Transcripts)
──────────────────────────────
8. Backend: emit 'turn-started' { speaker, timer: 60 }
9. Speaker unmutes and speaks
   ├─ Audio flows via WebRTC P2P to all participants
   └─ Frontend STT: emit 'speech-transcript' { text }
      └─ Backend saves to DB and sends to AI agent

10. AI analyzes transcript (instant feedback)
    └─ emit 'english-feedback' (private to speaker)

11. Turn ends (timer or manual)
    └─ emit 'turn-ended' → emit 'turn-started' (next speaker)

Phase 5: AI Agent Turn (Sockets + TTS)
──────────────────────────────
12. Backend detects AI agent turn
    ├─ orchestrator.get_facilitator_response()
    ├─ tts_service.synthesize(text) → audio_url
    └─ emit 'ai-speaking' { audio_url, text, duration }

13. Frontend plays AI audio
    ├─ new Audio(audio_url).play()
    └─ On end: emit 'ai-turn-complete'

Phase 6: Room End (REST API)
──────────────────────────────
14. All rounds complete
    ├─ Backend: UPDATE rooms SET status = "COMPLETED", ended_at = NOW()
    ├─ orchestrator.get_english_feedback(all_statements, instant: false)
    └─ emit 'discussion-ended' { comprehensive_feedback }

15. GET /feedback/participant/:id → Fetch detailed feedback summary
```

---

### 11.6 Implementation Checklist

**Backend Changes (server_py):**
- [x] Existing: `GET /api/rooms`, `POST /api/rooms` (room_routes.py)
- [x] Existing: `POST /api/participants`, `GET /api/participants/:id` (participant_routes.py)
- [x] Existing: `PATCH /api/participants/:id` (participant_routes.py)
- [ ] New: `POST /api/rooms/:roomId/start` endpoint in room_routes.py
  - Validate all participants ready
  - Generate topic if needed
  - Create AI agent participant entry
  - Update room status to IN_PROGRESS
  - Emit 'room-started' socket event
- [ ] New: `GET /api/rooms/:roomId/participants` endpoint in room_routes.py
- [ ] New: TTS service implementation (tts_service.py)
  - AWSPollyTTS class for production
  - BrowserTTS class for development
- [ ] New: Socket handler for AI agent turn (`ai-agent-turn` event)
  - Generate AI response via orchestrator
  - Call TTS service
  - Emit 'ai-speaking' event
- [ ] New: Turn order assignment logic including AI agent
- [x] Existing: WebRTC signaling handlers (webrtc-offer, webrtc-answer, webrtc-ice-candidate)
- [x] Existing: Transcript saving (speech-transcript event)

**Frontend Changes (client):**
- [ ] New: Use REST APIs for state management
  - Fetch rooms: `GET /api/rooms`
  - Create room: `POST /api/rooms`
  - Join room: `POST /api/participants`
  - Mark ready: `PATCH /api/participants/:id`
  - Start room: `POST /api/rooms/:id/start`
- [ ] Update: Refetch participant list on socket events (participant-joined, participant-left)
- [ ] New: Handle 'room-started' event
  - Initialize WebRTC if not already connected
  - Update UI to show room is live
- [ ] New: Handle 'ai-speaking' event
  - Play audio from URL or use browser TTS
  - Show "AI Facilitator is speaking" indicator
  - Emit 'ai-turn-complete' when audio ends
- [x] Existing: WebRTC connection management (AudioContext.jsx)
- [x] Existing: Real-time participant updates (SocketContext.jsx)

**Documentation:**
- [x] This section: WebRTC architecture and API flow
- [ ] Update API reference docs with new endpoints
- [ ] Add code examples for hybrid API + socket usage
- [ ] Update product_docs_and_updates.md changelog

---

**Document Status**: ✅ Ready for Implementation  
**Last Updated**: October 2025  
**Version**: 1.0  
**Authors**: Product Team - AWS AI Agent Hackathon 2025
