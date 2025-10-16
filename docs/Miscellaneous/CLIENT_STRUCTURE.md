# Client Folder Structure

This document describes the organization of the `client/src` folder, which follows the architecture defined in the UML diagrams (`docs/diagrams/plan/uml/04-class-diagram-frontend.puml` and `13-package-diagram-frontend.puml`).

## Folder Structure

```
client/src/
├── components/           # React components
│   ├── ui/              # User interface components
│   ├── feedback/        # Feedback-related components
│   └── common/          # Common/shared components
├── contexts/            # React Context providers
├── hooks/               # Custom React hooks
├── pages/               # Page-level components
├── services/            # API and service layer
├── types/               # Type definitions (JSDoc)
├── utils/               # Utility functions
├── tests/               # Test files
├── App.jsx              # Root application component
├── main.jsx             # Application entry point
└── index.css            # Global styles
```

## Component Organization

### `components/ui/`
UI components for the roundtable discussion interface:
- **RoundtableView.jsx**: Main roundtable visualization with circular participant layout
- **ParticipantCard.jsx**: Individual participant card with avatar, status, and audio level
- **SpeakerTimer.jsx**: Timer display for speaker time limits
- **TopicDisplay.jsx**: Discussion topic display component
- **AudioLevelBar.jsx**: Audio level visualization bar

### `components/feedback/`
Components related to feedback and transcription:
- **EnglishFeedbackModal.jsx**: Modal for displaying English language feedback
  - CEFR level badge
  - Grammar corrections
  - Vocabulary, fluency, and grammar scores
- **SpeechToTextPanel.jsx**: Live speech-to-text transcription panel

### `components/common/`
Shared/utility components:
- **ProtectedRoute.jsx**: Authentication guard for protected routes

## Contexts

### `contexts/`
React Context providers for global state management:
- **AuthContext.jsx**: User authentication and profile management
  - Login/logout functionality
  - User profile updates
  - Persistent authentication via localStorage
- **SocketContext.jsx**: Socket.io connection management
  - Real-time event handling
  - Room joining/leaving
  - Message broadcasting
- **AudioContext.jsx**: WebRTC audio management
  - Microphone access and permissions
  - Peer-to-peer audio connections
  - Mute/unmute functionality
  - Audio level monitoring

## Custom Hooks

### `hooks/`
Custom React hooks for accessing context and managing state:
- **useAuth.js**: Access authentication context
- **useSocket.js**: Access socket connection
- **useAudio.js**: Access audio/WebRTC functionality
- **useRoomState.js**: Manage room state (participants, speaker, metadata)

## Pages

### `pages/`
Page-level components representing different routes:
- **LoginPage.jsx**: User login and authentication
- **LobbyPage.jsx**: Room creation and joining
- **RoundtablePage.jsx**: Main discussion interface
- **AudioTestPage.jsx**: Microphone and audio testing
- **BroadcastTestPage.jsx**: WebRTC broadcast testing

## Services

### `services/`
Service layer for API calls and external integrations:

#### **api.js**
HTTP API service for backend communication:
- `get(endpoint, options)` - Generic GET request
- `post(endpoint, data, options)` - Generic POST request
- `fetchTopics()` - Get discussion topics
- `fetchAnalytics(userId)` - Get user analytics
- `createRoom(roomConfig)` - Create new discussion room
- `fetchActiveRooms()` - Get list of active rooms

#### **webrtc.js**
WebRTC service for peer-to-peer audio:
- `createPeerConnection(localStream)` - Create RTCPeerConnection
- `createOffer(peerConnection)` - Create SDP offer
- `handleOffer(peerConnection, offer)` - Handle incoming offer
- `handleAnswer(peerConnection, answer)` - Handle SDP answer
- `handleICECandidate(peerConnection, candidate)` - Handle ICE candidate
- `closePeerConnection(peerConnection)` - Cleanup connection

#### **speech.js**
Speech recognition service (Web Speech API wrapper):
- `isSupported()` - Check browser support
- `createRecognition(options)` - Create speech recognition instance
- `startRecognition(recognition, callbacks)` - Start listening
- `stopRecognition(recognition)` - Stop listening
- `detectLanguage()` - Auto-detect browser language

## Types

### `types/`
Type definitions using JSDoc for better IDE support:
- **User.js**: User profile type
- **Participant.js**: Discussion participant type
- **RoomState.js**: Room state and metadata type
- **Feedback.js**: English feedback and issue types
- **Transcript.js**: Speech transcript type

## Utilities

### `utils/`
Utility functions organized by category:

#### **constants.js**
Application-wide constants:
- API configuration (URLs, timeouts)
- Discussion settings (participant limits, speaking time)
- WebRTC configuration (STUN servers)
- Audio settings (sample rate, codecs)
- User roles and room status
- CEFR levels and feedback thresholds
- Socket event names
- UI configuration (timers, animations)
- Error and success messages

