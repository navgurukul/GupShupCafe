# Gup-Shup Café - MVP System Architecture & 3-Day Hackathon Plan

**Project**: Gup-Shup Café - AI-Powered English Speaking Skills Platform  
**Hackathon**: AWS AI Agent Hackathon 2025  
**Timeline**: 3 Days  
**Repository**: https://github.com/navgurukul/GupShupCafe  
**Date**: October 2025  

---

## Executive Summary

Gup-Shup Café is a gamified, peer-to-peer discussion platform that provides instant AI-driven feedback on English speaking skills using the CEFR framework. This document defines the MVP architecture, prioritizes features for a 3-day hackathon sprint, and provides actionable tasks for a 5-member team.

**Core MVP Loop**: User joins room → Speaks in structured discussion → Receives real-time AI feedback → Tracks progress on CEFR scale

---

## 1. MVP Feature Prioritization

### 1.1 Must-Have Features (Core Loop - Days 1-3)

**Priority 1: Basic Room Operations**
- ✅ User authentication (anonymous or simple login)
- ✅ Create/join discussion room (max 4-6 participants for MVP)
- ✅ Lobby system with ready-check mechanism
- ✅ Room state management (waiting, active, completed)

**Priority 2: Real-Time Audio Discussion**
- ✅ WebRTC peer-to-peer audio streaming
- ✅ Turn-based speaking system (60-second timers)
- ✅ Visual speaker indicators
- ✅ Microphone mute/unmute controls
- ✅ Basic audio level indicators

**Priority 3: AI Feedback Engine (Core Innovation)**
- ✅ Speech-to-Text (STT) using Web Speech Recognition API (MVP)
- ✅ LLM-based feedback on English quality (grammar, vocabulary, fluency)
- ✅ CEFR level estimation (A1-C2 scale)
- ✅ Text-to-Speech (TTS) for AI agent responses
- ✅ Real-time feedback display to users

**Priority 4: Minimal Persistence**
- ✅ Store session data (participants, transcripts, feedback)
- ✅ Track basic CEFR progress per user
- ✅ Save discussion history (last 24 hours for MVP)

### 1.2 Should-Have Features (Post-MVP / Nice-to-Have)

- ⚠️ Advanced topic generation (AI-curated topics)
- ⚠️ Detailed analytics dashboard
- ⚠️ User profiles with historical progress
- ⚠️ Multi-language support
- ⚠️ Mobile app version
- ⚠️ Gamification badges/achievements

### 1.3 Won't-Have for MVP

- ❌ User authentication with social login (OAuth)
- ❌ Payment/subscription systems
- ❌ Advanced moderation features
- ❌ Video streaming
- ❌ Recording and playback
- ❌ Export transcripts/reports

---

## 2. High-Level System Architecture

### 2.1 Component Overview

