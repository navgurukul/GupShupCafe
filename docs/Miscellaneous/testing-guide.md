# Testing Guide

## Overview

This guide covers testing strategies, best practices, and procedures for the GupShup Cafe platform.

---

## Testing Strategy

### Testing Pyramid

```
           ┌─────────────────┐
          /   E2E Tests      /
         /   (Manual)       /
        /─────────────────/
       /  Integration     /
      /     Tests        /
     /─────────────────/
    /   Unit Tests     /
   /                 /
  /─────────────────/
```

**Current Implementation:**
- **Manual Testing:** Primary method
- **Integration Testing:** Socket.io events
- **Unit Testing:** Planned for future

---

## Manual Testing

### Test Environment Setup

1. **Start Backend:**
```bash
cd server
npm install
npm run dev
```

2. **Start Frontend:**
```bash
cd client
npm install
npm run dev
```

3. **Open Multiple Browser Windows:**
- Use different browser profiles for testing multiple users
- Or use incognito/private windows

---

## Feature Testing Checklists

### 1. Authentication Flow

#### Login Page
- [ ] All form fields render correctly
- [ ] Required field validation works
- [ ] Error messages display for empty fields
- [ ] Anonymous name generates on login
- [ ] User data persists in localStorage
- [ ] Redirect to lobby after successful login

**Test Steps:**
```
1. Open http://localhost:5173
2. Leave all fields empty and submit
3. Verify error messages appear
4. Fill in all fields correctly
5. Submit form
6. Verify redirect to /lobby
7. Check localStorage for user data
8. Refresh page
9. Verify still logged in
```

---

### 2. Lobby Functionality

#### Room Management
- [ ] User can create/join a room
- [ ] Room ID displays correctly
- [ ] Multiple users can join same room
- [ ] Participant list updates in real-time
- [ ] User count displays correctly

**Test Steps:**
```
1. User A joins lobby
2. User A clicks "Create Room"
3. Note the room ID
4. User B joins lobby
5. User B enters same room ID
6. Verify both users see each other in participant list
```

#### Audio Permissions
- [ ] Audio permission dialog appears
- [ ] "Allow" grants microphone access
- [ ] "Deny" shows error message
- [ ] Audio permission state persists
- [ ] Can re-request permission if denied

**Test Steps:**
```
1. Click "Request Microphone Access"
2. Allow microphone in browser dialog
3. Verify green checkmark appears
4. Check browser console for stream object
5. Try with "Deny" in separate test
```

#### Ready Status
- [ ] Ready button toggles correctly
- [ ] Ready status shows for all participants
- [ ] "Start Discussion" enables when all ready
- [ ] Minimum participant requirement enforced
- [ ] Status persists during reconnection

**Test Steps:**
```
1. User A marks ready
2. Verify checkmark appears
3. User B joins and marks ready
4. Verify "Start Discussion" button activates
5. Click "Start Discussion"
6. Verify navigation to roundtable
```

---

### 3. Roundtable Discussion

#### Visual Layout
- [ ] Participants arranged in circle
- [ ] Current speaker highlighted
- [ ] All names visible and correct
- [ ] Topic displays correctly
- [ ] Timer shows accurate time

**Test Steps:**
```
1. Start discussion with 3+ participants
2. Verify circular arrangement
3. Check speaker highlighting (green ring)
4. Verify topic title and questions display
5. Watch timer count down
```

#### Speaking Turns
- [ ] First speaker starts automatically
- [ ] Timer counts down correctly
- [ ] Next speaker advances automatically
- [ ] Manual "Next" button works
- [ ] Round number increments correctly
- [ ] All participants get turns

**Test Steps:**
```
1. Note who is first speaker
2. Wait for timer to reach 0
3. Verify next speaker highlighted
4. Click "Next Speaker" button
5. Verify immediate advancement
6. Complete full round
7. Verify round counter increments
```

#### Audio Controls
- [ ] Mute button toggles correctly
- [ ] Mute icon changes state
- [ ] Audio level indicator works
- [ ] Remote audio plays for listeners
- [ ] No echo or feedback

**Test Steps:**
```
1. Speaker clicks mute
2. Verify icon changes to muted
3. Other users should not hear audio
4. Click unmute
5. Verify audio returns
6. Check audio level bar moves when speaking
```

---

### 4. WebRTC Audio

#### Connection Establishment
- [ ] Peer connections establish
- [ ] ICE candidates exchange
- [ ] Audio streams flow
- [ ] Connection survives brief network issues
- [ ] Reconnection works after disconnect

