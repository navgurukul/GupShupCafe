# Hooks API Reference

## Overview

This document provides detailed reference for custom React hooks used in the GupShup Cafe application.

---

## useAuth()

### Purpose

Provides access to authentication context and user management functions.

### Location

`client/src/contexts/AuthContext.jsx`

### Import

```javascript
import { useAuth } from '../contexts/AuthContext'
```

### Usage

```javascript
function MyComponent() {
  const { 
    isAuthenticated, 
    user, 
    anonymousName, 
    login, 
    logout, 
    updateProfile 
  } = useAuth()
  
  // Use authentication state and functions
}
```

### Return Value

```typescript
{
  // State
  isAuthenticated: boolean,
  user: {
    id: string,
    name: string,
    campus: string,
    location: string
  } | null,
  anonymousName: string | null,
  
  // Functions
  login: (userData: UserData, anonymousName: string) => void,
  logout: () => void,
  updateProfile: (updates: Partial<UserData>) => void
}
```

### Methods

#### login(userData, anonymousName)

Authenticates a user and stores their information.

**Parameters**:
```javascript
{
  userData: {
    id: string,      // UUID v4
    name: string,    // Full name
    campus: string,  // Campus/organization
    location: string // City/location
  },
  anonymousName: string // Display name (e.g., "Brave Lion")
}
```

**Example**:
```javascript
const userData = {
  id: uuidv4(),
  name: 'John Doe',
  campus: 'NavGurukul Bangalore',
  location: 'Bangalore'
}

login(userData, 'Brave Lion')
```

**Side Effects**:
- Sets `isAuthenticated` to `true`
- Stores data in localStorage
- Triggers re-render of dependent components

---

#### logout()

Logs out the current user and clears all authentication data.

**Parameters**: None

**Example**:
```javascript
const handleLogout = () => {
  logout()
  navigate('/')
}
```

**Side Effects**:
- Sets `isAuthenticated` to `false`
- Clears user data
- Removes data from localStorage
- Triggers re-render

---

#### updateProfile(updates)

Updates specific fields of user profile.

**Parameters**:
```javascript
{
  updates: {
    name?: string,
    campus?: string,
    location?: string
  }
}
```

**Example**:
```javascript
updateProfile({ campus: 'New Campus' })
```

**Side Effects**:
- Merges updates with existing user data
- Updates localStorage
- Triggers re-render

---

### State Persistence

- **Storage**: localStorage
- **Key**: `'auth'`
- **Format**: JSON string
- **Lifecycle**:
  - Loaded on app mount
  - Updated on state change
  - Cleared on logout

**localStorage Schema**:
```javascript
{
  user: {
    id: string,
    name: string,
    campus: string,
    location: string
  },
  anonymousName: string
}
```

---

### Error Handling

- Invalid JSON in localStorage: Clears and logs error
- Missing required fields: Falls back to unauthenticated state

---

### Usage Restrictions

⚠️ **Must be used within `AuthProvider`**

```javascript
// ❌ Wrong: Outside provider
function App() {
  const auth = useAuth() // Error!
  return <div>...</div>
}

// ✅ Correct: Inside provider
function App() {
  return (
    <AuthProvider>
      <MyComponent />
    </AuthProvider>
  )
}

function MyComponent() {
  const auth = useAuth() // Works!
}
```

---

### Example: Complete Login Flow

```javascript
function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    name: '',
    campus: '',
    location: ''
  })
  const [anonymousName, setAnonymousName] = useState('')
  
  const handleSubmit = (e) => {
    e.preventDefault()
    
    const userData = {
      id: uuidv4(),
      ...formData
    }
    
    login(userData, anonymousName)
    navigate('/lobby')
  }
  
  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
    </form>
  )
}
```

---

## useSocket()

### Purpose

Provides access to Socket.IO connection and real-time communication functions.

### Location

`client/src/contexts/SocketContext.jsx`

### Import

```javascript
import { useSocket } from '../contexts/SocketContext'
```

