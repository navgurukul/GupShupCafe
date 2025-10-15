# Multi-Agent System - Quick Start Guide

## Overview

The GupShup Cafe platform now features a **multi-agent architecture** that provides specialized feedback for roundtable discussions:

- **English Grammar Agent**: Instant English language feedback
- **Debate Facilitator Agent**: Discussion flow and content guidance
- **Multi-Agent Orchestrator**: Coordinates agents and combines responses

## Quick Start

### 1. Installation

```bash
cd server_py
pip install -r requirements.txt
```

### 2. Configuration

Create or update `.env` file:

```env
# Required: Gemini API key for agents
GEMINI_API_KEY=your_gemini_api_key

# Enable multi-agent mode
USE_MULTI_AGENT=true

# AWS deployment (optional - set to false for local)
USE_AWS_AGENTCORE=false
```

### 3. Test Installation

```bash
python test_multi_agent_integration.py
```

You should see:
```
✅ All required dependencies installed
✅ Multi-agent structure verified
✅ Configuration check complete
✅ Integration test complete!
```

## Usage

### Option 1: In Debate Facilitator (CLI)

```python
from src.llmTutor.debate_room_facilitator import DebateRoomFacilitator

# Enable multi-agent mode
facilitator = DebateRoomFacilitator(
    room_type="discussion",
    num_rounds=3,
    use_multi_agent=True
)

# Use as normal - agents work transparently
facilitator.setup_room(["Alice", "Bob", "Charlie"])
facilitator.initialize_agent()

# Feedback automatically includes both:
# - Discussion guidance
# - English language corrections
feedback = facilitator.get_agent_feedback()
```

### Option 2: Direct Orchestrator Usage

```python
from src.llmTutor.multiAgentOrchestrator import get_orchestrator

orchestrator = get_orchestrator()

# Initialize facilitator
orchestrator.initialize_debate_facilitator(
    room_type="discussion",
    topic="AI in Education",
    participants=["Alice", "Bob"]
)

# Get instant English feedback
statements = [
    {"speaker": "Alice", "content": "I goes to school yesterday."}
]
english_feedback = orchestrator.get_english_feedback(
    statements, 
    instant=True
)
print(english_feedback)
```

### Option 3: Backward Compatible Mode

```python
# Use original single-agent mode
facilitator = DebateRoomFacilitator(
    room_type="discussion",
    use_multi_agent=False
)
# Works exactly as before
```

## Architecture

```
┌─────────────────────────────┐
│   Debate Room Facilitator   │
│   (Main Entry Point)        │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Multi-Agent Orchestrator   │
│  (Request Router)           │
└──────┬──────────────────┬───┘
       │                  │
       ▼                  ▼
┌────────────┐    ┌──────────────┐
│  English   │    │   Debate     │
│  Grammar   │    │ Facilitator  │
│  Agent     │    │   Agent      │
└────────────┘    └──────────────┘
```

## Key Features

### Separation of Concerns
- **English Agent**: 100% focused on language
  - Grammar corrections
  - Sentence structure
  - Vocabulary suggestions
  - Clear explanations

- **Facilitator Agent**: 100% focused on content
  - Discussion flow
  - Fact-checking
  - Common ground identification
  - Productive guidance

### Instant Feedback
The dedicated English Grammar Agent enables real-time language correction:

```python
# Get instant feedback (analyzes last 3 statements)
feedback = orchestrator.get_english_feedback(statements, instant=True)

# Get comprehensive feedback (analyzes all statements)
summary = orchestrator.get_english_feedback(statements, instant=False)
```

### AWS Deployment Ready

Deploy to AWS Bedrock AgentCore for production:

```python
orchestrator = MultiAgentOrchestrator(use_aws_agentcore=True)
orchestrator.deploy_to_aws()
```

## Testing

### Run Integration Test

```bash
python test_multi_agent_integration.py
```

Checks:
- ✓ Dependencies installed
- ✓ File structure correct
- ✓ AWS configuration (optional)
- ✓ Usage examples

### Run Unit Tests

```bash
python src/llmTutor/test_multi_agent.py
```

Tests:
- Agent initialization
- Orchestrator setup
- Method signatures
- Backward compatibility

## Deployment Modes

### Local Development (Default)
```env
USE_AWS_AGENTCORE=false
```
- Agents run on your machine
- No AWS costs
- Suitable for development

### AWS Production
```env
USE_AWS_AGENTCORE=true
AWS_REGION=us-east-1
```
- Agents deployed to AWS
- Auto-scaling infrastructure
- Production reliability

See [AWS_AGENTCORE_DEPLOYMENT.md](../../docs/Miscellaneous/AWS_AGENTCORE_DEPLOYMENT.md) for full AWS setup.

## Configuration Reference

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | Yes | - | Gemini API key for agents |
| `USE_MULTI_AGENT` | No | `true` | Enable multi-agent mode |
| `USE_AWS_AGENTCORE` | No | `false` | Deploy to AWS |
| `AWS_REGION` | No* | `us-east-1` | AWS region (*required for AWS) |
| `AWS_ACCESS_KEY_ID` | No* | - | AWS credentials (*required for AWS) |
| `AWS_SECRET_ACCESS_KEY` | No* | - | AWS credentials (*required for AWS) |

### Agent Configuration

**English Grammar Agent:**
- Model: Gemini 2.5 Flash
- Temperature: 0.3 (consistent corrections)
- Focus: Language accuracy

**Debate Facilitator Agent:**
- Model: Gemini 2.5 Flash
- Temperature: 0.7 (balanced)
- Focus: Content and flow

## Troubleshooting

### Issue: "No module named 'strands'"

**Solution**: Install strands-agents
```bash
pip install strands-agents
```

### Issue: "GEMINI_API_KEY not set"

**Solution**: Add to `.env`
```env
GEMINI_API_KEY=your_api_key_here
```

### Issue: Multi-agent initialization fails

**Solution**: System automatically falls back to single-agent mode
```
⚠️ Failed to initialize Multi-Agent Orchestrator
   Falling back to single-agent mode
```

Check logs for specific error.

### Issue: AWS credentials error

**Solution**: Either configure AWS or use local mode
```env
USE_AWS_AGENTCORE=false  # Use local mode
```

## Documentation

- **Architecture Overview**: [MULTI_AGENT_ARCHITECTURE.md](../../docs/Miscellaneous/MULTI_AGENT_ARCHITECTURE.md)
- **AWS Deployment**: [AWS_AGENTCORE_DEPLOYMENT.md](../../docs/Miscellaneous/AWS_AGENTCORE_DEPLOYMENT.md)
- **API Reference**: [LLM_AGENT_INTEGRATION.md](../../docs/LLM_AGENT_INTEGRATION.md)

## Examples

See complete examples in:
- `src/llmTutor/debate_room_facilitator.py` - CLI usage
- `src/llmTutor/multiAgentOrchestrator.py` - Direct orchestrator usage
- `test_multi_agent_integration.py` - Integration examples

## Support

For issues or questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review [Documentation](#documentation)
3. File GitHub issue with logs

## Next Steps

1. ✅ Complete quick start above
2. ✅ Test with `python test_multi_agent_integration.py`
3. ✅ Try CLI: `python src/llmTutor/debate_room_facilitator.py`
4. ✅ Integrate into web app (set `ENABLE_LLM_AGENT=true`)
5. ✅ Deploy to AWS (optional): Follow AWS deployment guide

---

**Status**: ✅ Ready for use

**Compatibility**: Fully backward compatible with single-agent mode

**Production Ready**: Yes (with AWS deployment)