```
┌────────────────────────────────────────────────────────────────────────┐
│                            CLIENT LAYER                                 │
│  ┌──────────────────────────────────────────────────────────────┐     │
│  │                    React 18 + Vite                            │     │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐            │     │
│  │  │  Pages     │  │  Contexts  │  │ Components │            │     │
│  │  │ - Login    │  │ - Auth     │  │ - Table    │            │     │
│  │  │ - Lobby    │  │ - Socket   │  │ - Timer    │            │     │
│  │  │ - Room     │  │ - Audio    │  │ - Feedback │            │     │
│  │  └────────────┘  └────────────┘  └────────────┘            │     │
│  │                                                               │     │
│  │  ┌─────────────────────────────────────────────┐            │     │
│  │  │    WebRTC (Peer-to-Peer Audio Mesh)         │            │     │
│  │  │    - Local/Remote Stream Management          │            │     │
│  │  │    - STUN/TURN for NAT Traversal            │            │     │
│  │  └─────────────────────────────────────────────┘            │     │
│  └──────────────────────────────────────────────────────────────┘     │
│           │                    │                    │                  │
│      REST API          WebSocket (Socket.io)    WebRTC Signaling      │
│           │                    │                    │                  │
└───────────┼────────────────────┼────────────────────┼──────────────────┘
            │                    │                    │
            ▼                    ▼                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                           SERVER LAYER (AWS EC2)                        │
│  ┌──────────────────────────────────────────────────────────────┐     │
│  │              FastAPI + python-socketio                        │     │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │     │
│  │  │ REST API │  │ Socket.io│  │  WebRTC  │  │   CORS   │    │     │
│  │  │ Routes   │  │ Handlers │  │ Signaling│  │Middleware│    │     │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────────┘    │     │
│  └───────┼─────────────┼─────────────┼──────────────────────────┘     │
│          │             │             │                                 │
│  ┌───────▼─────┐  ┌────▼────┐  ┌────▼─────┐                          │
│  │ Room Manager│  │ Session │  │ WebRTC   │                          │
│  │  Service    │  │ Manager │  │ Relay    │                          │
│  └─────┬───────┘  └────┬────┘  └──────────┘                          │
│        │               │                                               │
└────────┼───────────────┼───────────────────────────────────────────────┘
         │               │
         │               ▼
         │    ┌─────────────────┐
         │    │   MongoDB/SQLite │
         │    │   - Sessions     │
         │    │   - Participants │
         │    │   - Transcripts  │
         │    │   - Feedback     │
         │    └─────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────────────────────┐
│                    PLUGGABLE AI SERVICE LAYER                           │
│  ┌──────────────────────────────────────────────────────────────┐     │
│  │                  AI Service Abstraction                       │     │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │     │
│  │  │ STT Module  │  │ LLM Module  │  │ TTS Module  │          │     │
│  │  │ (Interface) │  │ (Interface) │  │ (Interface) │          │     │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘          │     │
│  └─────────┼─────────────────┼─────────────────┼─────────────────┘     │
│            │                 │                 │                       │
│  ┌─────────▼───────┐ ┌───────▼───────┐ ┌──────▼──────┐              │
│  │ STT Providers   │ │ LLM Providers │ │TTS Providers│              │
│  │ ┌─────────────┐ │ │ ┌───────────┐ │ │ ┌─────────┐ │              │
│  │ │Web Speech   │ │ │ │  Gemini   │ │ │ │ Browser │ │              │
│  │ │ Recognition │ │ │ │  (Dev)    │ │ │ │   TTS   │ │              │
│  │ └─────────────┘ │ │ └───────────┘ │ │ └─────────┘ │              │
│  │ ┌─────────────┐ │ │ ┌───────────┐ │ │ ┌─────────┐ │              │
│  │ │ AWS         │ │ │ │  Bedrock  │ │ │ │ AWS     │ │              │
│  │ │ Transcribe  │ │ │ │  Claude   │ │ │ │ Polly   │ │              │
│  │ └─────────────┘ │ │ └───────────┘ │ │ └─────────┘ │              │
│  └─────────────────┘ └───────────────┘ └─────────────┘              │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow Sequence

```
┌──────────┐                ┌──────────┐                ┌──────────────┐
│  User A  │                │  Server  │                │  AI Service  │
└────┬─────┘                └────┬─────┘                └──────┬───────┘
     │                           │                              │
     │ 1. Join Room              │                              │
     │ ─────────────────────────>│                              │
     │                           │                              │
     │ 2. Room State + Topic     │                              │
     │ <─────────────────────────│                              │
     │                           │                              │
     │ 3. WebRTC Offer (P2P)     │                              │
     │ ─────────────────────────>│────────────────>             │
     │                           │        (Signaling)           │
     │ 4. WebRTC Answer          │                              │
     │ <─────────────────────────│<────────────────             │
     │                           │                              │
     │ 5. Audio Stream (P2P) ◄──────────────────────►          │
     │    (Direct between peers, no server relay)              │
     │                           │                              │
     │ 6. Speak (Turn Timer)     │                              │
     │ ───────────────►          │                              │
     │    Audio to STT           │                              │
     │                           │ 7. Transcript Text           │
     │                           │ ────────────────────────────>│
     │                           │                              │
     │                           │ 8. AI Analysis (CEFR)        │
     │                           │ <────────────────────────────│
     │                           │    - Grammar check           │
     │                           │    - Vocabulary level        │
     │                           │    - Fluency score           │
     │                           │                              │
     │ 9. Feedback Display       │                              │
     │ <─────────────────────────│                              │
     │    + TTS Audio Response   │                              │
     │                           │                              │
     │ 10. Next Turn             │                              │
     │ <─────────────────────────│                              │
     │                           │                              │