### Usage

```javascript
function MyComponent() {
  const { 
    socket, 
    connected, 
    joinRoom, 
    leaveRoom, 
    sendMessage, 
    signalReady, 
    requestNextSpeaker,
    changeRole 
  } = useSocket()
}
```

### Return Value

```typescript
{
  // State
  socket: Socket | null,
  connected: boolean,
  
  // Functions
  joinRoom: (roomId: string, userData?: UserData) => void,
  leaveRoom: () => void,
  sendMessage: (message: string) => void,
  signalReady: () => void,
  requestNextSpeaker: () => void,
  changeRole: (userId: string, newRole: Role, roomId?: string) => void
}
```

### Socket Instance

The raw Socket.IO client instance. Use for custom event listeners.

**Properties**:
- `socket.id`: Unique socket identifier
- `socket.connected`: Connection status
- `socket.rooms`: Set of joined rooms

**Example**:
```javascript
useEffect(() => {
  if (!socket) return
  
  socket.on('custom-event', (data) => {
    console.log('Custom event:', data)
  })
  
  return () => {
    socket.off('custom-event')
  }
}, [socket])
```

---

### Methods

#### joinRoom(roomId, userData)

Join a discussion room. Automatically leaves previous room.

**Parameters**:
```javascript
{
  roomId: string,      // Room identifier (e.g., 'general')
  userData?: {         // Optional override of handshake data
    userId: string,
    name: string,
    campus: string,
    location: string,
    anonymousName: string,
    role?: 'speaker' | 'listener'
  }
}
```

**Example**:
```javascript
useEffect(() => {
  if (connected && user) {
    joinRoom('general', {
      userId: user.id,
      name: user.name,
      campus: user.campus,
      location: user.location,
      anonymousName: anonymousName,
      role: 'listener'
    })
  }
  
  return () => {
    leaveRoom()
  }
}, [connected, user])
```

**Events Triggered**:
- Server: `join-room`
- Response: `participants-update`, `discussion-started` (if ongoing)

---

#### leaveRoom()

Leave the current room.

**Parameters**: None

**Example**:
```javascript
useEffect(() => {
  return () => {
    leaveRoom() // Cleanup on unmount
  }
}, [])
```

**Events Triggered**:
- Server: `leave-room`
- Response: `participants-update`, `user-disconnected`

---

#### sendMessage(message)

Send a chat message to current room (future feature).

**Parameters**:
```javascript
message: string
```

**Example**:
```javascript
const handleSendMessage = () => {
  sendMessage('Hello everyone!')
}
```

---

#### signalReady()

Signal that user is ready to start discussion.

**Parameters**: None

**Example**:
```javascript
const handleReady = () => {
  signalReady()
  setIsReady(true)
}
```

**Events Triggered**:
- Server: `user-ready`
- Response: `participants-update`, `discussion-started` (if conditions met)

---

#### requestNextSpeaker()

Request to advance to next speaker (for testing/manual control).

**Parameters**: None

**Example**:
```javascript
const handleNext = () => {
  requestNextSpeaker()
}
```

**Events Triggered**:
- Server: `next-speaker`
- Response: `speaker-changed`, `timer-update`

---

#### changeRole(userId, newRole, roomId)

Request role change between speaker and listener.

**Parameters**:
```javascript
{
  userId: string,
  newRole: 'speaker' | 'listener',
  roomId?: string // Optional, uses current room if omitted
}
```

**Example**:
```javascript
const handleRoleToggle = () => {
  const newRole = currentRole === 'speaker' ? 'listener' : 'speaker'
  changeRole(user.id, newRole)
}
```

**Events Triggered**:
- Server: `role-change`
- Response: `role-changed`, `role-change-success`, or `role-change-error`

---

### Connection Management

**Auto-reconnection**: Built-in Socket.IO reconnection with exponential backoff

