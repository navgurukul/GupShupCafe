# Component Reference

## Overview

This document provides a comprehensive reference for all React components in the GupShup Cafe application. Components are organized by category: Pages, UI Components, and Layout Components.

---

## Pages

### LoginPage

**Location:** `client/src/pages/LoginPage.jsx`

**Purpose:** User authentication and onboarding page.

**Props:** None (uses Context)

**State:**
```javascript
{
  id: string,          // User ID
  name: string,        // Full name
  campus: string,      // Campus name
  location: string,    // Location
  errors: object       // Validation errors
}
```

**Features:**
- Form validation for all fields
- Anonymous name generation
- Redirect to lobby after login
- Responsive design

**Usage:**
```jsx
<Route path="/" element={<LoginPage />} />
```

**Example:**
```javascript
// Validation
const validateForm = () => {
  const newErrors = {};
  if (!id.trim()) newErrors.id = 'ID is required';
  if (!name.trim()) newErrors.name = 'Name is required';
  if (!campus.trim()) newErrors.campus = 'Campus is required';
  if (!location.trim()) newErrors.location = 'Location is required';
  return newErrors;
};
```

---

### LobbyPage

**Location:** `client/src/pages/LobbyPage.jsx`

**Purpose:** Waiting room for participants before discussion starts.

**Props:** None (uses Context)

**Context Dependencies:**
- `useAuth()` - User authentication state
- `useSocket()` - Socket connection
- `useAudio()` - Audio permissions

**State:**
```javascript
{
  participants: array,     // List of participants
  roomId: string,          // Current room ID
  isReady: boolean,        // User ready state
  audioPermission: string, // 'granted' | 'denied' | null
  selectedRole: string     // 'speaker' | 'listener'
}
```

**Features:**
- Room creation/joining
- Participant list with ready indicators
- Audio permission request
- Role selection (Speaker/Listener)
- Ready status toggle
- Automatic discussion start when all ready

**Usage:**
```jsx
<Route path="/lobby" element={
  <ProtectedRoute>
    <LobbyPage />
  </ProtectedRoute>
} />
```

**Key Functions:**
```javascript
// Join room
const joinRoom = () => {
  const roomId = generateRoomId();
  socket.emit('join-room', roomId, { role: selectedRole });
};

// Toggle ready
const handleReadyToggle = () => {
  setIsReady(!isReady);
  socket.emit('user-ready', !isReady);
};
```

---

### RoundtablePage

**Location:** `client/src/pages/RoundtablePage.jsx`

**Purpose:** Main discussion interface with circular table view.

**Props:** None (uses Context)

**Context Dependencies:**
- `useAuth()` - User information
- `useSocket()` - Real-time communication
- `useAudio()` - Audio management

**State:**
```javascript
{
  participants: array,        // Discussion participants
  currentSpeaker: object,     // Current speaker info
  topic: object,             // Discussion topic
  timeRemaining: number,     // Speaking time left
  round: number,             // Current round
  discussionActive: boolean  // Discussion status
}
```

**Features:**
- Circular table visualization
- Dynamic participant positioning
- Active speaker highlighting
- Speaking timer
- Audio controls
- Topic display
- Turn advancement

**Usage:**
```jsx
<Route path="/roundtable" element={
  <ProtectedRoute>
    <RoundtablePage />
  </ProtectedRoute>
} />
```

**Chair Positioning Algorithm:**
```javascript
const getChairPosition = (index, total, radius) => {
  const angle = (index * 360) / total - 90; // Start from top
  const angleRad = (angle * Math.PI) / 180;
  
  return {
    left: `${50 + radius * Math.cos(angleRad)}%`,
    top: `${50 + radius * Math.sin(angleRad)}%`
  };
};
```

---

### AudioTestPage

**Location:** `client/src/pages/AudioTestPage.jsx`

**Purpose:** Audio testing and debugging interface.

**Props:** None

**State:**
```javascript
{
  audioStream: MediaStream | null,  // Audio stream
  isListening: boolean             // Recording state
}
```

**Features:**
- Microphone access testing
- Live audio level visualization
- Start/stop audio test
- Permission debugging

**Usage:**
```jsx
<Route path="/audio-test" element={<AudioTestPage />} />
```

---

### BroadcastTestPage

**Location:** `client/src/pages/BroadcastTestPage.jsx`