```

---

## 3. Pluggable AI Service Layer Design

### 3.1 Design Principles

1. **Abstraction**: Each AI service (STT, LLM, TTS) is behind an interface
2. **OpenAI Compatibility**: LLM interface uses standard OpenAI message format
3. **Easy Switching**: Toggle between Gemini (dev) and Bedrock (prod) with config
4. **Fallback Support**: Graceful degradation if AI services fail

### 3.2 Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                  AI Service Manager (ai_services.py)            │
│                                                                 │
│  config = {                                                     │
│    "stt_provider": "web_speech_api",    # or "aws_transcribe" │
│    "llm_provider": "gemini",            # or "bedrock"          │
│    "tts_provider": "browser_tts",       # or "aws_polly"       │
│  }                                                              │
└────────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  STTInterface   │  │  LLMInterface   │  │  TTSInterface   │
│  (Abstract)     │  │  (Abstract)     │  │  (Abstract)     │
└─────────────────┘  └─────────────────┘  └─────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ WebSpeechSTT    │  │  GeminiLLM      │  │  BrowserTTS     │
│ AWSTranscribeSTT│  │  BedrockLLM     │  │  AWSPollyTTS    │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### 3.3 Interface Definitions

#### STTInterface
```python
# server_py/src/ai/stt_interface.py
from abc import ABC, abstractmethod
from typing import Optional

class STTInterface(ABC):
    """Abstract interface for Speech-to-Text providers."""
    
    @abstractmethod
    async def transcribe(self, audio_data: bytes, language: str = "en") -> dict:
        """
        Transcribe audio to text.
        
        Args:
            audio_data: Raw audio bytes (WAV/PCM format)
            language: Language code (default: "en")
            
        Returns:
            {
                "success": bool,
                "text": str,
                "confidence": float,  # 0.0-1.0
                "language": str,
                "provider": str
            }
        """
        pass
    
    @abstractmethod
    def get_supported_languages(self) -> list[str]:
        """Return list of supported language codes."""
        pass
