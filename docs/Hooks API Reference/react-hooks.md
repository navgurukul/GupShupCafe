# Hooks API Reference

## Overview

This document provides a comprehensive reference for all custom React hooks in the GupShup Cafe application. These hooks manage authentication, real-time communication, and audio functionality through React Context API.

---

## Context Hooks

### useAuth

**Location:** `client/src/contexts/AuthContext.jsx`

**Purpose:** Manage user authentication and session state.

**Import:**
```javascript
import { useAuth } from './contexts/AuthContext';
```

**API:**

```typescript
interface UseAuthReturn {
  user: User | null;
  anonymousName: string | null;
  isAuthenticated: boolean;
  login: (userData: UserData) => void;
  logout: () => void;
}

interface User {
  id: string;
  name: string;
  campus: string;
  location: string;
}

interface UserData extends User {
  anonymousName?: string;
}
```

**Usage Example:**

```javascript
function LoginPage() {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  
  const handleLogin = (formData) => {
    login({
      id: formData.id,
      name: formData.name,
      campus: formData.campus,
      location: formData.location
    });
    
    navigate('/lobby');
  };
  
  if (isAuthenticated) {
    return <Navigate to="/lobby" />;
  }
  
  return <LoginForm onSubmit={handleLogin} />;
}
```

**Properties:**

#### `user: User | null`

Current authenticated user object or null if not logged in.

```javascript
const { user } = useAuth();

if (user) {
  console.log('User ID:', user.id);
  console.log('Name:', user.name);
  console.log('Campus:', user.campus);
  console.log('Location:', user.location);
}
```

#### `anonymousName: string | null`

Generated anonymous name for discussions (e.g., "Wise Owl").

```javascript
const { anonymousName } = useAuth();

// Display anonymous name in discussion
<div className="participant-name">{anonymousName}</div>
```

#### `isAuthenticated: boolean`

Boolean indicating if user is logged in.

```javascript
const { isAuthenticated } = useAuth();

// Protect routes
if (!isAuthenticated) {
  return <Navigate to="/" />;
}
```

**Methods:**

#### `login(userData: UserData): void`

Authenticate user and store session.

```javascript
const { login } = useAuth();

const handleLogin = () => {
  const anonymousName = generateAnonymousName();
  
  login({
    id: 'user-123',
    name: 'John Doe',
    campus: 'Delhi Campus',
    location: 'India',
    anonymousName: anonymousName
  });
};
```

**Storage:**
- User data stored in localStorage
- Key: `'user'`
- Persists across browser sessions

#### `logout(): void`

Clear user session and authentication state.

```javascript
const { logout } = useAuth();

const handleLogout = () => {
  logout();
  navigate('/');
};
```

**Implementation Details:**

```javascript
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [anonymousName, setAnonymousName] = useState(null);
  
  useEffect(() => {
    // Load from localStorage on mount
    const savedUser = localStorage.getItem('user');
    const savedAnonymousName = localStorage.getItem('anonymousName');
    
    if (savedUser) {
      setUser(JSON.parse(savedUser));
      setAnonymousName(savedAnonymousName);
    }
  }, []);
  
  const login = (userData) => {
    const name = userData.anonymousName || generateAnonymousName();
    
    setUser(userData);
    setAnonymousName(name);
    
    localStorage.setItem('user', JSON.stringify(userData));
    localStorage.setItem('anonymousName', name);
  };
  
  const logout = () => {
    setUser(null);
    setAnonymousName(null);
    
    localStorage.removeItem('user');
    localStorage.removeItem('anonymousName');
  };
  
  return (
    <AuthContext.Provider value={{
      user,
      anonymousName,
      isAuthenticated: !!user,
      login,
      logout
    }}>
      {children}
    </AuthContext.Provider>
  );
}
```

---

### useSocket

**Location:** `client/src/contexts/SocketContext.jsx`

**Purpose:** Manage Socket.io connection and real-time communication.

**Import:**
```javascript
import { useSocket } from './contexts/SocketContext';
```

**API:**

```typescript
interface UseSocketReturn {
  socket: Socket | null;
  connected: boolean;
  joinRoom: (roomId: string, options?: JoinOptions) => void;
  leaveRoom: () => void;
  getCurrentRoom: () => string | null;
  getSelectedRole: () => string | null;
}

interface JoinOptions {
  role: 'speaker' | 'listener';
}
```

**Usage Example:**

