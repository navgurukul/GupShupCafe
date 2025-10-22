# Participant Model Updates

## Overview
Updated the codebase to use the correct Pydantic participant models format across all files.

## Files Updated

### Backend Files

#### 1. `server_py/src/socket/room_manager.py`
- **Import Changes**: Updated imports to use `participant_pydantic_models`
- **Participant Reconstruction**: Updated `recover_room_from_database()` method to use correct ParticipantModel fields:
  - `participant_id` instead of `particid`
  - `user_id` for user identification
  - `anonymous_name` instead of `name`
  - `avatar_color` field added
  - `starting_cefr_level` and `ending_cefr_level` fields
  - `campusOrLocation` field
  - `speaking_time_seconds` field
  - `created_at` field

#### 2. `server_py/src/socket/socket_handlers.py`
- **Participant Saving**: Updated `check_and_start_discussion()` to save participants with correct Pydantic model format:
  - Complete participant data structure with all required fields
  - Proper datetime handling for `joined_at` field
  - Default values for optional fields
- **Transcript Handling**: Fixed user object access in `transcript_received()` handler

### Frontend Files

#### 3. `client/src/pages/LobbyPage.jsx`
- **Participant Creation**: Updated calls to `createParticipantForRoom()` to include default CEFR level
- **Error Handling**: Added fallback values for missing user data fields

#### 4. `client/src/utils/participantHelpers.js`
- **Already Correct**: This file was already using the correct participant model format
- **Fields Used**:
  - `user_id`
  - `room_id`
  - `anonymous_name`
  - `avatar_color`
  - `campusOrLocation`
  - `joined_at`
  - `starting_cefr_level`
  - `ending_cefr_level`

#### 5. `client/src/contexts/SocketContext.jsx`
- **Already Correct**: This file was already using the correct format for participant data

## Model Structure Used

### CreateParticipantModel Fields:
- `room_id`: Room identifier (foreign key)
- `user_id`: User identifier (foreign key)
- `anonymous_name`: Display name for the session
- `avatar_color`: Hex color code for avatar
- `role`: participant/host/listener
- `is_ready`: Ready status for discussion
- `turn_order`: Speaking order
- `is_speaking`: Currently speaking flag
- `is_muted`: Microphone muted flag
- `socket_id`: Socket.io connection ID
- `starting_cefr_level`: CEFR level at room start
- `ending_cefr_level`: CEFR level at room end
- `joined_at`: Join timestamp
- `left_at`: Leave timestamp
- `campusOrLocation`: Location information
- `speaking_time_seconds`: Total speaking time

### ParticipantModel (extends CreateParticipantModel):
- `participant_id`: Primary key UUID
- `created_at`: Creation timestamp

## Compatibility Notes

1. **Frontend-Backend Mapping**: The frontend still uses camelCase field names (e.g., `anonymousName`, `isReady`) for socket communication, while the backend uses snake_case for database operations.

2. **Socket Events**: Participant data in socket events maintains the existing format for frontend compatibility.

3. **Database Operations**: All database operations now use the correct Pydantic model structure.

## Testing Recommendations

1. Test participant creation through the API
2. Test room joining and participant synchronization
3. Test participant ready status updates
4. Test participant data persistence across reconnections
5. Verify transcript saving with correct participant references

## Migration Notes

- Existing participant data in the database should be compatible
- No database schema changes required
- Frontend components continue to work with existing socket event formats