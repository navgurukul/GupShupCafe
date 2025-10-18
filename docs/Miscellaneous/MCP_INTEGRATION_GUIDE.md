# MCP Tools Integration for GupShup Café

**Date:** October 18, 2025  
**Status:** ✅ Complete  
**Author:** AI Assistant

## Overview

This document describes the integration of Model Context Protocol (MCP) tools with the GupShup Café agent system. The integration follows patterns from both `strands-agents/sdk-python` and `aws/bedrock-agentcore-sdk-python` to provide a production-ready, scalable architecture.

---

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      GupShup Café Backend                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────┐      │
│  │            AgentCore / Orchestrator              │      │
│  │  ┌────────────────────────────────────────┐     │      │
│  │  │      EnglishFeedbackAgent              │     │      │
│  │  │  - CEFR assessment                     │     │      │
│  │  │  - Grammar analysis via MCP            │     │      │
│  │  │  - Vocabulary analysis via MCP         │     │      │
│  │  └────────────────────────────────────────┘     │      │
│  │  ┌────────────────────────────────────────┐     │      │
│  │  │    DebateFacilitatorAgent              │     │      │
│  │  │  - Topic selection via MCP             │     │      │
│  │  │  - Turn management via MCP             │     │      │
│  │  │  - Discussion pulse analysis           │     │      │
│  │  └────────────────────────────────────────┘     │      │
│  └──────────────────────────────────────────────────┘      │
│                         ↓↑                                  │
│  ┌──────────────────────────────────────────────────┐      │
│  │          MCPToolsManager                         │      │
│  │  - Client connection management                  │      │
│  │  - Tool registration & lifecycle                 │      │
│  │  - Context manager pattern                       │      │
│  └──────────────────────────────────────────────────┘      │
│                         ↓↑                                  │
├─────────────────────────────────────────────────────────────┤
│              Streamable HTTP Transport                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐              ┌──────────────┐            │
│  │ Debate Tools │              │ Grammar Tools│            │
│  │ MCP Server   │              │ MCP Server   │            │
│  │ Port: 8000   │              │ Port: 8001   │            │
│  └──────────────┘              └──────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Components

### 1. MCPToolsManager (`server_py/src/agents/mcp_tools_manager.py`)

Manages MCP client connections following Strands SDK patterns.

**Features:**
- Client registration with streamable HTTP transport
- Context manager pattern for safe resource management
- Tool listing and direct tool invocation
- Singleton pattern for application-wide access

**Usage:**
```python
from server_py.src.agents.mcp_tools_manager import get_mcp_tools_manager, initialize_mcp_clients

# Initialize clients
initialize_mcp_clients({
    'debate_tools': 'http://localhost:8000/mcp/',
    'grammar_tools': 'http://localhost:8001/mcp/'
})

# Get manager instance
manager = get_mcp_tools_manager()

# Use client within context
with manager.use_client('grammar_tools') as client:
    tools = manager.get_tools('grammar_tools')
    # tools are now available for agents
```

### 2. MCP Servers

#### Debate Room Tools Server (`server_py/src/mcp/debate_room_tools.py`)

**Port:** 8000  
**Endpoint:** `http://localhost:8000/mcp/`

**Available Tools:**
- `topic_selector`: Select random debate/discussion topics
- `get_next_speaker`: Determine next speaker in turn sequence
- `validate_turn`: Validate if speaker is speaking in correct turn
- `initialize_room`: Initialize debate/discussion room with participants
- `analyze_discussion_pulse`: Track discussion progress and identify convergence/divergence

**Start Server:**
```bash
python -m server_py.src.mcp.debate_room_tools

# Or with custom port
python -m server_py.src.mcp.debate_room_tools --port 8000 --host localhost
```

#### Grammar Tools Server (`server_py/src/mcp/grammar_tools.py`)

**Port:** 8001  
**Endpoint:** `http://localhost:8001/mcp/`

