# Troubleshooting Guide

## Overview

This guide helps diagnose and resolve common issues in the GupShup Cafe platform.

---

## Quick Diagnostics

### Health Checks

```bash
# Check backend server
curl http://localhost:3003/api/health

# Check frontend server
curl http://localhost:5173

# Check database
ls -l server/data/roundtable.db

# Check processes
ps aux | grep node
```

---

## Common Issues

### 1. Cannot Connect to Server

**Symptoms:**
- "Connection failed" error
- Frontend shows disconnected status
- Socket.io connection timeout

**Possible Causes:**
1. Backend server not running
2. Wrong port configuration
3. CORS issues
4. Firewall blocking connection

**Solutions:**

**Check if server is running:**
```bash
cd server
npm run dev
```

**Verify port configuration:**
```javascript
// client/.env
VITE_SOCKET_URL=http://localhost:3003

// server/.env
PORT=3003
```

**Check CORS settings:**
```javascript
// server/src/server.js
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

**Test connection:**
```bash
curl http://localhost:3003/api/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:00:00.000Z",
  "service": "AI Roundtable API"
}
```

---

### 2. Audio Not Working

**Symptoms:**
- Cannot hear other participants
- Microphone not capturing audio
- "Permission denied" errors
- Audio cuts in and out

**Diagnostics:**

**Check browser console:**
```javascript
// Should see:
"Microphone access granted"
"Audio stream started"
"Peer connection established"

// Should NOT see:
"Permission denied"
"getUserMedia failed"
"ICE connection failed"
```

**Test audio access:**
```javascript
navigator.mediaDevices.getUserMedia({ audio: true })
  .then(stream => {
    console.log('✓ Microphone access granted');
    console.log('Tracks:', stream.getAudioTracks());
  })
  .catch(error => {
    console.error('✗ Microphone error:', error);
  });
```

**Solutions:**

**Grant microphone permission:**
1. Click padlock in address bar
2. Click "Site settings"
3. Find "Microphone"
4. Change to "Allow"
5. Refresh page

**Reset browser permissions:**
```
Chrome: chrome://settings/content/microphone
Firefox: about:preferences#privacy
Safari: Safari > Preferences > Websites > Microphone
```

**Check audio device:**
```javascript
navigator.mediaDevices.enumerateDevices()
  .then(devices => {
    const audioInputs = devices.filter(d => d.kind === 'audioinput');
    console.log('Audio inputs:', audioInputs);
  });
```

**Test with audio-test page:**
```
http://localhost:5173/audio-test
```

**Verify WebRTC support:**
```javascript
const isSupported = !!(
  navigator.mediaDevices &&
  navigator.mediaDevices.getUserMedia &&
  RTCPeerConnection
);

console.log('WebRTC supported:', isSupported);
```

---

### 3. WebRTC Connection Fails

**Symptoms:**
- Cannot establish peer connection
- "ICE connection failed" errors
- Audio works locally but not remotely

**Diagnostics:**

**Check ICE connection state:**
```javascript
peerConnection.oniceconnectionstatechange = () => {
  console.log('ICE state:', peerConnection.iceConnectionState);
  // Should progress: new -> checking -> connected
};
```

**Check ICE candidates:**
```javascript
peerConnection.onicecandidate = (event) => {
  if (event.candidate) {
    console.log('ICE candidate:', event.candidate.candidate);
  }
};
```

**Solutions:**

**Check firewall:**
- Allow UDP ports for WebRTC
- Allow ICE/STUN/TURN traffic

**Use STUN server:**
```javascript
const config = {
  iceServers: [
    { urls: 'stun:stun.l.google.com:19302' },
    { urls: 'stun:stun1.l.google.com:19302' }
  ]
};
```

**Add TURN server (if behind strict firewall):**
```javascript
const config = {
  iceServers: [
    { urls: 'stun:stun.l.google.com:19302' },
    {
      urls: 'turn:turn.example.com:3478',
      username: 'user',
      credential: 'pass'
    }
  ]
};
```

---

### 4. Socket Disconnects Frequently

**Symptoms:**
- Frequent "disconnected" messages
- Connection drops during discussion
- Must rejoin room repeatedly

**Diagnostics:**

**Monitor disconnection reason:**
```javascript
socket.on('disconnect', (reason) => {
  console.log('Disconnect reason:', reason);
  // Common reasons:
  // - 'transport close': Network issue
  // - 'ping timeout': No response from server
  // - 'transport error': Connection error
});
```

**Check network stability:**
```bash
# Ping server
ping localhost

