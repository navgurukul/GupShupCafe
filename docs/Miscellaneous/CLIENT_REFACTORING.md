# Client Folder Structure Migration Guide

This guide shows the before and after state of the client folder refactoring to match UML architecture diagrams.

## Before Refactoring

```
client/src/
├── components/
│   ├── LiveAudioLevelBar.jsx
│   ├── ParticipantControls.jsx
│   ├── ProtectedRoute.jsx
│   ├── RoundtableView.jsx
│   ├── SpeakerTimer.jsx
│   ├── SpeechToText.jsx
│   └── TopicDisplay.jsx
├── contexts/
│   ├── AudioContext.jsx
│   ├── AuthContext.jsx
│   └── SocketContext.jsx
├── pages/
│   ├── AudioTestPage.jsx
│   ├── BroadcastTestPage.jsx
│   ├── LobbyPage.jsx
│   ├── LoginPage.jsx
│   └── RoundtablePage.jsx
├── tests/
│   ├── components/
│   ├── contexts/
│   ├── integration/
│   └── pages/
├── App.jsx
├── main.jsx
└── index.css
```

**Issues:**
- ❌ All components in single flat directory
- ❌ No service layer for API/WebRTC logic
- ❌ No utilities folder for helpers/formatters
- ❌ No type definitions
- ❌ Direct context imports in all files
- ❌ Components not following UML diagram structure

## After Refactoring

```
client/src/
├── components/
│   ├── ui/                          ✨ NEW: UI components
│   │   ├── AudioLevelBar.jsx        (renamed from LiveAudioLevelBar.jsx)
│   │   ├── ParticipantCard.jsx      ✨ NEW component
│   │   ├── RoundtableView.jsx       (refactored to use ParticipantCard)
│   │   ├── SpeakerTimer.jsx
│   │   └── TopicDisplay.jsx
│   ├── feedback/                    ✨ NEW: Feedback components
│   │   ├── EnglishFeedbackModal.jsx ✨ NEW component
│   │   └── SpeechToTextPanel.jsx    (renamed from SpeechToText.jsx)
│   ├── common/                      ✨ NEW: Common components
│   │   └── ProtectedRoute.jsx
│   └── ParticipantControls.jsx      (stays in root, specialized control)
├── contexts/
│   ├── AudioContext.jsx
│   ├── AuthContext.jsx
│   └── SocketContext.jsx
├── hooks/                           ✨ NEW: Custom hooks layer
│   ├── useAuth.js
│   ├── useSocket.js
│   ├── useAudio.js
│   └── useRoomState.js              ✨ NEW hook
├── pages/
│   ├── AudioTestPage.jsx
│   ├── BroadcastTestPage.jsx
│   ├── LobbyPage.jsx
│   ├── LoginPage.jsx
│   └── RoundtablePage.jsx
├── services/                        ✨ NEW: Service layer
│   ├── api.js                       (HTTP API calls)
│   ├── webrtc.js                    (WebRTC logic)
│   └── speech.js                    (Speech recognition)
├── types/                           ✨ NEW: Type definitions
│   ├── User.js
│   ├── Participant.js
│   ├── RoomState.js
│   ├── Feedback.js
│   └── Transcript.js
├── utils/                           ✨ NEW: Utilities
│   ├── constants.js                 (App-wide constants)
│   ├── helpers.js                   (Helper functions)
│   ├── formatters.js                (Data formatters)
│   └── validators.js                (Input validators)
├── tests/
│   ├── components/
│   ├── contexts/
│   ├── integration/
│   └── pages/
├── App.jsx
├── main.jsx
└── index.css
```

**Improvements:**
- ✅ Components organized by purpose (ui/, feedback/, common/)
- ✅ Service layer abstracts API, WebRTC, and Speech logic
- ✅ Utilities provide reusable helper functions
- ✅ Type definitions for better IDE support
- ✅ Custom hooks layer for cleaner component code
- ✅ Matches UML diagram structure exactly
- ✅ Better separation of concerns
- ✅ Easier to maintain and extend

## Import Path Changes

### Before
```javascript
// In pages/RoundtablePage.jsx
import { useAuth } from '../contexts/AuthContext'
import { useSocket } from '../contexts/SocketContext'
import RoundtableView from '../components/RoundtableView'
import SpeechToText from '../components/SpeechToText'
```

### After
```javascript
// In pages/RoundtablePage.jsx
import { useAuth } from '../hooks/useAuth'
import { useSocket } from '../hooks/useSocket'
import RoundtableView from '../components/ui/RoundtableView'
import SpeechToTextPanel from '../components/feedback/SpeechToTextPanel'
```

## Key Statistics

| Metric | Count |
|--------|-------|
| **New Folders** | 7 |
| **New Files** | 25 |
| **Renamed Files** | 2 |
| **Modified Files** | 10 |
| **Lines Added** | ~2,400 |
| **Lines Removed** | ~100 |