**Available Tools:**

**Start Server:**
```bash
python -m server_py.src.mcp.grammar_tools

# Or with custom port
python -m server_py.src.mcp.grammar_tools --port 8001 --host localhost
```

### 3. Enhanced Agents

#### EnglishFeedbackAgent

**Enhanced with MCP Tools:**
- Grammar checking via `check_grammar`
- Vocabulary analysis via `analyze_vocabulary`
- Filler detection via `detect_fillers`
- Sentence structure analysis via `analyze_sentence_structure`

**Integration Pattern:**
```python
from strands.models.gemini import GeminiModel

# Initialize model
model = GeminiModel(...)

# Create agent without MCP tools
agent = EnglishFeedbackAgent(model)

# Add MCP tools dynamically
with mcp_manager.use_client('grammar_tools') as client:
    tools = mcp_manager.get_tools('grammar_tools')
    agent.add_mcp_tools(tools)

# Agent will automatically use MCP tools when analyzing
result = await agent.analyze({
    'text': "This is a sample text to analyze.",
    'context': {...}
})
```

#### DebateFacilitatorAgent

**Enhanced with MCP Tools:**
- Topic selection via `topic_selector`
- Turn management via `get_next_speaker`, `validate_turn`
- Room initialization via `initialize_room`
- Discussion analysis via `analyze_discussion_pulse`

**Integration Pattern:**
```python
# Create agent without MCP tools
facilitator = DebateFacilitatorAgent(model)

# Add MCP tools dynamically
with mcp_manager.use_client('debate_tools') as client:
    tools = mcp_manager.get_tools('debate_tools')
    facilitator.add_mcp_tools(tools)

# Agent will use MCP tools when facilitating
response = await facilitator.facilitate_turn(context)
```

### 4. AgentCore Production Integration

Following Bedrock AgentCore patterns for production deployment:

```python
from server_py.src.agents.agentcore import AgentCore

# Initialize with MCP tools enabled
agent_core = AgentCore(
    model_provider='gemini',
    max_tokens=500,
    enable_mcp_tools=True
)

# Activate MCP tools before use
agent_core.activate_mcp_tools()

# Use agents
result = await agent_core.analyze_and_facilitate(
    statements=["Great discussion point!"],
    context={'topic': 'AI in Education'},
    instant=False
)
```

---

## MCP Server Launcher Utility

**Location:** `server_py/src/mcp/launcher.py`

**Purpose:** Manage MCP server lifecycle for development and testing.

### Usage

```bash
# Start all servers in background
python server_py/src/mcp/launcher.py start --all

# Start specific server
python server_py/src/mcp/launcher.py start --server debate_tools

# Start server in foreground (for debugging)
python server_py/src/mcp/launcher.py start --server grammar_tools --foreground

# Check server status
python server_py/src/mcp/launcher.py status

# Stop specific server
python server_py/src/mcp/launcher.py stop --server debate_tools

# Stop all servers
python server_py/src/mcp/launcher.py stop --all

# Restart servers
python server_py/src/mcp/launcher.py restart --all
```

### Output Example

```
🚀 Starting all MCP servers...
✅ Debate Room Tools started in background (PID: 12345)
   MCP endpoint: http://localhost:8000/mcp/
✅ Grammar Tools started in background (PID: 12346)
   MCP endpoint: http://localhost:8001/mcp/
✅ Started 2/2 MCP servers

📊 MCP Server Status:
------------------------------------------------------------
✅ Debate Room Tools        | Port: 8000 | Running
✅ Grammar Tools             | Port: 8001 | Running
------------------------------------------------------------
```

---

## Integration Benefits

### 1. **Modularity**
- MCP tools are isolated in separate servers
- Agents can work with or without MCP tools
- Easy to add new tools without modifying agents

### 2. **Scalability**
- MCP servers can run on separate machines/containers
- Tools can be scaled independently of agents
- Follows microservices architecture

