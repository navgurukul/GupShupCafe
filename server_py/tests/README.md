# GupShup Cafe Backend Test Suite

## Overview

Comprehensive test suite for the GupShup Cafe Python/FastAPI backend server covering all core features and functionality.

## Test Statistics

- **Total Tests**: 136 active tests (65 new + 71 existing; 4 skipped requiring DB initialization)
- **Test Files**: 8 (2 new: test_llm.py, test_agents.py)
- **Code Coverage**: All major components including LLM and AI agents
- **Success Rate**: 100% passing (132 passed, 4 skipped)

## Test Files

### 1. `test_ai.py` - AI Topic Generation (7 tests)
Tests the AI-powered topic generation system:
- ✅ Get random fallback topics
- ✅ Get all fallback topics
- ✅ Get topic by category
- ✅ Case-insensitive category matching
- ✅ AI response parsing
- ✅ Handle long titles gracefully
- ✅ Generate discussion topics

**Coverage**: Topic generation, fallback system, AI integration

### 2. `test_api.py` - REST API Endpoints (10 tests)
Tests all REST API endpoints:
- ✅ Root endpoint (/)
- ✅ Health check endpoints (/health, /api/health)
- ✅ Get all topics (/api/topics)
- ✅ Generate topic (/api/topics/generate)
- ✅ Get topic by category (/api/topics/category/{category})
- ✅ Invalid category handling
- ✅ Get configuration (/api/config)
- ✅ Submit feedback (/api/feedback)
- ✅ Get room state (/api/room/{roomId}/state)

**Coverage**: All REST endpoints, request/response handling

### 3. `test_database.py` - Database Operations (7 tests)
Tests database layer functionality:
- ✅ Database initialization
- ✅ Save session data
- ✅ Save participant data
- ✅ Record topic usage
- ✅ Topic usage counting
- ✅ Session analytics
- ✅ Server statistics
- ✅ Update session end data

**Coverage**: SQLite operations, data persistence, analytics

### 4. `test_room_manager.py` - Room Management (12 tests)
Tests real-time room and participant management:
- ✅ Create and get rooms
- ✅ Add users to rooms
- ✅ Remove users from rooms
- ✅ Update user information
- ✅ Get room participants
- ✅ Change user roles
- ✅ Invalid role handling
- ✅ Role statistics
- ✅ Speaker eligibility checks
- ✅ Discussion state tracking
- ✅ Get all rooms
- ✅ Get room statistics

**Coverage**: Real-time room management, WebSocket state

### 5. `test_regression_core.py` - Regression Tests (30 tests)
**NEW**: Comprehensive regression test suite for core features:

#### Session Lifecycle (3 tests)
- ✅ Create and retrieve sessions
- ✅ Update session end data
- ✅ Handle multiple participants per session

#### Participant Management (2 tests)
- ✅ Save participants with all fields
- ✅ Track participant speaking time

#### Topic Recording (2 tests)
- ✅ Record topic usage multiple times
- ✅ Record different topics

#### Error Handling (5 tests)
- ✅ Room state response structure
- ✅ Invalid category requests
- ✅ Feedback with missing fields
- ✅ Feedback with empty comments
- ✅ Config endpoint validation

#### Integration Workflows (2 tests)
- ✅ Complete discussion workflow
- ✅ Concurrent sessions handling

#### Topics Endpoints (4 tests)
- ✅ Get all topics with structure validation
- ✅ Generate discussion topics
- ✅ Get topics by valid category
- ✅ Handle invalid categories

#### Config Endpoint (2 tests)
- ✅ Config structure validation
- ✅ Features configuration

#### Feedback Endpoint (3 tests)
- ✅ Submit complete feedback
- ✅ Submit feedback with only rating
- ✅ Submit various rating values

#### Room State Endpoint (2 tests)
- ✅ Room state response structure
- ✅ Discussion fields validation

#### Analytics Endpoints (5 tests - skipped)
Note: These tests require database initialization and are marked as skipped:
- ⏭️ Session analytics with data
- ⏭️ Session limit parameter
- ⏭️ Analytics validation (tested separately)
- ⏭️ Topics analytics
- ⏭️ Server stats comprehensive

**Coverage**: End-to-end workflows, edge cases, error handling

### 6. `test_socket_handlers.py` - Socket.io Event Handlers (5 tests)
Tests real-time WebSocket event handling:
- ✅ User ready without data
- ✅ User ready with data
- ✅ User ready with false status
- ✅ User ready when room not found
- ✅ User ready triggers discussion start