# Check latency
curl -w "@curl-format.txt" http://localhost:3003/api/health
```

**Solutions:**

**Increase timeout:**
```javascript
const socket = io(url, {
  timeout: 20000,
  pingTimeout: 60000,
  pingInterval: 25000
});
```

**Enable reconnection:**
```javascript
const socket = io(url, {
  reconnection: true,
  reconnectionAttempts: 10,
  reconnectionDelay: 1000,
  reconnectionDelayMax: 5000
});
```

**Use more reliable transport:**
```javascript
const socket = io(url, {
  transports: ['websocket', 'polling']
});
```

---

### 5. Participant List Not Updating

**Symptoms:**
- New participants don't appear
- Left participants still shown
- Inconsistent participant counts

**Diagnostics:**

**Check event listeners:**
```javascript
socket.on('participants-update', (participants) => {
  console.log('Participants update:', participants.length);
  console.log('List:', participants.map(p => p.anonymousName));
});
```

**Verify socket room:**
```javascript
// Server side
console.log('Socket rooms:', Array.from(socket.rooms));
```

**Solutions:**

**Rejoin room on reconnection:**
```javascript
socket.on('connect', () => {
  if (currentRoom) {
    socket.emit('join-room', currentRoom, { role: userRole });
  }
});
```

**Clear stale listeners:**
```javascript
useEffect(() => {
  socket.on('participants-update', handleUpdate);
  
  return () => {
    socket.off('participants-update', handleUpdate);
  };
}, [socket]);
```

---

### 6. Timer Not Synchronizing

**Symptoms:**
- Different times shown for different users
- Timer doesn't advance
- Timer jumps or skips

**Diagnostics:**

**Check timer events:**
```javascript
socket.on('timer-update', (data) => {
  console.log('Time remaining:', data.timeRemaining);
  console.log('Local time:', new Date().toISOString());
});
```

**Solutions:**

**Use server time as source of truth:**
```javascript
// Don't run local timer
// Always rely on server updates
socket.on('timer-update', ({ timeRemaining }) => {
  setTimeRemaining(timeRemaining);
});
```

**Handle missed updates:**
```javascript
let lastUpdate = Date.now();

socket.on('timer-update', ({ timeRemaining }) => {
  const now = Date.now();
  const elapsed = (now - lastUpdate) / 1000;
  
  if (elapsed > 2) {
    console.warn('Missed timer updates');
  }
  
  setTimeRemaining(timeRemaining);
  lastUpdate = now;
});
```

---

### 7. Database Errors

**Symptoms:**
- "Database locked" errors
- Failed to save session
- Analytics not loading

**Diagnostics:**

**Check database file:**
```bash
# Check if file exists
ls -l server/data/roundtable.db

# Check permissions
chmod 644 server/data/roundtable.db

# Check size
du -h server/data/roundtable.db
```

**Test database:**
```bash
sqlite3 server/data/roundtable.db "SELECT * FROM sessions LIMIT 1;"
```

**Solutions:**

**Enable WAL mode:**
```javascript
db.run('PRAGMA journal_mode = WAL');
```

**Close connections properly:**
```javascript
process.on('SIGINT', () => {
  db.close((err) => {
    if (err) console.error(err);
    process.exit(0);
  });
});
```

**Backup and restore:**
```bash
# Backup
cp server/data/roundtable.db server/data/roundtable.db.backup

