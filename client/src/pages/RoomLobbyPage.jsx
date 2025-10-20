import React, { useState, useEffect, useRef } from "react";
import { useNavigate, useParams, useLocation } from "react-router-dom";
import { useSocket } from "../contexts/SocketContext";
import { useAuth } from "../contexts/AuthContext";
import { useAudio } from "../contexts/AudioContext";
import {
  Users,
  Clock,
  Mic,
  MicOff,
  LogOut,
  Settings,
  Share2,
  Copy,
  Check,
} from "lucide-react";

// Global flag to prevent multiple late join checks (accessible across components)
if (typeof window !== "undefined") {
  window.lateJoinCheckInProgress = window.lateJoinCheckInProgress || false;
}

/**
 * Room Lobby Page Component
 * Waiting area for a specific room until participants join and are ready
 */
function RoomLobbyPage() {
  const navigate = useNavigate();
  const { roomId: urlRoomId } = useParams();
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

  // Initialize state with localStorage persistence
  const [participants, setParticipants] = useState(() => {
    const saved = localStorage.getItem(
      `room-${urlRoomId || "general"}-participants`
    );
    return saved ? JSON.parse(saved) : [];
  });
  const [roomId, setRoomId] = useState(urlRoomId || "general");
  const [selectedRole, setSelectedRole] = useState(() => {
    const saved = localStorage.getItem(`room-${urlRoomId || "general"}-role`);
    return saved || "speaker";
  });
  const [minParticipants, setMinParticipants] = useState(1); // Default to 1 for solo testing
  const [isReady, setIsReady] = useState(() => {
    const saved = localStorage.getItem(`room-${urlRoomId || "general"}-ready`);
    return saved === "true";
  });
  const [waitingTime, setWaitingTime] = useState(0);
  const [systemMessage, setSystemMessage] = useState("Connecting to lobby...");
  const [isNavigating, setIsNavigating] = useState(false);
  const [showShareModal, setShowShareModal] = useState(false);
  const [shareableLink, setShareableLink] = useState("");
  const [linkCopied, setLinkCopied] = useState(false);
  const [roomDetails, setRoomDetails] = useState(null);
  const [discussionStartTime, setDiscussionStartTime] = useState(null);
  const [reconnectionStatus, setReconnectionStatus] = useState(null);

  // Update roomId when URL parameter changes
  useEffect(() => {
    if (urlRoomId && urlRoomId !== roomId) {
      console.log(`[RoomLobby][Debug] Room ID changed from URL: ${urlRoomId}`);
      setRoomId(urlRoomId);
    }
  }, [urlRoomId]);

  // Persist state changes to localStorage
  useEffect(() => {
    localStorage.setItem(
      `room-${roomId}-participants`,
      JSON.stringify(participants)
    );
  }, [participants, roomId]);

  useEffect(() => {
    localStorage.setItem(`room-${roomId}-role`, selectedRole);
  }, [selectedRole, roomId]);

  useEffect(() => {
    localStorage.setItem(`room-${roomId}-ready`, isReady.toString());
  }, [isReady, roomId]);

  // Fetch room details from API
  useEffect(() => {
    const fetchRoomDetails = async () => {
      if (!roomId) return;

      try {
        const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:3003";
        const response = await fetch(`${apiUrl}/rooms/${roomId}`);
        const result = await response.json();

        if (result.status === "success") {
          console.log("[RoomLobby][Debug] Fetched room details:", result.data);
          setRoomDetails(result.data);
        }
      } catch (error) {
        console.error("[RoomLobby][Debug] Error fetching room details:", error);
      }
    };

    fetchRoomDetails();
  }, [roomId]);

  // Handle URL query parameters for role
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const roleFromUrl = params.get("role");
    if (
      roleFromUrl &&
      (roleFromUrl === "speaker" || roleFromUrl === "listener")
    ) {
      console.log(`[RoomLobby][Debug] Setting role from URL: ${roleFromUrl}`);
      setSelectedRole(roleFromUrl);
    }
  }, [location.search]);

  // Timer for waiting time and late join check
  useEffect(() => {
    // Disable late join check in development to prevent loops
    const isDevelopment =
      import.meta.env.DEV || window.location.hostname === "localhost";
    if (isDevelopment) {
      console.log(
        "[RoomLobby][Debug] Development mode - disabling auto late join navigation"
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
            "[RoomLobby][Debug] Late join detected - navigating to /roundtable"
          );
          // Use a session flag to indicate a late join is in progress
          sessionStorage.setItem("late-join-navigating", "true");
          navigate("/roundtable", { replace: true });
        }
      } catch (err) {
        console.warn(
          "[RoomLobby][Debug] Failed to check room state for late join",
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

  // Room sharing functions
  const generateShareableLink = (roomIdParam, role = "speaker") => {
    const currentOrigin = window.location.origin;
    return `${currentOrigin}/lobby/${roomIdParam}?role=${role}`;
  };

  const handleShareRoom = () => {
    console.log(`[RoomLobby][Debug] Sharing room: ${roomId}`);
    const link = generateShareableLink(roomId, selectedRole);
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
      console.error("Failed to copy link: ", err);
      // Fallback for older browsers
      const textArea = document.createElement("textarea");
      textArea.value = shareableLink;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand("copy");
      document.body.removeChild(textArea);
      setLinkCopied(true);
      setTimeout(() => setLinkCopied(false), 2000);
    }
  };

  // Socket event handlers
  useEffect(() => {
    if (!socket || isNavigating) {
      console.log("[RoomLobby][Debug] Socket not available or navigating");
      return;
    }

    console.log("[Lobby][Debug] Socket available, connected:", connected);
    // Socket connect/disconnect events
    socket.on("connect", () => {
      if (!isNavigating) {
        console.log("[Lobby][Debug] Socket connected:", socket.id);
        console.log(
          `[Lobby][Debug] Calling joinRoom with roomId: ${roomId}, role: ${selectedRole} (on connect)`
        );

        // Restore ready status if it was previously set
        if (isReady) {
          console.log(
            "[Lobby][Debug] Restoring ready status after reconnection"
          );
          setTimeout(() => {
            signalReady();
          }, 1000); // Small delay to ensure room join is complete
        }

        joinRoom(roomId, selectedRole);
      }
    });
    socket.on("disconnect", () => {
      console.log("[Lobby][Debug] Socket disconnected");
    });

    // Handle participants update
    socket.on("participants-update", (updatedParticipants) => {
      console.log(
        "[Lobby][Debug] Received participants-update:",
        updatedParticipants
      );

      // Preserve local ready status during updates
      const currentLocalParticipant = participants.find(
        (p) => p.socketId === socket.id
      );
      const updatedLocalParticipant = updatedParticipants.find(
        (p) => p.socketId === socket.id
      );

      // If we have a local participant and they were ready, preserve that state
      if (
        currentLocalParticipant &&
        currentLocalParticipant.isReady &&
        updatedLocalParticipant
      ) {
        updatedLocalParticipant.isReady = true;
        console.log(
          "[Lobby][Debug] Preserved local ready status during update"
        );
      }

      setParticipants(updatedParticipants);

      // Enhanced debug: print all roles and readiness
      console.log(
        "[Lobby][Debug] Participants array:",
        updatedParticipants.map((p) => ({
          name: p.anonymousName,
          role: p.role,
          isReady: p.isReady,
          id: p.id,
          socketId: p.socketId,
        }))
      );
      console.log(
        "[Lobby][Debug] Local userRole:",
        userRole,
        "selectedRole:",
        selectedRole
      );
      // Find local participant in the update
      const local = updatedParticipants.find((p) => p.socketId === socket.id);
      if (local) {
        console.log("[Lobby][Debug] Local participant from update:", local);
        // Update local ready state to match server
        if (local.isReady !== isReady) {
          setIsReady(local.isReady);
        }
      } else {
        console.log(
          "[Lobby][Debug] Local participant not found in update. Socket ID:",
          socket.id
        );
      }
      if (updatedParticipants.length >= 1) {
        setSystemMessage(
          'Ready to start! Click "Ready" when you want to begin.'
        );
      } else {
        setSystemMessage("Connecting to discussion room...");
      }
    });

    // Handle discussion start
    socket.on("discussion-started", () => {
      console.log(
        "[Lobby][Debug] Received discussion-started event - navigating to /roundtable"
      );
      if (!isNavigating) {
        setIsNavigating(true);
        setSystemMessage("Discussion starting! Redirecting to roundtable...");
        console.log("[Lobby][Debug] Navigating to /roundtable now");

        // Mark discussion start time for polling
        setDiscussionStartTime(Date.now());

        // Store discussion start time in sessionStorage for roundtable page
        sessionStorage.setItem("discussion-start-time", Date.now().toString());

        // Update room status to 'in_progress' via API
        const updateRoomStatus = async () => {
          try {
            const apiUrl =
              import.meta.env.VITE_API_URL || "http://localhost:3003";
            const response = await fetch(`${apiUrl}/rooms/${roomId}/status`, {
              method: "PATCH",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({
                status: "in_progress",
              }),
            });

            const result = await response.json();
            console.log(
              "[RoomLobby][Debug] Room status updated to in_progress:",
              result
            );
          } catch (error) {
            console.error(
              "[RoomLobby][Debug] Error updating room status:",
              error
            );
          }
        };

        updateRoomStatus();
        navigate("/roundtable", { replace: true });
      }
    });

    // Handle host changes
    socket.on("host-changed", (data) => {
      console.log("[Lobby][Debug] Host changed:", data);
      const { newHost, previousHost } = data;

      if (newHost) {
        setSystemMessage(
          `👑 ${previousHost} left. ${newHost.anonymousName} is now the host.`
        );

        // Update participants to reflect new host role
        setParticipants((prevParticipants) =>
          prevParticipants.map((p) =>
            p.id === newHost.id ? { ...p, role: "host" } : p
          )
        );
      }
    });

    // Handle participant leaving with host info
    socket.on("participant-left", (data) => {
      console.log("[Lobby][Debug] Participant left:", data);
      const { participantId, anonymousName, wasHost, newHost } = data;

      if (wasHost && newHost) {
        setSystemMessage(
          `👑 Host ${anonymousName} left. A new host has been assigned.`
        );
      } else if (wasHost) {
        setSystemMessage(`👑 Host ${anonymousName} left the room.`);
      }
    });

    // Handle user reconnection
    socket.on("user-reconnected", (data) => {
      console.log("[Lobby][Debug] User reconnected:", data);
      const { userId, anonymousName, wasHost, preservedState } = data;

      setSystemMessage(`🔄 ${anonymousName} has reconnected to the room.`);

      // Restore preserved state if it's the current user
      if (preservedState) {
        console.log(
          "[Lobby][Debug] Restoring preserved state:",
          preservedState
        );
        if (preservedState.isReady !== undefined) {
          setIsReady(preservedState.isReady);
        }
      }

      // Send acknowledgment back to server
      socket.emit("user-reconnection-ack");
    });

    // Handle participant reconnection notification
    socket.on("participant-reconnected", (data) => {
      console.log("[Lobby][Debug] Participant reconnected:", data);
      const { participantId, anonymousName } = data;

      setSystemMessage(`🔄 ${anonymousName} has reconnected to the room.`);
    });

    // Note: Removed listeners for 'user-ready-update' and 'system-message'
    // as these events are not emitted by the server

    // Cleanup
    return () => {
      socket.off("connect");
      socket.off("disconnect");
      socket.off("participants-update");
      socket.off("discussion-started");
      socket.off("host-changed");
      socket.off("participant-left");
      socket.off("user-reconnected");
      socket.off("participant-reconnected");
    };
  }, [
    socket,
    joinRoom,
    roomId,
    selectedRole,
    navigate,
    connected,
    isNavigating,
  ]);

  // Poll for participants every 15 seconds for the first minute after discussion starts
  useEffect(() => {
    if (!discussionStartTime || !roomId) return;

    const fetchParticipants = async () => {
      try {
        const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:3003";
        const response = await fetch(`${apiUrl}/participants/room/${roomId}`);
        const result = await response.json();

        if (result.status === "success") {
          console.log("[RoomLobby][Debug] Polled participants:", result.data);
          // Update participants if needed (optional, socket updates should handle this)
        }
      } catch (error) {
        console.error("[RoomLobby][Debug] Error polling participants:", error);
      }
    };

    // Poll every 15 seconds
    const interval = setInterval(() => {
      const elapsed = Date.now() - discussionStartTime;

      // Stop polling after 60 seconds (1 minute)
      if (elapsed >= 60000) {
        console.log(
          "[RoomLobby][Debug] Stopping participant polling after 1 minute"
        );
        clearInterval(interval);
        return;
      }

      fetchParticipants();
    }, 15000); // 15 seconds

    // Initial fetch
    fetchParticipants();

    return () => clearInterval(interval);
  }, [discussionStartTime, roomId]);

  // Fetch server-side configuration (minParticipants, etc.)
  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const apiUrl = import.meta.env.VITE_API_URL || "";
        const res = await fetch(`${apiUrl}/api/config`);
        const json = await res.json();
        const serverMin = json?.data?.minParticipants;
        // Force minParticipants to 1 for local/single-user testing
        setMinParticipants(1);
        // If you want to use server config, comment out the line above and uncomment below
        // if (serverMin && Number.isFinite(serverMin)) setMinParticipants(serverMin)
      } catch (err) {
        console.warn("Failed to fetch server config, using defaults", err);
      }
    };

    fetchConfig();
  }, []);

  // Sync role between lobby selection and audio context
  useEffect(() => {
    if (updateUserRole && selectedRole !== userRole) {
      console.log(`[Lobby] Syncing role from ${userRole} to ${selectedRole}`);
      updateUserRole(selectedRole);
    }
  }, [selectedRole, userRole, updateUserRole]);

  // Cleanup localStorage when component unmounts
  useEffect(() => {
    return () => {
      // Clear localStorage when leaving the room
      localStorage.removeItem(`room-${roomId}-participants`);
      localStorage.removeItem(`room-${roomId}-role`);
      localStorage.removeItem(`room-${roomId}-ready`);
    };
  }, [roomId]);

  // Global reconnection event listeners
  useEffect(() => {
    const handleSocketReconnected = (event) => {
      console.log("[Lobby] Socket reconnected:", event.detail);
      setReconnectionStatus("reconnected");
      setTimeout(() => setReconnectionStatus(null), 3000);
    };

    const handleSocketDisconnected = (event) => {
      console.log("[Lobby] Socket disconnected:", event.detail);
      setReconnectionStatus("disconnected");
    };

    const handleSocketReconnectAttempt = (event) => {
      console.log("[Lobby] Socket reconnect attempt:", event.detail);
      setReconnectionStatus("reconnecting");
    };

    const handleSocketReconnectFailed = (event) => {
      console.log("[Lobby] Socket reconnect failed:", event.detail);
      setReconnectionStatus("failed");
    };

    // Add event listeners
    window.addEventListener("socket-reconnected", handleSocketReconnected);
    window.addEventListener("socket-disconnected", handleSocketDisconnected);
    window.addEventListener(
      "socket-reconnect-attempt",
      handleSocketReconnectAttempt
    );
    window.addEventListener(
      "socket-reconnect-failed",
      handleSocketReconnectFailed
    );

    // Cleanup
    return () => {
      window.removeEventListener("socket-reconnected", handleSocketReconnected);
      window.removeEventListener(
        "socket-disconnected",
        handleSocketDisconnected
      );
      window.removeEventListener(
        "socket-reconnect-attempt",
        handleSocketReconnectAttempt
      );
      window.removeEventListener(
        "socket-reconnect-failed",
        handleSocketReconnectFailed
      );
    };
  }, []);

  /**
   * Format waiting time as MM:SS
   */
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs
      .toString()
      .padStart(2, "0")}`;
  };

  /**
   * Handle ready button click
   */
  const handleReady = async () => {
    console.log(
      "[Lobby][Debug] Ready button clicked. Participants:",
      participants,
      "AudioEnabled:",
      audioEnabled
    );
    if (participants.length >= minParticipants && audioEnabled) {
      setIsReady(true);
      console.log("[Lobby][Debug] Emitting signalReady");
      signalReady();

      // Update participant ready status via API
      try {
        const participantData = JSON.parse(
          localStorage.getItem("participantData") || "{}"
        );
        const participantId = participantData.participantId;

        if (participantId) {
          const apiUrl =
            import.meta.env.VITE_API_URL || "http://localhost:3003";
          const response = await fetch(`${apiUrl}/participants/ready`, {
            method: "PATCH",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              participant_id: participantId,
              is_ready: true,
            }),
          });

          const result = await response.json();
          console.log(
            "[RoomLobby][Debug] Ready status updated via API:",
            result
          );
        } else {
          console.warn(
            "[RoomLobby][Debug] No participantId found in localStorage"
          );
        }
      } catch (error) {
        console.error("[RoomLobby][Debug] Error updating ready status:", error);
      }
    }
  };

  /**
   * Handle microphone setup
   */
  const handleMicrophoneSetup = async () => {
    if (!isWebRTCSupported) {
      alert(
        "Your browser does not support audio features. Please use a modern browser."
      );
      return;
    }

    // Ensure we're requesting as a speaker
    if (selectedRole !== "speaker") {
      console.warn("[Lobby] Trying to enable microphone but not a speaker");
      return;
    }

    await requestMicrophoneAccess("speaker");
  };

  /**
   * Handle logout
   */
  const handleLogout = () => {
    logout();
    navigate("/");
  };

  const canStart = participants.length >= minParticipants && audioEnabled;

  // Check if current user is host (explicit host role or first participant)
  const currentUser = participants.find((p) => p.socketId === socket?.id);
  const isHost =
    currentUser &&
    (currentUser.role === "host" ||
      (participants.length > 0 && participants.indexOf(currentUser) === 0));

  // Check if all participants are ready
  const allParticipantsReady =
    participants.length > 0 && participants.every((p) => p.isReady);

  // Show loading state while navigating
  if (isNavigating) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">{systemMessage}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
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
              className={`flex items-center space-x-1 text-sm ${
                connected ? "text-green-600" : "text-red-600"
              }`}
            >
              <div
                className={`w-2 h-2 rounded-full ${
                  connected ? "bg-green-600" : "bg-red-600"
                }`}
              ></div>
              <span>{connected ? "Connected" : "Disconnected"}</span>
            </div>

            {/* Reconnection Status */}
            {reconnectionStatus && (
              <div
                className={`flex items-center space-x-1 text-sm px-2 py-1 rounded ${
                  reconnectionStatus === "reconnected"
                    ? "text-green-600 bg-green-50"
                    : reconnectionStatus === "reconnecting"
                    ? "text-yellow-600 bg-yellow-50"
                    : reconnectionStatus === "disconnected"
                    ? "text-red-600 bg-red-50"
                    : "text-red-600 bg-red-50"
                }`}
              >
                <div
                  className={`w-2 h-2 rounded-full ${
                    reconnectionStatus === "reconnected"
                      ? "bg-green-600"
                      : reconnectionStatus === "reconnecting"
                      ? "bg-yellow-600 animate-pulse"
                      : "bg-red-600"
                  }`}
                ></div>
                <span>
                  {reconnectionStatus === "reconnected"
                    ? "Reconnected"
                    : reconnectionStatus === "reconnecting"
                    ? "Reconnecting..."
                    : reconnectionStatus === "disconnected"
                    ? "Disconnected"
                    : "Connection Failed"}
                </span>
              </div>
            )}

            {/* Waiting Time */}
            <div className="flex items-center space-x-1 text-sm text-gray-600">
              <Clock className="w-4 h-4" />
              <span>{formatTime(waitingTime)}</span>
            </div>

            {/* Share Room Button */}
            <button
              onClick={handleShareRoom}
              className="p-2 text-blue-600 hover:text-blue-800 transition-colors"
              title="Share Room"
            >
              <Share2 className="w-5 h-5" />
            </button>

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
      <main className="flex-1 max-w-4xl mx-auto w-full p-6">
        {/* Room Details Card */}
        {roomDetails && (
          <div className="mb-6 bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Room Details
            </h2>
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <span className="text-sm text-gray-600">Room Name:</span>
                <p className="font-semibold text-gray-900">
                  {roomDetails.room_name}
                </p>
              </div>
              <div>
                <span className="text-sm text-gray-600">Room ID:</span>
                <p className="font-semibold text-gray-900">
                  {roomDetails.room_id}
                </p>
              </div>
              <div>
                <span className="text-sm text-gray-600">Topic Category:</span>
                <p className="font-semibold text-gray-900 capitalize">
                  {roomDetails.topic_category
                    ?.replace(/([A-Z])/g, " $1")
                    .trim()}
                </p>
              </div>
              <div>
                <span className="text-sm text-gray-600">CEFR Level:</span>
                <p className="font-semibold text-gray-900">
                  {roomDetails.cefr_level}
                </p>
              </div>
              <div>
                <span className="text-sm text-gray-600">Max Participants:</span>
                <p className="font-semibold text-gray-900">
                  {roomDetails.max_participants}
                </p>
              </div>
              <div>
                <span className="text-sm text-gray-600">Status:</span>
                <p
                  className={`font-semibold capitalize ${
                    roomDetails.status === "waiting"
                      ? "text-orange-600"
                      : roomDetails.status === "in_progress"
                      ? "text-green-600"
                      : "text-gray-600"
                  }`}
                >
                  {roomDetails.status?.replace("_", " ")}
                </p>
              </div>
            </div>
          </div>
        )}

        <div className="grid md:grid-cols-2 gap-6">
          {/* Status Panel */}
          <div className="space-y-6">
            {/* System Status */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Session Status
              </h2>

              <div className="space-y-4">
                {/* Role Selection */}
                <div className="space-y-2">
                  <span className="text-gray-600 text-sm font-medium">
                    Your Role
                  </span>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => {
                        setSelectedRole("speaker");
                        if (connected) {
                          console.log(
                            "[Lobby] Role changed to speaker, rejoining room"
                          );
                          joinRoom(roomId, "speaker");
                        }
                      }}
                      className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                        selectedRole === "speaker"
                          ? "bg-primary-600 text-white"
                          : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                      }`}
                    >
                      🎤 Speaker
                    </button>
                    <button
                      onClick={() => {
                        setSelectedRole("listener");
                        if (connected) {
                          console.log(
                            "[Lobby] Role changed to listener, rejoining room"
                          );
                          joinRoom(roomId, "listener");
                        }
                      }}
                      className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                        selectedRole === "listener"
                          ? "bg-primary-600 text-white"
                          : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                      }`}
                    >
                      👂 Listener
                    </button>
                  </div>
                  <p className="text-xs text-gray-500">
                    {selectedRole === "speaker"
                      ? "You can speak and participate actively in discussions"
                      : "You will listen to discussions without speaking privileges"}
                  </p>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Participants</span>
                  <span
                    className={`font-semibold ${
                      participants.length >= 2
                        ? "text-green-600"
                        : "text-orange-600"
                    }`}
                  >
                    {participants.length}/{minParticipants}+ required
                  </span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Audio Setup</span>
                  <span
                    className={`font-semibold ${
                      audioEnabled ? "text-green-600" : "text-orange-600"
                    }`}
                  >
                    {audioEnabled ? "Ready" : "Setup Required"}
                  </span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Status</span>
                  <span
                    className={`font-semibold ${
                      canStart ? "text-green-600" : "text-gray-600"
                    }`}
                  >
                    {canStart ? "Ready to Start" : "Waiting"}
                  </span>
                </div>
              </div>

              {/* System Message */}
              <div className="mt-4 p-3 bg-blue-50 rounded-md">
                <p className="text-sm text-blue-800">{systemMessage}</p>
              </div>
            </div>

            {/* Audio Setup */}
            {selectedRole === "speaker" && !audioEnabled && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Audio Setup
                </h3>

                {!isWebRTCSupported ? (
                  <div className="text-center py-4">
                    <MicOff className="w-12 h-12 text-red-500 mx-auto mb-2" />
                    <p className="text-red-600 font-medium">
                      Audio Not Supported
                    </p>
                    <p className="text-sm text-gray-600 mt-1">
                      Please use a modern browser that supports WebRTC
                    </p>
                  </div>
                ) : micPermission === "denied" ? (
                  <div className="text-center py-4">
                    <MicOff className="w-12 h-12 text-red-500 mx-auto mb-2" />
                    <p className="text-red-600 font-medium">
                      Microphone Access Denied
                    </p>
                    <p className="text-sm text-gray-600 mt-1">
                      Please enable microphone access in your browser settings
                    </p>
                  </div>
                ) : (
                  <div className="text-center py-4">
                    <Mic className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                    <p className="text-gray-900 font-medium mb-2">
                      Enable Microphone
                    </p>
                    <p className="text-sm text-gray-600 mb-4">
                      We need access to your microphone for voice discussions
                    </p>
                    <button
                      onClick={handleMicrophoneSetup}
                      className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 
                                 transition-colors"
                    >
                      Enable Microphone
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* Audio Setup for Listeners */}
            {selectedRole === "listener" && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Audio Setup
                </h3>
                <div className="text-center py-4">
                  <div className="w-12 h-12 bg-blue-100 rounded-full mx-auto mb-2 flex items-center justify-center">
                    👂
                  </div>
                  <p className="text-blue-600 font-medium">
                    Listener Mode Active
                  </p>
                  <p className="text-sm text-gray-600 mt-1">
                    You'll receive audio from speakers without needing
                    microphone access
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Participants List */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Participants ({participants.length})
            </h2>

            <div className="space-y-3">
              {participants.map((participant) => (
                <div
                  key={participant.id}
                  className="flex items-center space-x-3 p-3 bg-gray-50 rounded-md"
                >
                  <div
                    className="w-10 h-10 bg-primary-600 rounded-full flex items-center 
                                  justify-center text-white font-semibold"
                  >
                    {participant.anonymousName.charAt(0).toUpperCase()}
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">
                      {participant.anonymousName}
                    </p>
                    <div className="flex items-center space-x-2">
                      <span
                        className={`text-xs px-2 py-1 rounded-full font-medium ${
                          participant.role === "speaker"
                            ? "bg-green-100 text-green-800"
                            : "bg-blue-100 text-blue-800"
                        }`}
                      >
                        {participant.role === "speaker"
                          ? "🎤 Speaker"
                          : "👂 Listener"}
                      </span>
                      <span className="text-sm text-gray-500">
                        {participant.isReady ? "Ready" : "Waiting"}
                      </span>
                    </div>
                  </div>
                  {participant.isReady && (
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  )}
                </div>
              ))}

              {/* Empty slots */}
              {participants.length < 2 && (
                <div className="text-center py-8 text-gray-500">
                  <Users className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>Waiting for more participants to join...</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Ready Button */}
        <div className="mt-8 text-center">
          {canStart && !isReady && (
            <button
              onClick={handleReady}
              className="px-8 py-3 bg-green-600 text-white text-lg font-semibold rounded-lg 
                         hover:bg-green-700 transition-colors shadow-lg"
            >
              I'm Ready to Start!
            </button>
          )}

          {isReady && !isHost && (
            <div className="text-center">
              <div className="inline-flex items-center space-x-2 text-green-600">
                <div className="w-3 h-3 bg-green-600 rounded-full animate-pulse"></div>
                <span className="font-semibold">
                  Ready! Waiting for others...
                </span>
              </div>
            </div>
          )}

          {/* Host Start Discussion Button */}
          {isHost && isReady && allParticipantsReady && (
            <div className="text-center space-y-4">
              <div className="inline-flex items-center space-x-2 text-green-600 mb-4">
                <div className="w-3 h-3 bg-green-600 rounded-full animate-pulse"></div>
                <span className="font-semibold">
                  All participants ready! You can start the discussion.
                </span>
              </div>
              <button
                onClick={() => {
                  console.log("[Lobby] Host starting discussion");
                  socket?.emit("start-discussion");
                }}
                className="px-8 py-3 bg-blue-600 text-white text-lg font-semibold rounded-lg 
                           hover:bg-blue-700 transition-colors shadow-lg"
              >
                🚀 Start Discussion
              </button>
            </div>
          )}

          {isHost && isReady && !allParticipantsReady && (
            <div className="text-center">
              <div className="inline-flex items-center space-x-2 text-orange-600">
                <div className="w-3 h-3 bg-orange-600 rounded-full animate-pulse"></div>
                <span className="font-semibold">
                  Ready! Waiting for all participants to be ready...
                </span>
              </div>
            </div>
          )}

          {!canStart && (
            <p className="text-gray-500">
              {!audioEnabled
                ? "Please enable your microphone to continue"
                : "Waiting for minimum participants..."}
            </p>
          )}
        </div>
      </main>

      {/* Share Room Modal */}
      {showShareModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 max-w-lg w-full mx-4">
            <h3 className="text-xl font-bold text-gray-900 mb-4">
              🎉 Share Room Link
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
                  className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                    linkCopied
                      ? "bg-green-100 text-green-800"
                      : "bg-blue-500 text-white hover:bg-blue-600"
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
                <strong>💡 Tip:</strong> Anyone with this link can join your
                room. Share it via WhatsApp, Email, or any messaging app!
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
                        title: "Join my GupShup Cafe discussion!",
                        text: "Join me for an English conversation practice session",
                        url: shareableLink,
                      });
                    } catch (err) {
                      console.log("Error sharing:", err);
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
    </div>
  );
}

export default RoomLobbyPage;