**Test Steps:**
```
1. Open browser console for all users
2. Check for "peer connection" logs
3. Verify "audio track" messages
4. Speak into microphone
5. Other users should hear audio
6. Disconnect network briefly
7. Verify automatic reconnection
```

#### Audio Quality
- [ ] Clear audio with no distortion
- [ ] Low latency (<500ms)
- [ ] No echo cancellation issues
- [ ] Proper volume levels
- [ ] Background noise suppression works

**Test Steps:**
```
1. Use headphones to prevent echo
2. Speak at normal volume
3. Ask other users to rate audio quality
4. Test with background noise
5. Verify noise suppression
```

---

### 5. Real-time Synchronization

#### Socket Events
- [ ] Join/leave notifications work
- [ ] Participant updates sync immediately
- [ ] Discussion state syncs across clients
- [ ] Timer syncs for all users
- [ ] No lag in state updates

**Test Steps:**
```
1. User A joins room
2. User B should see A immediately
3. User C joins
4. All users see C join notification
5. User B leaves
6. All users see B leave notification
7. Check timer synchronization across all clients
```

---

### 6. Error Handling

#### Network Errors
- [ ] Graceful handling of disconnection
- [ ] Automatic reconnection works
- [ ] State restored after reconnection
- [ ] Error messages are user-friendly
- [ ] No data loss during brief outage

**Test Steps:**
```
1. During discussion, disable network
2. Verify "Disconnected" message appears
3. Re-enable network
4. Verify automatic reconnection
5. Check that discussion state restored
```

#### Permission Errors
- [ ] Microphone denial handled gracefully
- [ ] Can re-request permission
- [ ] Alternative flow for denied permission
- [ ] Clear error messages

**Test Steps:**
```
1. Deny microphone permission
2. Verify error message shows
3. Check that can still join as listener
4. Reset permissions in browser
5. Try again
```

---

## Browser Compatibility Testing

### Supported Browsers

#### Chrome/Chromium
- [ ] All features work
- [ ] WebRTC audio clear
- [ ] Socket.io connects
- [ ] Performance good

#### Firefox
- [ ] All features work
- [ ] WebRTC audio clear
- [ ] Socket.io connects
- [ ] Performance good

#### Safari (macOS)
- [ ] All features work
- [ ] WebRTC audio clear
- [ ] Socket.io connects
- [ ] Performance acceptable

#### Edge
- [ ] All features work
- [ ] WebRTC audio clear
- [ ] Socket.io connects
- [ ] Performance good

**Test on each browser:**
```
1. Complete full user flow
2. Test audio quality
3. Test with multiple tabs
4. Check developer console for errors
5. Monitor performance metrics
```

---

## Performance Testing

### Metrics to Monitor

**Client-Side:**
- Page load time
- Time to interactive
- Memory usage
- CPU usage during audio
- Network bandwidth

**Server-Side:**
- Response time
- Concurrent connections
- Memory usage
- CPU usage
- Database query time

### Load Testing

#### Small Scale (5 users)
```
1. Open 5 browser windows
2. All join same room
3. Start discussion
4. Monitor server logs
5. Check for any errors or lag
```

#### Medium Scale (10 users)
```
1. Repeat with 10 users
2. Monitor performance degradation
3. Check audio quality
4. Note any synchronization issues
```

---

## Integration Testing

### Socket.io Events

**Test Event Flow:**

```javascript
// Test script
const io = require('socket.io-client');

const socket = io('http://localhost:3003', {
  auth: {
    userId: 'test-user',
    name: 'Test User',
    campus: 'Test Campus',
    location: 'Test Location',
    anonymousName: 'Test Owl'
  }
});

// Test join room
socket.emit('join-room', 'test-room', { role: 'speaker' });

socket.on('participants-update', (participants) => {
  console.log('✓ Participants update received:', participants.length);
});

socket.on('discussion-start', (data) => {
  console.log('✓ Discussion started:', data.topic.title);
});

// Cleanup
setTimeout(() => {
  socket.disconnect();
}, 5000);
```

---

## Database Testing

### Test Data Insertion

```javascript
// Test saving session
const testSession = {
  id: 'test-session-123',
  roomId: 'test-room',
  topic: {
    title: 'Test Topic',
    category: 'Test'
  },
  participantCount: 3,
  startedAt: new Date(),
  endedAt: new Date(),
  durationSeconds: 1800,
  roundsCompleted: 3
};

await saveSession(testSession);
console.log('✓ Session saved');

// Verify data
const sessions = await getSessionAnalytics(1);
console.log('✓ Session retrieved:', sessions[0].id);
```

---

## API Testing

### Using cURL