```

#### LLMInterface (OpenAI-Compatible)
```python
# server_py/src/ai/llm_interface.py
from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class LLMInterface(ABC):
    """
    Abstract interface for Language Model providers.
    Uses OpenAI message format for compatibility.
    """
    
    @abstractmethod
    async def chat(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> dict:
        """
        Generate chat completion.
        
        Args:
            messages: OpenAI-style messages
                [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello!"},
                    {"role": "assistant", "content": "Hi there!"}
                ]
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            {
                "success": bool,
                "message": {
                    "role": "assistant",
                    "content": str
                },
                "usage": {
                    "prompt_tokens": int,
                    "completion_tokens": int,
                    "total_tokens": int
                },
                "provider": str
            }
        """
        pass
    
    @abstractmethod
    async def analyze_english(self, transcript: str, context: dict) -> dict:
        """
        Analyze English speaking quality based on CEFR.
        
        Args:
            transcript: User's spoken text
            context: {
                "previous_feedback": List[dict],
                "topic": str,
                "participant_name": str
            }
            
        Returns:
            {
                "success": bool,
                "cefr_level": str,  # A1, A2, B1, B2, C1, C2
                "score": float,     # 0.0-10.0
                "feedback": {
                    "grammar": {"score": float, "issues": List[str]},
                    "vocabulary": {"score": float, "level": str},
                    "fluency": {"score": float, "comments": str},
                    "pronunciation": {"score": float, "notes": str}
                },
                "suggestions": List[str],
                "provider": str
            }
        """
        pass
```

#### TTSInterface
```python
# server_py/src/ai/tts_interface.py
from abc import ABC, abstractmethod

class TTSInterface(ABC):
    """Abstract interface for Text-to-Speech providers."""
    
    @abstractmethod
    async def synthesize(
        self, 
        text: str, 
        voice: str = "default",
        language: str = "en"
    ) -> dict:
        """
        Synthesize speech from text.
        
        Args:
            text: Text to speak
            voice: Voice ID/name
            language: Language code
            
        Returns:
            {
                "success": bool,
                "audio_url": str,  # URL or base64 data URI
                "audio_format": str,  # "mp3", "wav", etc.
                "duration": float,  # seconds
                "provider": str
            }
        """
        pass
    
    @abstractmethod
    def get_available_voices(self, language: str = "en") -> list[dict]:
        """Return list of available voices for language."""
        pass
```

### 3.4 Concrete Implementations (MVP)

#### Gemini LLM (Development)
```python
# server_py/src/ai/gemini_llm.py
import google.generativeai as genai
from .llm_interface import LLMInterface

class GeminiLLM(LLMInterface):
    """Gemini API implementation for development."""
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
    
    async def chat(self, messages, temperature=0.7, max_tokens=500):
        # Convert OpenAI format to Gemini format
        prompt = self._convert_messages(messages)
        
        response = await self.model.generate_content_async(
            prompt,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens
            }
        )
        
        return {
            "success": True,
            "message": {
                "role": "assistant",
                "content": response.text
            },
            "usage": {
                "prompt_tokens": 0,  # Gemini doesn't provide this
                "completion_tokens": 0,
                "total_tokens": 0
            },
            "provider": "gemini"
        }
    
    async def analyze_english(self, transcript, context):
        prompt = f"""
        Analyze this English transcript based on CEFR standards (A1-C2).
        
        Transcript: "{transcript}"
        Topic: {context.get('topic', 'General conversation')}
        
        Provide:
        1. CEFR Level (A1/A2/B1/B2/C1/C2)
        2. Grammar score (0-10)
        3. Vocabulary score (0-10)
        4. Fluency score (0-10)
        5. Top 3 improvement suggestions
        
        Format as JSON.
        """
        
        response = await self.chat([
            {"role": "system", "content": "You are an English language expert."},
            {"role": "user", "content": prompt}
        ])
        
        # Parse and structure response
        # (Implementation details...)
        
        return {
            "success": True,
            "cefr_level": "B1",
            "score": 7.5,
            "feedback": {...},
            "suggestions": [...],
            "provider": "gemini"
        }
```

#### Bedrock LLM (Production)
```python
# server_py/src/ai/bedrock_llm.py
import boto3
import json
from .llm_interface import LLMInterface

class BedrockLLM(LLMInterface):
    """AWS Bedrock (Claude) implementation for production."""
    
    def __init__(self, region: str = "us-east-1", model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"):
        self.client = boto3.client("bedrock-runtime", region_name=region)
        self.model_id = model_id
    
    async def chat(self, messages, temperature=0.7, max_tokens=500):
        # Convert OpenAI format to Claude format
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages
        }
        
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body)
        )
        
        result = json.loads(response['body'].read())
        
        return {
            "success": True,
            "message": {
                "role": "assistant",
                "content": result['content'][0]['text']
            },
            "usage": {
                "prompt_tokens": result['usage']['input_tokens'],
                "completion_tokens": result['usage']['output_tokens'],
                "total_tokens": result['usage']['input_tokens'] + result['usage']['output_tokens']
            },
            "provider": "bedrock"
        }
    
    async def analyze_english(self, transcript, context):
        # Similar to Gemini but using Bedrock
        # (Implementation details...)
        pass
```

### 3.5 Configuration & Factory Pattern

```python
# server_py/src/ai/ai_service_manager.py
from .stt_interface import STTInterface
from .llm_interface import LLMInterface
from .tts_interface import TTSInterface
from .web_speech_stt import WebSpeechSTT
from .gemini_llm import GeminiLLM
from .bedrock_llm import BedrockLLM
from .browser_tts import BrowserTTS

