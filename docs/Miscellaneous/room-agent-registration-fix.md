# Room and Agent Registration Fix

**Date**: October 20, 2025  
**Issue**: Agent registration was using incorrect room IDs, causing facilitator agents to be registered with UUID room IDs instead of the actual room IDs that users joined.

## Problem Description

1. **Room Creation Issue**: When a discussion started, the system was creating a new `active_room_id` using `str(uuid.uuid4())` and saving this as the `room_id` in the database, instead of using the actual room ID that users joined.

2. **Agent Registration Issue**: The facilitator and English agents were being created with the `active_room_id` (the UUID), not the original `room_id` that users joined.

3. **Topic Generation**: The topic generator wasn't using the room's topic category to generate relevant topics via MCP tools.

## Solution Implemented

### 1. Fixed Room ID Usage
- **Before**: Created separate `active_room_id = str(uuid.uuid4())` for database storage
- **After**: Use the original `room_id` that users joined for all database operations
- **Impact**: Agents are now registered with the correct room ID that matches user sessions

### 2. Updated Agent Registration
- **Before**: `agent_service.create_room_agents(active_room_id, topic)`
- **After**: `agent_service.create_room_agents(room_id, topic)`
- **Added**: Update room record with facilitator `agent_id` after creation
- **Impact**: Facilitator agent ID is now properly linked to the room record

### 3. Enhanced Topic Generation
- **Before**: `topic = await generate_discussion_topic()`
- **After**: `topic = await generate_discussion_topic(category=topic_category)`
- **Added**: Category-based topic selection using room metadata
- **Impact**: Topics are now generated based on the room's specified category

### 4. Database Consistency
- All database operations now use the original `room_id`:
  - Room creation: `room_id` instead of `active_room_id`
  - Participant saving: `room_id` instead of `active_room_id`
  - Transcript saving: `room_id` instead of `active_room_id`
  - Room updates: `room_id` instead of `active_room_id`

## Files Modified

1. **`server_py/src/socket/socket_handlers.py`**
   - `check_and_start_discussion()` function
   - `speech_transcript()` handler
   - `end_turn()` handler
   - Timer completion callback in `start_turn_timer()`

2. **`server_py/src/ai/topic_generator.py`**
   - `generate_discussion_topic()` function signature
   - Added category parameter support

## Database Schema Impact

The `rooms` table now properly stores:
- `room_id`: The actual room ID that users joined
- `agent_id`: The facilitator agent ID for the room
- Topic information based on room category

The `agents` table now properly stores:
- `room_id`: Matches the room ID that users joined
- Facilitator and English agents linked to correct room

## Testing Recommendations

1. **Room Creation Flow**:
   - Verify room is created with correct `room_id`
   - Verify agents are created with matching `room_id`
   - Verify room record is updated with facilitator `agent_id`

2. **Topic Generation**:
   - Test category-based topic selection
   - Verify fallback to random topics when category not found
   - Test MCP integration for topic generation

3. **Database Consistency**:
   - Verify all transcripts, participants, and feedback use correct `room_id`
   - Verify agent queries return correct results for room

## Benefits

1. **Correct Agent-Room Linking**: Facilitator agents are now properly associated with the rooms users actually joined
2. **Improved Topic Relevance**: Topics are generated based on room category preferences
3. **Database Consistency**: All records use consistent room identifiers
4. **MCP Integration Ready**: System is prepared for MCP-based topic generation
5. **Simplified Architecture**: Removed unnecessary UUID mapping complexity

## Next Steps

1. Test the changes with actual room creation and agent interactions
2. Implement MCP-based topic generation for enhanced topic variety
3. Add regression tests to prevent similar issues in the future
4. Monitor agent performance and room-agent associations in production