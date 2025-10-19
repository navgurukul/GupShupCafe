# Regression Test Suite for API Routes

## Quick Start

Run all regression tests:
```bash
cd server_py
python -m pytest tests/test_routes_regression.py -v
```

## Test Summary

- **Total Tests**: 42
- **Status**: ✅ All Passing
- **Coverage**: All 6 route files in `server_py/src/api/`
- **Test File**: `tests/test_routes_regression.py`

## Test Breakdown

### TestUserRoutes (8 tests)
- ✅ test_signup_user
- ✅ test_login_user
- ✅ test_get_user
- ✅ test_list_users
- ✅ test_delete_user
- ✅ test_update_cefr_level
- ✅ test_update_last_active
- ✅ test_update_password

### TestRoomRoutes (8 tests)
- ✅ test_create_room
- ✅ test_get_room
- ✅ test_list_rooms
- ✅ test_delete_room
- ✅ test_update_room_status
- ✅ test_update_room_state
- ✅ test_end_room

### TestParticipantRoutes (10 tests)
- ✅ test_create_participant
- ✅ test_get_participant
- ✅ test_list_participants_for_room
- ✅ test_update_participant
- ✅ test_delete_participant
- ✅ test_update_participant_left
- ✅ test_update_participant_muted
- ✅ test_update_participant_speaking
- ✅ test_update_participant_ready

### TestTranscriptRoutes (6 tests)
- ✅ test_create_transcript
- ✅ test_get_transcript
- ✅ test_list_transcripts_for_room
- ✅ test_delete_transcript
- ✅ test_update_transcript_processing
- ✅ test_update_transcript_audio_url

### TestFeedbackRoutes (6 tests)
- ✅ test_create_instant_feedback
- ✅ test_create_comprehensive_feedback
- ✅ test_list_feedback_for_participant
- ✅ test_list_feedback_for_room
- ✅ test_get_feedback
- ✅ test_delete_feedback

### TestGeneralRoutes (6 tests)
- ✅ test_health_check
- ✅ test_get_topics
- ✅ test_generate_topic
- ✅ test_get_topic_by_category
- ✅ test_submit_feedback
- ✅ test_get_config

## Key Features

### Mock Database
- Replicates complete schema from `database.py`
- In-memory storage with Python dictionaries
- Supports INSERT, SELECT, UPDATE, DELETE operations
- Automatic reset between tests

### Test Data
- Uses realistic dummy data
- Validates Pydantic models
- Covers all required and optional fields
- Tests enums and nested structures

### Test Strategy
- Service layer testing (business logic)
- Response structure validation
- Error handling verification
- Isolated, independent tests

## Documentation

Comprehensive documentation available at:
- `docs/Miscellaneous/regression_tests_documentation.md`

## Running Specific Tests

### By Class
```bash
python -m pytest tests/test_routes_regression.py::TestUserRoutes -v
```

### By Test
```bash
python -m pytest tests/test_routes_regression.py::TestUserRoutes::test_signup_user -v
```

### With Coverage
```bash
python -m pytest tests/test_routes_regression.py --cov=src/api --cov=src/services --cov=src/models
```

## Impact

This test suite provides:
- ✅ Verification that all routes, services, and models work correctly
- ✅ Safety net for refactoring and feature additions
- ✅ Documentation of expected API behavior
- ✅ Automated validation of integration between layers
- ✅ Confidence in code changes

## Maintenance

When adding new routes:
1. Add test method in appropriate test class
2. Create realistic test data using Pydantic models
3. Call service with mock database connection
4. Verify response structure
5. Ensure test isolation

When updating schema:
1. Update MockDatabase class
2. Update execute_side_effect function
3. Update test data to match new fields
4. Run tests to verify compatibility