class AIServiceManager:
    """Factory for creating and managing AI services."""
    
    def __init__(self, config: dict):
        self.config = config
        self._stt = None
        self._llm = None
        self._tts = None
    
    def get_stt(self) -> STTInterface:
        if not self._stt:
            provider = self.config.get("stt_provider", "web_speech_api")
            if provider == "web_speech_api":
                self._stt = WebSpeechSTT()
            elif provider == "aws_transcribe":
                # self._stt = AWSTranscribeSTT()
                pass
        return self._stt
    
    def get_llm(self) -> LLMInterface:
        if not self._llm:
            provider = self.config.get("llm_provider", "gemini")
            if provider == "gemini":
                api_key = self.config.get("gemini_api_key")
                self._llm = GeminiLLM(api_key)
            elif provider == "bedrock":
                self._llm = BedrockLLM()
        return self._llm
    
    def get_tts(self) -> TTSInterface:
        if not self._tts:
            provider = self.config.get("tts_provider", "browser_tts")
            if provider == "browser_tts":
                self._tts = BrowserTTS()
            elif provider == "aws_polly":
                # self._tts = AWSPollyTTS()
                pass
        return self._tts

# Usage in main application
ai_manager = AIServiceManager({
    "stt_provider": "web_speech_api",
    "llm_provider": "gemini",  # Switch to "bedrock" for production
    "tts_provider": "browser_tts",
    "gemini_api_key": os.getenv("GEMINI_API_KEY")
})

llm = ai_manager.get_llm()
feedback = await llm.analyze_english(transcript, context)
```

---

## 4. AWS Cloud Architecture

### 4.1 Infrastructure Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          AWS CLOUD (us-east-1)                           │
│                                                                          │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                    AWS AMPLIFY HOSTING                             │ │
│  │  ┌──────────────────────────────────────────────────────────────┐ │ │
│  │  │                  Frontend (React + Vite)                      │ │ │
│  │  │  - Static files (HTML, JS, CSS)                              │ │ │
│  │  │  - CloudFront CDN distribution                               │ │ │
│  │  │  - Auto SSL certificate (HTTPS)                              │ │ │
│  │  │  - CI/CD from GitHub                                         │ │ │
│  │  └──────────────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                    │                                    │
│                         HTTPS/WSS  │                                    │
│                                    ▼                                    │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                    VPC (Virtual Private Cloud)                     │ │
│  │                                                                    │ │
│  │  ┌─────────────────────────────────────────────────────────────┐ │ │
│  │  │               Public Subnet (10.0.1.0/24)                    │ │ │
│  │  │                                                              │ │ │
│  │  │  ┌──────────────────────────────────────────────────────┐  │ │ │
│  │  │  │      EC2 Instance (t2.small or t3.medium)            │  │ │ │
│  │  │  │                                                       │  │ │ │
│  │  │  │  - Ubuntu 22.04 LTS                                  │  │ │ │
│  │  │  │  - Python 3.11 + FastAPI                            │  │ │ │
│  │  │  │  - python-socketio                                   │  │ │ │
│  │  │  │  - Nginx (reverse proxy)                            │  │ │ │
│  │  │  │  - Systemd service management                        │  │ │ │
│  │  │  │                                                       │  │ │ │
│  │  │  │  Ports:                                              │  │ │ │
│  │  │  │  - 22 (SSH - restricted to admin IP)                │  │ │ │
│  │  │  │  - 80 (HTTP - redirects to 443)                     │  │ │ │
│  │  │  │  - 443 (HTTPS/WSS - public)                         │  │ │ │
│  │  │  │  - 3003 (Internal FastAPI - via Nginx)              │  │ │ │
│  │  │  └──────────────────────────────────────────────────────┘  │ │ │
│  │  │                           │                                 │ │ │
│  │  └───────────────────────────┼─────────────────────────────────┘ │ │
│  │                              │                                   │ │
│  └──────────────────────────────┼───────────────────────────────────┘ │
│                                 │                                     │
│  ┌──────────────────────────────▼───────────────────────────────────┐ │
│  │                    Security Group (sg-gupshup-api)                │ │
│  │                                                                   │ │
│  │  Inbound Rules:                                                  │ │
│  │  - SSH (22): Admin IP only                                       │ │
│  │  - HTTP (80): 0.0.0.0/0 (redirect to HTTPS)                     │ │
│  │  - HTTPS (443): 0.0.0.0/0                                        │ │
│  │                                                                   │ │
│  │  Outbound Rules:                                                 │ │
│  │  - All traffic: 0.0.0.0/0 (for API calls)                       │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                 │                                     │
│  ┌──────────────────────────────▼───────────────────────────────────┐ │
│  │                    EBS Volume (Elastic Block Storage)             │ │
│  │  - 20 GB gp3 (general purpose SSD)                               │ │
│  │  - Stores: Application code, MongoDB/SQLite DB, Logs             │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │              AWS Bedrock (AI/ML Services)                        │   │
│  │  ┌────────────────┐  ┌────────────────┐  ┌─────────────────┐   │   │
│  │  │ Claude 3       │  │ Amazon Polly   │  │ AWS Transcribe  │   │   │
│  │  │ (Anthropic)    │  │ (TTS)          │  │ (STT)           │   │   │
│  │  │ - LLM Analysis │  │ - Voice Synth  │  │ - Speech-to-Text│   │   │
│  │  │ - CEFR Feedback│  │                │  │                 │   │   │
│  │  └────────────────┘  └────────────────┘  └─────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                  CloudWatch (Monitoring)                         │   │
│  │  - EC2 metrics (CPU, memory, network)                           │   │
│  │  - Application logs                                              │   │
│  │  - Alarms for high CPU/memory                                    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                  Route 53 (DNS - Optional)                       │   │
│  │  - api.gupshup-cafe.com → EC2 Elastic IP                        │   │
│  │  - gupshup-cafe.com → Amplify                                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

                                    │
                                    │  Internet
                                    │
                        ┌───────────▼───────────┐
                        │   Users (Browsers)    │
                        │  - Chrome/Firefox     │
                        │  - WebRTC P2P Audio   │
                        └───────────────────────┘
```