**Purpose:** WebRTC broadcast testing.

**Props:** None

**Features:**
- Broadcaster mode
- Listener mode
- Simple audio broadcast test

---

## UI Components

### RoundtableView

**Location:** `client/src/components/RoundtableView.jsx`

**Purpose:** Circular table visualization with participant chairs.

**Props:**
```typescript
{
  participants: Array<{
    id: string,
    anonymousName: string,
    isReady?: boolean
  }>,
  currentSpeaker?: {
    id: string,
    anonymousName: string
  },
  radius?: number,  // Default: 35
  size?: string     // Default: 'medium'
}
```

**Features:**
- Responsive circular layout
- Dynamic chair positioning
- Speaker highlighting
- Visual feedback
- Smooth animations

**Usage:**
```jsx
<RoundtableView
  participants={participants}
  currentSpeaker={currentSpeaker}
  radius={35}
  size="large"
/>
```

**Styling:**
```css
.chair-active {
  @apply ring-4 ring-green-500 scale-110;
}

.chair-default {
  @apply bg-blue-500 hover:bg-blue-600;
}
```

---

### TopicDisplay

**Location:** `client/src/components/TopicDisplay.jsx`

**Purpose:** Display discussion topic with questions.

**Props:**
```typescript
{
  topic: {
    title: string,
    description: string,
    category: string,
    questions: string[]
  },
  className?: string
}
```

**Features:**
- Topic title and description
- Discussion questions list
- Category badge
- Expandable/collapsible view

**Usage:**
```jsx
<TopicDisplay
  topic={{
    title: "The Future of Education",
    description: "How will technology reshape learning?",
    category: "Education",
    questions: [
      "What role should AI play?",
      "How can we maintain human connection?"
    ]
  }}
/>
```

---

### SpeakerTimer

**Location:** `client/src/components/SpeakerTimer.jsx`

**Purpose:** Visual timer for speaker turns.

**Props:**
```typescript
{
  timeRemaining: number,    // Seconds remaining
  totalTime: number,        // Total time allocated
  isActive: boolean,        // Is timer running
  onTimeUp?: () => void     // Callback when time expires
}
```

**Features:**
- Circular progress indicator
- Color changes based on time
- Time display in MM:SS format
- Visual warnings

**Usage:**
```jsx
<SpeakerTimer
  timeRemaining={45}
  totalTime={60}
  isActive={true}
  onTimeUp={handleTimeUp}
/>
```

**Color Logic:**
```javascript
const getTimerColor = (remaining, total) => {
  const percentage = (remaining / total) * 100;
  if (percentage > 50) return 'green';
  if (percentage > 20) return 'yellow';
  return 'red';
};
```

---

### LiveAudioLevelBar

**Location:** `client/src/components/LiveAudioLevelBar.jsx`

**Purpose:** Real-time audio level visualization.

**Props:**
```typescript
{
  stream: MediaStream | null,  // Audio stream
  showLabel?: boolean,         // Show label text
  height?: number,             // Bar height
  sensitivity?: number         // Sensitivity (0-1)
}
```

**Features:**
- Real-time audio analysis
- Visual feedback bar
- Color-coded levels
- Smooth animations

**Usage:**
```jsx
<LiveAudioLevelBar
  stream={audioStream}
  showLabel={true}
  height={20}
  sensitivity={0.5}
/>
```

**Audio Analysis:**
```javascript
const analyzeAudio = (stream) => {
  const audioContext = new AudioContext();
  const analyser = audioContext.createAnalyser();
  const source = audioContext.createMediaStreamSource(stream);
  
  source.connect(analyser);
  analyser.fftSize = 256;
  
  const dataArray = new Uint8Array(analyser.frequencyBinCount);
  
  const checkLevel = () => {
    analyser.getByteFrequencyData(dataArray);
    const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
    setAudioLevel(average / 255);
    requestAnimationFrame(checkLevel);
  };
  
  checkLevel();
};
```

---

### ParticipantControls

**Location:** `client/src/components/ParticipantControls.jsx`

**Purpose:** Audio controls for participants.

**Props:**
```typescript
{
  isMuted: boolean,
  isSpeaking: boolean,
  onMuteToggle: () => void,
  onLeave?: () => void
}
```

**Features:**
- Mute/unmute button
- Speaking indicator
- Leave discussion button
- Keyboard shortcuts