**Health Check:**
```bash
curl http://localhost:3003/api/health
```

**Get Topics:**
```bash
curl http://localhost:3003/api/topics
```

**Generate Topic:**
```bash
curl -X POST http://localhost:3003/api/topics/generate \
  -H "Content-Type: application/json" \
  -d '{"category": "Education"}'
```

**Get Analytics:**
```bash
curl http://localhost:3003/api/analytics/stats
```

### Using Postman

1. Import collection from `/docs/postman/`
2. Set environment variables
3. Run test suite
4. Verify all tests pass

---

## Regression Testing

### Before Each Release

- [ ] Run full manual test suite
- [ ] Test on all supported browsers
- [ ] Test with different user counts
- [ ] Verify database operations
- [ ] Check API endpoints
- [ ] Test error scenarios
- [ ] Verify audio quality
- [ ] Check performance metrics

---

## Test Data

### Sample Users

```javascript
const testUsers = [
  {
    id: 'user-001',
    name: 'Alice Johnson',
    campus: 'Delhi Campus',
    location: 'India',
    anonymousName: 'Wise Owl'
  },
  {
    id: 'user-002',
    name: 'Bob Smith',
    campus: 'Mumbai Campus',
    location: 'India',
    anonymousName: 'Clever Fox'
  },
  {
    id: 'user-003',
    name: 'Charlie Brown',
    campus: 'Bangalore Campus',
    location: 'India',
    anonymousName: 'Swift Eagle'
  }
];
```

---

## Automated Testing (Future)

### Unit Tests

```javascript
// Example unit test
describe('generateAnonymousName', () => {
  test('generates valid name', () => {
    const name = generateAnonymousName();
    expect(name).toMatch(/^\w+ \w+$/);
  });
  
  test('generates unique names', () => {
    const names = new Set();
    for (let i = 0; i < 100; i++) {
      names.add(generateAnonymousName());
    }
    expect(names.size).toBeGreaterThan(10);
  });
});
```

### E2E Tests

```javascript
// Example Playwright test
test('complete discussion flow', async ({ page }) => {
  // Login
  await page.goto('http://localhost:5173');
  await page.fill('#id', 'test-user');
  await page.fill('#name', 'Test User');
  await page.fill('#campus', 'Test Campus');
  await page.fill('#location', 'Test Location');
  await page.click('button[type="submit"]');
  
  // Join lobby
  await expect(page).toHaveURL(/\/lobby/);
  await page.click('button:has-text("Create Room")');
  
  // Mark ready
  await page.click('button:has-text("Ready")');
  
  // Verify discussion starts
  await expect(page).toHaveURL(/\/roundtable/);
});
```

---

## Bug Reporting

### Bug Report Template

```markdown
**Title:** [Brief description]

**Environment:**
- Browser: Chrome 120
- OS: Windows 11
- Backend: v1.0.0
- Frontend: v1.0.0

**Steps to Reproduce:**
1. Go to login page
2. Enter credentials
3. Click submit
4. ...

**Expected Result:**
[What should happen]

**Actual Result:**
[What actually happens]

**Screenshots:**
[Attach screenshots if applicable]

**Console Logs:**
[Paste relevant console output]

**Additional Context:**
[Any other relevant information]
```

---

## Testing Best Practices

1. **Test Early and Often**
   - Test each feature as it's developed
   - Don't wait until the end

2. **Use Real Scenarios**
   - Test with realistic data
   - Simulate actual user behavior

3. **Test Edge Cases**
   - Maximum participants
   - Minimum participants
   - Long discussion durations
   - Network interruptions

4. **Document Findings**
   - Keep test results
   - Track issues found
   - Note patterns

5. **Automate When Possible**
   - Repetitive tests should be automated
   - Use test scripts for API testing

---

## Test Coverage Goals

**Current Coverage:**
- Manual testing: 100%
- Integration testing: 50%
- Unit testing: 0%

**Target Coverage:**
- Manual testing: 100%
- Integration testing: 80%
- Unit testing: 70%

---

## Continuous Testing

### Daily Smoke Tests
- [ ] App starts without errors
- [ ] Login works
- [ ] Can create room
- [ ] Basic discussion flow works

### Weekly Regression Tests
- [ ] Full test suite
- [ ] All browsers
- [ ] Performance benchmarks

### Pre-Release Tests
- [ ] Complete manual testing
- [ ] Load testing
- [ ] Security testing
- [ ] Compatibility testing

---

## Support

For testing-related questions:
- Review test checklists
- Check browser console for errors
- Use network tab to debug API calls
- Consult server logs for backend issues