### 4.2 Network Flow

```
┌───────────┐
│  User A   │ ─────────────────┐
└───────────┘                  │
                               ▼
┌───────────┐          ┌────────────────┐
│  User B   │ ────────►│ CloudFront CDN │
└───────────┘          │ (Amplify)      │
                       └────────┬───────┘
┌───────────┐                  │
│  User C   │ ─────────────────┘
└───────────┘
         │
         │ HTTPS/WSS (443)
         │
         ▼
┌─────────────────────┐
│ AWS EC2 Instance    │
│ (Nginx → FastAPI)   │
│                     │
│ • REST API          │
│ • WebSocket Events  │
│ • WebRTC Signaling  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  AWS Bedrock API    │
│  • Claude 3 (LLM)   │
│  • Amazon Polly     │
│  • AWS Transcribe   │
└─────────────────────┘

WebRTC Audio (P2P):
User A ◄──────────► User B  (Direct, no server relay)
User A ◄──────────► User C
User B ◄──────────► User C
```

### 4.3 Cost Estimation (MVP - 3 Months)

| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| **AWS Amplify** | Build minutes: 100 mins<br>Hosting: 5 GB storage, 15 GB data transfer | $5-10 |
| **EC2 (t3.medium)** | 1 instance, 2 vCPU, 4 GB RAM<br>730 hours/month | $30 |
| **EBS Storage** | 20 GB gp3 | $2 |
| **Data Transfer** | 50 GB/month (free tier covers first 100 GB) | $0-5 |
| **AWS Bedrock (Claude 3 Sonnet)** | ~10,000 requests/month<br>~1M input tokens, ~200K output tokens | $15-25 |
| **Amazon Polly** | 1M characters TTS | $4 |
| **AWS Transcribe** | 100 hours audio | $24 |
| **CloudWatch** | Basic monitoring + logs | $3 |
| **Route 53** (Optional) | Hosted zone + queries | $1 |
| **Total (Estimated)** | | **$84-104/month** |

**Note**: For MVP, you can reduce costs by:
- Using Gemini API (free tier) instead of Bedrock
- Using Web Speech API (browser STT/TTS) - **$0 cost**
- Using t2.micro (free tier) for first year
- **Estimated MVP cost with free services: $5-15/month**

---

## 5. Team Task Distribution & 3-Day Action Plan

### 5.1 Team Composition