**Example: Monitor Connection**:
```javascript
useEffect(() => {
  if (!socket) return
  
  socket.on('connect', () => {
    console.log('Connected:', socket.id)
  })
  
  socket.on('disconnect', () => {
    console.log('Disconnected')
  })
  
  socket.on('connect_error', (error) => {
    console.error('Connection error:', error)
  })
  
  return () => {
    socket.off('connect')
    socket.off('disconnect')
    socket.off('connect_error')
  }
}, [socket])
```

---

### Usage Restrictions

⚠️ **Must be used within `SocketProvider`**

⚠️ **SocketProvider must be within `AuthProvider`** (requires auth data)

---

### Example: Complete Room Join Flow

```javascript
function LobbyPage() {
  const { user, anonymousName } = useAuth()
  const { socket, connected, joinRoom } = useSocket()
  const [participants, setParticipants] = useState([])
  
  useEffect(() => {
    if (!socket || !connected || !user) return
    
    // Join room
    joinRoom('general', {
      userId: user.id,
      name: user.name,
      campus: user.campus,
      location: user.location,
      anonymousName: anonymousName
    })
    
    // Listen for updates
    socket.on('participants-update', (updatedParticipants) => {
      setParticipants(updatedParticipants)
    })
    
    // Cleanup
    return () => {
      socket.off('participants-update')
      leaveRoom()
    }
  }, [socket, connected, user])
  
  return <div>{/* Lobby UI */}</div>
}
```

---

## useAudio()

### Purpose

Manages WebRTC audio streams, peer connections, and microphone access.

### Location

`client/src/contexts/AudioContext.jsx`

### Import

```javascript
import { useAudio } from '../contexts/AudioContext'
```

### Usage

```javascript
function MyComponent() {
  const {
    audioEnabled,
    micPermission,
    localStream,
    isMuted,
    audioLevel,
    userRole,
    remoteStreams,
    isWebRTCSupported,
    requestMicrophoneAccess,
    updateUserRole,
    toggleMute,
    stopAudio,
    enableSpeaking,
    disableSpeaking,
    enableAudioPlayback
  } = useAudio()
}
```

### Return Value

```typescript
{
  // State
  audioEnabled: boolean,
  micPermission: 'granted' | 'denied' | null,
  localStream: MediaStream | null,
  isMuted: boolean,
  audioLevel: number, // 0-255
  userRole: 'speaker' | 'listener',
  remoteStreams: { [socketId: string]: MediaStream },
  isWebRTCSupported: boolean,
  
  // Functions
  requestMicrophoneAccess: () => Promise<MediaStream | null>,
  updateUserRole: (newRole: Role) => Promise<void>,
  toggleMute: () => void,
  stopAudio: () => void,
  enableSpeaking: () => Promise<void>,
  disableSpeaking: () => void,
  enableAudioPlayback: () => void
}
```

### State Properties

#### audioEnabled
- **Type**: `boolean`
- **Description**: Whether audio system is active
- **True when**: Microphone access granted and stream created

#### micPermission
- **Type**: `'granted' | 'denied' | null`
- **Description**: Browser microphone permission status
- **Values**:
  - `null`: Not requested yet
  - `'granted'`: User allowed microphone access
  - `'denied'`: User blocked microphone access

#### localStream
- **Type**: `MediaStream | null`
- **Description**: User's microphone audio stream
- **Usage**: Add to RTCPeerConnection tracks

#### isMuted
- **Type**: `boolean`
- **Description**: Whether microphone is muted
- **Note**: Only applies to speakers

#### audioLevel
- **Type**: `number` (0-255)
- **Description**: Real-time audio level from microphone
- **Usage**: Visual feedback (audio bars)

#### userRole
- **Type**: `'speaker' | 'listener'`
- **Description**: User's current role in discussion
- **Impact**:
  - Speaker: Can enable microphone, streams audio
  - Listener: Cannot enable microphone, only receives

#### remoteStreams
- **Type**: `{ [socketId: string]: MediaStream }`
- **Description**: Map of peer socket IDs to their audio streams
- **Usage**: Play remote audio from other speakers

---

