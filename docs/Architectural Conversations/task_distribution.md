## Team Task Distribution & 3-Day Action Plan

### 1 Team Composition

| Role | Responsibilities | Key Skills |
|------|-----------------|------------|
| **Product Lead (Full-Stack + AI)** | Architecture, AI integration, coordination | FastAPI, React, LLMs, AWS |
| **Frontend Developer** | React UI, WebRTC, real-time features | React, Socket.io, WebRTC, Tailwind |
| **AI Engineer #1** | LLM integration, CEFR feedback, prompt engineering | Gemini/Bedrock, NLP, Python |
| **AI Engineer #2** | STT/TTS integration, audio processing | Speech APIs, Audio processing |
| **AWS DevOps Specialist** | Infrastructure, deployment, CI/CD | AWS (EC2, Amplify, Bedrock), Docker, Nginx |

### 2 Day 1: Foundation & Core Setup

#### Product Lead (Full-Stack + AI)
- [ ] **Hour 1-2**: Review existing codebase, document current state
- [ ] **Hour 3-4**: Set up project structure for AI service layer
  - Create `ai_services/` directory structure
  - Define interface classes (STTInterface, LLMInterface, TTSInterface)
  - Set up configuration management
- [ ] **Hour 5-6**: Implement basic AIServiceManager factory
- [ ] **Hour 7-8**: Integrate LLM basic chat endpoint with FastAPI
  - POST `/api/ai/analyze` endpoint
  - Test with sample transcript

#### Frontend Developer
- [ ] **Hour 1-2**: Audit existing React components (Login, Lobby, Roundtable)
- [ ] **Hour 3-4**: Set up feedback display components
  - Create `FeedbackPanel` component
  - Create `CEFRLevelIndicator` component
  - Create `SpeakingStatsCard` component
- [ ] **Hour 5-6**: Wire Socket.io events for AI feedback
  - Listen for `ai-feedback` event
  - Display real-time feedback in UI
- [ ] **Hour 7-8**: Test end-to-end flow (dummy data)

#### AI Engineer #1 (LLM)
- [ ] **Hour 1-2**: Research Gemini API for CEFR analysis
- [ ] **Hour 3-4**: Implement `GeminiLLM` class
  - Implement `chat()` method with OpenAI format conversion
  - Write unit tests
- [ ] **Hour 5-6**: Design CEFR analysis prompt
  - System prompt for English teacher role
  - JSON output format for structured feedback
- [ ] **Hour 7-8**: Implement `analyze_english()` method
  - Grammar scoring
  - Vocabulary assessment
  - Fluency evaluation
  - Test with sample transcripts

#### AI Engineer #2 (STT/TTS)
- [ ] **Hour 1-2**: Research Web Speech Recognition API
- [ ] **Hour 3-4**: Implement client-side STT integration
  - Hook into AudioContext
  - Send transcripts to server via Socket.io
- [ ] **Hour 5-6**: Implement `BrowserTTS` class
  - Text-to-speech for AI feedback
  - Voice selection logic
- [ ] **Hour 7-8**: Test STT/TTS integration
  - Record sample audio
  - Verify transcript accuracy

#### AWS DevOps Specialist
- [ ] **Hour 1-2**: Set up AWS account, configure IAM users
- [ ] **Hour 3-4**: Provision EC2 instance (t2.micro for testing)
  - Install Ubuntu 22.04
  - Configure security groups
  - Assign Elastic IP
- [ ] **Hour 5-6**: Install dependencies on EC2
  - Python 3.11, FastAPI, nginx
  - Clone repository
  - Set up virtual environment
- [ ] **Hour 7-8**: Deploy initial backend version
  - Configure systemd service
  - Test health check endpoint
  - Set up CloudWatch logging

**Day 1 Goal**: Core infrastructure is running; Basic AI chat endpoint works; Frontend displays feedback UI skeleton.

---

### 3 Day 2: Integration & AI Features

#### Product Lead (Full-Stack + AI)
- [ ] **Hour 1-2**: Implement feedback storage in database
  - Create `feedback` table schema
  - Store feedback per participant per session
- [ ] **Hour 3-4**: Implement CEFR progress tracking
  - Calculate average CEFR level over time
  - Store historical scores
- [ ] **Hour 5-6**: Create `/api/feedback/history/:userId` endpoint
- [ ] **Hour 7-8**: Integration testing with all AI services
  - Test full flow: Speak → STT → LLM → Feedback → DB
  - Debug issues

#### Frontend Developer
- [ ] **Hour 1-2**: Implement real-time feedback display
  - Show feedback panel when user finishes speaking
  - Display CEFR level, scores, suggestions
- [ ] **Hour 3-4**: Add progress tracking UI
  - Line chart for CEFR level over sessions
  - Display improvement metrics
- [ ] **Hour 5-6**: Implement TTS audio playback
  - Play AI agent feedback as audio
  - Sync text + audio
- [ ] **Hour 7-8**: Polish UI/UX
  - Animations for feedback appearance
  - Mobile responsiveness
  - Loading states

