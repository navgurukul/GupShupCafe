# Client Components Reference

## Overview

This document provides a comprehensive reference for all React components in the GupShup Cafe frontend application.

---

## Page Components

### LoginPage

**Location**: `client/src/pages/LoginPage.jsx`

**Purpose**: User authentication and onboarding page

**Features**:
- User information collection (name, campus, location)
- Anonymous name generation and selection
- Form validation
- Redirection to lobby after login

**State**:
```javascript
{
  name: string,
  campus: string,
  location: string,
  anonymousName: string,
  errors: object,
  suggestedNames: string[]
}
```

**Props**: None (top-level page)

**Hooks Used**:
- `useAuth()`: Access authentication context
- `useNavigate()`: Programmatic navigation
- `useState()`: Local state management
- `useEffect()`: Generate suggested names on mount

**Key Functions**:
- `generateAnonymousName()`: Create random animal-adjective combinations
- `validateForm()`: Validate user inputs
- `handleSubmit()`: Process login and save to context

**Navigation**:
- Redirects to `/lobby` on successful login
- Checks authentication state and redirects if already logged in

---

### LobbyPage

**Location**: `client/src/pages/LobbyPage.jsx`

**Purpose**: Pre-discussion lobby where users wait for others and signal readiness

**Features**:
- Display participant list
- Show ready status for each participant
- Allow user to signal ready
- Display minimum participant requirement
- Audio permission request
- Automatic transition to roundtable when discussion starts

**State**:
```javascript
{
  participants: Participant[],
  isReady: boolean,
  canStartDiscussion: boolean
}
```

**Props**: None (top-level page)

**Hooks Used**:
- `useAuth()`: Get user information
- `useSocket()`: Real-time communication
- `useAudio()`: Microphone access
- `useNavigate()`: Navigation to roundtable
- `useState()`: Local state
- `useEffect()`: Join room, listen for events

**Socket Events**:
- **Emits**:
  - `join-room`: On mount
  - `user-ready`: When user clicks ready
  - `leave-room`: On unmount
- **Listens**:
  - `participants-update`: Update participant list
  - `discussion-started`: Navigate to roundtable

**Key Functions**:
- `handleReady()`: Signal ready status
- `handleAudioPermission()`: Request microphone access

**Navigation**:
- From `/` after login
- To `/roundtable` when discussion starts

---

### RoundtablePage

**Location**: `client/src/pages/RoundtablePage.jsx`

**Purpose**: Main discussion interface with visual roundtable and audio controls

**Features**:
- Circular seating arrangement visualization
- Current speaker highlighting
- Speaking timer display
- Topic display
- Round counter
- Audio level indicators
- Mute/unmute controls
- Next speaker button (for testing)
- Discussion completion handling

**State**:
```javascript
{
  topic: Topic | null,
  currentSpeaker: Participant | null,
  timeRemaining: number,
  round: number,
  discussionActive: boolean,
  participants: Participant[]
}
```

**Props**: None (top-level page)

**Hooks Used**:
- `useAuth()`: User information
- `useSocket()`: Real-time updates
- `useAudio()`: Audio management
- `useNavigate()`: Navigation after discussion
- `useState()`: Local state
- `useEffect()`: Socket event listeners

**Socket Events**:
- **Listens**:
  - `discussion-started`: Initialize discussion state
  - `speaker-changed`: Update current speaker
  - `timer-update`: Update countdown
  - `discussion-ended`: Navigate back to lobby
  - `participants-update`: Update participant list

**Components Used**:
- `RoundtableView`: Visual representation
- `TopicDisplay`: Show discussion topic
- `SpeakerTimer`: Countdown timer
- `ParticipantControls`: Audio controls

**Key Functions**:
- `handleNextSpeaker()`: Request next speaker (testing)
- `handleDiscussionEnd()`: Navigate to lobby after discussion

**Navigation**:
- From `/lobby` when discussion starts
- To `/lobby` when discussion ends

---

### AudioTestPage

**Location**: `client/src/pages/AudioTestPage.jsx`

**Purpose**: Debugging and testing audio functionality

**Features**:
- Microphone permission testing
- Audio level visualization
- Mute/unmute testing
- Browser compatibility check

