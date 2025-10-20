import React, { useState, useEffect, useRef } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useSocket } from "../contexts/SocketContext";
import { useAuth } from "../contexts/AuthContext";
import { useAudio } from "../contexts/AudioContext";
import URLTest from "../components/URLTest";
import {
  Users,
  Clock,
  Mic,
  MicOff,
  LogOut,
  Settings,
  Plus,
  BookOpen,
  Atom,
  PenTool,
  Brain,
  Star,
  Copy,
  Share2,
  Check,
} from "lucide-react";

import { generateAvatarColor } from "../utils/helpers";
import { fetchWaitingRooms } from "../services/api";
import { createParticipantForRoom } from "../utils/participantHelpers";

// Global flag to prevent multiple late join checks (accessible across components)
if (typeof window !== "undefined") {
  window.lateJoinCheckInProgress = window.lateJoinCheckInProgress || false;
}

// CEFR Levels
const cefrLevels = [
  {
    id: "A1",
    label: "A1 - Beginner",
    color: "bg-red-100 text-red-800",
    description: "Can understand and use familiar everyday expressions",
  },
  {
    id: "A2",
    label: "A2 - Elementary",
    color: "bg-orange-100 text-orange-800",
    description: "Can communicate in simple routine tasks",
  },
  {
    id: "B1",
    label: "B1 - Intermediate",
    color: "bg-yellow-100 text-yellow-800",
    description: "Can deal with most situations while travelling",
  },
  {
    id: "B2",
    label: "B2 - Upper Intermediate",
    color: "bg-blue-100 text-blue-800",
    description: "Can understand complex texts on concrete and abstract topics",
  },
  {
    id: "C1",
    label: "C1 - Advanced",
    color: "bg-green-100 text-green-800",
    description: "Can express ideas fluently and spontaneously",
  },
  {
    id: "C2",
    label: "C2 - Proficiency",
    color: "bg-purple-100 text-purple-800",
    description: "Can understand virtually everything heard or read",
  },
];

// Suggested Anonymous Names
const suggestedNames = [
  "ThoughtfulMind",
  "KindPerson",
  "WiseVoice",
  "CuriousExplorer",
  "InsightfulSpeaker",
  "CreativeThinker",
];

// Topic Categories
const topicCategories = [
  {
    id: "currentAffairs",
    label: "Current Affairs",
    color: "bg-red-100 text-red-800",
  },
  {
    id: "scienceAndTechnology",
    label: "Science & Technology",
    color: "bg-blue-100 text-blue-800",
  },
  {
    id: "literature",
    label: "Literature",
    color: "bg-purple-100 text-purple-800",
  },
  { id: "education", label: "Education", color: "bg-green-100 text-green-800" },
  { id: "politics", label: "Politics", color: "bg-yellow-100 text-yellow-800" },
  {
    id: "environment",
    label: "Environment",
    color: "bg-emerald-100 text-emerald-800",
  },
  { id: "healthcare", label: "Healthcare", color: "bg-pink-100 text-pink-800" },
  { id: "business", label: "Business", color: "bg-orange-100 text-orange-800" },
  { id: "sports", label: "Sports", color: "bg-indigo-100 text-indigo-800" },
  {
    id: "entertainment",
    label: "Entertainment",
    color: "bg-violet-100 text-violet-800",
  },
  { id: "philosophy", label: "Philosophy", color: "bg-gray-100 text-gray-800" },
  { id: "history", label: "History", color: "bg-amber-100 text-amber-800" },
];

/**
 * Lobby Page Component
 * Waiting area until minimum participants (1+) join the session
 */
function LobbyPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { socket, connected, joinRoom, signalReady } = useSocket();
  const { user, anonymousName, logout } = useAuth();
  const {
    audioEnabled,
    micPermission,
    requestMicrophoneAccess,
    isWebRTCSupported,
    userRole,
    updateUserRole,
  } = useAudio();

  const [participants, setParticipants] = useState([]);
  const [roomId, setRoomId] = useState("general");
  const [selectedRole, setSelectedRole] = useState("speaker"); // Default to speaker
  const [minParticipants, setMinParticipants] = useState(1); // Default to 1 for solo testing
  const [waitingTime, setWaitingTime] = useState(0);
  const [systemMessage, setSystemMessage] = useState("Connecting to lobby...");
  const [isNavigating, setIsNavigating] = useState(false);

  // New state for room management
  const [showCreateRoom, setShowCreateRoom] = useState(false);
  const [newRoomId, setNewRoomId] = useState("");
  const [currentRoom, setCurrentRoom] = useState(null);

  // New room creation form state
  const [roomForm, setRoomForm] = useState({
    room_name: "",
    max_participants: 6,
    topic_category: "",
    cefr_level: "",
  });
  const [hostAnonymousName, setHostAnonymousName] = useState("");

  // Room sharing state
  const [showShareModal, setShowShareModal] = useState(false);
  const [shareableLink, setShareableLink] = useState("");
  const [linkCopied, setLinkCopied] = useState(false);
  const [joinedViaLink, setJoinedViaLink] = useState(false);

  // Join room modal state
  const [showJoinModal, setShowJoinModal] = useState(false);
  const [pendingRoomData, setPendingRoomData] = useState(null);
  const [joiningAnonymousName, setJoiningAnonymousName] = useState("");

  // Check if we're on a room-specific lobby route (any /lobby/:roomId)
  const isInRoomLobby = location.pathname.startsWith("/lobby/") && location.pathname !== "/lobby";

  // Waiting rooms from backend
  const [waitingRooms, setWaitingRooms] = useState([]);
  const [roomsLoading, setRoomsLoading] = useState(true);

  // Fetch waiting rooms from backend
  useEffect(() => {
    const loadWaitingRooms = async () => {
      try {
        setRoomsLoading(true);
        console.log('[Lobby][Debug] Fetching waiting rooms from backend...');
        const rooms = await fetchWaitingRooms();
        console.log('[Lobby][Debug] Received waiting rooms:', rooms);
        setWaitingRooms(rooms);
      } catch (error) {
        console.error('[Lobby][Debug] Error fetching waiting rooms:', error);
        setWaitingRooms([]);
      } finally {
        setRoomsLoading(false);
      }
    };

    // Always load waiting rooms for the main lobby
    loadWaitingRooms();

    // Refresh room list every 10 seconds
    const interval = setInterval(loadWaitingRooms, 10000);
    return () => clearInterval(interval);
  }, []);

  // Handle URL parameters for room joining
  useEffect(() => {
    // Get URL parameters from multiple sources to ensure detection
    const windowSearch = window.location.search;
    const routerSearch = location.search;
    const windowHref = window.location.href;

    // Also try parsing the full URL directly
    let directUrlParams = null;
    try {
      const url = new URL(windowHref);
      directUrlParams = url.searchParams;
    } catch (e) {
      console.log(`[Lobby][Debug] Failed to parse URL: ${e.message}`);
    }

    console.log(`[Lobby][Debug] === URL DEBUGGING ===`);
    console.log(`[Lobby][Debug] Full window.location.href: ${windowHref}`);
    console.log(`[Lobby][Debug] window.location.search: "${windowSearch}"`);
    console.log(`[Lobby][Debug] React router location.search: "${routerSearch}"`);
    console.log(`[Lobby][Debug] location.pathname: "${location.pathname}"`);
    console.log(`[Lobby][Debug] Direct URL parsing available: ${!!directUrlParams}`);

    // Try multiple parameter sources
    const sources = [
      { name: 'window.location.search', search: windowSearch },
      { name: 'router location.search', search: routerSearch },
      { name: 'direct URL parsing', search: directUrlParams ? directUrlParams.toString() : '' }
    ];

    let roomFromUrl = null;
    let roleFromUrl = 'speaker';
    let workingSource = null;

    // Try each source until we find room parameters
    for (const source of sources) {
      if (source.search) {
        const testParams = source.name === 'direct URL parsing'
          ? directUrlParams
          : new URLSearchParams(source.search);
        const testRoom = testParams.get('room');
        const testRole = testParams.get('role') || 'speaker';

        console.log(`[Lobby][Debug] Testing ${source.name}: room="${testRoom}", role="${testRole}"`);

        if (testRoom && testRoom.trim() !== '') {
          roomFromUrl = testRoom;
          roleFromUrl = testRole;
          workingSource = source.name;
          console.log(`[Lobby][Debug] ✅ Found parameters using ${source.name}`);
          break;
        }
      }
    }

    console.log(`[Lobby][Debug] Final result - Room: "${roomFromUrl}", Role: "${roleFromUrl}", Source: ${workingSource}`);
    console.log(`[Lobby][Debug] Socket status - Socket: ${!!socket}, Connected: ${connected}`);
    console.log(`[Lobby][Debug] Current state - RoomId: "${roomId}", IsInRoomLobby: ${isInRoomLobby}`);
    console.log(`[Lobby][Debug] === END URL DEBUGGING ===`);

    if (roomFromUrl && roomFromUrl.trim() !== '') {
      console.log(`[Lobby][Debug] ✅ Found room in URL: ${roomFromUrl} as ${roleFromUrl}`);
      console.log(`[Lobby][Debug] Redirecting to room-specific lobby page`);

      // Navigate to the room-specific lobby route
      const targetPath = `/lobby/${roomFromUrl}?role=${roleFromUrl}`;
      if (location.pathname + location.search !== targetPath) {
        console.log(`[Lobby][Debug] Redirecting from "${location.pathname}" to "${targetPath}"`);
        navigate(targetPath, { replace: true });
      }
    } else {
      console.log(`[Lobby][Debug] ❌ No room found in URL or empty room`);
      console.log(`[Lobby][Debug] Checked sources:`, sources.map(s => `${s.name}: "${s.search}"`));
    }
  }, [location.search, socket, connected, roomId, joinRoom, navigate, location.pathname, isInRoomLobby]);

  // Map backend room data to frontend format
  const mapBackendRoomToFrontend = (backendRoom) => {
    // Map topic category to icon and color
    const categoryMap = {
      education: { icon: BookOpen, color: "bg-blue-500" },
      scienceAndTechnology: { icon: Atom, color: "bg-green-500" },
      literature: { icon: PenTool, color: "bg-purple-500" },
      currentAffairs: { icon: Brain, color: "bg-red-500" },
      politics: { icon: Users, color: "bg-yellow-500" },
      environment: { icon: Users, color: "bg-emerald-500" },
      healthcare: { icon: Users, color: "bg-pink-500" },
      business: { icon: Users, color: "bg-orange-500" },
      sports: { icon: Users, color: "bg-indigo-500" },
      entertainment: { icon: Users, color: "bg-violet-500" },
      philosophy: { icon: Users, color: "bg-gray-500" },
      history: { icon: Users, color: "bg-amber-500" },
    };

    const categoryInfo = categoryMap[backendRoom.topic_category] || { icon: Users, color: "bg-gray-500" };

    return {
      roomId: backendRoom.room_id,
      room_name: backendRoom.room_name,
      icon: categoryInfo.icon,
      color: categoryInfo.color,
      description: backendRoom.topic_title || `Room for ${backendRoom.topic_category}`,
      cefr_level: backendRoom.cefr_level,
      topic_category: backendRoom.topic_category,
      max_participants: backendRoom.max_participants,
      participant_count: backendRoom.participant_count || 0,
      status: backendRoom.status,
      created_at: backendRoom.created_at
    };
  };

  // Combine backend rooms with predefined rooms (backend rooms take priority)
  const allWaitingRooms = React.useMemo(() => {
    const backendMapped = waitingRooms.map(mapBackendRoomToFrontend);
    // Only show predefined rooms if no backend rooms are available
    return backendMapped;
  }, [waitingRooms]);

  // Room sharing functions
  const generateShareableLink = (roomIdParam, role = 'speaker') => {
    // Use the current window location to ensure correct port
    const currentOrigin = window.location.origin;
    // Generate URL with room-specific path
    return `${currentOrigin}/lobby/${roomIdParam}?role=${role}`;
  };

  const handleShareRoom = (roomId) => {
    console.log(`[Lobby][Debug] handleShareRoom called with roomId: "${roomId}"`);
    console.log(`[Lobby][Debug] selectedRole: "${selectedRole}"`);
    console.log(`[Lobby][Debug] currentRoom:`, currentRoom);

    const link = generateShareableLink(roomId, selectedRole);
    console.log(`[Lobby][Debug] Generated link: "${link}"`);

    setShareableLink(link);
    setShowShareModal(true);
    setLinkCopied(false);
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(shareableLink);
      setLinkCopied(true);
      setTimeout(() => setLinkCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy link: ', err);
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = shareableLink;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      setLinkCopied(true);
      setTimeout(() => setLinkCopied(false), 2000);
    }
  };

  // Room management functions
  const handleCreateRoom = async () => {
    console.log(`[Lobby][Debug] === ROOM CREATION START ===`);
    console.log(`[Lobby][Debug] Room form:`, roomForm);
    console.log(`[Lobby][Debug] Host anonymous name: "${hostAnonymousName}"`);
    console.log(`[Lobby][Debug] Selected role: "${selectedRole}"`);

    if (
      roomForm.room_name.trim() &&
      roomForm.topic_category &&
      roomForm.cefr_level &&
      hostAnonymousName.trim()
    ) {
      // Load user data from localStorage
      const storedHostData = JSON.parse(localStorage.getItem('userData')); // User is the host for this new room

      const roomData = {
        room_name: roomForm.room_name.trim(),
        max_participants: roomForm.max_participants,
        topic_title: '',
        topic_category: roomForm.topic_category,
        cefr_level: roomForm.cefr_level.trim(),
        rounds_completed: 0,
        created_at: new Date().toISOString(),
        created_by: storedHostData.userId,
        status: 'waiting'
      }

      try {
        // Create session in the database
        console.log(`[Lobby][Debug] Creating session in database for room:`, roomData);
        console.log(`[Lobby][Debug] Host for the room ${roomData.room_name} is ${storedHostData.userId}`)
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:3003'
        const sessionResponse = await fetch(`${apiUrl}/rooms/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(roomData),
        })

        const sessionResult = await sessionResponse.json()
        console.log('[Lobby] Session created:', sessionResult)

        // Store session_id for later use
        if (sessionResult.status === 'success') {
          sessionStorage.setItem('current_session_id', sessionResult.data)
          roomData.roomId = sessionResult.data; // Assign generated room ID


          // Create participant entry using helper function
          await createParticipantForRoom({
            userId: storedHostData.userId,
            roomId: sessionResult.data,
            anonymousName: hostAnonymousName,
            currentCefrLevel: storedHostData.currentCefrLevel,
            campusOrLocation: null
          })
        }
      } catch (error) {
        console.error('[Lobby] Error creating session/participant:', error)
      }


      console.log(`[Lobby][Debug] Generated room data:`, roomData);
      console.log(`[Lobby][Debug] Calling joinRoom with ID: "${roomData.roomId}"`);

      // Pass room metadata as third parameter to joinRoom
      joinRoom(roomData.roomId, selectedRole, {
        name: roomData.name,
        room_name: roomData.name,
        topic_category: roomData.topic_category,
        cefr_level: roomData.cefr_level,
        max_participants: roomData.max_participants
      })
      setCurrentRoom(roomData)
      setShowCreateRoom(false)

      // Navigate to room-specific lobby
      navigate(`/lobby/${roomData.roomId}?role=${selectedRole}`);

      console.log(`[Lobby][Debug] Room creation complete, navigating to /lobby/${roomData.roomId}`);


      // Automatically show share modal for new room (will be shown on RoomLobbyPage)
      // setTimeout(() => {
      //   console.log(`[Lobby][Debug] Triggering share modal for room: "${roomData.roomId}"`);
      //   handleShareRoom(roomData.roomId);
      // }, 500);
      // Reset form
      setRoomForm({
        room_name: "",
        max_participants: 6,
        topic_category: "",
        cefr_level: "",
      });
      setHostAnonymousName("");
    } else {
      console.log(`[Lobby][Debug] ❌ Room creation failed - missing required fields`);
      console.log(`[Lobby][Debug] Room name: "${roomForm.room_name}"`);
      console.log(`[Lobby][Debug] Topic category: "${roomForm.topic_category}"`);
      console.log(`[Lobby][Debug] CEFR level: "${roomForm.cefr_level}"`);
      console.log(`[Lobby][Debug] Host name: "${hostAnonymousName}"`);
    }
    console.log(`[Lobby][Debug] === ROOM CREATION END ===`);
  };

  const handleRoomFormChange = (field, value) => {
    setRoomForm((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleJoinRoom = async (roomData) => {
    console.log('[Lobby][Debug] Joining room:', roomData);

    // Store the room data and show modal for anonymous name
    setPendingRoomData(roomData);
    setJoiningAnonymousName(""); // Reset the name field
    setShowJoinModal(true);
  }

  // New function to handle the actual join after name submission
  const handleJoinSubmit = async () => {
    if (!joiningAnonymousName.trim() || !pendingRoomData) return;

    const roomData = pendingRoomData;

    // If this is a backend room (already exists in DB), skip creation
    console.log('[Lobby][Debug] Completing join for room:', roomData.roomId);

    // Load user data from localStorage
    const storedUserData = JSON.parse(localStorage.getItem('userData'));

    try {
      // Create participant entry for the user joining this room using helper function
      await createParticipantForRoom({
        userId: storedUserData?.userId,
        roomId: roomData.roomId,
        anonymousName: joiningAnonymousName,
        currentCefrLevel: storedUserData?.currentCefrLevel,
        campusOrLocation: null
      })
    } catch (error) {
      console.error('[Lobby][Debug] Error creating participant for existing room:', error)
    }

    // Pass room metadata to joinRoom
    // joinRoom(roomData.roomId, selectedRole, {
    //   name: roomData.name,
    //   room_name: roomData.name,
    //   topic_category: roomData.topic_category,
    //   cefr_level: roomData.cefr_level,
    //   max_participants: roomData.max_participants
    // });
    setCurrentRoom(roomData);
    
    // Close modal and clear pending data
    setShowJoinModal(false);
    setPendingRoomData(null);
    setJoiningAnonymousName("");

    // Navigate to the room URL (RoomLobbyPage will handle room joining)
    navigate(`/lobby/${roomData.roomId}?role=${selectedRole}`);

  }

  // Timer for waiting time and late join check
  useEffect(() => {
    // Disable late join check in development to prevent loops
    const isDevelopment = window.location.hostname === 'localhost'
    if (isDevelopment) {
      console.log(
        "[Lobby][Debug] Development mode - disabling auto late join navigation"
      );
      // Just start the timer, skip late join check
      const timer = setInterval(() => {
        setWaitingTime((prev) => prev + 1);
      }, 1000);
      return () => clearInterval(timer);
    }

    // Production late join logic
    let isMounted = true; // Flag to check if component is still mounted

    const checkDiscussionState = async () => {
      // Check if a discussion is already active for late joiners
      try {
        const apiUrl = import.meta.env.VITE_API_URL || "";
        const res = await fetch(`${apiUrl}/api/room/${roomId}/state`);
        const json = await res.json();

        if (isMounted && json?.discussion?.active) {
          console.log(
            "[Lobby][Debug] Late join detected - navigating to /roundtable"
          );
          // Use a session flag to indicate a late join is in progress
          sessionStorage.setItem("late-join-navigating", "true");
          navigate("/roundtable", { replace: true });
        }
      } catch (err) {
        console.warn(
          "[Lobby][Debug] Failed to check room state for late join",
          err
        );
      }
    };

    // If not in development, and not already joining, check the state
    if (!isDevelopment && !sessionStorage.getItem("late-join-navigating")) {
      checkDiscussionState();
    }

    const timer = setInterval(() => {
      if (isMounted) {
        setWaitingTime((prev) => prev + 1);
      }
    }, 1000);

    return () => {
      isMounted = false;
      clearInterval(timer);
    };
  }, [roomId, isNavigating, navigate]);

  // Socket event handlers for main lobby (minimal, room-specific handlers in RoomLobbyPage)
  useEffect(() => {
    if (!socket || isNavigating) {
      console.log("[Lobby][Debug] Socket not available or navigating");
      return;
    }

    console.log("[Lobby][Debug] Socket available, connected:", connected);
    
    // Socket connect/disconnect events
    socket.on("connect", () => {
      console.log("[Lobby][Debug] Socket connected:", socket.id);
    });
    
    socket.on("disconnect", () => {
      console.log("[Lobby][Debug] Socket disconnected");
    });

    // Cleanup event listeners
    return () => {
      socket.off("connect");
      socket.off("disconnect");
    };
  }, [socket, connected, isNavigating]);

  // User actions
  const handleLogout = () => {
    console.log("[Lobby][Debug] Logout clicked");
    logout();
  };

  // Format time display
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  // Early return for development debugging
  const isDevelopment = window.location.hostname === 'localhost'
  if (isDevelopment && participants.length === 0) {
    // In development, show the interface even with no participants
    console.log(
      "[Lobby][Debug] Development mode - showing interface with 0 participants"
    );
  }

  // Early return to prevent rendering if navigating
  if (isNavigating) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-lg text-gray-600">Starting discussion...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* URL Test Component - for debugging */}
      <URLTest />

      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-6xl mx-auto px-4 py-3 flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center">
              <Users className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-gray-900">Lobby</h1>
              <p className="text-sm text-gray-500">Welcome, {anonymousName}</p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            {/* Connection Status */}
            <div
              className={`flex items-center space-x-1 text-sm ${connected ? "text-green-600" : "text-red-600"
                }`}
            >
              <div
                className={`w-2 h-2 rounded-full ${connected ? "bg-green-600" : "bg-red-600"
                  }`}
              ></div>
              <span>{connected ? "Connected" : "Disconnected"}</span>
            </div>

            {/* Waiting Time */}
            <div className="flex items-center space-x-1 text-sm text-gray-600">
              <Clock className="w-4 h-4" />
              <span>{formatTime(waitingTime)}</span>
            </div>

            {/* Logout */}
            <button
              onClick={handleLogout}
              className="p-2 text-gray-600 hover:text-gray-900 transition-colors"
              title="Logout"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-6xl mx-auto w-full px-4 py-8 space-y-8">
        {/* Room Selection View */}
        <div className="space-y-8">
            {/* Header */}
            <div className="text-center space-y-4">
              <h2 className="text-3xl font-bold text-gray-900">
                Welcome to GupShup Cafe
              </h2>
              <p className="text-lg text-gray-600">
                Join a discussion room or create your own
              </p>
            </div>

            {/* Create New Room Card */}
            <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-dashed border-gray-300 hover:border-blue-400 transition-colors">
              <div className="text-center space-y-4">
                <div className="w-16 h-16 bg-blue-100 rounded-full mx-auto flex items-center justify-center">
                  <Plus className="w-8 h-8 text-blue-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900">
                  Create New Room
                </h3>
                <p className="text-gray-600">
                  Start your own discussion room with a custom topic
                </p>

                {!showCreateRoom ? (
                  <button
                    onClick={() => setShowCreateRoom(true)}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Create Room
                  </button>
                ) : (
                  <div className="space-y-6 max-w-2xl mx-auto text-left">
                    {/* Room Name */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Room Name
                      </label>
                      <input
                        type="text"
                        value={roomForm.room_name}
                        onChange={(e) =>
                          handleRoomFormChange("room_name", e.target.value)
                        }
                        placeholder="Enter room name..."
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>

                    {/* Max Participants */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Max Participants
                      </label>
                      <select
                        value={roomForm.max_participants}
                        onChange={(e) =>
                          handleRoomFormChange(
                            "max_participants",
                            parseInt(e.target.value)
                          )
                        }
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        {[2, 3, 4, 5, 6].map((num) => (
                          <option key={num} value={num}>
                            {num} participants
                          </option>
                        ))}
                      </select>
                    </div>

                    {/* Topic Category */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Topic Category
                      </label>
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                        {topicCategories.map((category) => (
                          <button
                            key={category.id}
                            type="button"
                            onClick={() =>
                              handleRoomFormChange(
                                "topic_category",
                                category.id
                              )
                            }
                            className={`px-3 py-2 text-xs font-medium rounded-full border transition-colors ${roomForm.topic_category === category.id
                              ? `${category.color} border-current`
                              : "bg-gray-100 text-gray-600 border-gray-300 hover:bg-gray-200"
                              }`}
                          >
                            {category.label}
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* CEFR Level */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        CEFR Level
                      </label>
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                        {cefrLevels.map((level) => (
                          <button
                            key={level.id}
                            type="button"
                            onClick={() =>
                              handleRoomFormChange("cefr_level", level.id)
                            }
                            className={`px-3 py-2 text-xs font-medium rounded-full border transition-colors ${roomForm.cefr_level === level.id
                              ? `${level.color} border-current`
                              : "bg-gray-100 text-gray-600 border-gray-300 hover:bg-gray-200"
                              }`}
                            title={level.description}
                          >
                            {level.label}
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Host Anonymous Name */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Your Anonymous Name for this Session
                      </label>
                      <input
                        type="text"
                        value={hostAnonymousName}
                        onChange={(e) => setHostAnonymousName(e.target.value)}
                        placeholder="Enter your anonymous display name..."
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />

                      {/* Suggested Names */}
                      <div className="mt-3">
                        <p className="text-xs text-gray-500 mb-2">
                          Quick suggestions:
                        </p>
                        <div className="flex flex-wrap gap-2">
                          {suggestedNames.map((name, index) => (
                            <button
                              key={index}
                              type="button"
                              onClick={() => setHostAnonymousName(name)}
                              className="px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded-full hover:bg-blue-100 hover:text-blue-800 transition-colors border border-gray-200"
                            >
                              {name}
                            </button>
                          ))}
                        </div>
                      </div>
                    </div>

                    <div className="flex justify-center space-x-3">
                      <button
                        onClick={handleCreateRoom}
                        disabled={
                          !roomForm.room_name.trim() ||
                          !roomForm.topic_category ||
                          !roomForm.cefr_level ||
                          !hostAnonymousName.trim()
                        }
                        className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                      >
                        Publish Room
                      </button>
                      <button
                        onClick={() => {
                          setShowCreateRoom(false);
                          setRoomForm({
                            room_name: "",
                            max_participants: 6,
                            topic_category: "",
                            cefr_level: "",
                          });
                          setHostAnonymousName("");
                        }}
                        className="px-6 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Existing Rooms */}
            <div className="space-y-4">
              <h3 className="text-2xl font-bold text-gray-900 text-center">
                Available Rooms
              </h3>

              {roomsLoading ? (
                <div className="text-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                  <p className="text-gray-600">Loading rooms...</p>
                </div>
              ) : allWaitingRooms.length === 0 ? (
                <div className="text-center py-12 bg-gray-50 rounded-xl">
                  <Users className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                  <p className="text-gray-600 text-lg">No rooms available at the moment</p>
                  <p className="text-gray-500 text-sm mt-2">Be the first to create one!</p>
                </div>
              ) : (
                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                  {allWaitingRooms.map((room) => {
                    const IconComponent = room.icon;
                    const cefrLevel = cefrLevels.find(
                      (level) => level.id === room.cefr_level
                    );
                    const topicCategory = topicCategories.find(
                      (cat) => cat.id === room.topic_category
                    );

                    return (
                      <div
                        key={room.roomId}
                        className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-all duration-300 transform hover:scale-105"
                      >
                        <div className="text-center space-y-4">
                          <div
                            className={`w-16 h-16 ${room.color} rounded-full mx-auto flex items-center justify-center`}
                          >
                            <IconComponent className="w-8 h-8 text-white" />
                          </div>
                          <div>
                            <h4 className="text-lg font-semibold text-gray-900">
                              {room.name}
                            </h4>
                            <p className="text-sm text-gray-600 mt-2">
                              {room.description}
                            </p>
                          </div>

                          {/* Room Details */}
                          <div className="space-y-2">
                            <div className="flex flex-wrap justify-center gap-2">
                              {cefrLevel && (
                                <span
                                  className={`px-2 py-1 text-xs font-medium rounded-full ${cefrLevel.color} flex items-center`}
                                >
                                  <Star className="w-3 h-3 mr-1" />
                                  {cefrLevel.id}
                                </span>
                              )}
                              {topicCategory && (
                                <span
                                  className={`px-2 py-1 text-xs font-medium rounded-full ${topicCategory.color}`}
                                >
                                  {topicCategory.label}
                                </span>
                              )}
                            </div>
                            <div className="text-xs text-gray-500">
                              {room.participant_count !== undefined && (
                                <span className="mr-2">
                                  {room.participant_count} / {room.max_participants} joined
                                </span>
                              )}
                              {!room.participant_count && (
                                <span>Max: {room.max_participants} participants</span>
                              )}
                            </div>
                          </div>

                          <div className="flex space-x-2">
                            <button
                              onClick={() => handleJoinRoom(room)}
                              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
                            >
                              Join
                            </button>
                            <button
                              onClick={() => handleShareRoom(room.roomId)}
                              className="px-3 py-2 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 transition-colors"
                              title="Share this room"
                            >
                              <Share2 size={16} />
                            </button>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
      </main>

      {/* Share Room Modal */}
      {showShareModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-xl p-6 max-w-lg w-full mx-4">
              <h3 className="text-xl font-bold text-gray-900 mb-4">
                🎉 Room Created! Invite Others
              </h3>
              <p className="text-gray-600 mb-4">
                Share this link with others so they can join your discussion room:
              </p>

              <div className="bg-gray-50 rounded-lg p-3 mb-4">
                <div className="flex items-center space-x-2">
                  <input
                    type="text"
                    readOnly
                    value={shareableLink}
                    className="flex-1 bg-transparent border-none outline-none text-sm text-gray-700 cursor-pointer break-all"
                    onClick={(e) => e.target.select()}
                    title={shareableLink}
                  />
                  <button
                    onClick={copyToClipboard}
                    className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${linkCopied
                      ? 'bg-green-100 text-green-800'
                      : 'bg-blue-500 text-white hover:bg-blue-600'
                      }`}
                  >
                    {linkCopied ? (
                      <div className="flex items-center space-x-1">
                        <Check size={16} />
                        <span>Copied!</span>
                      </div>
                    ) : (
                      <div className="flex items-center space-x-1">
                        <Copy size={16} />
                        <span>Copy</span>
                      </div>
                    )}
                  </button>
                </div>
              </div>

              <div className="bg-blue-50 rounded-lg p-3 mb-4">
                <p className="text-sm text-blue-800">
                  <strong>💡 Tip:</strong> Anyone with this link can join your room. Share it via WhatsApp, Email, or any messaging app!
                </p>
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => setShowShareModal(false)}
                  className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
                >
                  Close
                </button>
                <button
                  onClick={async () => {
                    if (navigator.share) {
                      try {
                        await navigator.share({
                          title: 'Join my GupShup Cafe discussion!',
                          text: 'Join me for an English conversation practice session',
                          url: shareableLink,
                        });
                      } catch (err) {
                        console.log('Error sharing:', err);
                      }
                    } else {
                      copyToClipboard();
                    }
                  }}
                  className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center space-x-2"
                >
                  <Share2 size={16} />
                  <span>Share</span>
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Join Room Modal - Anonymous Name Input */}
        {showJoinModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 backdrop-blur-sm">
            <div className="bg-white rounded-xl p-6 max-w-lg w-full mx-4 shadow-2xl">
              <h3 className="text-xl font-bold text-gray-900 mb-4">
                👋 Join the Discussion
              </h3>
              <p className="text-gray-600 mb-4">
                Choose an anonymous name for this session. This name will be visible to other participants.
              </p>

              {/* Anonymous Name Input */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Your Anonymous Name for this Session
                </label>
                <input
                  type="text"
                  value={joiningAnonymousName}
                  onChange={(e) => setJoiningAnonymousName(e.target.value)}
                  placeholder="Enter your anonymous display name..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && joiningAnonymousName.trim()) {
                      handleJoinSubmit();
                    }
                  }}
                  autoFocus
                />

                {/* Quick Suggestions */}
                <div className="mt-3">
                  <p className="text-xs text-gray-500 mb-2">
                    Quick suggestions:
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {suggestedNames.map((name, index) => (
                      <button
                        key={index}
                        type="button"
                        onClick={() => setJoiningAnonymousName(name)}
                        className="px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded-full hover:bg-blue-100 hover:text-blue-800 transition-colors border border-gray-200"
                      >
                        {name}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => {
                    setShowJoinModal(false);
                    setPendingRoomData(null);
                    setJoiningAnonymousName("");
                    // Navigate back to main lobby
                    navigate('/lobby');
                  }}
                  className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleJoinSubmit}
                  disabled={!joiningAnonymousName.trim()}
                  className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                >
                  Join Room
                </button>
              </div>
            </div>
          </div>
        )}
    </div>
  );
}

export default LobbyPage;
