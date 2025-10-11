# Environment Variables and Configuration

## Overview

This document describes all environment variables, configuration options, and setup requirements for GupShup Cafe.

---

## Environment Files

### File Locations

**Client**: `client/.env`
**Server**: `server/.env`

### Example Files

**Client**: `client/.env.example`
**Server**: `server/.env.example`

---

## Client Environment Variables

### Location
`client/.env`

### Variables

#### VITE_API_URL

**Description**: Backend API URL for Socket.IO and REST API connections

**Type**: `string` (URL)

**Required**: Yes

**Default**: None

**Development**:
```bash
VITE_API_URL=http://localhost:3003
```

**Production**:
```bash
VITE_API_URL=https://your-backend.onrender.com
```

**Usage in Code**:
```javascript
const socket = io(import.meta.env.VITE_API_URL)
```

**Notes**:
- Must include protocol (`http://` or `https://`)
- No trailing slash
- Must be accessible from client browser
- Vite exposes variables prefixed with `VITE_`

---

## Server Environment Variables

### Location
`server/.env`

### Variables

#### PORT

**Description**: Port number for the Express server

**Type**: `number`

**Required**: No

**Default**: `3003`

**Example**:
```bash
PORT=3003
```

**Usage**:
```javascript
const PORT = process.env.PORT || 3003
server.listen(PORT)
```

**Notes**:
- Cloud platforms may override this (e.g., Render)
- Choose port > 1024 for non-root users
- Ensure port is not already in use

---

#### NODE_ENV

**Description**: Application environment mode

**Type**: `string`

**Required**: No

**Default**: `development`

**Values**:
- `development`: Development mode (verbose logging, dev features)
- `production`: Production mode (optimized, minimal logging)
- `test`: Testing mode

**Example**:
```bash
NODE_ENV=production
```

**Usage**:
```javascript
if (process.env.NODE_ENV === 'production') {
  // Production-specific code
}
```

**Impact**:
- Logging verbosity
- Error message detail
- CORS configuration
- Performance optimizations

---

#### MIN_PARTICIPANTS

**Description**: Minimum participants required to start a discussion

**Type**: `number`

**Required**: No

**Default**: `1`

**Example**:
```bash
MIN_PARTICIPANTS=2
```

**Usage**:
```javascript
const minParticipants = parseInt(process.env.MIN_PARTICIPANTS) || 1
if (readyCount >= minParticipants) {
  startDiscussion()
}
```

**Constraints**:
- Must be >= 1
- Should be <= MAX_PARTICIPANTS
- Recommended: 2-4 for meaningful discussions

---

#### MAX_PARTICIPANTS

**Description**: Maximum participants allowed in a room

**Type**: `number`

**Required**: No

**Default**: `8`

**Example**:
```bash
MAX_PARTICIPANTS=8
```

**Usage**:
```javascript
const maxParticipants = parseInt(process.env.MAX_PARTICIPANTS) || 8
```

**Notes**:
- WebRTC mesh scales poorly beyond 6-8 peers
- Higher values require SFU (media server)
- Recommend: 6-8 for P2P audio

---

#### DEFAULT_SPEAKING_TIME

**Description**: Default speaking duration per turn (in seconds)

**Type**: `number`

**Required**: No

**Default**: `60`

**Example**:
```bash
DEFAULT_SPEAKING_TIME=90
```

**Usage**:
```javascript
const speakingTime = parseInt(process.env.DEFAULT_SPEAKING_TIME) || 60
```

**Recommendations**:
- 30s: Quick discussions
- 60s: Standard discussions
- 90-120s: In-depth discussions

---

#### HUGGINGFACE_API_KEY

**Description**: API key for Hugging Face Inference API (AI topic generation)

**Type**: `string`

**Required**: No (fallback topics used if missing)

**Default**: None

**Example**:
```bash
HUGGINGFACE_API_KEY=hf_xxxxxxxxxxxxxxxxxxxxx
```

**How to Get**:
1. Sign up at https://huggingface.co
2. Go to Settings → Access Tokens
3. Create new token (read permission)
4. Copy token

**Usage**:
```javascript
const apiKey = process.env.HUGGINGFACE_API_KEY
if (apiKey && apiKey !== 'your_huggingface_api_key_here') {
  // Use AI generation
} else {
  // Use fallback topics
}
```

**Notes**:
- Free tier has rate limits
- Not required for basic functionality
- Graceful fallback if missing or invalid

---

#### ALLOWED_ORIGINS

**Description**: Comma-separated list of allowed CORS origins

**Type**: `string` (comma-separated URLs)

**Required**: No (defaults used)

**Default (Development)**:
```bash
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5174
```

**Default (Production)**:
```bash
ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

**Example**:
```bash
ALLOWED_ORIGINS=https://app.example.com,https://www.example.com
```

**Usage**:
```javascript
const allowedOrigins = process.env.ALLOWED_ORIGINS
  ? process.env.ALLOWED_ORIGINS.split(',')
  : defaultOrigins