# Restore
cp server/data/roundtable.db.backup server/data/roundtable.db
```

---

### 8. AI Topic Generation Fails

**Symptoms:**
- Always gets fallback topics
- "Failed to generate topic" errors
- Slow response times

**Diagnostics:**

**Check API key:**
```bash
echo $HUGGINGFACE_API_KEY
```

**Test API directly:**
```bash
curl https://api-inference.huggingface.co/models/gpt2 \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"inputs": "Generate a topic"}'
```

**Solutions:**

**Verify API key:**
```bash
# In .env
HUGGINGFACE_API_KEY=hf_your_actual_key_here
```

**Check rate limits:**
- Free tier: 1000 requests/month
- Consider caching topics

**Use fallback gracefully:**
```javascript
try {
  const topic = await generateDiscussionTopic();
  return topic;
} catch (error) {
  console.warn('AI failed, using fallback');
  return getTopicByCategory(category);
}
```

---

### 9. High Memory Usage

**Symptoms:**
- Server becomes slow
- Browser tab crashes
- "Out of memory" errors

**Diagnostics:**

**Check memory usage:**
```bash
# Server memory
node --max-old-space-size=4096 server.js

# Monitor process
top -p $(pgrep -f "node server")
```

**Check browser memory:**
```javascript
// Chrome DevTools > Memory tab
// Take heap snapshot
// Check for memory leaks
```

**Solutions:**

**Clean up room data:**
```javascript
// Remove empty rooms
setInterval(() => {
  roomManager.cleanupEmptyRooms();
}, 60000);
```

**Limit stored sessions:**
```javascript
// Keep only recent sessions in memory
const MAX_SESSIONS = 100;

if (sessions.size > MAX_SESSIONS) {
  const oldest = sessions.keys().next().value;
  sessions.delete(oldest);
}
```

**Fix memory leaks:**
```javascript
// Always clean up listeners
useEffect(() => {
  socket.on('event', handler);
  return () => socket.off('event', handler);
}, []);

// Close audio contexts
audioContext.close();

// Stop media streams
stream.getTracks().forEach(track => track.stop());
```

---

### 10. CORS Errors

**Symptoms:**
- "Access-Control-Allow-Origin" errors
- API requests blocked
- Cannot connect from deployed frontend

**Diagnostics:**

**Check browser console:**
```
Access to fetch at 'http://localhost:3003/api/health' from origin 
'http://localhost:5173' has been blocked by CORS policy
```

**Solutions:**

**Update CORS origins:**
```javascript
// server/.env
ALLOWED_ORIGINS=http://localhost:5173,https://your-frontend.vercel.app
```

**Enable credentials:**
```javascript
app.use(cors({
  origin: allowedOrigins,
  credentials: true
}));
```

**For development:**
```javascript
// Allow all origins (dev only!)
app.use(cors({ origin: '*' }));
```

---

## Deployment Issues

### 1. Production Build Fails

**Check build logs:**
```bash
# Frontend
cd client
npm run build

# Backend
cd server
npm run build  # If using TypeScript
```

**Common fixes:**
- Update dependencies
- Check for TypeScript errors
- Verify environment variables

### 2. Environment Variables Not Working

**Verify .env files:**
```bash
# Check if .env exists
ls -la .env

# Check contents
cat .env

# Ensure no quotes
PORT=3003  # Good
PORT="3003"  # Bad
```

**Restart servers after changes:**
```bash
# Stop servers
# Update .env
# Restart servers
npm run dev
```

### 3. WebSocket Not Working in Production

**Use WSS instead of WS:**
```javascript
const socketUrl = window.location.protocol === 'https:'
  ? 'wss://your-backend.com'
  : 'ws://localhost:3003';
