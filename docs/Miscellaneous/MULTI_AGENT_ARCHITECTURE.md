# Multi-Agent Architecture with AWS AgentCore Integration

## Overview

The GupShup Cafe platform now supports a **multi-agent architecture** with dedicated agents for different aspects of roundtable discussions. This architecture separates concerns and provides more specialized, focused feedback to participants.

## Architecture

### Agent Types

1. **English Grammar Agent** (`englishGrammarAgent.py`)
   - **Purpose**: Provides instant, specialized feedback on English language usage
   - **Responsibilities**:
     - Grammar correction (tenses, subject-verb agreement, articles, prepositions)
     - Sentence structure and framing analysis
     - Vocabulary suggestions
     - Clarity and coherence assessment
   - **Model**: Gemini 2.5 Flash (optimized for language instruction)
   - **Temperature**: 0.3 (lower for consistent corrections)

2. **Debate Facilitator Agent** (part of `debate_room_facilitator.py`)
   - **Purpose**: Manages discussion flow and provides content feedback
   - **Responsibilities**:
     - Topic selection and management
     - Turn-taking coordination
     - Fact-checking claims
     - Identifying common ground and divergence
     - Guiding discussion toward productive outcomes
   - **Model**: Gemini 2.5 Flash
   - **Temperature**: 0.7 (balanced creativity and consistency)

3. **Multi-Agent Orchestrator** (`multiAgentOrchestrator.py`)
   - **Purpose**: Coordinates multiple agents and routes requests
   - **Responsibilities**:
     - Agent lifecycle management
     - Request routing to appropriate agents
     - Response combination and formatting
     - AWS AgentCore integration (when enabled)

### Why Multi-Agent?

**Benefits of Multi-Agent Architecture:**

1. **Separation of Concerns**: Each agent focuses on its specialty
   - English agent doesn't need to know about discussion flow
   - Facilitator agent doesn't need to analyze grammar

2. **Better Feedback Quality**: Specialized agents provide deeper insights
   - Grammar agent can focus 100% on language patterns
   - Facilitator can concentrate on content and flow

3. **Instant English Feedback**: Dedicated agent enables real-time language correction
   - No mixed responsibilities
   - Faster, more accurate grammar analysis

4. **Scalability**: Easy to add new specialized agents
   - Pronunciation coach
   - Cultural context advisor
   - Technical vocabulary expert

5. **Independent Improvement**: Each agent can be optimized separately
   - Different prompts, models, or parameters
   - A/B testing individual agents

## AWS Bedrock AgentCore Integration

### What is AWS Bedrock AgentCore?

AWS Bedrock AgentCore is a managed service for deploying and orchestrating AI agents in production environments. It provides:

- **Scalable Infrastructure**: Auto-scaling for agent workloads
- **Managed Runtime**: No server management required
- **Security**: Built-in AWS security and compliance
- **Monitoring**: CloudWatch integration for observability
- **Cost Optimization**: Pay only for what you use

### Integration Approach

Our multi-agent orchestrator supports **two modes**:

#### 1. Local Development Mode (Default)
```python
orchestrator = MultiAgentOrchestrator(use_aws_agentcore=False)
```
- Agents run locally on your development machine
- No AWS credentials required
- Suitable for development and testing

#### 2. AWS Production Mode
```python
orchestrator = MultiAgentOrchestrator(use_aws_agentcore=True)
```
- Agents deployed to AWS Bedrock AgentCore
- Requires AWS credentials and permissions
- Suitable for production deployment
- Provides scalability, reliability, and monitoring

### AWS Configuration

#### Prerequisites

1. **AWS Account**: Active AWS account with Bedrock access
2. **IAM Permissions**: Required permissions:
   - `bedrock:InvokeAgent`
   - `bedrock:GetAgent`
   - `bedrock:ListAgents`
   - CloudWatch Logs permissions

3. **AWS CLI Configured**:
   ```bash
   aws configure
   # Enter your AWS Access Key ID
   # Enter your AWS Secret Access Key
   # Enter default region (e.g., us-east-1)
   ```

4. **Environment Variables**:
   ```bash
   export AWS_REGION=us-east-1
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   ```

#### Setup Steps

1. **Install Dependencies**:
   ```bash
   cd server_py
   pip install -r requirements.txt
   ```

2. **Configure Environment** (`.env`):
   ```env
   # AWS Configuration
   AWS_REGION=us-east-1
   
   # Gemini API for agents
   GEMINI_API_KEY=your_gemini_api_key
   
   # Enable Multi-Agent Mode
   USE_MULTI_AGENT=true
   USE_AWS_AGENTCORE=true  # Set to false for local mode
   ```

3. **Deploy Agents to AWS**:
   ```python
   from multiAgentOrchestrator import get_orchestrator
   
   orchestrator = get_orchestrator()
   success = orchestrator.deploy_to_aws()
   ```

### AWS Deployment Architecture

```
┌─────────────────────────────────────────────────────┐
│              GupShup Cafe Application               │
│                 (FastAPI Server)                    │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│          Multi-Agent Orchestrator                   │
│         (Request Router & Coordinator)              │
└──────────┬──────────────────────┬───────────────────┘
           │                      │
           ▼                      ▼
┌──────────────────┐    ┌──────────────────┐
│  AWS Bedrock     │    │  AWS Bedrock     │
│  AgentCore       │    │  AgentCore       │
│                  │    │                  │
│  English         │    │  Debate          │
│  Grammar Agent   │    │  Facilitator     │
└──────────────────┘    └──────────────────┘
           │                      │
           ▼                      ▼
    Gemini Model API      Gemini Model API
```

