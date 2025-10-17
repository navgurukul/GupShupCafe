# LLM and Agents Testing & Independent Execution Guide

## Overview

This document describes the test coverage and independent execution capabilities added to the `llm` and `agents` modules in the `server_py` project.

**Date Created:** 2025-10-17

## Test Coverage

### LLM Module Tests (`tests/test_llm.py`)

Comprehensive test coverage for all LLM-related components:

#### 1. LLM Interface Tests
- **test_cannot_instantiate_abstract_class**: Verifies that the abstract `LLMInterface` cannot be instantiated directly
- **test_interface_methods_exist**: Validates that required interface methods (`chat`, `analyze_english`) are defined

#### 2. Gemini LLM Tests
- **Initialization tests**: 
  - With API key
  - From environment variable
  - Without API key
- **Chat functionality tests**:
  - Basic chat
  - Chat with custom parameters (temperature, max_tokens)
- **English analysis tests**:
  - Basic analysis
  - Analysis with context

#### 3. Bedrock LLM Tests
- **Initialization tests**:
  - With model_id and region parameters
  - With default values
  - From environment variables
- **Chat functionality tests**:
  - Basic chat
  - Chat with custom parameters
- **English analysis tests**:
  - Basic analysis
  - Analysis with context

#### 4. AI Service Manager Tests
- **Initialization tests**:
  - Default provider (Gemini)
  - Custom configuration
  - With Gemini API key in config
- **Provider management tests**:
  - Get LLM instance
  - Switch between providers (Gemini ↔ Bedrock)
  - Unknown provider fallback
  - Multiple calls return same instance
  - Singleton pattern
- **Integration tests**:
  - Manager can use Gemini LLM
  - Manager can use Bedrock LLM
  - English analysis across providers

**Total LLM Tests:** 29 tests

### Agents Module Tests (`tests/test_agents.py`)

Comprehensive test coverage for all agent components:

#### 1. English Feedback Agent Tests
- **Initialization**: Agent setup with LLM provider
- **Analysis tests**:
  - Basic analysis
  - Analysis with context
  - Grammar analysis
  - Vocabulary analysis (including empty text)
  - Fluency analysis
- **CEFR level determination**: Tests for all levels (C2, C1, B2, B1, A2, A1)

#### 2. Debate Facilitator Agent Tests
- **Initialization**: Agent setup
- **Facilitate turn tests**:
  - Basic turn facilitation
  - Without speaker name
  - With default topic
- **Topic direction tests**:
  - Empty statements
  - With statements
- **Moderation tests**: Discussion moderation
- **Prompt generation tests**:
  - Basic prompt generation
  - With custom parameters

#### 3. AWS Strands Orchestrator Tests
- **Initialization**: Orchestrator setup with both agents
- **Feedback tests**:
  - Instant English feedback
  - Comprehensive English feedback
  - Empty statements handling
  - Multiple statements combination
  - Facilitation inclusion
- **Formatting tests**:
  - Feedback message formatting
  - Message formatting without suggestions
  - Gentle mention formatting
- **Integration tests**:
  - Orchestrator uses both agents
  - Full workflow

#### 4. Agents Integration Tests
- English agent with real LLM implementation
- Facilitator agent with real LLM implementation
- Orchestrator full workflow
- Error handling

**Total Agent Tests:** 36 tests

### Test Execution

Run all tests:
```bash
cd server_py
python -m pytest tests/ -v
```

Run specific test files:
```bash
# LLM tests only
python -m pytest tests/test_llm.py -v

# Agents tests only
python -m pytest tests/test_agents.py -v

# Both LLM and agents tests
python -m pytest tests/test_llm.py tests/test_agents.py -v
```

Run with coverage:
```bash
python -m pytest tests/test_llm.py tests/test_agents.py --cov=src.llm --cov=src.agents
```

## Independent Execution

Both the `llm` and `agents` modules can now be run independently for testing and demonstration purposes.

### LLM Module (`python -m src.llm`)

#### Available Modes

1. **Default Mode** (runs all demonstrations):
```bash
python -m src.llm
```

2. **Manager Mode** (demonstrate AI Service Manager):
```bash
python -m src.llm manager
```

3. **Gemini Mode** (demonstrate Gemini LLM):
```bash
python -m src.llm gemini
```

4. **Bedrock Mode** (demonstrate Bedrock LLM):
```bash
python -m src.llm bedrock
```

5. **Interactive Mode** (interactive testing):
```bash
python -m src.llm interactive
```

#### Interactive Mode Commands

In interactive mode, you can use the following commands:
- `gemini` - Switch to Gemini provider
- `bedrock` - Switch to Bedrock provider
- `analyze <text>` - Analyze English text
- Type any message to chat with the current LLM
- `quit` or `exit` - Exit interactive mode