### Methods

#### requestMicrophoneAccess()

Request browser permission and get microphone stream.

**Returns**: `Promise<MediaStream | null>`

**Example**:
```javascript
const handleEnableMic = async () => {
  const stream = await requestMicrophoneAccess()
  if (stream) {
    console.log('Microphone enabled')
  } else {
    alert('Microphone access denied')
  }
}
```

**Audio Constraints**:
```javascript
{
  audio: {
    echoCancellation: true,
    noiseSuppression: true,
    autoGainControl: true,
    sampleRate: 48000,
    sampleSize: 16,
    channelCount: 1,
    latency: 0.01
  }
}
```

**Side Effects**:
- Sets `micPermission`
- Sets `localStream`
- Sets `audioEnabled`
- Starts audio level monitoring

---

#### updateUserRole(newRole)

Change user's role between speaker and listener.

**Parameters**:
```javascript
newRole: 'speaker' | 'listener'
```

**Returns**: `Promise<void>`

**Example**:
```javascript
const handleRoleChange = async () => {
  await updateUserRole('speaker')
  console.log('Role updated to speaker')
}
```

**Side Effects**:
- Updates `userRole`
- If speaker: Requests microphone access
- Does NOT stop stream on demotion (listener can be promoted again)

---

#### toggleMute()

Toggle microphone mute status (speakers only).

**Parameters**: None

**Example**:
```javascript
const MuteButton = () => {
  const { isMuted, toggleMute } = useAudio()
  
  return (
    <button onClick={toggleMute}>
      {isMuted ? '🔇 Unmute' : '🔊 Mute'}
    </button>
  )
}
```

**Side Effects**:
- Toggles `isMuted`
- Enables/disables audio tracks in localStream

---

#### stopAudio()

Stop microphone stream and clean up resources.

**Parameters**: None

**Example**:
```javascript
useEffect(() => {
  return () => {
    stopAudio() // Cleanup on unmount
  }
}, [])
```

**Side Effects**:
- Stops all tracks in localStream
- Clears localStream
- Sets audioEnabled to false
- Sets isMuted to true

---

#### enableSpeaking()

Convenience method to enable microphone and unmute (for speakers).

**Returns**: `Promise<void>`

**Example**:
```javascript
const handleStartSpeaking = async () => {
  await enableSpeaking()
  console.log('Ready to speak')
}
```

**Side Effects**:
- Requests microphone if not already active
- Updates role to speaker
- Unmutes if muted

---

#### disableSpeaking()

Convenience method to mute microphone (but keep stream active).

**Parameters**: None

**Example**:
```javascript
const handleStopSpeaking = () => {
  disableSpeaking()
}
```

**Side Effects**:
- Mutes microphone if unmuted

---

#### enableAudioPlayback()

Manually enable audio playback (required for autoplay policies).

**Parameters**: None

**Example**:
```javascript
const handleUserInteraction = () => {
  enableAudioPlayback()
  // Now remote audio streams will play
}
```

**Usage**: Call on user interaction to bypass browser autoplay restrictions

---

### WebRTC Peer Connection

The AudioContext handles WebRTC peer connections automatically when used with SocketContext.

**Flow**:
```
1. User joins room
2. Socket emits 'ready-for-webrtc'
3. Server sends 'participants-update'
4. AudioContext creates RTCPeerConnection for each peer
5. Exchanges offers/answers via Socket.IO
6. Exchanges ICE candidates
7. P2P audio connection established
```

**Example: Listen for Remote Streams**:
```javascript
const { remoteStreams } = useAudio()

useEffect(() => {
  Object.entries(remoteStreams).forEach(([socketId, stream]) => {
    console.log(`Remote stream from ${socketId}:`, stream)
    // Play audio or visualize
  })
}, [remoteStreams])
```

---

### Audio Level Monitoring

**Setup**: Automatically started when microphone is accessed

