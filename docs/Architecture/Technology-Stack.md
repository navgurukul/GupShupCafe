# Technology Stack Overview

## Frontend Technologies

### Core Framework & Build Tools

#### React 18.x
- **Purpose**: UI component library
- **Why**: Virtual DOM performance, large ecosystem, component reusability
- **Key Features Used**:
  - Functional components with Hooks
  - Context API for state management
  - React Router for navigation
  - Effect hooks for side effects

#### Vite 5.x
- **Purpose**: Build tool and development server
- **Why**: Fast HMR (Hot Module Replacement), optimized builds, ES modules
- **Benefits**:
  - Sub-second server start
  - Lightning-fast HMR
  - Optimized production builds
  - Native ES modules support

#### Tailwind CSS 3.x
- **Purpose**: Utility-first CSS framework
- **Why**: Rapid UI development, consistent design, small bundle size
- **Configuration**:
  - Custom color palette
  - Responsive breakpoints
  - Custom animations
  - PurgeCSS for optimization

### Routing & Navigation

#### React Router v6
- **Purpose**: Client-side routing
- **Features Used**:
  - Declarative routing
  - Protected routes
  - Route parameters
  - Programmatic navigation
  - Nested routes

### State Management

#### React Context API
- **Purpose**: Global state management
- **Contexts Implemented**:
  - `AuthContext`: User authentication state
  - `SocketContext`: WebSocket connection
  - `AudioContext`: WebRTC and audio management
- **Why Not Redux**: Simpler API, sufficient for app complexity

### Real-Time Communication

#### Socket.IO Client
- **Version**: 4.x
- **Purpose**: Real-time bidirectional communication
- **Features**:
  - Automatic reconnection
  - Event-based messaging
  - Room support
  - Binary data support
  - Authentication via handshake

#### WebRTC
- **Purpose**: Peer-to-peer audio streaming
- **APIs Used**:
  - `getUserMedia()`: Microphone access
  - `RTCPeerConnection`: P2P connections
  - `RTCDataChannel`: Optional data channel
  - STUN servers for NAT traversal
- **Configuration**:
  ```javascript
  {
    iceServers: [
      { urls: 'stun:stun.l.google.com:19302' },
      { urls: 'stun:stun1.l.google.com:19302' }
    ]
  }
  ```

---

## Backend Technologies

### Runtime & Framework

#### Node.js 18+
- **Purpose**: JavaScript runtime
- **Why**: Event-driven, non-blocking I/O, JavaScript everywhere
- **Features Used**:
  - ES modules (import/export)
  - Async/await
  - File system operations
  - HTTP/WebSocket servers

#### Express.js 4.x
- **Purpose**: Web application framework
- **Why**: Minimal, flexible, large middleware ecosystem
- **Middleware Used**:
  - `cors`: Cross-Origin Resource Sharing
  - `helmet`: Security headers
  - `express.json()`: JSON parsing
  - Custom error handling

### Real-Time Communication

#### Socket.IO Server
- **Version**: 4.x
- **Purpose**: WebSocket server with fallbacks
- **Features**:
  - Room management
  - Event broadcasting
  - Acknowledgments
  - Adapter for scaling (future)
- **Configuration**:
  ```javascript
  {
    cors: { origin: ALLOWED_ORIGINS },
    transports: ['websocket', 'polling'],
    allowEIO3: true
  }
  ```

### Database

#### SQLite 3.x
- **Purpose**: Embedded relational database
- **Why**: Zero-config, serverless, portable, sufficient for app scale
- **Tables**:
  - `sessions`: Discussion sessions
  - `participants`: User participation records
  - `topics`: Topic usage analytics
- **Limitations**: Single writer, file-based (not distributed)

### External Services

#### Hugging Face Inference API
- **Purpose**: AI-powered topic generation
- **Model Used**: Microsoft DialoGPT-medium
- **Fallback**: Predefined topic list when API unavailable
- **Rate Limits**: Free tier limitations apply

### Security

#### Helmet.js
- **Purpose**: HTTP security headers
- **Headers Set**:
  - X-Content-Type-Options
  - X-Frame-Options
  - X-XSS-Protection
  - Strict-Transport-Security (HTTPS)

#### CORS
- **Purpose**: Control cross-origin requests
- **Configuration**: Whitelist of allowed origins
- **Development**: `localhost:5173`, `localhost:5174`
- **Production**: Configurable via `ALLOWED_ORIGINS`

### Utilities

#### uuid
- **Purpose**: Generate unique identifiers
- **Usage**: Session IDs, user IDs, message IDs
- **Version**: v4 (random)

#### dotenv
- **Purpose**: Environment variable management
- **Usage**: Load `.env` files for configuration
- **Variables**: API keys, ports, CORS origins, etc.

#### node-fetch
- **Purpose**: HTTP client for API requests
- **Usage**: Calling Hugging Face API
- **Why**: Native fetch API for Node.js

---

## Development Tools

### Package Management

#### npm
- **Purpose**: Package manager and task runner
- **Scripts**:
  - `dev`: Start both client and server
  - `build`: Build production bundle
  - `start`: Start production server

#### Concurrently
- **Purpose**: Run multiple npm scripts in parallel
- **Usage**: `npm run dev` runs both client and server

### Code Quality

#### ESLint
- **Purpose**: JavaScript linting
- **Configuration**: `client/eslint.config.js`
- **Rules**: React best practices, hook dependencies

#### Prettier (Recommended)
- **Purpose**: Code formatting
- **Benefits**: Consistent code style across team

---

## Production Technologies

### Hosting