```javascript
function LobbyPage() {
  const { socket, connected, joinRoom } = useSocket();
  const [participants, setParticipants] = useState([]);
  
  useEffect(() => {
    if (!socket || !connected) return;
    
    // Join a room
    const roomId = `room-${Date.now()}`;
    joinRoom(roomId, { role: 'speaker' });
    
    // Listen for participants update
    socket.on('participants-update', (updatedParticipants) => {
      setParticipants(updatedParticipants);
    });
    
    return () => {
      socket.off('participants-update');
    };
  }, [socket, connected]);
  
  return <ParticipantList participants={participants} />;
}
```

**Properties:**

#### `socket: Socket | null`

Socket.io client instance or null if not connected.

```javascript
const { socket } = useSocket();

if (socket) {
  socket.emit('custom-event', data);
  
  socket.on('server-event', (data) => {
    console.log('Received:', data);
  });
}
```

#### `connected: boolean`

Connection status indicator.

```javascript
const { connected } = useSocket();

return (
  <div>
    Status: {connected ? '🟢 Connected' : '🔴 Disconnected'}
  </div>
);
```

**Methods:**

#### `joinRoom(roomId: string, options?: JoinOptions): void`

Join a discussion room.

```javascript
const { joinRoom } = useSocket();

const handleJoinRoom = () => {
  const roomId = generateRoomId();
  joinRoom(roomId, { role: 'speaker' });
};
```

#### `leaveRoom(): void`

Leave the current room.

```javascript
const { leaveRoom } = useSocket();

const handleLeaveRoom = () => {
  leaveRoom();
  navigate('/lobby');
};
```

#### `getCurrentRoom(): string | null`

Get current room ID.

```javascript
const { getCurrentRoom } = useSocket();

const roomId = getCurrentRoom();
console.log('Current room:', roomId);
```

#### `getSelectedRole(): string | null`

Get user's selected role in the room.

```javascript
const { getSelectedRole } = useSocket();

const role = getSelectedRole();
console.log('Role:', role); // 'speaker' or 'listener'
```

**Connection Configuration:**

```javascript
// Socket.io connection options
const socketOptions = {
  auth: {
    userId: user.id,
    name: user.name,
    campus: user.campus,
    location: user.location,
    anonymousName: anonymousName
  },
  transports: ['websocket', 'polling'],
  reconnection: true,
  reconnectionAttempts: 10,
  reconnectionDelay: 1000,
  autoConnect: true
};
```

**Auto-Reconnection:**

The socket automatically reconnects and rejoins the room:

```javascript
socket.on('connect', () => {
  console.log('Connected:', socket.id);
  
  // Rejoin room if was in one
  if (currentRoom && selectedRole) {
    socket.emit('join-room', currentRoom, { role: selectedRole });
  }
});
```

---

### useAudio

**Location:** `client/src/contexts/AudioContext.jsx`

**Purpose:** Manage WebRTC audio streams and microphone controls.

**Import:**
```javascript
import { useAudio } from './contexts/AudioContext';
```

**API:**

```typescript
interface UseAudioReturn {
  audioEnabled: boolean;
  micPermission: 'granted' | 'denied' | null;
  localStream: MediaStream | null;
  isMuted: boolean;
  audioLevel: number;
  userRole: 'speaker' | 'listener';
  isWebRTCSupported: boolean;
  requestMicrophoneAccess: () => Promise<MediaStream | null>;
  updateUserRole: (role: string) => void;
  toggleMute: () => void;
  stopAudio: () => void;
  enableSpeaking: () => void;
  disableSpeaking: () => void;
  enableAudioPlayback: () => void;
}
```

**Usage Example:**

```javascript
function AudioControls() {
  const {
    audioEnabled,
    isMuted,
    audioLevel,
    toggleMute,
    requestMicrophoneAccess
  } = useAudio();
  
  useEffect(() => {
    // Request microphone access
    requestMicrophoneAccess();
  }, []);
  
  return (
    <div>
      <button onClick={toggleMute}>
        {isMuted ? '🎤 Unmute' : '🔇 Mute'}
      </button>
      <AudioLevelBar level={audioLevel} />
    </div>
  );
}
```

**Properties:**

#### `audioEnabled: boolean`

Indicates if audio system is initialized.

```javascript
const { audioEnabled } = useAudio();

if (!audioEnabled) {
  return <div>Initializing audio...</div>;
}
```

#### `micPermission: 'granted' | 'denied' | null`

Microphone permission status.

