# Migration Guide: Node.js to Python FastAPI

> **Note:** This is a historical migration document. The Node.js backend is no longer actively maintained. The current platform uses Python FastAPI backend deployed on AWS EC2.

This document guides you through migrating from the Node.js Express backend to the Python FastAPI backend.

## Why Migrate?

### Benefits of Python FastAPI Backend

1. **AWS EC2 Ready**: Complete deployment configuration with systemd service files
2. **Better Type Safety**: Python type hints provide better code clarity
3. **Native Async**: Python's async/await is more natural and performant
4. **Comprehensive Testing**: 36 unit tests with 100% pass rate
5. **Simpler Dependencies**: Easier package management with pip
6. **Same API Contract**: No frontend changes needed

## Migration Steps

### 1. API Compatibility

The Python backend maintains **100% API compatibility** with the Node.js backend:

| Endpoint | Method | Node.js | Python | Status |
|----------|--------|---------|--------|--------|
| `/health` | GET | ✅ | ✅ | Compatible |
| `/` | GET | ✅ | ✅ | Compatible |
| `/api/health` | GET | ✅ | ✅ | Compatible |
| `/api/topics` | GET | ✅ | ✅ | Compatible |
| `/api/topics/generate` | GET | ✅ | ✅ | Compatible |
| `/api/topics/category/:category` | GET | ✅ | ✅ | Compatible |
| `/api/analytics/sessions` | GET | ✅ | ✅ | Compatible |
| `/api/analytics/topics` | GET | ✅ | ✅ | Compatible |
| `/api/analytics/stats` | GET | ✅ | ✅ | Compatible |
| `/api/feedback` | POST | ✅ | ✅ | Compatible |
| `/api/config` | GET | ✅ | ✅ | Compatible |
| `/api/room/:roomId/state` | GET | ✅ | ✅ | Compatible |

### 2. WebSocket Events Compatibility

Socket.io events are fully compatible:

| Event | Direction | Node.js | Python | Status |
|-------|-----------|---------|--------|--------|
| `connect` | Client → Server | ✅ | ✅ | Compatible |
| `disconnect` | Client → Server | ✅ | ✅ | Compatible |
| `join-room` | Client → Server | ✅ | ✅ | Compatible |
| `user-ready` | Client → Server | ✅ | ✅ | Compatible |
| `change-role` | Client → Server | ✅ | ✅ | Compatible |
| `message` | Client → Server | ✅ | ✅ | Compatible |
| `participants-update` | Server → Client | ✅ | ✅ | Compatible |
| `discussion-started` | Server → Client | ✅ | ✅ | Compatible |
| `role-changed` | Server → Client | ✅ | ✅ | Compatible |
| `user-left` | Server → Client | ✅ | ✅ | Compatible |

### 3. Environment Variables

The Python backend uses the same environment variables with slight naming changes:

```env
# Node.js Backend (.env)
NODE_ENV=development
PORT=3003
ALLOWED_ORIGINS=...
DATABASE_URL=...
HUGGINGFACE_API_KEY=...
DEFAULT_SPEAKING_TIME=60
MIN_PARTICIPANTS=1
MAX_PARTICIPANTS=8
```

```env
# Python Backend (.env)
PYTHON_ENV=development  # Changed from NODE_ENV
PORT=3003                # Same
ALLOWED_ORIGINS=...     # Same
DATABASE_URL=...        # Same
HUGGINGFACE_API_KEY=... # Same
DEFAULT_SPEAKING_TIME=60 # Same
MIN_PARTICIPANTS=1       # Same
MAX_PARTICIPANTS=8       # Same
```

### 4. Database Compatibility

Both backends use the **same SQLite database schema**:
- `sessions` table
- `participants` table
- `topics` table

You can copy the existing database file directly:
```bash
cp server/data/roundtable.db server_py/data/roundtable.db
```

### 5. Testing the Migration

#### Step 1: Install Python Backend
```bash
cd server_py
pip install -r requirements.txt
```

#### Step 2: Copy Configuration
```bash
# Copy your Node.js .env (if it exists)
cp ../server/.env .env

# Update PYTHON_ENV if you had NODE_ENV
sed -i 's/NODE_ENV/PYTHON_ENV/g' .env
```

#### Step 3: Run Tests
```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

#### Step 4: Start Python Backend
```bash
# Development mode
python main.py

