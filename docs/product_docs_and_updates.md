# Product Documentation & Updates Changelog

This document serves as a living changelog for all product and architectural changes made to the Gup-Shup Café platform. Every significant code update, architectural decision, or feature change should be documented here with a timestamp and informative description.

---

## Format

```
### [YYYY-MM-DD HH:MM UTC] - Brief Title
**Commit**: <commit_hash_or_message>
**Author**: <name_or_role>
**Type**: [Architecture | Feature | Bugfix | Documentation | Refactor | Performance]

**Changes**:
- Detailed description of what changed
- Why the change was made
- Impact on the system

**Files Modified**:
- List of key files changed
```

---

## Changelog

### [2025-10-15 17:06 UTC] - MVP System Architecture & 3-Day Hackathon Plan

**Commit**: `Initial analysis and planning for MVP system architecture documentation`  
**Author**: AWS AI Agent Hackathon Team  
**Type**: Architecture | Documentation

**Changes**:
- Created comprehensive MVP system architecture document for AWS AI Agent Hackathon 2025
- Defined 3-day sprint plan with task distribution for 5-member team
- Designed pluggable AI service layer with OpenAI-compatible interface
- Created ASCII art diagrams for:
  - High-level system architecture (Client → Server → AI Services)
  - AWS cloud infrastructure (Amplify + EC2 + Bedrock)
  - Data flow sequences for core user journey
  - Team task dependencies and critical path
- Prioritized MVP features (Must-Have vs Should-Have vs Won't-Have)
- Defined success metrics and risk mitigation strategies
- Documented cost estimates for AWS infrastructure ($5-15/month MVP, $84-104/month production)
- Created detailed team task breakdowns for:
  - Product Lead (Full-Stack + AI)
  - Frontend Developer
  - AI Engineer #1 (LLM)
  - AI Engineer #2 (STT/TTS)
  - AWS DevOps Specialist

**Key Architectural Decisions**:
1. **Pluggable AI Design**: Abstract interfaces for STT, LLM, and TTS allow easy switching between providers
   - Development: Gemini + Web Speech API (free)
   - Production: AWS Bedrock (Claude 3) + AWS Transcribe + AWS Polly
2. **OpenAI Message Format**: LLM interface standardized on OpenAI format for maximum compatibility
3. **WebRTC P2P Audio**: Direct peer-to-peer audio streaming reduces server load
4. **AWS Cloud Architecture**: Amplify (frontend) + EC2 (backend) + Bedrock (AI)
5. **CEFR Framework**: Core AI feedback based on Common European Framework of Reference for Languages

**Core MVP Loop Defined**:
```
User joins room → Speaks in discussion → AI transcribes (STT) 
→ LLM analyzes English quality → Provides CEFR feedback 
→ TTS speaks feedback → User improves → Repeat
```

**Files Created**:
- `docs/Architectural Conversations/product_system_design.md` - Main architecture document (46KB)
- `docs/product_docs_and_updates.md` - This changelog file

**Files Modified**:
- `.github/copilot-instructions.md` - Added requirement to track all updates in this changelog

**Impact**:
- Provides clear technical roadmap for 3-day hackathon
- Establishes architectural patterns for AI service integration
- Defines success criteria for MVP demo
- Ensures team alignment on priorities and dependencies

**Next Steps**:
- Day 1: Foundation setup (EC2, AI service layer, feedback UI components)
- Day 2: Integration (Full AI feedback loop, Amplify deployment)
- Day 3: Polish, testing, production deployment with Bedrock

---

## Instructions for Future Updates

When making significant changes to the codebase, please add an entry to this changelog following this format:

1. **Date & Time**: Use UTC timezone in YYYY-MM-DD HH:MM format
2. **Title**: Short, descriptive title (50 chars max)
3. **Commit Message**: The actual git commit message
4. **Type**: One or more of: Architecture, Feature, Bugfix, Documentation, Refactor, Performance
5. **Changes**: Bullet points describing what changed and why
6. **Files Modified**: List key files (not every single file, just important ones)
7. **Impact**: How this affects the system, users, or team

**Example Entry**:
```markdown
### [2025-10-16 14:30 UTC] - Implemented Gemini LLM Integration

**Commit**: `feat: add Gemini LLM with CEFR analysis endpoint`  
**Author**: AI Engineer #1  
**Type**: Feature

**Changes**:
- Implemented GeminiLLM class with OpenAI-compatible interface
- Created CEFR analysis prompt for English feedback
- Added /api/ai/analyze endpoint to FastAPI backend
- Integrated with room manager for real-time feedback

**Files Modified**:
- server_py/src/ai/gemini_llm.py (new)
- server_py/src/api/routes.py
- server_py/requirements.txt

**Impact**:
- Users now receive instant AI feedback on English speaking quality
- CEFR levels (A1-C2) are assigned based on grammar, vocabulary, fluency
- Foundation for switching to Bedrock in production
```

---

**Document Maintained By**: Product Team  
**Last Updated**: 2025-10-15 17:06 UTC  
**Version**: 1.0