#### AI Engineer #1 (LLM)
- [ ] **Hour 1-2**: Refine CEFR analysis prompt
  - Add more detailed grammar rules
  - Improve vocabulary level detection
- [ ] **Hour 3-4**: Implement context-aware feedback
  - Use previous feedback to track improvement
  - Personalize suggestions
- [ ] **Hour 5-6**: Add topic-specific analysis
  - Adjust scoring based on topic difficulty
  - Provide topic-relevant vocabulary tips
- [ ] **Hour 7-8**: Prepare Bedrock LLM implementation
  - Set up AWS Bedrock access
  - Implement `BedrockLLM` class (for Day 3 production switch)

#### AI Engineer #2 (STT/TTS)
- [ ] **Hour 1-2**: Optimize STT accuracy
  - Add noise filtering
  - Handle silence detection
- [ ] **Hour 3-4**: Implement transcript post-processing
  - Remove filler words (um, uh, like)
  - Normalize punctuation
- [ ] **Hour 5-6**: Add language detection
  - Detect if user speaks in English vs other languages
  - Provide appropriate feedback
- [ ] **Hour 7-8**: Prepare AWS Transcribe integration (optional)
  - Research API usage
  - Implement basic wrapper (for future use)

#### AWS DevOps Specialist
- [ ] **Hour 1-2**: Set up AWS Amplify for frontend
  - Connect GitHub repository
  - Configure build settings
  - Deploy to staging environment
- [ ] **Hour 3-4**: Configure environment variables
  - Set `VITE_API_URL` to EC2 backend
  - Test frontend → backend connectivity
- [ ] **Hour 5-6**: Set up SSL certificate (Let's Encrypt or ACM)
  - Configure nginx for HTTPS
  - Update security groups
- [ ] **Hour 7-8**: Set up monitoring
  - Configure CloudWatch alarms
  - Set up log aggregation
  - Test error reporting

**Day 2 Goal**: Full AI feedback loop is working end-to-end; Frontend shows real-time CEFR analysis; AWS infrastructure is stable.

---

### 4 Day 3: Polish, Testing & Production Deployment

#### Product Lead (Full-Stack + AI)
- [ ] **Hour 1-2**: Switch from Gemini to AWS Bedrock (production)
  - Update `ai_service_manager.py` config
  - Test Bedrock LLM integration
  - Compare quality with Gemini
- [ ] **Hour 3-4**: Implement analytics endpoints
  - `/api/analytics/session/:sessionId`
  - `/api/analytics/user/:userId`
- [ ] **Hour 5-6**: Code review and bug fixes
  - Review all PRs
  - Fix critical bugs
- [ ] **Hour 7-8**: Prepare demo presentation
  - Create demo script
  - Prepare test scenarios

#### Frontend Developer
- [ ] **Hour 1-2**: Final UI polish
  - Fix CSS issues
  - Add loading spinners
  - Improve error messages
- [ ] **Hour 3-4**: Cross-browser testing
  - Test on Chrome, Firefox, Safari
  - Fix WebRTC compatibility issues
- [ ] **Hour 5-6**: Mobile responsiveness
  - Test on iOS and Android
  - Adjust layouts for small screens
- [ ] **Hour 7-8**: User acceptance testing
  - Run through full user journey
  - Create bug list and fix critical issues

#### AI Engineer #1 (LLM)
- [ ] **Hour 1-2**: Fine-tune CEFR accuracy
  - Test with diverse transcripts
  - Adjust scoring thresholds
- [ ] **Hour 3-4**: Implement fallback for AI failures
  - Handle API timeouts
  - Provide generic feedback if LLM fails
- [ ] **Hour 5-6**: Optimize prompt tokens
  - Reduce prompt length to lower costs
  - Maintain quality
- [ ] **Hour 7-8**: Document AI configuration
  - Write README for AI services
  - Document prompt templates

#### AI Engineer #2 (STT/TTS)
- [ ] **Hour 1-2**: Test STT with various accents
  - Indian, American, British accents
  - Adjust confidence thresholds
- [ ] **Hour 3-4**: Optimize TTS voice quality
  - Select best voice for AI agent
  - Adjust speaking rate
- [ ] **Hour 5-6**: Add audio recording debugging
  - Log audio quality metrics
  - Detect poor microphone issues
- [ ] **Hour 7-8**: Document STT/TTS usage
  - Write user guide for audio setup
  - Troubleshooting guide

#### AWS DevOps Specialist
- [ ] **Hour 1-2**: Production deployment to EC2
  - Deploy final backend version
  - Run database migrations
  - Verify all services are running
- [ ] **Hour 3-4**: Deploy frontend to Amplify (production)
  - Merge to main branch
  - Trigger production build
  - Verify deployment
- [ ] **Hour 5-6**: Load testing
  - Simulate 20-50 concurrent users
  - Monitor CPU/memory usage
  - Optimize if needed
- [ ] **Hour 7-8**: Backup and disaster recovery
  - Set up automated DB backups
  - Document recovery procedures
  - Create runbook for common issues

**Day 3 Goal**: Production system is live and stable; Demo is ready; All critical bugs are fixed.