## Usage

### Using Multi-Agent System in Debate Facilitator

```python
from debate_room_facilitator import DebateRoomFacilitator

# Initialize with multi-agent mode
facilitator = DebateRoomFacilitator(
    room_type="discussion",
    num_rounds=3,
    use_multi_agent=True  # Enable multi-agent architecture
)

# Setup and run as normal - agents work transparently
facilitator.setup_room(["Alice", "Bob", "Charlie"])
facilitator.initialize_agent()

# Get feedback - automatically uses both agents
feedback = facilitator.get_agent_feedback()
# Returns combined discussion + English feedback

# Get final summary - comprehensive English analysis
summary = facilitator.get_final_english_summary()
```

### Direct Orchestrator Usage

```python
from multiAgentOrchestrator import get_orchestrator

# Get global orchestrator instance
orchestrator = get_orchestrator()

# Initialize facilitator agent
orchestrator.initialize_debate_facilitator(
    room_type="discussion",
    topic="AI in Education",
    participants=["Alice", "Bob"]
)

# Get instant English feedback
statements = [
    {"speaker": "Alice", "content": "AI are very helpful."},
    {"speaker": "Bob", "content": "I thinks so too."}
]
english_feedback = orchestrator.get_english_feedback(statements, instant=True)

# Get discussion feedback
discussion_feedback = orchestrator.get_discussion_feedback(
    topic="AI in Education",
    recent_statements=statements
)

# Get combined feedback
combined = orchestrator.get_combined_feedback(
    topic="AI in Education",
    recent_statements=statements
)
```

## Backward Compatibility

The multi-agent system is **fully backward compatible**:

```python
# Legacy mode - single agent
facilitator = DebateRoomFacilitator(
    room_type="discussion",
    num_rounds=3,
    use_multi_agent=False  # Disable multi-agent
)
# Works exactly as before with combined feedback
```

**Graceful Fallback:**
- If multi-agent initialization fails, automatically falls back to single-agent mode
- If AWS AgentCore is unavailable, uses local agent execution
- No breaking changes to existing code

## Testing

### Unit Tests

```bash
cd server_py/src/llmTutor
python test_multi_agent.py
```

Tests cover:
- Agent initialization
- Orchestrator setup
- Method signatures
- AWS integration (mocked)
- Backward compatibility

### Integration Tests

```bash
cd server_py/src/llmTutor
python debate_room_facilitator.py
```

Test with multi-agent mode:
1. Provides combined feedback
2. Separates discussion and English concerns
3. Generates comprehensive summaries

## Performance Considerations

### Local Mode
- **Latency**: 2-5 seconds per agent response
- **Cost**: Only API calls to Gemini
- **Scalability**: Limited by local resources

### AWS Mode
- **Latency**: 1-3 seconds (AWS infrastructure)
- **Cost**: AWS Bedrock pricing + Gemini API
- **Scalability**: Auto-scales with demand
- **Reliability**: AWS SLA guarantees

### Optimization Tips

1. **Batch Feedback**: Collect statements before requesting feedback
2. **Instant vs Comprehensive**: Use instant mode during discussion, comprehensive at end
3. **Cache Responses**: Consider caching for repeated patterns
4. **Parallel Execution**: Agents can run in parallel (orchestrator handles this)

## Monitoring and Observability

### Local Mode
- Check console logs for agent activity
- Monitor response times manually

### AWS Mode
- **CloudWatch Logs**: Agent execution logs
- **CloudWatch Metrics**: Custom metrics for agent performance
- **X-Ray**: Distributed tracing for request flow

## Cost Estimation

### Development (Local Mode)
- **Gemini API**: ~$0.10 per 1000 requests
- **No AWS costs**

### Production (AWS Mode)
- **Gemini API**: ~$0.10 per 1000 requests  
- **AWS Bedrock AgentCore**: ~$0.008 per agent invocation
- **Data Transfer**: Minimal (text only)
- **Total**: ~$0.11-0.15 per 1000 feedback cycles

## Troubleshooting

### Agent Initialization Fails

**Problem**: `Failed to initialize Multi-Agent Orchestrator`

**Solutions**:
1. Check `GEMINI_API_KEY` is set in `.env`
2. Verify strands-agents is installed: `pip install strands-agents`
3. Check logs for specific error messages

### AWS AgentCore Connection Issues

**Problem**: `Cannot connect to AWS AgentCore`

**Solutions**:
1. Verify AWS credentials: `aws sts get-caller-identity`
2. Check IAM permissions for Bedrock
3. Confirm region supports Bedrock: `us-east-1`, `us-west-2`
4. Fallback to local mode if AWS not needed

### English Feedback Not Appearing

**Problem**: Only discussion feedback shown

**Solutions**:
1. Ensure `use_multi_agent=True` in facilitator init
2. Check orchestrator initialized successfully
3. Verify English Grammar Agent loaded
4. Check logs for agent routing errors

## Future Enhancements

1. **Additional Specialized Agents**:
   - Pronunciation Coach Agent
   - Cultural Context Agent
   - Domain-Specific Vocabulary Agent

2. **Enhanced AWS Integration**:
   - Agent versioning and rollback
   - A/B testing framework
   - Multi-region deployment

3. **Advanced Features**:
   - Real-time streaming feedback
   - Personalized learning paths
   - Progress tracking over time

## References

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Strands Agents SDK](https://github.com/strands-agents/sdk-python)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [Multi-Agent Systems Best Practices](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-multi.html)

## Support

For issues or questions:
1. Check logs: `server_py/logs/`
2. Review documentation: `docs/`
3. File issue: GitHub repository
4. Contact: Development team
