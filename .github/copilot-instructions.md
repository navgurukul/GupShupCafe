# GupShup Cafe – Copilot Guide

## Architecture snapshot
- React 18 + Vite frontend in `client/` drives UI (pages in `src/pages`, contexts in `src/contexts`). Context providers (`AuthContext`, `SocketContext`, `AudioContext`) wrap `main.jsx`.
- Real-time flow: client uses Socket.io + WebRTC; `AudioContext.jsx` manages microphone permission, local/remote streams, and emits `webrtc-*` events that Node/FastAPI backends simply relay.
- Backend FastAPI in `server_py/` exposes `/api/*` REST endpoints and Socket.io namespaces on port `3003`, backed by SQLite.

## Everyday commands
- Install everything with `npm run install:all`; Server only with `npm run install:py`.
- Launch Vite + Python backend concurrently using `npm run dev` (runs `python main.py` via `concurrently`).
- Run the React lint rules with `cd client && npm run lint`; execute backend tests with `npm run test:server:py` (pytest in `server_py/tests`).

## Environment defaults
- Copy `client/.env.example` → `.env` and set `VITE_API_URL` / `VITE_SOCKET_URL` to the backend URL (default `http://localhost:3003`).
- The Express server reads `server/.env` (see `.env.example`) for `HUGGINGFACE_API_KEY`, `DATABASE_URL`, and speaking timers; FastAPI mirrors the same variables via `server_py/.env`.
- SQLite files are local (`server/data/roundtable.db`, `server_py/data/roundtable.db`). Keep paths consistent when scripting migrations.

## Frontend patterns to follow
- Routing lives in `client/src/App.jsx` with `ProtectedRoute` gating roundtable routes; new routes should hook into `AuthContext` the same way.
- Socket usage flows through `SocketContext.jsx`. When adding events, mirror the handler registration pattern there and document payload shapes.
- `AudioContext.jsx` optimizes WebRTC for audio-only calls (Opus prioritization, STUN servers, hidden `<audio>` sinks). Respect its `toggleMute`, `enableSpeaking`, and `ready-for-webrtc` handshake when extending audio features.
- UI components expect participant objects shaped like `participants-update` payloads (`id`, `socketId`, `anonymousName`, `role`, `isReady`). Keep that schema intact to avoid layout issues in `RoundtableView.jsx`.

## Backend cues (Express + FastAPI)
- Legacy Express entrypoint (`server/src/server.js`) wires Socket.io via `setupSocketHandlers`. If you add events, update both `socketHandlers.js` and the shared `roomManager.js` to keep timer/turn logic consistent.
- Legacy AI topics live in `server/src/ai/topicGenerator.js`; missing Hugging Face keys fall back to curated topics—preserve that optional behaviour.
- Current FastAPI equivalent routes sit in `server_py/src/api/routes.py`, with async DB helpers in `server_py/src/database/database.py`. Maintain the `{ "success": bool, "data": ... }` envelope so the client fetches keep working.
- `server_py/src/socket/socket_handlers.py` mirrors the JavaScript handlers; when changing room state shape, adjust `room_manager.py` and keep `participants-update` serialization minimal (id, anonymousName, role, readiness).
- LLM tutor utilities under `server_py/src/llmTutor/` rely on the MCP transport defined in `debate_room_facilitator.py` (`streamablehttp_client` hitting `http://localhost:8000/mcp/`). If you add tools, register them via `MCPClient` and sync dependencies in `requirements.txt`.

## Working agreements
- Log prefixes (`[Audio]`, `[Backend]`, `[WebRTC]`) are used for tracing cross-stack issues—preserve them or extend consistently.
- When introducing new real-time events or REST routes, update the living docs under `docs/API Reference/` so tutors and UI stay aligned.
- Save all the relevant documentation for the changes done in the `docs/Miscellaneous/` folder.
- For every new change, make sure to create/update the regression tests accordingly. Ensure tests are passing before finalizing a PR or provide clear justification for every failing test case.
- **IMPORTANT**: Keep adding every code update summary to `docs/product_docs_and_updates.md` along with date, time, and an informative commit message about the update. This file serves as a living changelog for all product and architectural changes.
- IGNORE `clientMain` and `server` folders. 