**Usage:**
```jsx
<ParticipantControls
  isMuted={isMuted}
  isSpeaking={isCurrentSpeaker}
  onMuteToggle={handleMuteToggle}
  onLeave={handleLeave}
/>
```

---

### ProtectedRoute

**Location:** `client/src/components/ProtectedRoute.jsx`

**Purpose:** Route protection with authentication check.

**Props:**
```typescript
{
  children: ReactNode  // Child components
}
```

**Features:**
- Authentication check
- Automatic redirect to login
- Preserves authentication state

**Usage:**
```jsx
<Route path="/lobby" element={
  <ProtectedRoute>
    <LobbyPage />
  </ProtectedRoute>
} />
```

**Implementation:**
```javascript
export default function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/');
    }
  }, [isAuthenticated, navigate]);
  
  return isAuthenticated ? children : null;
}
```

---

## Component Patterns

### 1. Context-Based State Management

All components use React Context for global state:

```javascript
const { user, isAuthenticated } = useAuth();
const { socket, connected } = useSocket();
const { audioEnabled, isMuted } = useAudio();
```

### 2. Effect Cleanup

Proper cleanup in components:

```javascript
useEffect(() => {
  socket.on('event', handler);
  
  return () => {
    socket.off('event', handler);
  };
}, [socket]);
```

### 3. Conditional Rendering

```javascript
{isLoading ? (
  <LoadingSpinner />
) : error ? (
  <ErrorMessage error={error} />
) : (
  <MainContent data={data} />
)}
```

### 4. Event Handlers

```javascript
const handleClick = useCallback(() => {
  // Handler logic
}, [dependencies]);
```

---

## Styling Conventions

### Tailwind CSS Classes

**Buttons:**
```javascript
className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
```

**Cards:**
```javascript
className="bg-white rounded-lg shadow-lg p-6"
```

**Animations:**
```javascript
className="transition-all duration-300 transform hover:scale-105"
```

---

## Component Testing

### Manual Testing Checklist

**LoginPage:**
- [ ] Validate all fields
- [ ] Test error messages
- [ ] Test anonymous name generation
- [ ] Verify navigation to lobby

**LobbyPage:**
- [ ] Join room successfully
- [ ] Request audio permissions
- [ ] Toggle ready state
- [ ] See other participants
- [ ] Start discussion when ready

**RoundtablePage:**
- [ ] See all participants in circle
- [ ] Identify current speaker
- [ ] Timer counts down correctly
- [ ] Audio controls work
- [ ] Advance to next speaker

---

## Performance Considerations

### 1. Memoization

```javascript
const MemoizedComponent = React.memo(ExpensiveComponent);
```

### 2. Lazy Loading

```javascript
const HeavyComponent = React.lazy(() => import('./HeavyComponent'));
```

### 3. Virtual Lists (Future)

For large participant lists:

```javascript
import { FixedSizeList } from 'react-window';
```

---

## Accessibility

### ARIA Labels

```javascript
<button aria-label="Mute microphone">
  🎤
</button>
```

### Keyboard Navigation

```javascript
<button
  onClick={handleClick}
  onKeyPress={(e) => e.key === 'Enter' && handleClick()}
>
  Action
</button>
```

### Focus Management

```javascript
useEffect(() => {
  if (isVisible) {
    buttonRef.current?.focus();
  }
}, [isVisible]);
```

---

## Common Issues

### Issue: Component Not Re-rendering

**Solution:** Check dependencies in useEffect

```javascript
useEffect(() => {
  // Effect logic
}, [dependency1, dependency2]); // Include all dependencies
```

### Issue: Memory Leaks

**Solution:** Clean up listeners and timers

```javascript
useEffect(() => {
  const timer = setInterval(() => {}, 1000);
  
  return () => clearInterval(timer);
}, []);
```

### Issue: Stale Closures

**Solution:** Use functional updates

```javascript
setCount(prevCount => prevCount + 1);
```

---

## Future Components

### Planned Components

1. **ChatPanel** - Text chat interface
2. **ReactionBar** - Emoji reactions
3. **TranscriptViewer** - Discussion transcript
4. **AnalyticsDashboard** - Session analytics
5. **SettingsPanel** - User preferences

---

## Support

For component-related questions:
- Check component source code
- Review PropTypes/TypeScript definitions
- See example usage in pages
- Consult React DevTools for debugging
