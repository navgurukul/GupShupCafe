/**
 * Application Constants
 * Centralized configuration values and constants
 */

// API Configuration
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_URL || "http://localhost:3003",
  SOCKET_URL: import.meta.env.VITE_SOCKET_URL || "http://localhost:3003",
  TIMEOUT: 30000, // 30 seconds
};

// Discussion Settings
export const DISCUSSION_CONFIG = {
  MIN_PARTICIPANTS: 2,
  MAX_PARTICIPANTS: 8,
  DEFAULT_SPEAKING_TIME: 60, // seconds
  DEFAULT_MAX_ROUNDS: 3,
  MIN_SPEAKING_TIME: 30, // seconds
  MAX_SPEAKING_TIME: 300, // seconds (5 minutes)
};

// WebRTC Configuration
export const WEBRTC_CONFIG = {
  STUN_SERVERS: [
    "stun:stun.l.google.com:19302",
    "stun:stun1.l.google.com:19302",
    "stun:stun2.l.google.com:19302",
  ],
  ICE_GATHERING_TIMEOUT: 5000, // 5 seconds
  CONNECTION_TIMEOUT: 10000, // 10 seconds
};

// Audio Settings
export const AUDIO_CONFIG = {
  SAMPLE_RATE: 48000,
  SAMPLE_SIZE: 16,
  CHANNEL_COUNT: 1,
  ECHO_CANCELLATION: true,
  NOISE_SUPPRESSION: true,
  AUTO_GAIN_CONTROL: true,
  AUDIO_LEVEL_UPDATE_INTERVAL: 100, // milliseconds
};

// User Roles
export const USER_ROLES = {
  SPEAKER: "speaker",
  LISTENER: "listener",
};

// Room Status
export const ROOM_STATUS = {
  WAITING: "waiting",
  IN_PROGRESS: "in-progress",
  ENDED: "ended",
};

// CEFR Levels
export const CEFR_LEVELS = {
  A1: { level: "A1", name: "Beginner", color: "red" },
  A2: { level: "A2", name: "Elementary", color: "orange" },
  B1: { level: "B1", name: "Intermediate", color: "yellow" },
  B2: { level: "B2", name: "Upper Intermediate", color: "green" },
  C1: { level: "C1", name: "Advanced", color: "blue" },
  C2: { level: "C2", name: "Proficient", color: "purple" },
};

// Feedback Thresholds
export const FEEDBACK_THRESHOLDS = {
  GRAMMAR_EXCELLENT: 90,
  GRAMMAR_GOOD: 75,
  GRAMMAR_FAIR: 60,
  VOCABULARY_EXCELLENT: 85,
  VOCABULARY_GOOD: 70,
  VOCABULARY_FAIR: 55,
  FLUENCY_EXCELLENT: 80,
  FLUENCY_GOOD: 65,
  FLUENCY_FAIR: 50,
};

// Socket Events
export const SOCKET_EVENTS = {
  // Connection events
  CONNECT: "connect",
  DISCONNECT: "disconnect",
  CONNECT_ERROR: "connect_error",

  // Room events
  JOIN_ROOM: "join-room",
  LEAVE_ROOM: "leave-room",
  ROOM_UPDATE: "room-update",

  // Participant events
  PARTICIPANTS_UPDATE: "participants-update",
  USER_READY: "user-ready",
  ROLE_CHANGE: "role-change",

  // Discussion events
  DISCUSSION_STARTED: "discussion-started",
  DISCUSSION_ENDED: "discussion-ended",
  SPEAKER_CHANGE: "speaker-change",
  NEXT_SPEAKER: "next-speaker",

  // WebRTC events
  WEBRTC_OFFER: "webrtc-offer",
  WEBRTC_ANSWER: "webrtc-answer",
  WEBRTC_ICE_CANDIDATE: "webrtc-ice-candidate",
  READY_FOR_WEBRTC: "ready-for-webrtc",

  // WebRTC connection state events
  WEBRTC_CONNECTION_STATE: "webrtc-connection-state",
  WEBRTC_CONNECTION_FAILED: "webrtc-connection-failed",
  WEBRTC_CONNECTION_RESTORED: "webrtc-connection-restored",
  WEBRTC_CONNECTION_CLOSED: "webrtc-connection-closed",
  WEBRTC_PEER_DISCONNECTED: "webrtc-peer-disconnected",
  WEBRTC_CLEANUP_REQUEST: "webrtc-cleanup-request",
  WEBRTC_CONNECTION_TEST: "webrtc-connection-test",
  WEBRTC_CONNECTION_VERIFIED: "webrtc-connection-verified",
  WEBRTC_ERROR: "webrtc-error",
  WEBRTC_STATS_UPDATE: "webrtc-stats-update",
  WEBRTC_QUALITY_WARNING: "webrtc-quality-warning",

  // Audio state events
  AUDIO_STATE_CHANGE: "audio-state-change",
  AUDIO_LEVEL_UPDATE: "audio-level-update",
  MICROPHONE_PERMISSION_CHANGE: "microphone-permission-change",

  // WebRTC acknowledgment events
  WEBRTC_OFFER_ACK: "webrtc-offer-ack",
  WEBRTC_ANSWER_ACK: "webrtc-answer-ack",
  WEBRTC_ICE_ACK: "webrtc-ice-ack",

  // WebRTC lifecycle events
  WEBRTC_CONNECTION_CREATED: "webrtc-connection-created",
  WEBRTC_CONNECTION_DESTROYED: "webrtc-connection-destroyed",
  WEBRTC_CONNECTION_PAUSED: "webrtc-connection-paused",
  WEBRTC_CONNECTION_RESUMED: "webrtc-connection-resumed",

  // Feedback events
  ENGLISH_FEEDBACK: "english-feedback",
  TRANSCRIPT_UPDATE: "transcript-update",
};

// UI Constants
export const UI_CONFIG = {
  FEEDBACK_AUTO_DISMISS_TIME: 10000, // 10 seconds
  TOAST_DURATION: 3000, // 3 seconds
  DEBOUNCE_DELAY: 300, // milliseconds
  ANIMATION_DURATION: 300, // milliseconds
};

// Error Messages
export const ERROR_MESSAGES = {
  MIC_PERMISSION_DENIED:
    "Microphone access denied. Please enable it in your browser settings.",
  MIC_NOT_FOUND:
    "No microphone found. Please connect a microphone and try again.",
  SOCKET_CONNECTION_FAILED:
    "Failed to connect to server. Please check your internet connection.",
  ROOM_JOIN_FAILED: "Failed to join room. Please try again.",
  WEBRTC_CONNECTION_FAILED:
    "Failed to establish audio connection. Please check your network settings.",
  AUTHENTICATION_REQUIRED: "Please log in to continue.",
};

// Success Messages
export const SUCCESS_MESSAGES = {
  ROOM_CREATED: "Room created successfully!",
  ROOM_JOINED: "Joined room successfully!",
  MIC_ENABLED: "Microphone enabled successfully.",
  FEEDBACK_RECEIVED: "Feedback received!",
};

export default {
  API_CONFIG,
  DISCUSSION_CONFIG,
  WEBRTC_CONFIG,
  AUDIO_CONFIG,
  USER_ROLES,
  ROOM_STATUS,
  CEFR_LEVELS,
  FEEDBACK_THRESHOLDS,
  SOCKET_EVENTS,
  UI_CONFIG,
  ERROR_MESSAGES,
  SUCCESS_MESSAGES,
};