io = new Server(server, {
  cors: { origin: allowedOrigins }
})
```

**Important**:
- Must match exact frontend URL
- Include protocol (http/https)
- No trailing slashes
- Critical for WebSocket connections

---

#### CORS_ORIGIN (Legacy)

**Description**: Single CORS origin (legacy, use ALLOWED_ORIGINS instead)

**Type**: `string` (URL)

**Required**: No

**Example**:
```bash
CORS_ORIGIN=https://your-frontend.vercel.app
```

**Notes**:
- Supported for backward compatibility
- Use ALLOWED_ORIGINS for multiple origins
- Will be deprecated in future versions

---

#### DATABASE_PATH

**Description**: Path to SQLite database file

**Type**: `string` (file path)

**Required**: No

**Default**: `./data/discussions.db`

**Example**:
```bash
DATABASE_PATH=/var/lib/gupshup/database.db
```

**Notes**:
- Directory must exist and be writable
- Relative to server root
- Backup this file regularly

---

## Configuration Files

### Tailwind CSS Configuration

**Location**: `client/tailwind.config.js`

**Purpose**: Styling configuration

**Key Settings**:
```javascript
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}"
  ],
  theme: {
    extend: {
      colors: {
        // Custom colors
      },
      animation: {
        // Custom animations
      }
    }
  }
}
```

---

### Vite Configuration

**Location**: `client/vite.config.js`

**Purpose**: Build tool configuration

**Key Settings**:
```javascript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173
  },
  build: {
    outDir: 'dist',
    sourcemap: false
  }
})
```

**Build Command**: `npm run build`

**Output**: `client/dist/`

---

### Package.json Scripts

**Root**: `package.json`
```json
{
  "scripts": {
    "dev": "Run both client and server",
    "dev:client": "Run client only",
    "dev:server": "Run server only",
    "build": "Build client for production",
    "start": "Start production server"
  }
}
```

**Client**: `client/package.json`
```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }
}
```

**Server**: `server/package.json`
```json
{
  "scripts": {
    "dev": "nodemon src/server.js",
    "start": "node src/server.js"
  }
}
```

---

## Setup Instructions

### First-Time Setup

#### 1. Clone Repository
```bash
git clone https://github.com/navgurukul/GupShupCafe.git
cd GupShupCafe
```

#### 2. Run Setup Script
```bash
# Linux/Mac
bash setup.sh

# Windows
setup.bat
```

**What it does**:
- Installs root dependencies
- Installs client dependencies
- Installs server dependencies
- Creates `.env` files from examples
- Creates data directory

#### 3. Configure Environment Variables

**Client** (`client/.env`):
```bash
VITE_API_URL=http://localhost:3003
```

**Server** (`server/.env`):
```bash
PORT=3003
NODE_ENV=development
MIN_PARTICIPANTS=1
MAX_PARTICIPANTS=8
DEFAULT_SPEAKING_TIME=60
HUGGINGFACE_API_KEY=your_api_key_here
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5174
```

#### 4. Start Development Servers
```bash
npm run dev
```

**Access**:
- Frontend: http://localhost:5173
- Backend: http://localhost:3003
- Health check: http://localhost:3003/api/health

---

### Production Setup

#### Vercel (Frontend)

**1. Connect Repository**:
- Go to Vercel dashboard
- Import Git repository
- Select `client` as root directory

**2. Configure Build**:
- Framework: Vite
- Build Command: `npm run build`
- Output Directory: `dist`

**3. Environment Variables**:
```
VITE_API_URL=https://your-backend.onrender.com
```

**4. Deploy**:
- Automatic on push to main branch

---

#### Render (Backend)

**1. Create Web Service**:
- Connect Git repository
- Root Directory: `server`

**2. Configure Build**:
- Build Command: `npm install`
- Start Command: `npm start`

**3. Environment Variables**:
```
NODE_ENV=production
PORT=3003
MIN_PARTICIPANTS=2
MAX_PARTICIPANTS=8
DEFAULT_SPEAKING_TIME=60
HUGGINGFACE_API_KEY=your_api_key_here
ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

**4. Persistent Disk** (Optional):
- Mount path: `/opt/render/project/src/data`
- For SQLite persistence

**5. Deploy**:
- Automatic on push to main branch

---

## Configuration Best Practices

### Security

**Don't**:
- ❌ Commit `.env` files to Git
- ❌ Share API keys publicly
- ❌ Use development settings in production
- ❌ Hardcode secrets in source code

**Do**:
- ✅ Use `.env.example` for documentation
- ✅ Add `.env` to `.gitignore`
- ✅ Rotate API keys regularly
- ✅ Use platform environment variables in production

---

### Environment-Specific Configurations

**Development**:
- Verbose logging
- CORS: localhost origins
- Long timeouts
- Error stack traces

**Production**:
- Minimal logging
- CORS: production domains only
- Short timeouts
- Generic error messages
- Compression enabled
- HTTPS enforced

