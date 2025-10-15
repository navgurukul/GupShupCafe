# Multi-Agent System Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    GupShup Cafe Application                         │
│                     (FastAPI + Socket.io)                           │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ User requests feedback
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  Debate Room Facilitator                            │
│                  (Main Entry Point)                                 │
│                                                                     │
│  Options:                                                           │
│  • use_multi_agent=True  → Multi-Agent Orchestrator                │
│  • use_multi_agent=False → Single Agent (legacy)                   │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ use_multi_agent=True
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│             Multi-Agent Orchestrator                                │
│             (Request Router & Coordinator)                          │
│                                                                     │
│  Capabilities:                                                      │
│  • Route requests to appropriate agents                             │
│  • Combine responses intelligently                                  │
│  • Manage agent lifecycle                                           │
│  • Handle local/AWS deployment modes                                │
│                                                                     │
│  Methods:                                                           │
│  • get_english_feedback(statements, instant=True/False)             │
│  • get_discussion_feedback(topic, statements)                       │
│  • get_combined_feedback(topic, statements)                         │
│  • deploy_to_aws()                                                  │
└──────────────┬────────────────────────────┬─────────────────────────┘
               │                            │
               │ English requests           │ Discussion requests
               ▼                            ▼
┌───────────────────────────┐    ┌──────────────────────────┐
│   English Grammar Agent   │    │  Debate Facilitator      │
│                           │    │  Agent                   │
│  Focus:                   │    │  Focus:                  │
│  • Grammar corrections    │    │  • Discussion flow       │
│  • Sentence structure     │    │  • Fact-checking         │
│  • Vocabulary suggestions │    │  • Common ground         │
│  • Clarity assessment     │    │  • Content guidance      │
│                           │    │                          │
│  Model: Gemini 2.5 Flash  │    │  Model: Gemini 2.5 Flash │
│  Temp: 0.3 (consistent)   │    │  Temp: 0.7 (balanced)    │
└─────────────┬─────────────┘    └─────────────┬────────────┘
              │                                 │
              │ API calls                       │ API calls
              ▼                                 ▼
┌─────────────────────────────────────────────────────────────┐
│                    Gemini API                               │
│              (Google Generative AI)                         │
└─────────────────────────────────────────────────────────────┘
```

## Deployment Modes

### Local Development Mode
```
┌──────────────────────┐
│  Developer Machine   │
│                      │
│  ┌────────────────┐  │
│  │ Orchestrator   │  │
│  │  (Local)       │  │
│  └────┬───────┬───┘  │
│       │       │      │
│   ┌───▼──┐ ┌──▼───┐ │
│   │English│ │Debate│ │
│   │Agent  │ │Agent │ │
│   └───────┘ └──────┘ │
└──────────────────────┘
         │
         ▼
   Gemini API
```

### AWS Production Mode
```
┌────────────────────────────────────────────────┐
│              AWS Cloud                         │
│                                                │
│  ┌──────────────────────────────────────────┐ │
│  │   AWS Bedrock AgentCore                  │ │
│  │                                          │ │
│  │  ┌────────────────────────────────────┐ │ │
│  │  │  Multi-Agent Orchestrator          │ │ │
│  │  │  (Managed Runtime)                 │ │ │
│  │  └──────┬───────────┬─────────────────┘ │ │
│  │         │           │                   │ │
│  │    ┌────▼────┐  ┌───▼──────┐          │ │
│  │    │ English │  │  Debate  │          │ │
│  │    │ Agent   │  │  Agent   │          │ │
│  │    │ Runtime │  │  Runtime │          │ │
│  │    └─────────┘  └──────────┘          │ │
│  │                                        │ │
│  │  Features:                             │ │
│  │  • Auto-scaling                        │ │
│  │  • Load balancing                      │ │
│  │  • CloudWatch monitoring               │ │
│  │  • High availability                   │ │
│  └────────────────────────────────────────┘ │
└────────────────────────────────────────────────┘
                 │
                 ▼
           Gemini API
```

## Request Flow

### Combined Feedback Request
```
User Input
   │
   ▼
┌─────────────────────────┐
│ Debate Room Facilitator │
│ get_agent_feedback()    │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ Multi-Agent Orchestrator        │
│ get_combined_feedback()         │
└──────┬──────────────┬───────────┘
       │              │
       │ Parallel     │ Parallel
       │ Request      │ Request
       ▼              ▼
┌─────────────┐  ┌──────────────┐
│ English     │  │ Debate       │
│ Agent       │  │ Facilitator  │
└──────┬──────┘  └──────┬───────┘
       │                │
       │ Response       │ Response
       ▼                ▼
┌──────────────────────────────────┐
│ Orchestrator                     │
│ • Combines responses             │
│ • Formats output                 │
│ • Returns structured feedback    │
└────────────┬─────────────────────┘
             │
             ▼
        User receives:
        {
          "discussion_feedback": "...",
          "english_feedback": "..."
        }
```

### Instant English Feedback
```
Recent Statements
   │
   ▼
┌──────────────────────┐
│ Orchestrator         │
│ get_english_feedback │
│ (instant=True)       │
└──────────┬───────────┘
           │
           │ Last 3 statements
           ▼
