# MCP Tools Integration - Quick Start

This guide helps you get started with the MCP (Model Context Protocol) tools integration in GupShup Café.

## What is MCP?

MCP (Model Context Protocol) is a protocol that allows AI agents to interact with external tools and services. In GupShup Café, we use MCP to provide specialized capabilities to our agents:

- **Grammar Tools**: Grammar checking, vocabulary analysis, filler detection
- **Debate Tools**: Topic selection, turn management, discussion facilitation

## Quick Start

### 1. Start MCP Servers

```bash
# Start all MCP servers in background
python server_py/src/mcp/launcher.py start --all

# Verify servers are running
python server_py/src/mcp/launcher.py status
```

Expected output:
```
🚀 Starting all MCP servers...
✅ Debate Room Tools started in background (PID: 12345)
   MCP endpoint: http://localhost:8000/mcp/
✅ Grammar Tools started in background (PID: 12346)
   MCP endpoint: http://localhost:8001/mcp/
✅ Started 2/2 MCP servers
```

### 2. Use Agents with MCP Tools

```python
from server_py.src.agents.agentcore import AgentCore

# Initialize AgentCore with MCP tools enabled
core = AgentCore(
    model_provider='gemini',  # or 'bedrock'
    enable_mcp_tools=True
)

# Activate MCP tools
core.activate_mcp_tools()

# Now agents can use MCP tools automatically!
result = await core.analyze_and_facilitate(
    statements=["This sentence have grammar error."],
    context={'topic': 'English Learning'},
    instant=False
)

# The EnglishFeedbackAgent will automatically use 
# check_grammar and analyze_vocabulary tools
print(result['feedback_message'])
```

### 3. Stop MCP Servers

```bash
# Stop all servers
python server_py/src/mcp/launcher.py stop --all
```

## Architecture Overview

```
┌───────────────────────────────────────┐
│         GupShup Café Backend          │
│                                        │
│  ┌──────────────────────────────┐    │
│  │   EnglishFeedbackAgent       │    │
│  │   + Grammar MCP Tools        │    │
│  └──────────────────────────────┘    │
│                ↕                      │
│  ┌──────────────────────────────┐    │
│  │   DebateFacilitatorAgent     │    │
│  │   + Debate MCP Tools         │    │
│  └──────────────────────────────┘    │
│                ↕                      │
│  ┌──────────────────────────────┐    │
│  │     MCPToolsManager          │    │
│  └──────────────────────────────┘    │
└───────────────────────────────────────┘
                ↕
┌───────────────────────────────────────┐
│         MCP Servers                   │
│                                        │
│  ┌────────────────┐  ┌─────────────┐ │
│  │ Debate Tools   │  │ Grammar     │ │
│  │ :8000/mcp/     │  │ Tools       │ │
│  └────────────────┘  │ :8001/mcp/  │ │
│                       └─────────────┘ │
└───────────────────────────────────────┘
```

## MCP Tools Available

### Debate Tools (Port 8000)

| Tool | Description |
|------|-------------|
| `topic_selector` | Select random debate/discussion topics |
| `get_next_speaker` | Determine next speaker in turn sequence |
| `validate_turn` | Validate if speaker is speaking in correct turn |
| `initialize_room` | Initialize debate/discussion room |
| `analyze_discussion_pulse` | Track discussion progress |

### Grammar Tools (Port 8001)

| Tool | Description |
|------|-------------|
| `check_grammar` | Detect grammar issues in text |
| `analyze_vocabulary` | Analyze vocabulary complexity (CEFR-aligned) |
| `detect_fillers` | Count filler words (um, uh, like, etc.) |
| `analyze_sentence_structure` | Analyze sentence complexity |

## Advanced Usage

### Custom MCP Configuration

```python
from server_py.src.agents.agentcore import AgentCore

# Custom MCP server endpoints
core = AgentCore(
    enable_mcp_tools=True,
    mcp_config={
        'debate_tools': 'http://mcp-server:8000/mcp/',
        'grammar_tools': 'http://mcp-server:8001/mcp/',
        'custom_tools': 'http://custom-server:9000/mcp/'
    }
)
```

### Using Individual MCP Clients

```python
from server_py.src.agents.mcp_tools_manager import get_mcp_tools_manager

manager = get_mcp_tools_manager()

# Use specific tool directly
with manager.use_client('grammar_tools') as client:
    result = manager.call_tool(
        'grammar_tools',
        'check_grammar',
        {'text': 'Sample text to check'}
    )
    print(result)
```

### Running MCP Servers in Foreground (for debugging)

```bash
# Run server in foreground to see logs
python server_py/src/mcp/launcher.py start --server grammar_tools --foreground
```

## Troubleshooting

### Ports Already in Use

If ports 8000 or 8001 are in use:

```bash
# Stop existing servers
python server_py/src/mcp/launcher.py stop --all

# Or start servers on different ports
python -m server_py.src.mcp.debate_room_tools --port 8100
python -m server_py.src.mcp.grammar_tools --port 8101
```

Then update configuration:

```python
core = AgentCore(
    enable_mcp_tools=True,
    mcp_config={
        'debate_tools': 'http://localhost:8100/mcp/',
        'grammar_tools': 'http://localhost:8101/mcp/'
    }
)
```

### MCP Tools Not Working

1. **Check if servers are running:**
   ```bash
   python server_py/src/mcp/launcher.py status
   ```

2. **Check server logs:**
   ```bash
   # Run server in foreground to see logs
   python -m server_py.src.mcp.grammar_tools
   ```

3. **Verify agent activation:**
   ```python
   core = AgentCore(enable_mcp_tools=True)
   core.activate_mcp_tools()  # Don't forget this step!
   ```

## Environment Variables

```bash
# LLM provider selection
export LLM_PROVIDER=gemini  # or 'bedrock'

# API keys (if needed)
export GOOGLE_API_KEY=your_key
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

## Next Steps

- 📖 Read [MCP Integration Guide](./docs/Miscellaneous/MCP_INTEGRATION_GUIDE.md) for detailed documentation
- 🏗️ See [Backend Architecture](./docs/diagrams/plan/uml/03-class-diagram-backend.puml) for system design
- 🔧 Check [Product Updates](./docs/product_docs_and_updates.md) for latest changes

## Testing

Run tests to verify MCP integration:

```bash
# Run agent tests
python -m pytest server_py/tests/test_agents.py -v

# Run MCP-specific tests
python -m pytest server_py/tests/test_mcp_integration.py -v
```

## Production Deployment

For production deployment, consider:

1. **Run MCP servers as separate services**
2. **Use container orchestration (Docker/Kubernetes)**
3. **Implement health checks and monitoring**
4. **Scale MCP servers independently**
5. **Use production-grade HTTP servers**

See [Deployment Guide](./docs/Miscellaneous/DEPLOYMENT_GUIDE.md) for details.

---

**Questions or Issues?** Check the [troubleshooting section](#troubleshooting) or create an issue on GitHub.