**State**:
```javascript
{
  audioLevel: number,
  isMuted: boolean,
  micPermission: string
}
```

**Props**: None (development/testing page)

**Hooks Used**:
- `useAudio()`: All audio functionality
- `useState()`: Local state
- `useEffect()`: Setup audio monitoring

---

### BroadcastTestPage

**Location**: `client/src/pages/BroadcastTestPage.jsx`

**Purpose**: Test WebRTC broadcasting with one broadcaster and multiple listeners

**Features**:
- First user becomes broadcaster
- Subsequent users become listeners
- Real-time peer connection setup
- Audio streaming test

**State**:
```javascript
{
  role: 'broadcaster' | 'listener' | null,
  participants: Participant[],
  localStream: MediaStream | null,
  remoteStreams: Map<string, MediaStream>
}
```

**Props**: None (development/testing page)

**Hooks Used**:
- `useSocket()`: WebRTC signaling
- `useState()`: Local state
- `useEffect()`: Connection setup

**Socket Events**:
- **Emits**: `join-broadcast-test`, `webrtc-offer`, `webrtc-answer`, `webrtc-ice-candidate`
- **Listens**: `broadcast-test-role`, `broadcast-test-participants`, WebRTC signaling events

---

## Reusable UI Components

### RoundtableView

**Location**: `client/src/components/RoundtableView.jsx`

**Purpose**: Visual circular arrangement of participants in discussion

**Props**:
```javascript
{
  participants: Participant[], // Required
  currentSpeaker: Participant | null, // Required
  audioLevels: Map<string, number> // Optional
}
```

**Features**:
- Circular positioning calculation using trigonometry
- Current speaker highlighting (border, glow)
- Visual audio level indicators
- Responsive layout
- Smooth animations

**Styling**:
- Uses Tailwind CSS utilities
- Custom CSS for circular positioning
- Conditional styling for active speaker

**Layout Algorithm**:
```javascript
// Position calculation for N participants
const angle = (index * 360) / participants.length
const x = Math.cos(angleInRadians) * radius
const y = Math.sin(angleInRadians) * radius
```

---

### TopicDisplay

**Location**: `client/src/components/TopicDisplay.jsx`

**Purpose**: Display the current discussion topic with questions

**Props**:
```javascript
{
  topic: {
    title: string,
    description: string,
    category: string,
    questions: string[]
  } | null
}
```

**Features**:
- Expandable/collapsible question list
- Category badge
- Animated transitions
- Loading state

**State**:
```javascript
{
  isExpanded: boolean
}
```

**Styling**:
- Card-based layout
- Gradient background
- Smooth expand/collapse animation

---

### SpeakerTimer

**Location**: `client/src/components/SpeakerTimer.jsx`

**Purpose**: Display countdown timer for current speaker

**Props**:
```javascript
{
  timeRemaining: number, // seconds
  speakingTime: number, // total seconds
  currentSpeaker: Participant | null
}
```

**Features**:
- Circular progress bar
- Color coding (green → yellow → red)
- Percentage display
- Current speaker name

**Visual States**:
- Green: > 50% time remaining
- Yellow: 25-50% time remaining
- Red: < 25% time remaining
- Pulsing animation when time is low

**Styling**:
- SVG-based circular progress
- Smooth transitions
- Responsive sizing

---

### ParticipantControls

**Location**: `client/src/components/ParticipantControls.jsx`

**Purpose**: Audio controls for participants (mute/unmute)

**Props**:
```javascript
{
  isMuted: boolean,
  audioEnabled: boolean,
  onToggleMute: () => void,
  currentUser: Participant,
  userRole: 'speaker' | 'listener'
}
```

**Features**:
- Mute/unmute button
- Visual feedback (icon changes)
- Disabled state for listeners
- Tooltip/hint text

**Styling**:
- Icon-based buttons
- Color coding (red for muted, green for unmuted)
- Disabled state styling

---

### LiveAudioLevelBar

**Location**: `client/src/components/LiveAudioLevelBar.jsx`

**Purpose**: Real-time audio level visualization