### 3. **Flexibility**
- Strands Agent framework automatically uses tools when relevant
- LLM decides when to invoke MCP tools based on context
- No hardcoded tool invocation logic

### 4. **Production-Ready**
- Based on Bedrock AgentCore patterns
- Proper resource management via context managers
- Comprehensive error handling and logging

### 5. **Developer Experience**
- Simple server launcher for local development
- Clear separation of concerns
- Easy to test and debug

---

## Development Workflow

### 1. Start MCP Servers

```bash
# Terminal 1: Start MCP servers
python server_py/src/mcp/launcher.py start --all

# Verify servers are running
python server_py/src/mcp/launcher.py status
```

### 2. Run Backend with MCP Integration

```python
# server_py/main.py or similar
from server_py.src.agents.agentcore import AgentCore

# Initialize with MCP enabled
core = AgentCore(enable_mcp_tools=True)
core.activate_mcp_tools()

# Agents are now ready with MCP tools
```

### 3. Test Integration

```python
# Test English analysis with grammar tools
result = await core.english_agent.analyze({
    'text': 'I am go to school yesterday.',
    'context': {}
})

# Agent will use check_grammar tool automatically
print(result)
```

---

## Troubleshooting

### MCP Servers Not Starting

**Issue:** Servers fail to start  
**Solution:**
1. Check if ports 8000, 8001 are available
2. Verify Python MCP library is installed: `pip install mcp`
3. Check logs for specific errors

### Agents Not Using MCP Tools

**Issue:** Agents don't invoke MCP tools  
**Solution:**
1. Verify `activate_mcp_tools()` was called
2. Check if MCP servers are running
3. Review agent prompts - make sure task benefits from tools
4. Check logs for MCP client errors

### Connection Timeouts

**Issue:** MCPClient connection timeouts  
**Solution:**
1. Increase `startup_timeout` in `MCPToolsManager.register_client()`
2. Verify network connectivity to MCP server endpoints
3. Check server logs for startup errors

---

## Future Enhancements

1. **Additional MCP Servers:**
   - Pronunciation analysis tools
   - Content moderation tools
   - Real-time translation tools

2. **Enhanced Tool Capabilities:**
   - Integration with LanguageTool API for advanced grammar
   - CEFR vocabulary database integration
   - Speech-to-text analysis tools

3. **Observability:**
   - OpenTelemetry instrumentation for MCP calls
   - Metrics for tool usage and performance
   - Distributed tracing across agents and tools

4. **Deployment:**
   - Containerization of MCP servers
   - Kubernetes deployment manifests
   - Load balancing for high availability

---

## References

- [Strands Agents SDK](https://github.com/strands-agents/sdk-python)
- [AWS Bedrock AgentCore SDK](https://github.com/aws/bedrock-agentcore-sdk-python)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/modelcontextprotocol/python-sdk)

---

## Testing

### Unit Tests

Add tests for MCP integration in `server_py/tests/test_mcp_integration.py`:

```python
import pytest
from server_py.src.agents.mcp_tools_manager import MCPToolsManager

@pytest.fixture
def mcp_manager():
    manager = MCPToolsManager()
    manager.register_client('test_tools', 'http://localhost:8000/mcp/')
    return manager

def test_register_client(mcp_manager):
    assert 'test_tools' in mcp_manager.clients

def test_use_client_context(mcp_manager):
    with mcp_manager.use_client('test_tools') as client:
        assert 'test_tools' in mcp_manager.active_clients
    
    assert 'test_tools' not in mcp_manager.active_clients
```

### Integration Tests

Test end-to-end MCP integration with live servers (see `server_py/tests/test_agents.py` for examples).

---

## Conclusion

The MCP tools integration provides a modular, scalable architecture for enhancing GupShup Café agents with specialized capabilities. By following patterns from both Strands SDK and Bedrock AgentCore, we've created a production-ready system that maintains flexibility for future growth.