**Implementation**:
```javascript
const audioContext = new AudioContext()
const analyser = audioContext.createAnalyser()
const microphone = audioContext.createMediaStreamSource(stream)

microphone.connect(analyser)
analyser.fftSize = 256

// requestAnimationFrame loop updates audioLevel
```

**Usage Example**:
```javascript
const AudioLevelBar = () => {
  const { audioLevel, isMuted } = useAudio()
  
  const width = (audioLevel / 255) * 100
  
  return (
    <div className="audio-bar-container">
      <div 
        className="audio-bar" 
        style={{ 
          width: `${width}%`,
          backgroundColor: isMuted ? 'gray' : 'green'
        }} 
      />
    </div>
  )
}
```

---

### Browser Compatibility

**WebRTC Support**:
- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support (with minor quirks)
- Mobile browsers: ✅ Most support (may require HTTPS)

**Check Support**:
```javascript
const { isWebRTCSupported } = useAudio()

if (!isWebRTCSupported) {
  return <div>Your browser doesn't support WebRTC audio</div>
}
```

---

### Usage Restrictions

⚠️ **Must be used within `AudioProvider`**

⚠️ **AudioProvider must be within `SocketProvider` and `AuthProvider`**

⚠️ **Microphone access requires HTTPS in production**

---

### Example: Complete Audio Setup

```javascript
function RoundtablePage() {
  const { userRole } = useAudio()
  const { socket } = useSocket()
  const [currentSpeaker, setCurrentSpeaker] = useState(null)
  
  useEffect(() => {
    if (!socket) return
    
    // Listen for speaker changes
    socket.on('speaker-changed', ({ speaker }) => {
      setCurrentSpeaker(speaker)
    })
    
    return () => {
      socket.off('speaker-changed')
    }
  }, [socket])
  
  // Automatically update role based on current speaker
  useEffect(() => {
    if (currentSpeaker && currentSpeaker.id === user.id) {
      updateUserRole('speaker')
    } else {
      updateUserRole('listener')
    }
  }, [currentSpeaker])
  
  return (
    <div>
      <p>Your role: {userRole}</p>
      {/* Audio controls */}
    </div>
  )
}
```

---

## Best Practices

### General Hook Usage

1. **Always check dependencies**: Ensure hooks have loaded before using their values
   ```javascript
   useEffect(() => {
     if (!socket || !connected) return
     // Use socket
   }, [socket, connected])
   ```

2. **Clean up listeners**: Remove event listeners on unmount
   ```javascript
   useEffect(() => {
     socket?.on('event', handler)
     return () => {
       socket?.off('event', handler)
     }
   }, [socket])
   ```

3. **Handle loading states**: Show loading UI while hooks initialize
   ```javascript
   if (!socket || !user) {
     return <Loading />
   }
   ```

4. **Error boundaries**: Wrap components using hooks in error boundaries

5. **Type safety**: Consider TypeScript for better type checking

---

### Common Patterns

#### Protected Component
```javascript
function ProtectedComponent() {
  const { isAuthenticated } = useAuth()
  const navigate = useNavigate()
  
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/')
    }
  }, [isAuthenticated, navigate])
  
  return <div>{/* Protected content */}</div>
}
```

#### Real-time Data Sync
```javascript
function DataComponent() {
  const { socket } = useSocket()
  const [data, setData] = useState([])
  
  useEffect(() => {
    if (!socket) return
    
    socket.on('data-update', setData)
    socket.emit('request-data')
    
    return () => {
      socket.off('data-update')
    }
  }, [socket])
  
  return <div>{/* Render data */}</div>
}
```

#### Audio Control
```javascript
function AudioControls() {
  const { 
    isMuted, 
    toggleMute, 
    audioLevel, 
    userRole 
  } = useAudio()
  
  if (userRole !== 'speaker') {
    return <div>Listening mode</div>
  }
  
  return (
    <div>
      <button onClick={toggleMute}>
        {isMuted ? 'Unmute' : 'Mute'}
      </button>
      <AudioLevelBar level={audioLevel} />
    </div>
  )
}
```
