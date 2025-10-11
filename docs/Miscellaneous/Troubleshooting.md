# Troubleshooting Guide

## Overview

This guide helps diagnose and resolve common issues in GupShup Cafe.

---

## Connection Issues

### Socket.IO Connection Failed

**Symptoms**:
- "Connection failed" errors
- Cannot join lobby
- Participants list not updating

**Possible Causes**:
1. Backend server not running
2. Wrong API URL configured
3. CORS configuration mismatch
4. Network firewall blocking WebSocket
5. Port not accessible

**Solutions**:

**1. Verify Backend is Running**:
```bash
# Check health endpoint
curl http://localhost:3003/api/health

# Expected response:
# {"status":"healthy","timestamp":"...","service":"AI Roundtable API"}
```

**2. Check Client Configuration**:
```javascript
// client/.env
VITE_API_URL=http://localhost:3003  // Must match backend
```

**3. Verify CORS Configuration**:
```javascript
// server/.env
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5174
```

**4. Check Browser Console**:
```
F12 → Console tab
Look for Socket.IO errors
```

**5. Test WebSocket Connection**:
```javascript
// Browser console
const socket = io('http://localhost:3003')
socket.on('connect', () => console.log('Connected!'))
socket.on('connect_error', (err) => console.error('Error:', err))
```

**6. Disable Browser Extensions**:
- Ad blockers may block WebSocket
- Try incognito/private mode

---

### Cannot Connect in Production

**Symptoms**:
- Works locally but not in production
- CORS errors in production

**Solutions**:

**1. Check HTTPS**:
- Frontend must be HTTPS if backend is HTTPS
- Mixed content (HTTP + HTTPS) blocked by browsers