```javascript
const { micPermission } = useAudio();

if (micPermission === 'denied') {
  return <MicPermissionDeniedMessage />;
}
```

#### `localStream: MediaStream | null`

User's local audio stream.

```javascript
const { localStream } = useAudio();

if (localStream) {
  const tracks = localStream.getAudioTracks();
  console.log('Audio tracks:', tracks.length);
}
```

#### `isMuted: boolean`

Microphone mute state.

```javascript
const { isMuted } = useAudio();

return (
  <div className={isMuted ? 'muted' : 'unmuted'}>
    {isMuted ? 'Muted' : 'Speaking'}
  </div>
);
```

#### `audioLevel: number`

Current audio level (0 to 1).

```javascript
const { audioLevel } = useAudio();

// Display audio level bar
<div 
  className="audio-bar"
  style={{ width: `${audioLevel * 100}%` }}
/>
```

#### `userRole: 'speaker' | 'listener'`

User's current role in discussion.

```javascript
const { userRole } = useAudio();

if (userRole === 'speaker') {
  return <SpeakerControls />;
} else {
  return <ListenerControls />;
}
```

#### `isWebRTCSupported: boolean`

Browser WebRTC support check.

```javascript
const { isWebRTCSupported } = useAudio();

if (!isWebRTCSupported) {
  return <BrowserNotSupportedMessage />;
}
```

**Methods:**

#### `requestMicrophoneAccess(): Promise<MediaStream | null>`

Request microphone access from user.

```javascript
const { requestMicrophoneAccess } = useAudio();

const setupAudio = async () => {
  try {
    const stream = await requestMicrophoneAccess();
    
    if (stream) {
      console.log('Microphone access granted');
    } else {
      console.log('Microphone access denied');
    }
  } catch (error) {
    console.error('Failed to access microphone:', error);
  }
};
```

**Audio Constraints:**
```javascript
const constraints = {
  audio: {
    echoCancellation: true,
    noiseSuppression: true,
    autoGainControl: true
  }
};
```

#### `updateUserRole(role: string): void`

Update user's role in discussion.

```javascript
const { updateUserRole } = useAudio();

const handleRoleChange = (newRole) => {
  updateUserRole(newRole);
  
  if (newRole === 'speaker') {
    // Enable microphone
  } else {
    // Disable microphone
  }
};
```

#### `toggleMute(): void`

Toggle microphone mute state.

```javascript
const { toggleMute, isMuted } = useAudio();

const handleMuteClick = () => {
  toggleMute();
  console.log('Muted:', !isMuted);
};
```

**Implementation:**
```javascript
const toggleMute = () => {
  if (localStream) {
    localStream.getAudioTracks().forEach(track => {
      track.enabled = !track.enabled;
    });
    setIsMuted(!isMuted);
  }
};
```

#### `stopAudio(): void`

Stop all audio streams and clean up.

```javascript
const { stopAudio } = useAudio();

useEffect(() => {
  return () => {
    // Clean up on unmount
    stopAudio();
  };
}, []);
```

#### `enableSpeaking(): void`

Enable microphone for speaking.

```javascript
const { enableSpeaking } = useAudio();

socket.on('your-turn', () => {
  enableSpeaking();
});
```

#### `disableSpeaking(): void`

Disable microphone after speaking.

```javascript
const { disableSpeaking } = useAudio();

socket.on('turn-end', () => {
  disableSpeaking();
});
```

#### `enableAudioPlayback(): void`

Enable audio playback for remote streams.

```javascript
const { enableAudioPlayback } = useAudio();

// Call when user interaction happens
const handleStartDiscussion = () => {
  enableAudioPlayback();
  startDiscussion();
};
```

**Audio Level Monitoring:**

