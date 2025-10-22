# Get Models Documentation

## Overview
Added Get<Name>Model classes for all Pydantic models to provide flexible query capabilities for GET requests. These models inherit from BaseDictModel and have only the primary key field as required, with all other fields as optional.

## Get Models Added

### 1. GetParticipantModel
- **Required Field**: `participant_id: str`
- **Optional Fields**: All fields from CreateParticipantModel
- **Purpose**: Flexible participant queries with optional filtering
- **Location**: `server_py/src/models/participant_pydantic_models.py`

### 2. GetAgentModel
- **Required Field**: `agent_id: str`
- **Optional Fields**: All fields from CreateAgentModel
- **Purpose**: Flexible agent queries with optional filtering
- **Location**: `server_py/src/models/agent_pydantic_models.py`

### 3. GetInstantFeedbackModel
- **Required Field**: `feedback_id: str`
- **Optional Fields**: All fields from CreateInstantFeedbackModel
- **Purpose**: Flexible instant feedback queries with optional filtering
- **Location**: `server_py/src/models/feedback_pydantic_models.py`

### 4. GetComprehensiveFeedbackModel
- **Required Field**: `feedback_id: str`
- **Optional Fields**: All fields from CreateComprehensiveFeedbackModel
- **Purpose**: Flexible comprehensive feedback queries with optional filtering
- **Location**: `server_py/src/models/feedback_pydantic_models.py`

### 5. GetTranscriptModel
- **Required Field**: `transcript_id: str`
- **Optional Fields**: All fields from CreateTranscriptModel
- **Purpose**: Flexible transcript queries with optional filtering
- **Location**: `server_py/src/models/transcript_pydantic_models.py`

### 6. GetRoomModel
- **Required Field**: `room_id: str`
- **Optional Fields**: All fields from CreateRoomModel
- **Purpose**: Flexible room queries with optional filtering
- **Location**: `server_py/src/models/room_pydantic_models.py`

### 7. GetUserModel
- **Required Field**: `user_id: str`
- **Optional Fields**: All fields from SignUpModel
- **Purpose**: Flexible user queries with optional filtering
- **Location**: `server_py/src/models/user_pydantic_models.py`

## Model Structure Pattern

Each Get model follows this pattern:

```python
class Get<Name>Model(BaseDictModel):
    """Model for getting <name> with optional filters"""
    <name>_id: str = Field(..., description="<Name> UUID, Primary Key")
    
    # All other fields from Create<Name>Model as optional
    field1: Optional[Type] = Field(None, description="...")
    field2: Optional[Type] = Field(None, description="...")
    # ... etc
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
```

## Usage Examples

### 1. Basic Query (ID only)
```python
get_participant = GetParticipantModel(participant_id="123e4567-e89b-12d3-a456-426614174000")
```

### 2. Query with Filters
```python
get_participant = GetParticipantModel(
    participant_id="123e4567-e89b-12d3-a456-426614174000",
    room_id="room-123",
    is_ready=True
)
```

### 3. Query with Multiple Optional Fields
```python
get_room = GetRoomModel(
    room_id="room-456",
    status="waiting",
    cefr_level="B1",
    max_participants=6
)
```

## Benefits

1. **Flexible Querying**: Allows optional filtering on any field
2. **Type Safety**: Maintains Pydantic validation for all fields
3. **Consistent API**: Follows the same pattern across all models
4. **Backward Compatibility**: Doesn't break existing code
5. **Documentation**: Clear field descriptions for API documentation

## Integration with Services

These Get models can be used in service methods for:
- Database queries with optional WHERE clauses
- API endpoint parameter validation
- Search and filtering operations
- Complex query building

## API Route Integration

Example usage in API routes:

```python
@router.get("/{participant_id}")
async def get_participant(participant_id: str, filters: GetParticipantModel = Depends()):
    """Get participant with optional filters"""
    return participant_service.get_participant_with_filters(filters)
```

## Export Configuration

All Get models are exported in `server_py/src/models/__init__.py` and available for import:

```python
from src.models import (
    GetParticipantModel,
    GetAgentModel,
    GetInstantFeedbackModel,
    GetComprehensiveFeedbackModel,
    GetTranscriptModel,
    GetRoomModel,
    GetUserModel
)
```

## Testing Recommendations

1. Test basic ID-only queries
2. Test queries with single optional field
3. Test queries with multiple optional fields
4. Test validation of required ID field
5. Test optional field type validation
6. Test integration with database services
7. Test API endpoint parameter binding

## Future Enhancements

1. Add query operators (gt, lt, contains, etc.)
2. Add pagination support
3. Add sorting capabilities
4. Add relationship filtering
5. Add aggregation support