**Example:**
```
You: analyze I am going to the store yesterday
📊 Analysis Results:
   CEFR Level: B1
   Grammar: 0.80
   Vocabulary: 0.75
   Fluency: 0.85
   Suggestions:
     • Consider using more varied vocabulary
     • Watch out for subject-verb agreement

You: What is machine learning?
Assistant: This is a placeholder response from Gemini LLM.
```

### Agents Module (`python -m src.agents`)

#### Available Modes

1. **Default Mode** (runs all demonstrations):
```bash
python -m src.agents
```

2. **English Agent Mode**:
```bash
python -m src.agents english
```

3. **Facilitator Agent Mode**:
```bash
python -m src.agents facilitator
```

4. **Orchestrator Mode**:
```bash
python -m src.agents orchestrator
```

5. **Interactive Mode**:
```bash
python -m src.agents interactive
```

#### Interactive Mode Commands

In interactive mode, you can use:
- `analyze <text>` - Get English analysis
- `feedback <text>` - Get instant feedback
- `comprehensive <text>` - Get comprehensive feedback
- `facilitate <topic>` - Get facilitation prompt
- `quit` or `exit` - Exit interactive mode

**Example:**
```
Command: analyze The quick brown fox jumps over the lazy dog
📊 Analysis:
   CEFR Level: B2
   Grammar: 0.8
   Vocabulary: 0.75
   Fluency: 0.85

Command: facilitate Climate Change
🎤 Speaking Prompt:
   This is a placeholder response from Gemini LLM.
```

## Environment Variables

The modules respect the following environment variables:

### LLM Module
- `GOOGLE_API_KEY` - API key for Gemini LLM
- `BEDROCK_MODEL_ID` - Model ID for AWS Bedrock (default: `anthropic.claude-v2`)
- `AWS_REGION` - AWS region for Bedrock (default: `us-east-1`)

### Usage
```bash
export GOOGLE_API_KEY="your-api-key"
export BEDROCK_MODEL_ID="anthropic.claude-v2"
export AWS_REGION="us-east-1"

python -m src.llm manager
```

## Architecture

### LLM Module Structure
```
server_py/src/llm/
├── __init__.py              # Module exports
├── __main__.py              # Independent execution entry point
├── llm_interface.py         # Abstract LLM interface
├── gemini_llm.py            # Gemini LLM implementation
├── bedrock_llm.py           # Bedrock LLM implementation
└── ai_service_manager.py    # Factory for managing LLM providers
```

### Agents Module Structure
```
server_py/src/agents/
├── __init__.py                    # Module exports
├── __main__.py                    # Independent execution entry point
├── english_feedback_agent.py     # English proficiency analysis
├── debate_facilitator_agent.py   # Discussion facilitation
└── aws_strands_orchestrator.py   # Multi-agent orchestration
```

## Test Design Patterns

### 1. Mock Usage
Tests use mocks for LLM providers to ensure:
- Fast test execution
- No dependency on external APIs
- Predictable test outcomes
- No API costs during testing

### 2. Fixtures
Pytest fixtures provide:
- `mock_llm` - Mock LLM provider for testing
- `ai_service_manager` - Real AI service manager instance

### 3. Test Organization
Tests are organized into classes by component:
- `TestLLMInterface` - Interface tests
- `TestGeminiLLM` - Gemini-specific tests
- `TestBedrockLLM` - Bedrock-specific tests
- `TestAIServiceManager` - Manager tests
- `TestLLMIntegration` - Integration tests

### 4. Async Testing
All async methods are tested using `@pytest.mark.asyncio` decorator

## Integration with CI/CD

The tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run LLM and Agents Tests
  run: |
    cd server_py
    python -m pytest tests/test_llm.py tests/test_agents.py -v --tb=short
```

## Regression Testing

Both test suites ensure:
1. **No breaking changes** to existing interfaces
2. **Backward compatibility** with existing code
3. **Provider switching** works correctly
4. **Error handling** is robust

## Future Enhancements

Potential areas for expansion:

1. **Performance Tests**: Add timing benchmarks for LLM operations
2. **Load Tests**: Test behavior under concurrent requests
3. **Real API Tests**: Optional tests against actual LLM APIs (marked as integration tests)
4. **More Providers**: Add tests for additional LLM providers
5. **Enhanced Mocking**: More sophisticated mock responses based on input

## Contributing

When adding new features:
1. Add corresponding tests to `test_llm.py` or `test_agents.py`
2. Update the `__main__.py` demonstration if the feature is user-facing
3. Ensure all existing tests continue to pass
4. Update this documentation

## Related Documentation

- [API Reference](../API%20Reference/) - API documentation
- [Product Updates](../product_docs_and_updates.md) - Product changelog
- [pytest documentation](https://docs.pytest.org/) - Testing framework
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/) - FastAPI testing guide