┌──────────────────────┐
│ English Grammar Agent│
│                      │
│ • Quick analysis     │
│ • Pattern detection  │
│ • Immediate feedback │
└──────────┬───────────┘
           │
           ▼
    Instant feedback
    (2-3 seconds)
```

### Comprehensive Summary
```
All Discussion Statements
   │
   ▼
┌──────────────────────┐
│ Orchestrator         │
│ get_english_feedback │
│ (instant=False)      │
└──────────┬───────────┘
           │
           │ All statements
           │ grouped by speaker
           ▼
┌──────────────────────┐
│ English Grammar Agent│
│                      │
│ • Deep analysis      │
│ • Progress tracking  │
│ • Actionable tips    │
└──────────┬───────────┘
           │
           ▼
  Comprehensive summary
  (5-10 seconds)
```

## Agent Specialization

### English Grammar Agent System Prompt
```
Role: Expert English language instructor

Focus Areas:
├── Grammar
│   ├── Verb tenses
│   ├── Subject-verb agreement
│   ├── Articles (a, an, the)
│   └── Prepositions
├── Sentence Structure
│   ├── Word order
│   ├── Run-ons & fragments
│   └── Complex sentences
├── Vocabulary
│   ├── Word choice
│   ├── Context-appropriate usage
│   └── Synonyms & variety
└── Clarity
    ├── Coherence
    ├── Natural flow
    └── Meaning clarity

Temperature: 0.3 (consistent corrections)
```

### Debate Facilitator Agent System Prompt
```
Role: Discussion facilitator

Focus Areas:
├── Content
│   ├── Fact-checking
│   ├── Claim verification
│   └── Logical flow
├── Discussion Flow
│   ├── Turn management
│   ├── Topic guidance
│   └── Productive direction
├── Analysis
│   ├── Common ground
│   ├── Diverging points
│   └── Discussion pulse
└── Guidance
    ├── Suggestions
    ├── Encouragement
    └── Balance

Temperature: 0.7 (balanced creativity)
```

## Data Flow

```
┌─────────────────────────────────────────────────────────┐
│                  Conversation History                   │
│                                                         │
│  [                                                      │
│    {speaker: "Alice", content: "..."},                  │
│    {speaker: "Bob", content: "..."},                    │
│    {speaker: "Charlie", content: "..."}                 │
│  ]                                                      │
└───────────────────┬─────────────────────────────────────┘
                    │
         ┌──────────┴──────────┐
         │                     │
         ▼                     ▼
┌─────────────────┐   ┌────────────────────┐
│ English Agent   │   │ Facilitator Agent  │
│                 │   │                    │
│ Analyzes:       │   │ Analyzes:          │
│ • Grammar       │   │ • Content          │
│ • Structure     │   │ • Flow             │
│ • Vocabulary    │   │ • Logic            │
└────────┬────────┘   └─────────┬──────────┘
         │                      │
         │ Feedback             │ Feedback
         │                      │
         └──────────┬───────────┘
                    │
                    ▼
         ┌────────────────────┐
         │  Combined Response │
         │                    │
         │  ╔════════════════╗│
         │  ║ Discussion     ║│
         │  ║ Feedback       ║│
         │  ╚════════════════╝│
         │                    │
         │  ╔════════════════╗│
         │  ║ English        ║│
         │  ║ Feedback       ║│
         │  ╚════════════════╝│
         └────────────────────┘
```

## Fallback Chain

```
User Request
   │
   ▼
Try Multi-Agent Mode
   │
   ├─ Success → Return combined feedback
   │
   └─ Failure
      │
      ▼
   Fallback to Single-Agent Mode
      │
      ├─ Success → Return combined feedback
      │
      └─ Failure
         │
         ▼
      Return error message
      (Graceful degradation)
```

## Configuration Decision Tree

```
                Start
                  │
                  ▼
         USE_MULTI_AGENT=true?
                  │
          ┌───────┴───────┐
          │               │
         Yes              No
          │               │
          ▼               ▼
    USE_AWS_AGENTCORE?   Single Agent Mode
          │              (Legacy)
    ┌─────┴─────┐
    │           │
   Yes         No
    │           │
    ▼           ▼
AWS Mode     Local Mode
(Production) (Development)
```

## Agent Lifecycle

```
┌─────────────────────────────────────────┐
│           Initialization                │
│                                         │
│  1. Load environment variables          │
│  2. Check AWS credentials (if needed)   │
│  3. Initialize English Grammar Agent    │
│  4. Prepare Facilitator Agent (on-demand)│
│  5. Set up orchestrator                 │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│           Runtime                       │
│                                         │
│  1. Receive feedback request            │
│  2. Route to appropriate agent(s)       │
│  3. Process responses                   │
│  4. Combine and format                  │
│  5. Return to user                      │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│           Cleanup                       │
│                                         │
│  1. Clear conversation history          │
│  2. Release agent resources             │
│  3. Close connections                   │
└─────────────────────────────────────────┘
```

## Legend

```
┌─────────┐
│  Box    │  Component or process
└─────────┘

    │
    │       Flow direction
    ▼

    ┼       Decision point

═══════     Emphasized content

┌┐└┘│─      ASCII box drawing
```
