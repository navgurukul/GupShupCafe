# Strands Integration Quick Reference

## Environment Setup

### Switch LLM Providers

**Gemini (Default):**
```bash
export LLM_PROVIDER=gemini
export GEMINI_API_KEY=your_gemini_key
```

**Amazon Bedrock:**
```bash
export LLM_PROVIDER=bedrock
export AWS_REGION=us-east-1
export BEDROCK_MODEL_ID=us.amazon.nova-pro-v1:0
```

## Code Examples

### Create a Model

```python
from server_py.src.llm.strands_model_adapter import create_model

# Auto-detect from environment
model = create_model()

# Explicit provider
gemini_model = create_model(provider="gemini")
bedrock_model = create_model(provider="bedrock")

# With custom config
model = create_model(
    provider="gemini",
    temperature=0.8,
    max_tokens=3000
)
```

### Use EnglishFeedbackAgent

```python
from server_py.src.agents.english_feedback_agent import EnglishFeedbackAgent
from server_py.src.llm.strands_model_adapter import create_model

# Initialize
model = create_model()
agent = EnglishFeedbackAgent(model)

# Analyze text
result = await agent.analyze({
    "text": "I think climate change is important...",
    "context": {
        "topic": "Climate Change",
        "speaker_info": {"name": "Student A"}
    }
})

# Result includes:
# - cefr_level: "B1", "B2", etc.
# - grammar_score: 0.0 - 1.0
# - vocabulary_score: 0.0 - 1.0
# - fluency_score: 0.0 - 1.0
# - analysis: Detailed text feedback
# - suggestions: List of improvement tips
```

### Use DebateFacilitatorAgent

```python
from server_py.src.agents.debate_facilitator_agent import DebateFacilitatorAgent
from server_py.src.llm.strands_model_adapter import create_model

# Initialize
model = create_model()
facilitator = DebateFacilitatorAgent(model)

# Generate speaking prompt
prompt = await facilitator.facilitate_turn({
    "topic": "Climate Change",
    "current_speaker": {"anonymous_name": "Blue Fox"},
    "turn_number": 2,
    "current_round": 1,
    "total_rounds": 3,
    "previous_statements": ["I believe we need action now"]
})

# Suggest discussion direction
suggestion = await facilitator.suggest_topic_direction([
    "Climate change affects everyone",
    "We need renewable energy"
])

# Summarize discussion
summary = await facilitator.summarize_discussion({
    "topic": "Climate Change",
    "statements": [...],
    "participants": [...]
})
```

### Use AWSStrandsOrchestrator

```python
from server_py.src.agents.aws_strands_orchestrator import AWSStrandsOrchestrator

# Initialize (auto-detects provider from env)
orchestrator = AWSStrandsOrchestrator()

# Or specify provider
orchestrator = AWSStrandsOrchestrator(model_provider="bedrock")

# Get comprehensive feedback
feedback = await orchestrator.get_english_feedback(
    statements=["I think technology helps us a lot"],
    instant=False,  # Set to True for quick feedback
    context={
        "speaker_info": {"name": "Student A"},
        "topic": "Technology in Education"
    }
)
```

## CEFR Assessment

### How It Works
- **No manual logic** - LLM determines CEFR level via prompts
- **Key factor**: Depth and descriptiveness of content
- **Progression**: A1 (basic) → C2 (sophisticated, detailed)

### CEFR Levels
- **A1**: Simple phrases, limited depth
- **A2**: Basic connected text, some detail  
- **B1**: Clear descriptions, moderate depth
- **B2**: Detailed text, good depth with examples
- **C1**: Well-structured, high depth with nuance
- **C2**: Sophisticated, maximum depth and subtlety

## Installation

```bash
cd server_py
pip install -r requirements.txt
```

## Testing

```bash
# Test agents
pytest tests/test_agents.py -v

# Test LLM integration
pytest tests/test_llm.py -v

# Interactive testing
python -m server_py.src.agents
```

## Troubleshooting

### "GEMINI_API_KEY not found"
```bash
export GEMINI_API_KEY=your_key_here
```

### "Bedrock credentials not configured"
```bash
# Configure AWS CLI
aws configure

# Or use environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_REGION=us-east-1
```

### "Module not found: strands"
```bash
pip install strands-agents
```

### Switch provider not working
```bash
# Check current provider
python -c "from server_py.src.llm.strands_model_adapter import StrandsModelAdapter; print(StrandsModelAdapter.get_current_provider())"

# Set explicitly
export LLM_PROVIDER=gemini  # or bedrock
```

## Key Files

- `server_py/src/llm/strands_model_adapter.py` - Model creation
- `server_py/src/agents/english_feedback_agent.py` - English analysis
- `server_py/src/agents/debate_facilitator_agent.py` - Discussion facilitation
- `server_py/src/agents/aws_strands_orchestrator.py` - Multi-agent coordination
- `server_py/src/llm/ai_service_manager.py` - Backward compatibility layer

## Documentation

- Full Summary: `docs/Miscellaneous/STRANDS_INTEGRATION_SUMMARY.md`
- Changelog: `docs/product_docs_and_updates.md`
- Architecture: `docs/diagrams/plan/uml/03-class-diagram-backend.puml`

## Support

For issues or questions:
1. Check documentation files above
2. Review test files for usage examples
3. Consult [Strands documentation](https://strandsagents.com/)
