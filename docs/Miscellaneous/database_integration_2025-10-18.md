# Database Integration Documentation
**Date:** 2025-10-18  
**Author:** GitHub Copilot  
**Commit:** Database Integration - Frontend and Backend Data Capture

## Overview
This document describes the integration of frontend and backend systems to capture and persist user data, session data, and participant data into the SQLite database (`gupshup-database.db`).

## Changes Summary

### 1. Database Configuration
- **File:** `server_py/.env.example`
- **Status:** Already configured correctly
- **Configuration:**
  ```
  DATABASE_URL=./data/gupshup-database.db
  ```

### 2. Database Schema Fixes
- **File:** `server_py/src/database/database.py`
- **Changes:**
  - Fixed `save_session()` method to handle both camelCase and snake_case field names
  - Added missing `status` parameter to session insert (fixed binding count mismatch)
  - Updated `get_session_analytics()` to include `room_name` in SELECT query
  - Updated `update_session_end()` to use `session_id` instead of `id`
  - Made all database methods flexible to accept both naming conventions

### 3. Room Metadata Support
- **File:** `server_py/src/models/room.py`
- **Changes:**
  - Added `metadata` attribute to `Room` class to store additional room information
  - This allows storing room_name, topic_category, cefr_level, and max_participants

### 4. Socket Handler Enhancements
- **File:** `server_py/src/socket/socket_handlers.py`
- **Changes:**
  - Updated `join_room` handler to accept room metadata as third parameter
  - Store room metadata in `room.metadata` for later use
  - Enhanced `check_and_start_discussion()` to:
    - Extract room_name from metadata
    - Map CEFR level string (A1-C2) to integer (1-6)
    - Save session data with complete metadata
    - Save all participant data when discussion starts
    - Include campus and location for participants

### 5. Frontend Socket Context
- **File:** `client/src/contexts/SocketContext.jsx`
- **Changes:**
  - Updated `joinRoom()` function to accept `roomMetadata` parameter
  - Pass room metadata to backend when joining rooms
  - Store metadata in `metaRef` for reconnection scenarios
  - Emit room metadata as third parameter in 'join-room' event

### 6. Frontend Lobby Page
- **File:** `client/src/pages/LobbyPage.jsx`
- **Changes:**
  - Updated `handleCreateRoom()` to pass room metadata when joining
  - Updated `handleJoinPredefinedRoom()` to pass room metadata
  - Metadata includes: name, room_name, topic_category, cefr_level, max_participants

### 7. Authentication Context Enhancement
- **File:** `client/src/contexts/AuthContext.jsx`
- **Changes:**
  - Added `anonymousName` to authentication state
  - Updated `login()` to accept anonymousName parameter
  - Store anonymousName separately in localStorage (`auth_anonymousName`)
  - Load anonymousName on page refresh

### 8. User Signup Integration
- **File:** `client/src/pages/SignupPage.jsx`
- **Changes:**
  - Integrated with backend `/users/signup` API endpoint
  - Send user data (name, email, password, categories) to backend
  - Generate random anonymous name (e.g., "Happy Tiger", "Clever Eagle")
  - Login user with backend-generated user ID on successful signup
  - Handle and display signup errors

### 9. Testing
- **File:** `server_py/tests/test_database.py`
- **Changes:** Fixed test assertions to match new schema field names

- **File:** `server_py/tests/test_integration.py` (NEW)
- **Added Tests:**
  - `test_session_creation_with_participants` - Verifies session and participant data saving
  - `test_cefr_level_mapping` - Validates CEFR level storage
  - `test_room_metadata_handling` - Ensures room metadata is correctly persisted

## Data Flow

### User Registration Flow
1. User fills signup form in `SignupPage.jsx`
2. Frontend sends POST request to `/users/signup`
3. Backend `user_services.py` creates user record in `users` table
4. Backend returns user ID
5. Frontend generates anonymous name and logs in user
6. User data persisted in `users` table