#### Vercel (Frontend)
- **Purpose**: Static site hosting with CDN
- **Features**:
  - Automatic deployments from Git
  - Preview deployments for PRs
  - Edge network (CDN)
  - HTTPS by default
  - Environment variables

#### Render (Backend)
- **Purpose**: Platform as a Service (PaaS)
- **Features**:
  - Automatic deployments from Git
  - Persistent disk for SQLite
  - Environment variables
  - HTTPS certificates
  - Health checks
  - Logs and metrics

### Infrastructure

#### STUN Servers
- **Purpose**: NAT traversal for WebRTC
- **Providers**: Google STUN servers (free)
- **Limitation**: No TURN (media relay) for complex NAT

---

## Browser APIs Used

### Media Devices API
```javascript
navigator.mediaDevices.getUserMedia({
  audio: {
    echoCancellation: true,
    noiseSuppression: true,
    autoGainControl: true
  }
})
```

### Web Audio API
```javascript
const audioContext = new AudioContext()
const analyser = audioContext.createAnalyser()
// Used for audio level visualization
```

### Local Storage API
```javascript
localStorage.setItem('auth', JSON.stringify(userData))
// Used for persisting authentication
```

### RTCPeerConnection API
```javascript
const pc = new RTCPeerConnection(config)
pc.addTrack(track, stream)
// Used for P2P audio connections
```

---

## Testing Technologies (Future Enhancement)

### Recommended Tools

#### Frontend Testing
- **Vitest**: Fast unit testing (Vite-native)
- **React Testing Library**: Component testing
- **Playwright**: E2E testing
- **MSW**: Mock Service Worker for API mocking

#### Backend Testing
- **Jest**: Unit and integration testing
- **Supertest**: HTTP endpoint testing
- **Socket.IO Client**: Socket event testing

---

## Performance Technologies

### Frontend Optimization

#### Code Splitting
```javascript
const LazyComponent = React.lazy(() => import('./Component'))
```

#### Bundle Analysis
- **vite-plugin-visualizer**: Bundle size analysis
- **lighthouse**: Performance auditing

### Backend Optimization

#### Compression
- **compression**: Gzip compression middleware
- **express-rate-limit**: Rate limiting (future)

---

## Monitoring & Analytics (Recommended)

### Error Tracking
- **Sentry**: Real-time error tracking
- **LogRocket**: Session replay

### Performance Monitoring
- **New Relic**: APM (Application Performance Monitoring)
- **Datadog**: Infrastructure monitoring

### Analytics
- **Google Analytics**: User behavior tracking
- **Mixpanel**: Event-based analytics

---

## Version Control & CI/CD

### Git & GitHub
- **Version Control**: Git
- **Repository Hosting**: GitHub
- **Branching Strategy**: Feature branches, main branch

### Continuous Deployment
- **Vercel**: Auto-deploy on push to main (frontend)
- **Render**: Auto-deploy on push to main (backend)
- **Preview Deployments**: Available for both platforms

---

## Security Technologies

### HTTPS/TLS
- **Vercel**: Automatic HTTPS with Let's Encrypt
- **Render**: Automatic HTTPS with Let's Encrypt

### Environment Variables
- **Development**: `.env` files (not committed)
- **Production**: Platform environment variable management

### Input Validation
- **express-validator**: (Recommended for future)
- Manual validation in current implementation

---

## Documentation Tools

### Markdown
- **Purpose**: Documentation format
- **Files**: All `.md` files in `/docs`
- **Benefits**: Version controlled, easy to read

### Mermaid (Recommended)
- **Purpose**: Diagram generation
- **Usage**: UML, sequence, flowcharts in markdown

---

## Alternative Technologies Considered

### State Management
- **Redux**: Too complex for current needs
- **MobX**: Different paradigm, Context API sufficient
- **Zustand**: Lighter than Redux, but Context API works

### Database
- **PostgreSQL**: More powerful but requires server
- **MongoDB**: NoSQL not needed for relational data
- **Redis**: For caching/sessions in scaled setup

### Real-Time
- **WebSockets (native)**: Less feature-rich than Socket.IO
- **Server-Sent Events**: One-way communication only
- **Long Polling**: Higher latency, more overhead

### Build Tools
- **Webpack**: Slower than Vite, more complex config
- **Parcel**: Less ecosystem, less control
- **esbuild**: Lower-level, Vite uses it internally

---

## Technology Decision Matrix

| Feature | Technology | Alternatives | Decision Reason |
|---------|-----------|--------------|-----------------|
| Frontend Framework | React | Vue, Svelte, Angular | Largest ecosystem, team familiarity |
| Build Tool | Vite | Webpack, Parcel | Speed, DX (Developer Experience) |
| Styling | Tailwind CSS | Bootstrap, Material-UI | Utility-first, customizable |
| Backend | Node.js + Express | Python/FastAPI, Go | JavaScript everywhere, async I/O |
| Database | SQLite | PostgreSQL, MySQL | Simplicity, zero-config |
| Real-Time | Socket.IO | Native WS, SSE | Feature-rich, fallbacks |
| P2P Audio | WebRTC | Agora, Twilio | Free, standards-based |
| Hosting | Vercel + Render | AWS, DigitalOcean | Free tier, easy deployment |

---

## Future Technology Roadmap

### Short Term (3-6 months)
- TypeScript for type safety
- React Query for data fetching
- Vitest for unit testing

### Medium Term (6-12 months)
- Redis for state management
- PostgreSQL for scalable DB
- Docker for containerization

### Long Term (1+ years)
- Kubernetes for orchestration
- Microservices architecture
- SFU for audio routing