| Role | Responsibilities | Key Skills |
|------|-----------------|------------|
| **Product Lead (Full-Stack + AI)** | Architecture, AI integration, coordination | FastAPI, React, LLMs, AWS |
| **Frontend Developer** | React UI, WebRTC, real-time features | React, Socket.io, WebRTC, Tailwind |
| **AI Engineer #1** | LLM integration, CEFR feedback, prompt engineering | Gemini/Bedrock, NLP, Python |
| **AI Engineer #2** | STT/TTS integration, audio processing | Speech APIs, Audio processing |
| **AWS DevOps Specialist** | Infrastructure, deployment, CI/CD | AWS (EC2, Amplify, Bedrock), Docker, Nginx |

### 5.2 Day 1: Foundation & Core Setup

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

### 5.3 Day 2: Integration & AI Features

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

### 5.4 Day 3: Polish, Testing & Production Deployment

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

---

### 5.5 Task Dependencies & Critical Path

```
DAY 1: Foundation
─────────────────────────────────────────────────────────────────
┌──────────────────┐
│ DevOps: EC2      │──┐
│ Setup            │  │
└──────────────────┘  │
                      ▼
┌──────────────────┐  ┌──────────────────┐
│ Product: AI      │─►│ AI#1: LLM        │
│ Service Layer    │  │ Implementation   │
└──────────────────┘  └──────────────────┘
         │                     │
         │                     ▼
         │            ┌──────────────────┐
         │            │ Backend: Deploy  │
         │            │ AI Endpoint      │
         │            └──────────────────┘
         ▼
┌──────────────────┐
│ Frontend: UI     │
│ Components       │
└──────────────────┘

DAY 2: Integration
─────────────────────────────────────────────────────────────────
┌──────────────────┐  ┌──────────────────┐
│ Product: DB      │─►│ Frontend: Real-  │
│ Feedback Storage │  │ time Feedback UI │
└──────────────────┘  └──────────────────┘
         │                     │
         ▼                     ▼
┌──────────────────┐  ┌──────────────────┐
│ AI#1: Context-   │  │ DevOps: Amplify  │
│ Aware Feedback   │  │ Deployment       │
└──────────────────┘  └──────────────────┘
         │
         ▼
┌──────────────────┐
│ AI#2: STT/TTS    │
│ Optimization     │
└──────────────────┘

DAY 3: Production
─────────────────────────────────────────────────────────────────
┌──────────────────┐  ┌──────────────────┐
│ Product: Bedrock │─►│ DevOps: Prod     │
│ Switch           │  │ Deployment       │
└──────────────────┘  └──────────────────┘
         │                     │
         ▼                     ▼
┌──────────────────┐  ┌──────────────────┐
│ Frontend: Polish │─►│ Team: Testing    │
│ & Testing        │  │ & Demo Prep      │
└──────────────────┘  └──────────────────┘
```

### 5.6 Communication & Standup Schedule

**Daily Standups (15 minutes at 9 AM)**
- What did I complete yesterday?
- What am I working on today?
- Any blockers?

**Mid-Day Sync (30 minutes at 2 PM)**
- Integration testing
- Resolve blockers
- Adjust priorities

**End-of-Day Review (30 minutes at 6 PM)**
- Demo progress
- Plan next day
- Update task board

**Communication Channels**
- Slack/Discord: Real-time questions
- GitHub: Code reviews, issues
- Zoom: Standups and demos

---

## 6. Risk Mitigation & Contingency Plans

### 6.1 Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **WebRTC Fails on Some Browsers** | High | Medium | Test early; Provide browser compatibility list; Use WebRTC polyfills |
| **AI API Rate Limits** | Medium | Medium | Implement caching; Add retry logic; Use fallback messages |
| **Database Performance Issues** | Medium | Low | Use SQLite for MVP (simpler); Optimize queries; Add indexes |
| **Deployment Issues** | High | Medium | DevOps starts Day 1; Use proven stack; Document setup steps |
| **Speech Recognition Inaccuracy** | Medium | High | Set user expectations; Allow manual transcript editing; Use noise filtering |

### 6.2 Timeline Risks

| Risk | Mitigation |
|------|------------|
| **Scope Creep** | Stick to Must-Have features only; Product Lead enforces priorities |
| **Blocking Dependencies** | Identify critical path early; Parallel work where possible |
| **Team Member Unavailable** | Document all work; Knowledge sharing in standups |