**Coverage**: Socket.io events, WebSocket communication

### 7. `test_llm.py` - LLM Module (29 tests)
**NEW**: Comprehensive tests for Language Model providers:

#### LLM Interface (2 tests)
- ✅ Cannot instantiate abstract class
- ✅ Interface methods exist

#### Gemini LLM (9 tests)
- ✅ Initialization with API key
- ✅ Initialization from environment
- ✅ Initialization without API key
- ✅ Basic chat functionality
- ✅ Chat with custom parameters
- ✅ English analysis
- ✅ English analysis with context

#### Bedrock LLM (7 tests)
- ✅ Initialization with parameters
- ✅ Initialization with defaults
- ✅ Initialization from environment
- ✅ Basic chat functionality
- ✅ Chat with custom parameters
- ✅ English analysis
- ✅ English analysis with context

#### AI Service Manager (10 tests)
- ✅ Initialization with default provider
- ✅ Initialization with custom config
- ✅ Get LLM instance
- ✅ Switch provider to Bedrock
- ✅ Switch provider to Gemini
- ✅ Unknown provider fallback
- ✅ Multiple calls return same instance
- ✅ Get current provider
- ✅ Singleton pattern
- ✅ Initialization with Gemini API key

#### LLM Integration (3 tests)
- ✅ Manager can use Gemini LLM
- ✅ Manager can use Bedrock LLM
- ✅ Analyze English across providers

**Coverage**: LLM providers, factory pattern, provider switching, English analysis

### 8. `test_agents.py` - AI Agents Module (36 tests)
**NEW**: Comprehensive tests for AI agent functionality:

#### English Feedback Agent (13 tests)
- ✅ Agent initialization
- ✅ Basic analysis
- ✅ Analysis with context
- ✅ Grammar analysis
- ✅ Vocabulary analysis
- ✅ Vocabulary analysis with empty text
- ✅ Fluency analysis
- ✅ CEFR level determination - 6 separate tests for each level:
  - ✅ C2 (Proficiency)
  - ✅ C1 (Advanced)
  - ✅ B2 (Upper Intermediate)
  - ✅ B1 (Intermediate)
  - ✅ A2 (Elementary)
  - ✅ A1 (Beginner)

#### Debate Facilitator Agent (9 tests)
- ✅ Agent initialization
- ✅ Facilitate turn basic
- ✅ Facilitate turn without speaker name
- ✅ Facilitate turn with default topic
- ✅ Suggest topic direction with empty statements
- ✅ Suggest topic direction with statements
- ✅ Moderate discussion
- ✅ Generate speaking prompt
- ✅ Generate speaking prompt with custom parameters

#### AWS Strands Orchestrator (10 tests)
- ✅ Orchestrator initialization
- ✅ Get instant English feedback
- ✅ Get comprehensive English feedback
- ✅ Handle empty statements
- ✅ Combine multiple statements
- ✅ Include facilitation suggestion
- ✅ Format feedback message
- ✅ Format feedback message without suggestions
- ✅ Format gentle mention
- ✅ Use both agents

#### Agents Integration (4 tests)
- ✅ English agent with real LLM
- ✅ Facilitator agent with real LLM
- ✅ Orchestrator full workflow
- ✅ Agent error handling

**Coverage**: English feedback, CEFR analysis, debate facilitation, multi-agent orchestration

## Running Tests

### Run All Tests
```bash
cd server_py
pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/test_regression_core.py -v
pytest tests/test_llm.py -v
pytest tests/test_agents.py -v
```

### Run LLM and Agents Tests Only
```bash
pytest tests/test_llm.py tests/test_agents.py -v
```

### Run Specific Test Class
```bash
pytest tests/test_regression_core.py::TestSessionLifecycle -v
```

### Run With Coverage
```bash
pytest tests/ -v --cov=src --cov-report=html
```

### Run Only Fast Tests (Skip Skipped)
```bash
pytest tests/ -v -k "not skip"
```

## Test Structure

### Fixtures (from `conftest.py`)

- `test_db`: Temporary database for testing
- `sample_topic`: Sample topic data
- `sample_session`: Sample session data
- `sample_participant`: Sample participant data

### Test Organization