**2. Verify Production URLs**:
```bash
# Client env
VITE_API_URL=https://your-backend.onrender.com

# Server env
ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

**3. Test Production Backend**:
```bash
curl https://your-backend.onrender.com/api/health
```

**4. Check Render Logs**:
- Render Dashboard → Your Service → Logs
- Look for CORS or connection errors

**5. Verify Deployment**:
- Check last deploy was successful
- Ensure environment variables are set

---

## Audio/WebRTC Issues

### Microphone Not Working

**Symptoms**:
- Microphone permission denied
- Cannot hear own audio
- Audio level bars not moving

**Solutions**:

**1. Check Browser Permissions**:
```
Chrome: chrome://settings/content/microphone
Firefox: about:preferences#privacy
Safari: Preferences → Websites → Microphone
```

**2. Grant Permission When Prompted**:
- Click "Allow" when browser asks
- Some browsers require user interaction first

**3. Check Microphone in System Settings**:
- Ensure microphone is connected
- Verify it's not muted in OS
- Test in other apps (Zoom, Discord, etc.)

**4. HTTPS Required in Production**:
- WebRTC requires HTTPS (except localhost)
- Ensure frontend is deployed with HTTPS

**5. Test Audio Page**:
```
Navigate to: http://localhost:5173/audio-test
Check if audio level bars move
```

**6. Check Browser Compatibility**:
- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Supported (may have quirks)
- Mobile browsers: Varies

---

### Cannot Hear Other Participants

**Symptoms**:
- Own microphone works
- Cannot hear others speaking
- No audio from remote streams

**Solutions**:

**1. Check Speaker Volume**:
- Ensure system volume is up
- Check browser tab is not muted
- Look for muted tab indicator

**2. Enable Audio Playback**:
```javascript
// Some browsers require user interaction
// Click anywhere on the page to enable audio
```

**3. Check WebRTC Connection**:
```javascript
// Browser console
// Look for "Remote stream from" logs
```

**4. Network Issues**:
- Check NAT/firewall settings
- STUN servers may be blocked
- Try different network (mobile hotspot)

**5. Peer Connection Failed**:
- Check console for RTCPeerConnection errors
- Verify ICE candidates are exchanged
- May need TURN server for strict NATs

**6. Browser Autoplay Policy**:
- Some browsers block autoplay
- Requires user interaction first
- Click "Enable Audio" if prompted

---

### Echo or Feedback

**Symptoms**:
- Hearing own voice echoed back
- Loud feedback noise

**Solutions**:

**1. Use Headphones**:
- Prevents speaker output feeding back to mic
- Best practice for all participants

**2. Check Echo Cancellation**:
```javascript
// Should be enabled in AudioContext
echoCancellation: true
```

**3. Reduce Speaker Volume**:
- Lower system volume
- Move mic away from speakers

**4. Mute When Not Speaking**:
- Use mute button
- Only unmute when your turn

---

## Discussion/Room Issues

### Discussion Not Starting

**Symptoms**:
- Clicked "Ready" but nothing happens
- Stuck in lobby
- Other participants ready but discussion won't start

**Solutions**:

**1. Check Minimum Participants**:
```bash
# server/.env
MIN_PARTICIPANTS=1  # Set to 1 for testing
```

**2. Verify All Required Participants Ready**:
- Need MIN_PARTICIPANTS users
- Each must click "Ready"
- Check ready status indicators

**3. Check Server Logs**:
```bash
# Look for:
[Backend] checkAndStartDiscussion called for room: general
Ready count: X, Min required: Y
```

**4. Manual Start (Testing)**:
```javascript
// Browser console
socket.emit('start-discussion-manual')
```

**5. Refresh and Rejoin**:
- Leave room (close tab)
- Re-login and join lobby
- Signal ready again

---

### Stuck on Same Speaker

**Symptoms**:
- Timer expired but speaker didn't change
- Manual "Next" button not working

**Solutions**:

**1. Check Console for Errors**:
```javascript
// Look for timer or speaker-changed errors
```

**2. Manually Advance**:
```javascript
// Only works if discussion active
socket.emit('next-speaker')
```

**3. End and Restart Discussion**:
- Wait for discussion to end (3 rounds)
- Start new discussion

**4. Server Restart** (Development):
```bash
# Stop and restart server
npm run dev:server
```

---

### Participants Not Showing

**Symptoms**:
- Cannot see other participants
- Participant list empty

**Solutions**:

**1. Verify Room Join**:
```javascript
// Browser console
// Should see: "📥 [Username] joining room: general"
```

**2. Check Socket Connection**:
```javascript
console.log(socket?.connected)  // Should be true
```

**3. Listen for Updates**:
```javascript
socket.on('participants-update', (p) => console.log('Participants:', p))
```

**4. Different Browser/Incognito**:
- Test with second browser window
- Use incognito mode to avoid cache

---

## Database/Persistence Issues

### Analytics Not Saving

**Symptoms**:
- Sessions not appearing in analytics
- Topic usage not tracked

**Solutions**:

**1. Check Database File**:
```bash
ls -la server/data/discussions.db
# Should exist with recent timestamp
```

**2. Check Database Permissions**:
```bash
# Ensure write access
chmod 644 server/data/discussions.db
```

**3. Verify Database Initialized**:
```
# Server logs should show:
🗄️ Initializing database...
```

**4. Query Database Directly**:
```bash
sqlite3 server/data/discussions.db
sqlite> SELECT COUNT(*) FROM sessions;
```

---

### Data Lost After Restart

**Symptoms**:
- Sessions lost on server restart
- Room state reset

**Expected Behavior**:
- **In-Memory State**: Lost on restart (by design)
- **Database**: Persists across restarts

**Solutions**:

**1. Understanding Persistence**:
- Sessions: ✅ Persisted to database
- Room state: ❌ In-memory only
- Active discussions: ❌ Lost on restart

**2. Production Persistence (Render)**:
- Configure persistent disk
- Mount path: `/opt/render/project/src/data`
- Check disk is actually persistent

---

## Performance Issues

### Slow or Lagging

**Symptoms**:
- UI feels sluggish
- Delayed updates
- Audio cutting out

**Solutions**:

**1. Check Network**:
```bash
# Test latency
ping your-backend.onrender.com
```

**2. Reduce Participant Count**:
- WebRTC mesh scales poorly beyond 8 peers
- Recommend maximum 6 participants

**3. Close Other Apps**:
- Browser can be resource-intensive
- Close unused tabs
- Check system resources (CPU, RAM)

**4. Use Wired Connection**:
- WiFi can be unreliable for real-time audio
- Ethernet preferred

**5. Check Server Resources**:
- Render free tier has limits
- Check server logs for issues

---

### High CPU Usage

**Symptoms**:
- Computer fan loud
- Browser tab using 100% CPU

**Causes**:
- Audio processing
- Multiple peer connections
- Animation rendering

**Solutions**:

**1. Limit Participants**:
- Each peer = CPU overhead
- Recommend ≤ 6 participants

**2. Disable Animations**:
- Reduce visual effects
- Stop audio visualizations

**3. Update Browser**:
- Newer versions more optimized
- Enable hardware acceleration

---

## Development Issues

### npm install Failures

**Symptoms**:
- Errors during `npm install`
- Missing dependencies

**Solutions**:

**1. Check Node.js Version**:
```bash
node --version  # Should be 18+
```

**2. Clear Cache**:
```bash
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

**3. Use Correct Directory**:
```bash
# Install in correct locations
cd client && npm install
cd server && npm install
```

**4. Check Internet Connection**:
- npm requires internet to download packages

---

### Module Not Found Errors

**Symptoms**:
- "Cannot find module" errors
- Import errors

**Solutions**:

**1. Install Missing Dependencies**:
```bash
npm install
```

**2. Check Import Paths**:
```javascript
// Correct
import { useAuth } from '../contexts/AuthContext'

// Wrong
import { useAuth } from 'contexts/AuthContext'
```

**3. ES Modules Configuration**:
```json
// package.json
{
  "type": "module"
}
```

---

### Hot Reload Not Working

**Symptoms**:
- Changes not reflecting
- Need to manually refresh

**Solutions**:

**1. Check Vite Dev Server**:
- Ensure `npm run dev:client` is running
- Look for Vite errors

**2. Check File Save**:
- Ensure file is actually saved
- Check for unsaved indicator

**3. Restart Dev Server**:
```bash
# Stop (Ctrl+C) and restart
npm run dev
```

---

## Error Messages

### "Failed to join room"

**Cause**: Server error during room join

**Solution**:
- Check server logs
- Verify user data is valid
- Restart server

---

### "Speaker limit reached"

**Cause**: Too many speakers in room

**Solution**:
- Max 6 speakers (configurable)
- Someone needs to switch to listener role

---

### "Not in a room"

**Cause**: Trying to perform room action without being in room

**Solution**:
- Ensure you joined a room
- Check socket connection
- Rejoin lobby

---

## Debugging Tools

### Browser Developer Tools

**Chrome DevTools**:
```
F12 or Ctrl+Shift+I
- Console: JavaScript errors
- Network: WebSocket traffic
- Application: localStorage
```

**Network Tab**:
- Filter: WS (WebSocket)
- View messages exchanged

---

### Server Logs

**Development**:
```bash
# Server logs printed to terminal
# Look for [Backend] prefixed messages
```

**Production (Render)**:
- Dashboard → Service → Logs
- Real-time log streaming

---

### Socket.IO Debug Mode

**Client**:
```javascript
localStorage.debug = 'socket.io-client:*'
// Refresh page
```

**Server**:
```bash
DEBUG=socket.io* npm run dev:server
```

---

### Database Inspection

**Query Database**:
```bash
sqlite3 server/data/discussions.db

# Useful queries
SELECT * FROM sessions ORDER BY started_at DESC LIMIT 10;
SELECT * FROM participants WHERE session_id = 'xxx';
SELECT * FROM topics ORDER BY used_count DESC;
```

---

## Getting Help

### Before Asking for Help

1. Check this troubleshooting guide
2. Review relevant documentation
3. Check browser console for errors
4. Check server logs
5. Try reproducing in incognito mode
6. Test on different network

### What to Include

When reporting an issue:
- **Environment**: OS, browser, Node.js version
- **Steps to reproduce**: Exact steps
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Error messages**: Full error text
- **Screenshots**: If UI issue
- **Console logs**: Browser and server
- **Configuration**: Relevant env vars (redact secrets)

---

## Common Error Patterns

### TypeError: Cannot read property 'X' of undefined

**Cause**: Trying to access property of undefined object

**Common locations**:
- Missing hook context
- Socket not connected
- User not authenticated

**Solution**:
- Add null checks
- Verify dependencies loaded

---

### Network Error / Failed to fetch

**Cause**: Cannot reach backend

**Solution**:
- Check backend URL
- Verify backend is running
- Check CORS configuration

---

### CORS Policy Error

**Cause**: CORS misconfiguration

**Solution**:
- Add frontend URL to ALLOWED_ORIGINS
- Include protocol (http/https)
- No trailing slash

---

## Preventive Measures

### Best Practices

1. **Always use headphones** for audio discussions
2. **Close unnecessary tabs** to reduce resource usage
3. **Use modern browsers** (Chrome/Firefox/Edge)
4. **Stable internet connection** for real-time features
5. **HTTPS in production** for WebRTC to work
6. **Monitor server logs** for early issue detection
7. **Regular backups** of database file
8. **Test after deployments** to catch issues early

---

## Advanced Debugging

### WebRTC Debugging

**Chrome Internal Page**:
```
chrome://webrtc-internals
```
- View peer connections
- ICE candidate exchanges
- Audio/video tracks
- Connection statistics

**Check ICE Connection State**:
```javascript
pc.oniceconnectionstatechange = () => {
  console.log('ICE state:', pc.iceConnectionState)
}
// States: new, checking, connected, completed, failed, disconnected, closed
```

---

### Memory Leaks

**Symptoms**:
- Browser tab using increasing memory
- Eventually becomes unresponsive

**Check**:
```
Chrome DevTools → Performance → Memory
Take heap snapshots over time
```

**Common Causes**:
- Not removing event listeners
- Circular references
- Leaked peer connections

**Solutions**:
- Clean up listeners on unmount
- Close peer connections properly
- Use WeakMap for caches

---

### Network Diagnostics

**Test WebSocket Connection**:
```bash
# Install wscat
npm install -g wscat

# Connect to server
wscat -c ws://localhost:3003

# Should see socket.io protocol messages
```

**Trace Route**:
```bash
traceroute your-backend.onrender.com
```

---

## Quick Reference

### Restart Everything
```bash
# Kill all processes
pkill -f node

# Restart
npm run dev
```

### Clear Everything
```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules
rm -rf node_modules
rm -rf client/node_modules
rm -rf server/node_modules

# Reinstall
npm run install:all
```

### Reset Database
```bash
# Backup first!
cp server/data/discussions.db server/data/discussions.db.backup

# Delete
rm server/data/discussions.db

# Will be recreated on next server start
```