# Or with uvicorn directly
uvicorn main:socket_app --reload --port 3003
```

#### Step 5: Test with Frontend
```bash
# In another terminal
cd ../client
npm run dev
```

#### Step 6: Verify Functionality
1. Open http://localhost:5173
2. Join a room
3. Test all features:
   - User authentication
   - Room joining
   - Ready/unready
   - Role changes (speaker/listener)
   - Discussion starting
   - Real-time updates

### 6. Side-by-Side Comparison

Run both backends simultaneously to compare:

```bash
# Terminal 1: Node.js backend
cd server
PORT=3003 npm start

# Terminal 2: Python backend  
cd server_py
PORT=3004 python main.py

# Terminal 3: Frontend pointing to Node.js
cd client
VITE_API_URL=http://localhost:3003 npm run dev

# Terminal 4: Frontend pointing to Python
cd client
VITE_API_URL=http://localhost:3004 VITE_PORT=5174 npm run dev
```

### 7. Performance Testing

Compare performance between backends:

```bash
# Test Node.js backend
ab -n 1000 -c 10 http://localhost:3003/health

# Test Python backend
ab -n 1000 -c 10 http://localhost:3004/health
```

### 8. Deployment Migration

#### From Render to AWS EC2

1. **Setup EC2 instance** (see [server_py/DEPLOYMENT.md](../server_py/DEPLOYMENT.md))
2. **Install Python and dependencies**
3. **Deploy with systemd service**
4. **Update frontend CORS settings**
5. **Test thoroughly**
6. **Switch DNS/traffic**

### 9. Rollback Plan

If issues arise, you can quickly rollback:

1. **Keep Node.js backend running** during migration
2. **Update frontend environment variables** to point back to Node.js
3. **No database changes needed** (both use same schema)

### 10. Gradual Migration Strategy

**Phase 1: Testing (Week 1)**
- Deploy Python backend to staging/test environment
- Run comprehensive tests
- Verify all features work

**Phase 2: Beta Testing (Week 2)**
- Route 10% of traffic to Python backend
- Monitor for errors
- Collect performance metrics

**Phase 3: Full Migration (Week 3)**
- Route 100% of traffic to Python backend
- Keep Node.js backend as backup
- Monitor for 1 week

**Phase 4: Cleanup (Week 4)**
- If stable, remove Node.js backend
- Update all documentation
- Archive old code

## Code Comparison

### API Route Example

**Node.js (Express)**
```javascript
router.get('/topics', (req, res) => {
  try {
    const topics = getAllFallbackTopics()
    res.json({
      success: true,
      data: topics,
      count: topics.length
    })
  } catch (error) {
    console.error('Error getting topics:', error)
    res.status(500).json({
      success: false,
      error: 'Failed to retrieve topics'
    })
  }
})
```

**Python (FastAPI)**
```python
@router.get("/topics")
async def get_topics():
    """Get all available fallback topics"""
    try:
        topics = get_all_fallback_topics()
        return {
            "success": True,
            "data": topics,
            "count": len(topics)
        }
    except Exception as e:
        print(f"Error getting topics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve topics")
```

### Socket.io Handler Example

**Node.js**
```javascript
socket.on('join-room', (roomId, userData) => {
  socket.join(roomId)
  roomManager.addUserToRoom(roomId, userData)
  const participants = roomManager.getRoomParticipants(roomId)
  io.to(roomId).emit('participants-update', participants)
})
```

**Python**
```python
@sio.event
async def join_room(sid, room_id, user_data):
    await sio.enter_room(sid, room_id)
    room_manager.add_user_to_room(room_id, user_data)
    participants = room_manager.get_room_participants(room_id)
    await sio.emit('participants-update', participants, room=room_id)
```

## Troubleshooting

### Issue: Frontend can't connect to Python backend

**Solution**: Check CORS settings in .env:
```env
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5174
```

### Issue: Database locked

**Solution**: Ensure proper file permissions:
```bash
chmod 755 server_py/data/
chmod 644 server_py/data/roundtable.db
```

### Issue: Socket.io connection fails

**Solution**: Verify Socket.io client is compatible:
- Python backend uses `python-socketio` 5.10.0
- Client should use `socket.io-client` 4.x

### Issue: Tests fail

**Solution**: Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Support

If you encounter issues during migration:
1. Check [server_py/README.md](../server_py/README.md)
2. Review [server_py/DEPLOYMENT.md](../server_py/DEPLOYMENT.md)
3. Open an issue on GitHub with logs and error messages

## Summary

✅ **API Compatible**: No frontend changes needed
✅ **Database Compatible**: Same schema, can copy data
✅ **Feature Complete**: All functionality ported
✅ **Well Tested**: 36 tests, 100% pass rate
✅ **Production Ready**: AWS EC2 deployment documentation
✅ **Easy Rollback**: Can switch back to Node.js anytime

The migration is straightforward and can be done with minimal risk!