### 6.3 Demo Risks

| Risk | Mitigation |
|------|------------|
| **Live Demo Fails** | Record backup video demo; Have staging environment ready; Test demo script 3x |
| **Internet Connectivity Issues** | Use mobile hotspot backup; Test offline scenarios |

---

## 7. Success Metrics (MVP)

### 7.1 Technical Success Criteria

- [x] **Core Loop Works**: User can join room → speak → receive feedback
- [x] **Real-Time Communication**: WebRTC audio works for 4+ participants
- [x] **AI Feedback**: CEFR level is assigned with 80%+ accuracy
- [x] **Uptime**: Backend stays up for 24 hours without crashes
- [x] **Response Time**: AI feedback delivered within 5 seconds

### 7.2 Hackathon Demo Metrics

- [x] **Wow Factor**: Live demo of 3 users speaking and getting instant feedback
- [x] **CEFR Visualization**: Show progress chart with improving scores
- [x] **AWS Integration**: Demonstrate Bedrock usage (Claude 3)
- [x] **Scalability**: Explain how architecture scales to 100+ concurrent rooms

### 7.3 User Experience Metrics

- [x] **Onboarding**: User can join room in < 2 minutes
- [x] **Intuitive UI**: No training needed to use platform
- [x] **Feedback Quality**: Users understand feedback and can act on it
- [x] **Mobile-Friendly**: Works on phones (iOS/Android)

---

## 8. Post-Hackathon Roadmap

### Phase 2 (Week 1-2 Post-Hackathon)
- Advanced topic generation (AI-curated)
- User profiles with authentication (OAuth)
- Historical progress dashboard
- Advanced CEFR analytics (pronunciation, coherence)

### Phase 3 (Month 1-2)
- Multi-language support
- Gamification (badges, leaderboards)
- Teacher dashboard for classrooms
- Export transcripts and reports

### Phase 4 (Month 3+)
- Mobile app (React Native)
- Video support
- Recorded sessions playback
- AI-generated practice exercises

---

## 9. References & Resources

### Documentation Links
- **Main Repo**: https://github.com/navgurukul/GupShupCafe
- **Existing Docs**: https://github.com/navgurukul/GupShupCafe/tree/dev/docs
- **AWS Bedrock**: https://aws.amazon.com/bedrock/
- **Gemini API**: https://ai.google.dev/docs
- **Web Speech API**: https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API

### Technical Specs
- **CEFR Framework**: https://www.coe.int/en/web/common-european-framework-reference-languages
- **WebRTC Best Practices**: https://webrtc.org/getting-started/overview
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Socket.io Docs**: https://socket.io/docs/

### AWS Services
- **AWS Amplify Console**: https://console.aws.amazon.com/amplify/
- **EC2 Dashboard**: https://console.aws.amazon.com/ec2/
- **Bedrock Console**: https://console.aws.amazon.com/bedrock/

---

## 10. Conclusion

This MVP architecture prioritizes the **core feedback loop** that makes Gup-Shup Café unique: instant, AI-driven English speaking feedback in a gamified peer discussion. By using a pluggable AI service layer with OpenAI-compatible interfaces, we ensure flexibility to switch between Gemini (dev) and AWS Bedrock (production) seamlessly.

The 3-day plan balances ambition with realism, focusing on a working demo that showcases the innovation while ensuring the team can deliver on time. The AWS cloud architecture is cost-effective for MVP ($5-15/month with free tiers) and scalable for future growth.

**Key Takeaways:**
1. **Focus on Core Loop**: Don't get distracted by nice-to-have features
2. **Pluggable AI Design**: Flexibility to swap AI providers without code changes
3. **Clear Task Distribution**: Each team member knows their role and dependencies
4. **Risk-Aware Planning**: Contingencies for common hackathon pitfalls
5. **Demo-Ready by Day 3**: Live demo is the ultimate success metric

**Let's build something amazing! 🚀**

---

**Document Status**: ✅ Ready for Implementation  
**Last Updated**: October 2025  
**Version**: 1.0  
**Authors**: Product Team - AWS AI Agent Hackathon 2025