```

**Configure reverse proxy:**
```nginx
# Nginx config
location /socket.io/ {
  proxy_pass http://localhost:3003;
  proxy_http_version 1.1;
  proxy_set_header Upgrade $http_upgrade;
  proxy_set_header Connection "upgrade";
}
```

---

## Performance Issues

### Slow Page Load

**Check:**
1. Bundle size
2. Network requests
3. Asset optimization

**Optimize:**
```bash
# Analyze bundle
npm run build -- --analyze

# Lazy load routes
const Page = React.lazy(() => import('./Page'));
```

### High CPU Usage

**Check:**
- Infinite render loops
- Too many socket listeners
- Heavy computations in render

**Fix:**
```javascript
// Memoize expensive computations
const result = useMemo(() => expensiveFunc(), [dep]);

// Debounce frequent updates
const debouncedUpdate = debounce(update, 300);
```

---

## Browser-Specific Issues

### Safari Issues

**Audio autoplay blocked:**
```javascript
// Require user interaction
button.addEventListener('click', () => {
  audioElement.play();
});
```

**WebRTC quirks:**
```javascript
// Safari needs specific constraints
const constraints = {
  audio: {
    echoCancellation: true
  }
};
```

### Firefox Issues

**WebSocket connection:**
```javascript
// Use polling as fallback
const socket = io(url, {
  transports: ['polling', 'websocket']
});
```

---

## Getting Help

### Check Logs

**Browser Console:**
```
F12 > Console tab
Look for errors (red text)
```

**Server Logs:**
```bash
cd server
npm run dev

# Look for:
# - Connection errors
# - Database errors
# - API errors
```

### Collect Debug Info

```javascript
// In browser console
console.log('User agent:', navigator.userAgent);
console.log('Socket connected:', socket?.connected);
console.log('Audio enabled:', audioEnabled);
console.log('WebRTC support:', !!RTCPeerConnection);
```

### Report Issues

When reporting bugs, include:
1. Steps to reproduce
2. Expected vs actual behavior
3. Browser and OS
4. Console errors
5. Network tab screenshots
6. Server logs (if relevant)

---

## Prevention Tips

1. **Test thoroughly before deployment**
2. **Monitor server logs**
3. **Use error boundaries in React**
4. **Implement proper error handling**
5. **Keep dependencies updated**
6. **Have rollback plan**
7. **Monitor performance metrics**
8. **Regular database backups**

---

## Emergency Procedures

### Server Down

1. Check if process is running
2. Check server logs
3. Restart server
4. Check for port conflicts
5. Verify environment variables

### Database Corrupted

1. Stop server
2. Restore from backup
3. Verify data integrity
4. Restart server

### Production Outage

1. Check service status
2. Review recent deployments
3. Check error rates
4. Roll back if needed
5. Fix and redeploy

---

## Support Resources

- **Documentation:** `/docs`
- **GitHub Issues:** [GupShupCafe/issues](https://github.com/navgurukul/GupShupCafe/issues)
- **Stack Overflow:** Tag with `socket.io`, `webrtc`, `react`
- **Community:** Discord/Slack channel

---

## Useful Commands

```bash
# Restart everything
npm run dev

# Clear node_modules
rm -rf node_modules package-lock.json
npm install

# Clear browser cache
Ctrl+Shift+Delete

# Check ports in use
lsof -i :3003
lsof -i :5173

# Kill process on port
kill -9 $(lsof -t -i:3003)

# View full logs
tail -f server/logs/app.log

# Database backup
sqlite3 data/roundtable.db ".backup backup.db"

# Check disk space
df -h

# Check process memory
ps aux | grep node
```

---

## Quick Fixes

```bash
# Try these in order:
1. Refresh browser (Ctrl+R)
2. Hard refresh (Ctrl+Shift+R)
3. Clear browser data
4. Restart servers
5. Restart computer
6. Reinstall dependencies
```