#### **helpers.js**
General helper functions:
- `generateRoomCode()` - Random room code generator
- `generateAnonymousName()` - Random name generator
- `generateAvatarColor()` - Random avatar color
- `debounce()`, `throttle()` - Function throttling
- `deepClone()` - Deep object cloning
- `isEmpty()` - Check if object/array is empty
- `getInitials()` - Extract initials from name
- `capitalize()`, `truncate()` - String manipulation

#### **formatters.js**
Data formatting functions:
- `formatTime(seconds)` - Format time as MM:SS
- `formatDate(date)`, `formatDateTime(date)` - Date formatting
- `formatRelativeTime(date)` - "2 hours ago" format
- `formatNumber(num)` - Number with commas
- `formatPercentage(value)` - Percentage formatting
- `formatCEFRLevel(level)` - CEFR level with name
- `formatDuration(seconds)` - Human-readable duration
- `formatFileSize(bytes)` - File size formatting
- `formatScore(score)` - Score with color coding

#### **validators.js**
Input validation functions:
- `isValidEmail(email)` - Email validation
- `isValidRoomCode(code)` - Room code format check
- `validateUsername(username)` - Username validation
- `validatePassword(password)` - Password strength check
- `isValidURL(url)` - URL validation
- `isValidCEFRLevel(level)` - CEFR level check
- `validateSpeakingTime(seconds)` - Speaking time validation
- `validateParticipantCount(count)` - Participant count check
- `sanitizeInput(input)` - XSS prevention

## Import Patterns

### Before Refactoring
```javascript
import { useAuth } from '../contexts/AuthContext'
import RoundtableView from '../components/RoundtableView'
```

### After Refactoring
```javascript
import { useAuth } from '../hooks/useAuth'
import RoundtableView from '../components/ui/RoundtableView'
```

## Architecture Patterns

### 1. Context + Hooks Pattern
Global state is managed via Context API and accessed through custom hooks:
```javascript
// In component
import { useAuth } from '../hooks/useAuth'

function MyComponent() {
  const { user, login, logout } = useAuth()
  // ...
}
```

### 2. Service Layer Pattern
API calls and external integrations are abstracted into service modules:
```javascript
import { fetchTopics, createRoom } from '../services/api'

const topics = await fetchTopics()
const room = await createRoom({ topic, maxParticipants })
```

### 3. Component Composition
Complex components are broken down into smaller, reusable pieces:
```javascript
// RoundtableView uses ParticipantCard
<RoundtableView participants={participants}>
  {participants.map(p => (
    <ParticipantCard key={p.id} participant={p} />
  ))}
</RoundtableView>
```

### 4. Type Safety via JSDoc
Type definitions provide IDE support without TypeScript:
```javascript
/**
 * @typedef {import('../types/User').User} User
 * @param {User} user - User object
 */
function updateProfile(user) {
  // TypeScript-like type checking
}
```

## Testing Structure

Tests mirror the component structure:
```
tests/
├── components/
│   ├── AudioLevelBar.test.jsx
│   ├── ProtectedRoute.test.jsx
│   └── SpeakerTimer.test.jsx
├── contexts/
│   ├── AuthContext.test.jsx
│   └── AudioContext.test.jsx
├── pages/
│   └── LoginPage.test.jsx
├── integration/
│   └── LoginFlow.test.jsx
├── test-utils.jsx
└── setup.js
```

## Development Workflow

### Adding a New Component
1. Create component file in appropriate subfolder (`ui/`, `feedback/`, `common/`)
2. Add JSDoc type definitions if needed
3. Export component as default
4. Create corresponding test file
5. Update this README if it introduces new patterns

### Adding a New Service
1. Create service file in `services/`
2. Export functions as named exports
3. Add JSDoc documentation
4. Update constants if needed
5. Create unit tests

### Adding a New Utility
1. Choose appropriate utility file (`helpers.js`, `formatters.js`, `validators.js`)
2. Add function with JSDoc
3. Export as named export
4. Add unit tests
5. Update constants if adding new configuration

## Build and Development

```bash
# Install dependencies
npm install

# Development server
npm run dev

# Linting
npm run lint

# Tests
npm run test

# Build for production
npm run build
```

## Code Style

- Use functional components with hooks
- Prefer named exports for utilities and services
- Use default exports for components
- Add JSDoc comments for public APIs
- Follow existing naming conventions
- Keep components focused and single-purpose
- Extract reusable logic into custom hooks
- Use constants for magic numbers and strings

## Future Improvements

- [ ] Migrate to TypeScript for better type safety
- [ ] Add Storybook for component documentation
- [ ] Implement lazy loading for routes
- [ ] Add code splitting for better performance
- [ ] Create integration tests for critical flows
- [ ] Add E2E tests with Playwright
- [ ] Implement proper error boundaries
- [ ] Add loading states and skeletons
- [ ] Improve accessibility (ARIA labels, keyboard navigation)