**Example Pattern**:
```javascript
const config = {
  logging: process.env.NODE_ENV === 'development' ? 'verbose' : 'error',
  corsOrigins: process.env.ALLOWED_ORIGINS?.split(',') || defaultOrigins,
  timeout: process.env.NODE_ENV === 'production' ? 30000 : 60000
}
```

---

### Validating Configuration

**Startup Checks**:
```javascript
// server/src/server.js
console.log('🔍 Validating configuration...')
console.log(`PORT: ${PORT}`)
console.log(`NODE_ENV: ${process.env.NODE_ENV || 'development'}`)
console.log(`CORS Origins: ${ALLOWED_ORIGINS.join(', ')}`)
console.log(`Hugging Face: ${process.env.HUGGINGFACE_API_KEY ? 'Configured' : 'Not configured'}`)
```

**Health Check Endpoint**:
```javascript
app.get('/api/config', (req, res) => {
  res.json({
    minParticipants: parseInt(process.env.MIN_PARTICIPANTS) || 1,
    maxParticipants: parseInt(process.env.MAX_PARTICIPANTS) || 8,
    defaultSpeakingTime: parseInt(process.env.DEFAULT_SPEAKING_TIME) || 60,
    features: {
      aiTopics: !!process.env.HUGGINGFACE_API_KEY
    }
  })
})
```

---

## Troubleshooting Configuration Issues

### Issue: Frontend can't connect to backend

**Symptoms**:
- Socket.IO connection errors
- "Failed to fetch" errors
- CORS errors in browser console

**Solutions**:
1. Check `VITE_API_URL` matches backend URL
2. Ensure backend is running
3. Check CORS configuration in backend
4. Verify network connectivity
5. Check browser console for exact error

**Debug**:
```javascript
// client/src/contexts/SocketContext.jsx
console.log('Connecting to:', import.meta.env.VITE_API_URL)
```

---

### Issue: CORS errors in production

**Symptoms**:
- "Access-Control-Allow-Origin" errors
- Socket.IO connection refused

**Solutions**:
1. Verify `ALLOWED_ORIGINS` includes exact frontend URL
2. Include protocol (https://)
3. No trailing slashes
4. Redeploy backend after changes

**Test**:
```bash
curl -H "Origin: https://your-frontend.vercel.app" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS \
     https://your-backend.onrender.com/api/health
```

---

### Issue: Environment variables not loading

**Symptoms**:
- Default values used instead of configured values
- Features not working (e.g., AI topics)

**Solutions**:
1. Verify `.env` file exists in correct directory
2. Check file is named exactly `.env` (not `.env.txt`)
3. Restart dev server after changes
4. Check for syntax errors (no spaces around `=`)

**Debug**:
```javascript
console.log('Environment variables:', {
  PORT: process.env.PORT,
  NODE_ENV: process.env.NODE_ENV,
  HAS_API_KEY: !!process.env.HUGGINGFACE_API_KEY
})
```

---

### Issue: Database not persisting in production

**Symptoms**:
- Analytics reset on server restart
- Sessions lost

**Solutions**:
1. Configure persistent disk in Render
2. Mount at correct path
3. Verify write permissions
4. Check disk space

**Verify**:
```bash
# In Render shell
ls -la /opt/render/project/src/data/
```

---

## Configuration Checklist

### Development Setup
- [ ] Node.js 18+ installed
- [ ] Dependencies installed (`npm run install:all`)
- [ ] Client `.env` created from example
- [ ] Server `.env` created from example
- [ ] `VITE_API_URL` points to localhost:3003
- [ ] Data directory exists (`server/data`)
- [ ] Dev servers start without errors
- [ ] Can access frontend at localhost:5173
- [ ] Health check returns success

### Production Deployment
- [ ] Frontend deployed to Vercel
- [ ] Backend deployed to Render
- [ ] `VITE_API_URL` points to production backend
- [ ] `ALLOWED_ORIGINS` includes production frontend
- [ ] Environment variables configured in platforms
- [ ] HTTPS certificates active
- [ ] Health check accessible
- [ ] WebSocket connections working
- [ ] Database persisting (if configured)
- [ ] Monitoring/logging active

---

## Configuration Reference Summary

| Variable | Type | Default | Required | Scope |
|----------|------|---------|----------|-------|
| `VITE_API_URL` | URL | - | Yes | Client |
| `PORT` | number | 3003 | No | Server |
| `NODE_ENV` | string | development | No | Server |
| `MIN_PARTICIPANTS` | number | 1 | No | Server |
| `MAX_PARTICIPANTS` | number | 8 | No | Server |
| `DEFAULT_SPEAKING_TIME` | number | 60 | No | Server |
| `HUGGINGFACE_API_KEY` | string | - | No | Server |
| `ALLOWED_ORIGINS` | CSV | localhost:5173,5174 | No | Server |
| `CORS_ORIGIN` | URL | - | No | Server (legacy) |
| `DATABASE_PATH` | path | ./data/discussions.db | No | Server |