### Session Creation Flow
1. User joins room in `LobbyPage.jsx`
2. Frontend calls `joinRoom(roomId, role, roomMetadata)`
3. `SocketContext` emits 'join-room' event with user data and room metadata
4. Backend `join_room` handler stores metadata in `room.metadata`
5. When minimum participants ready, `check_and_start_discussion()` fires
6. Session data saved to `sessions` table with:
   - session_id
   - room_id
   - room_name (from metadata)
   - topic_title, topic_category
   - participant_count
   - timestamps
   - status
   - crf_level (converted from A1-C2 to 1-6)

### Participant Data Flow
1. When discussion starts, all ready participants are saved
2. For each participant, data saved to `participants` table:
   - user_id
   - session_id
   - anonymous_name
   - campus
   - location
   - joined_at
   - speaking_time_seconds (initially 0)

## Database Schema

### users Table
```sql
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    category TEXT,
    crf_level INTEGER NOT NULL DEFAULT 0
)
```

### sessions Table
```sql
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    room_id TEXT NOT NULL,
    room_name TEXT NOT NULL,
    topic_title TEXT,
    topic_category TEXT,
    participant_count INTEGER,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    ended_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    duration_seconds INTEGER,
    rounds_completed INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL DEFAULT 'active',
    crf_level INTEGER NOT NULL DEFAULT 0
)
```

### participants Table
```sql
CREATE TABLE participants (
    user_id TEXT PRIMARY KEY,
    session_id TEXT,
    anonymous_name TEXT,
    campus TEXT,
    location TEXT,
    joined_at DATETIME,
    left_at DATETIME,
    speaking_time_seconds INTEGER DEFAULT 0,
    FOREIGN KEY (session_id) REFERENCES sessions (session_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id)
)
```

## API Endpoints Used

### User Management
- **POST /users/signup**
  - Request: `{ name, email, password, category }`
  - Response: `{ status, data: userId, message }`

### Session Management
- Sessions are created automatically via Socket.io events
- No direct API calls needed from frontend

## Socket.io Events

### join-room
- **Emit:** Client → Server
- **Parameters:**
  1. `roomId` (string)
  2. `userData` (object): { userId, name, campus, location, anonymousName, role }
  3. `roomMetadata` (object, optional): { name, room_name, topic_category, cefr_level, max_participants }

### user-ready
- **Emit:** Client → Server
- **Effect:** Marks user as ready; triggers discussion start when minimum participants ready

### discussion-started
- **Listen:** Client ← Server
- **Payload:** { topic, firstSpeaker, duration }
- **Effect:** Session and participants saved to database

## Testing

### Run All Tests
```bash
cd server_py
export PYTHONPATH=$(pwd):$PYTHONPATH
pytest tests/test_database.py tests/test_integration.py -v
```

### Test Coverage
- Database operations: 7 tests
- Integration scenarios: 3 tests
- **Total: 10 tests, all passing**

## Configuration Notes

1. **Database Location:** `server_py/data/gupshup-database.db`
2. **Database is created automatically** on first run
3. **CEFR Level Mapping:**
   - A1 → 1
   - A2 → 2
   - B1 → 3
   - B2 → 4
   - C1 → 5
   - C2 → 6

## Known Limitations

1. User passwords are stored in plain text (should be hashed in production)
2. No user authentication validation on socket connections
3. No data validation for room metadata
4. Participant table uses user_id as PRIMARY KEY, preventing same user from joining multiple sessions (should be fixed to composite key)
5. **Note:** Database uses `crf_level` column name instead of the more standard `cefr_level` (CEFR = Common European Framework of Reference). This is a legacy naming convention that should be corrected in a future migration.

## Future Enhancements

1. Add password hashing for user security
2. Add session tokens for authentication
3. Validate room metadata before storage
4. Track participant speaking time during discussions
5. Add indexes for better query performance
6. Implement data archival for old sessions

## Regression Prevention

All changes maintain backward compatibility:
- Database methods accept both camelCase and snake_case
- Socket handlers gracefully handle missing metadata
- Frontend remains functional if backend API calls fail
- Tests validate both old and new data formats

## Migration Notes

No migration required. The integration works with existing database schema and automatically creates tables if they don't exist.