Tests are organized by functionality:
1. **Unit Tests**: Test individual functions (test_ai.py)
2. **API Tests**: Test HTTP endpoints (test_api.py)
3. **Database Tests**: Test data persistence (test_database.py)
4. **Integration Tests**: Test component interactions (test_room_manager.py)
5. **Regression Tests**: Test complete workflows and edge cases (test_regression_core.py)

## Test Coverage

### Core Features Tested

✅ **Authentication & User Management**
- Anonymous name generation
- User data persistence

✅ **Real-time Communication**
- Room creation and management
- Participant tracking
- Role management

✅ **AI Integration**
- Topic generation with HuggingFace
- Fallback topic system
- Category-based selection

✅ **LLM Providers**
- Gemini LLM (Google)
- Bedrock LLM (AWS)
- AI Service Manager factory
- Provider switching
- English language analysis

✅ **AI Agents**
- English Feedback Agent
- Debate Facilitator Agent
- AWS Strands Orchestrator
- CEFR level analysis (A1-C2)
- Multi-agent orchestration

✅ **Database Operations**
- Session tracking
- Participant data
- Topic usage analytics
- Server statistics

✅ **REST API**
- All 10+ endpoints
- Error handling
- Input validation
- Response formatting

✅ **Analytics**
- Session analytics
- Topic analytics
- Server statistics
- Participant metrics

## Adding New Tests

### Template for New Test

```python
def test_new_feature(client):
    """Test description"""
    # Arrange
    test_data = {"key": "value"}
    
    # Act
    response = client.post("/api/endpoint", json=test_data)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
```

### Best Practices

1. **Use descriptive test names**: `test_<feature>_<scenario>_<expected_result>`
2. **Follow AAA pattern**: Arrange, Act, Assert
3. **Test one thing per test**: Keep tests focused
4. **Use fixtures**: Reuse common test data
5. **Test edge cases**: Include error scenarios
6. **Document complex tests**: Add comments for clarity

## Continuous Integration

Tests are designed to run in CI/CD pipelines:
- Fast execution (< 1 second)
- No external dependencies (uses in-memory DB)
- Clean setup/teardown
- Isolated test cases

## Test Maintenance

### When to Update Tests

- ✏️ API endpoint changes
- ✏️ Database schema changes
- ✏️ New features added
- ✏️ Bug fixes requiring regression tests
- ✏️ Breaking changes in dependencies

### Test Health Checklist

- [ ] All tests passing
- [ ] No deprecated test patterns
- [ ] Coverage for new features
- [ ] No flaky tests
- [ ] Fast execution time
- [ ] Clear test names
- [ ] Proper documentation

## Troubleshooting

### Common Issues

**Issue**: Tests fail with database errors
```bash
# Solution: Ensure clean test database
pytest tests/ --cache-clear
```

**Issue**: Import errors
```bash
# Solution: Install test dependencies
pip install -r requirements-dev.txt
```

**Issue**: Tests hang
```bash
# Solution: Check for async/await issues
pytest tests/ -v --timeout=10
```

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure 100% test pass rate
3. Update this documentation
4. Run full test suite before committing

## Test Metrics

| Metric | Value |
|--------|-------|
| Total Tests | 136 active (71 existing + 65 new) |
| Pass Rate | 97.06% (132 passed, 4 skipped) |
| Execution Time | < 1s |
| Code Coverage | All major components + LLM + Agents |
| Test Files | 8 (6 existing + 2 new) |
| New LLM Tests | 29 |
| New Agent Tests | 36 |

## Independent Module Execution

Both LLM and Agents modules can be run independently for testing and demonstration:

### LLM Module
```bash
# Run all demos
python -m src.llm

# Interactive mode
python -m src.llm interactive

# Specific demos
python -m src.llm manager
python -m src.llm gemini
python -m src.llm bedrock
```

### Agents Module
```bash
# Run all demos
python -m src.agents

# Interactive mode
python -m src.agents interactive

# Specific demos
python -m src.agents english
python -m src.agents facilitator
python -m src.agents orchestrator
```

See [LLM and Agents Testing Guide](../../docs/Miscellaneous/llm_and_agents_testing_guide.md) for detailed documentation.

## Future Enhancements

- [x] Add LLM provider tests
- [x] Add AI agent tests
- [ ] Add performance/load tests
- [ ] Add security tests
- [ ] Increase code coverage to 90%+
- [ ] Add mutation testing
- [ ] Add contract tests for API
- [ ] Add real API integration tests for LLM providers