```javascript
const monitorAudioLevel = (stream) => {
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

## Hook Patterns

### 1. Hook Composition

Combine multiple hooks for complex functionality:

```javascript
function DiscussionPage() {
  const { user } = useAuth();
  const { socket, connected } = useSocket();
  const { audioEnabled, toggleMute } = useAudio();
  
  const isReady = user && connected && audioEnabled;
  
  return isReady ? <Discussion /> : <Loading />;
}
```

### 2. Conditional Hook Usage

Hooks must be called unconditionally, but values can be used conditionally:

```javascript
function Component() {
  const { socket } = useSocket();
  
  useEffect(() => {
    if (!socket) return; // Check value, not hook
    
    socket.on('event', handler);
    return () => socket.off('event', handler);
  }, [socket]);
}
```

### 3. Custom Hook Dependencies

Always include all dependencies in useEffect:

```javascript
function useParticipants(roomId) {
  const { socket } = useSocket();
  const [participants, setParticipants] = useState([]);
  
  useEffect(() => {
    if (!socket || !roomId) return;
    
    socket.on('participants-update', setParticipants);
    return () => socket.off('participants-update', setParticipants);
  }, [socket, roomId]); // Include all dependencies
  
  return participants;
}
```

### 4. Error Handling in Hooks

```javascript
function useAudioWithErrorHandling() {
  const audio = useAudio();
  const [error, setError] = useState(null);
  
  const safeRequestMicrophone = async () => {
    try {
      setError(null);
      await audio.requestMicrophoneAccess();
    } catch (err) {
      setError(err.message);
    }
  };
  
  return {
    ...audio,
    error,
    requestMicrophoneAccess: safeRequestMicrophone
  };
}
```

---

## Testing Hooks

### Unit Testing

```javascript
import { renderHook, act } from '@testing-library/react';
import { AuthProvider, useAuth } from './AuthContext';

describe('useAuth', () => {
  test('login updates user state', () => {
    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider
    });
    
    act(() => {
      result.current.login({
        id: 'test-123',
        name: 'Test User',
        campus: 'Test Campus',
        location: 'Test Location'
      });
    });
    
    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user.id).toBe('test-123');
  });
  
  test('logout clears user state', () => {
    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider
    });
    
    act(() => {
      result.current.login({ /* user data */ });
      result.current.logout();
    });
    
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBe(null);
  });
});
```

---

## Performance Considerations

### 1. Memoization

Memoize expensive computations:

```javascript
const { participants } = useSocket();

const sortedParticipants = useMemo(() => {
  return participants.sort((a, b) => 
    a.anonymousName.localeCompare(b.anonymousName)
  );
}, [participants]);
```

### 2. Callback Optimization

Use useCallback for event handlers:

```javascript
const { toggleMute } = useAudio();

const handleMuteClick = useCallback(() => {
  toggleMute();
}, [toggleMute]);
```

### 3. Avoid Unnecessary Re-renders

```javascript
// Bad: Creates new object every render
const value = {
  user: user,
  login: login
};

// Good: Memoized value
const value = useMemo(() => ({
  user,
  login
}), [user, login]);
```

---

## Common Issues

### Issue: Hook Called Outside Provider

**Error:**
```
Cannot read property 'user' of undefined
```

**Solution:**
Ensure component is wrapped in provider:

```javascript
function App() {
  return (
    <AuthProvider>
      <SocketProvider>
        <AudioProvider>
          <MyComponent />
        </AudioProvider>
      </SocketProvider>
    </AuthProvider>
  );
}
```

### Issue: Stale Closure

**Problem:**
```javascript
useEffect(() => {
  socket.on('event', () => {
    // Uses old value of count
    console.log(count);
  });
}, []); // Missing count dependency
```

**Solution:**
```javascript
useEffect(() => {
  socket.on('event', () => {
    console.log(count);
  });
  
  return () => socket.off('event');
}, [count]); // Include count
```

### Issue: Memory Leaks

**Problem:**
Not cleaning up listeners

**Solution:**
Always return cleanup function:

```javascript
useEffect(() => {
  socket.on('event', handler);
  
  return () => {
    socket.off('event', handler);
  };
}, [socket]);
```

---

## Best Practices

1. **Always clean up effects:**
   ```javascript
   useEffect(() => {
     const timer = setInterval(() => {}, 1000);
     return () => clearInterval(timer);
   }, []);
   ```

2. **Handle null/undefined values:**
   ```javascript
   const { socket } = useSocket();
   if (!socket) return <Loading />;
   ```

3. **Use TypeScript for type safety:**
   ```typescript
   const { user }: { user: User | null } = useAuth();
   ```

4. **Provide fallback values:**
   ```javascript
   const { user = { id: '', name: '' } } = useAuth();
   ```

5. **Document custom hooks:**
   ```javascript
   /**
    * Custom hook for managing participant list
    * @param {string} roomId - Room identifier
    * @returns {Array} List of participants
    */
   function useParticipants(roomId) {
     // ...
   }
   ```

---

## Support

For hook-related issues:
- Check provider hierarchy
- Verify hook dependencies
- Review React DevTools for state
- Consult React documentation for hook rules