**Props**:
```javascript
{
  audioLevel: number, // 0-255
  isMuted: boolean,
  height: number, // optional, default: 4
  className: string // optional
}
```

**Features**:
- Real-time audio level display
- Smooth animations
- Muted state indicator
- Customizable height

**Visualization**:
- Horizontal bar graph
- Green color gradient
- Width based on audio level
- Gray when muted

**Update Frequency**: Updates on every `requestAnimationFrame` tick

---

### ProtectedRoute

**Location**: `client/src/components/ProtectedRoute.jsx`

**Purpose**: Route wrapper that requires authentication

**Props**:
```javascript
{
  children: ReactNode
}
```

**Features**:
- Check authentication state
- Redirect to login if not authenticated
- Render children if authenticated

**Usage**:
```javascript
<Route path="/lobby" element={
  <ProtectedRoute>
    <LobbyPage />
  </ProtectedRoute>
} />
```

**Hooks Used**:
- `useAuth()`: Check authentication
- `Navigate`: Redirect component

---

## Component Hierarchy

```
App.jsx
├── AuthProvider
│   ├── SocketProvider
│   │   ├── AudioProvider
│   │   │   ├── Router
│   │   │   │   ├── LoginPage
│   │   │   │   ├── ProtectedRoute
│   │   │   │   │   ├── LobbyPage
│   │   │   │   │   └── RoundtablePage
│   │   │   │   │       ├── RoundtableView
│   │   │   │   │       ├── TopicDisplay
│   │   │   │   │       ├── SpeakerTimer
│   │   │   │   │       └── ParticipantControls
│   │   │   │   │           └── LiveAudioLevelBar
│   │   │   │   ├── AudioTestPage
│   │   │   │   │   └── LiveAudioLevelBar
│   │   │   │   └── BroadcastTestPage
```

---

## Common Props Patterns

### Participant Object
```javascript
{
  id: string,
  anonymousName: string,
  isReady: boolean,
  joinedAt: string, // ISO timestamp
  socketId: string,
  role: 'speaker' | 'listener'
}
```

### Topic Object
```javascript
{
  title: string,
  description: string,
  category: string,
  questions: string[],
  source: 'AI Generated' | 'fallback'
}
```

---

## Styling Conventions

### Tailwind CSS Classes
- Consistent spacing: `p-4`, `m-2`, `gap-4`
- Responsive: `md:`, `lg:` prefixes
- Colors: Custom palette in `tailwind.config.js`
- Animations: `transition-all`, `duration-300`

### Component-Specific Styles
- Inline styles for dynamic positioning (RoundtableView)
- SVG for complex graphics (SpeakerTimer)
- CSS modules not used (Tailwind preferred)

---

## Accessibility Considerations

### Current Implementation
- Semantic HTML elements
- Button elements for clickable actions
- Alt text for icons (where applicable)

### Recommended Improvements
- ARIA labels for icons
- Keyboard navigation
- Focus management
- Screen reader support
- Color contrast validation

---

## Performance Optimization

### React Optimization
- Functional components (faster than class components)
- useCallback for event handlers (future)
- useMemo for expensive computations (future)
- React.memo for pure components (future)

### Rendering Optimization
- Conditional rendering to minimize DOM updates
- CSS transitions over JavaScript animations
- RequestAnimationFrame for smooth audio visualization

---

## Testing Strategy (Recommended)

### Unit Tests
```javascript
// ParticipantControls.test.jsx
describe('ParticipantControls', () => {
  it('renders mute button', () => {
    render(<ParticipantControls {...props} />)
    expect(screen.getByRole('button')).toBeInTheDocument()
  })
})
```

### Integration Tests
```javascript
// LobbyPage.test.jsx
describe('LobbyPage', () => {
  it('joins room on mount', () => {
    const mockJoinRoom = jest.fn()
    render(<LobbyPage />)
    expect(mockJoinRoom).toHaveBeenCalledWith('general')
  })
})
```

### E2E Tests
```javascript
// discussion-flow.spec.js
test('complete discussion flow', async ({ page }) => {
  await page.goto('/login')
  await page.fill('input[name="name"]', 'Test User')
  await page.click('button[type="submit"]')
  await expect(page).toHaveURL('/lobby')
})
```
