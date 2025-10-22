import React, { createContext, useContext, useEffect, useState } from "react";
import { io } from "socket.io-client";
import { useAuth } from "./AuthContext";

/**
 * Socket Context for managing real-time communication
 * Handles connection to the backend via Socket.io
 */

const SocketContext = createContext();

/**
 * SocketProvider Component
 * Manages socket connection and provides socket instance to children
 */
export function SocketProvider({ children }) {
  const socketRef = React.useRef(null);
  // metaRef holds plain metadata so we never overwrite the socket instance
  const metaRef = React.useRef({
    currentRoom: null,
    selectedRole: null,
    roomMetadata: null,
  });
  const [socket, setSocket] = useState(null);
  const [connected, setConnected] = useState(false);
  const [reconnectionState, setReconnectionState] = useState({
    isReconnecting: false,
    lastRoom: null,
    lastRole: null,
    lastMetadata: null,
  });
  const { isAuthenticated, user: userData } = useAuth();

  // Load persisted state on mount
  useEffect(() => {
    const persistedState = localStorage.getItem("gupshup-socket-state");
    if (persistedState) {
      try {
        const state = JSON.parse(persistedState);
        setReconnectionState((prev) => ({
          ...prev,
          lastRoom: state.currentRoom,
          lastRole: state.selectedRole,
          lastMetadata: state.roomMetadata,
        }));
        metaRef.current = {
          currentRoom: state.currentRoom,
          selectedRole: state.selectedRole,
          roomMetadata: state.roomMetadata,
        };
        console.log("[Socket] Restored state from localStorage:", state);
      } catch (error) {
        console.error("[Socket] Error parsing persisted state:", error);
      }
    }
  }, []);

  useEffect(() => {
    // Only connect if user is authenticated
    // Only initialize socket once when auth becomes available
    // Development bypass: allow connection without auth in development
    const isDevelopment =
      import.meta.env.DEV || window.location.hostname === "localhost";
    const shouldConnect = (isAuthenticated && userData) || isDevelopment;

    console.log("[Socket] Connection check:", {
      isAuthenticated,
      hasUserData: !!userData,
      isDevelopment,
      shouldConnect,
      hasSocket: !!socketRef.current,
    });

    if (shouldConnect && !socketRef.current) {
      const isProd = import.meta.env.MODE === "production";
      const socketUrl =
        import.meta.env.VITE_SOCKET_URL ||
        (isProd ? undefined : "http://localhost:3003");

      // Get stored user data from localStorage
      const storedUserData = JSON.parse(
        localStorage.getItem("userData") || "{}"
      );

      // For development: create mock data if no user data exists
      if (isDevelopment && !storedUserData.userId && !userData?.userId) {
        const mockUserData = {
          userId: "dev-user-" + Math.random().toString(36).substr(2, 9),
          name: "Dev User",
          campusOrLocation: "Development",
        };
        localStorage.setItem("userData", JSON.stringify(mockUserData));
        localStorage.setItem(
          "participantData",
          JSON.stringify({
            anonymous_name: "DevUser" + Math.random().toString(36).substr(2, 4),
          })
        );
        console.log(
          "[Socket] Created mock user data for development:",
          mockUserData
        );
      }

      console.log("[Socket] Creating socket connection to:", socketUrl);
      console.log("[Socket] Auth data:", {
        storedUserId: storedUserData.userId,
        userDataUserId: userData?.userId,
        storedName: storedUserData.name,
        userDataName: userData?.name,
      });

      // Create socket with enhanced reconnection options
      const newSocket = io(socketUrl, {
        auth: {
          userId:
            storedUserData.userId ||
            userData?.userId ||
            "anonymous-" + Math.random().toString(36).substr(2, 9),
          name: storedUserData.name || userData?.name || "Anonymous User",
          campusOrLocation:
            storedUserData.campusOrLocation ||
            userData?.campusOrLocation ||
            null,
        },
        transports: ["polling", "websocket"], // Try polling first, then upgrade to websocket
        reconnection: true,
        reconnectionAttempts: 15, // Increased attempts
        reconnectionDelay: 1000,
        reconnectionDelayMax: 10000, // Max delay between attempts
        randomizationFactor: 0.5, // Add randomness to prevent thundering herd
        timeout: 20000, // Connection timeout
        pingTimeout: 60000, // Ping timeout
        pingInterval: 25000, // Ping interval
        autoConnect: true,
        upgrade: true, // Allow transport upgrade
        forceNew: false, // Reuse existing connection if possible
      });

      console.log("[Socket] Setting up socket event listeners");

      newSocket.on("connect", () => {
        console.log("[Socket] Connected to server:", newSocket.id);
        setConnected(true);

        // Emit reconnection event to notify components
        window.dispatchEvent(
          new CustomEvent("socket-reconnected", {
            detail: { socketId: newSocket.id },
          })
        );

        // Small delay to ensure connection is fully established
        setTimeout(() => {
          // re-join room if needed after reconnect using metaRef
          if (metaRef.current.currentRoom && metaRef.current.selectedRole) {
            // Get stored data from localStorage
            const storedUserData = JSON.parse(
              localStorage.getItem("userData") || "{}"
            );
            const storedParticipantData = JSON.parse(
              localStorage.getItem("participantData") || "{}"
            );

            const reconnectUserData = {
              userId:
                storedUserData.userId || userData?.userId || "anonymous-user",
              name: storedUserData.name || userData?.name || "Anonymous User",
              campusOrLocation:
                storedUserData.campusOrLocation ||
                userData?.campusOrLocation ||
                null,
              anonymousName:
                storedParticipantData.anonymous_name ||
                storedUserData.name ||
                userData?.name ||
                "Anonymous",
              role: metaRef.current.selectedRole,
            };

            console.log(
              "[Socket] Reconnecting to room:",
              metaRef.current.currentRoom
            );
            console.log("[Socket] Reconnection user data:", reconnectUserData);

            if (metaRef.current.roomMetadata) {
              newSocket.emit(
                "join-room",
                metaRef.current.currentRoom,
                reconnectUserData,
                metaRef.current.roomMetadata
              );
            } else {
              newSocket.emit(
                "join-room",
                metaRef.current.currentRoom,
                reconnectUserData
              );
            }
          }
        }, 1000); // Increased delay to 1 second for better stability
      });

      newSocket.on("disconnect", (reason) => {
        console.log("[Socket] Disconnected from server:", reason);
        setConnected(false);

        // Emit disconnection event to notify components
        window.dispatchEvent(
          new CustomEvent("socket-disconnected", {
            detail: { reason, socketId: newSocket.id },
          })
        );
      });

      newSocket.on("connect_error", (error) => {
        console.error("[Socket] Connection error:", error);
        setConnected(false);

        // Emit connection error event
        window.dispatchEvent(
          new CustomEvent("socket-connection-error", {
            detail: { error, socketId: newSocket.id },
          })
        );
      });

      newSocket.on("reconnect", (attemptNumber) => {
        console.log("[Socket] Reconnected after", attemptNumber, "attempts");
        setConnected(true);
        setReconnectionState((prev) => ({ ...prev, isReconnecting: false }));

        // Attempt to rejoin room if we were in one
        if (metaRef.current.currentRoom) {
          console.log(
            "[Socket] Attempting to rejoin room:",
            metaRef.current.currentRoom
          );
          setTimeout(() => {
            joinRoom(
              metaRef.current.currentRoom,
              metaRef.current.selectedRole,
              metaRef.current.roomMetadata
            );
          }, 500); // Small delay to ensure connection is stable
        }

        // Emit reconnection success event
        window.dispatchEvent(
          new CustomEvent("socket-reconnect-success", {
            detail: { attemptNumber, socketId: newSocket.id },
          })
        );
      });

      newSocket.on("reconnect_attempt", (attemptNumber) => {
        console.log("[Socket] Reconnection attempt", attemptNumber);

        // Emit reconnection attempt event
        window.dispatchEvent(
          new CustomEvent("socket-reconnect-attempt", {
            detail: { attemptNumber, socketId: newSocket.id },
          })
        );
      });

      newSocket.on("reconnect_error", (error) => {
        console.error("[Socket] Reconnection error:", error);

        // Emit reconnection error event
        window.dispatchEvent(
          new CustomEvent("socket-reconnect-error", {
            detail: { error, socketId: newSocket.id },
          })
        );
      });

      newSocket.on("reconnect_failed", () => {
        console.error("[Socket] Reconnection failed after all attempts");

        // Emit reconnection failed event
        window.dispatchEvent(
          new CustomEvent("socket-reconnect-failed", {
            detail: { socketId: newSocket.id },
          })
        );
      });

      socketRef.current = newSocket;
      setSocket(newSocket);

      console.log("[Socket] Socket instance created and stored");
    }

    // Cleanup when auth is removed entirely
    return () => {
      if (!isAuthenticated && socketRef.current) {
        try {
          socketRef.current.close();
        } catch (e) {
          console.warn("[Socket] Error closing socket during cleanup", e);
        }
        socketRef.current = null;
        metaRef.current = {
          currentRoom: null,
          selectedRole: null,
          roomMetadata: null,
        };
        setSocket(null);
        setConnected(false);
      }
    };
  }, [isAuthenticated, userData]);

  /**
   * Join a room
   * @param {string} roomId - Room identifier
   * @param {string} role - User role ('speaker' or 'listener')
   * @param {object} roomMetadata - Optional room metadata (name, topic_category, cefr_level, etc.)
   * @param {string} anonymousName - Optional anonymous name to use instead of cached data
   */
  const joinRoom = (
    roomId,
    role = "listener",
    roomMetadata = null,
    anonymousName = null
  ) => {
    const s = socketRef.current || socket;
    if (s && s.emit) {
      // store current room/role in metaRef so reconnects can rejoin
      metaRef.current.currentRoom = roomId;
      metaRef.current.selectedRole = role;
      metaRef.current.roomMetadata = roomMetadata;

      // Persist state to localStorage for browser refresh recovery
      const stateToPersist = {
        currentRoom: roomId,
        selectedRole: role,
        roomMetadata: roomMetadata,
        timestamp: Date.now(),
      };
      localStorage.setItem(
        "gupshup-socket-state",
        JSON.stringify(stateToPersist)
      );
      console.log("[Socket] Persisted state to localStorage:", stateToPersist);

      // Get stored data from localStorage
      const storedUserData = JSON.parse(
        localStorage.getItem("userData") || "{}"
      );
      const storedParticipantData = JSON.parse(
        localStorage.getItem("participantData") || "{}"
      );
      const finalAnonymousName =
        anonymousName || storedParticipantData.anonymous_name || "Anonymous";

      console.log("[Socket] Using participant data:", {
        storedParticipantData,
        providedAnonymousName: anonymousName,
        finalAnonymousName,
        role,
      });

      // Debug: Log the full localStorage data
      console.log(
        "[Socket] Full localStorage participantData:",
        localStorage.getItem("participantData")
      );
      console.log(
        "[Socket] Full localStorage userData:",
        localStorage.getItem("userData")
      );

      const joinUserData = {
        userId: storedUserData.userId || userData?.userId || "anonymous-user",
        name: storedUserData.name || userData?.name || "Anonymous User",
        campus: storedUserData.campus || userData?.campus || null,
        location: storedUserData.location || userData?.location || null,
        anonymousName: finalAnonymousName,
        role: role,
      };

      // Emit with room metadata as third parameter if provided
      if (roomMetadata) {
        s.emit("join-room", roomId, joinUserData, roomMetadata);
      } else {
        s.emit("join-room", roomId, joinUserData);
      }
    }
  };

  /**
   * Retry failed socket operations with exponential backoff
   */
  const retryOperation = async (
    operation,
    maxRetries = 3,
    baseDelay = 1000
  ) => {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        return await operation();
      } catch (error) {
        console.log(
          `[Socket] Operation failed (attempt ${attempt}/${maxRetries}):`,
          error
        );

        if (attempt === maxRetries) {
          throw error;
        }

        // Exponential backoff with jitter
        const delay =
          baseDelay * Math.pow(2, attempt - 1) + Math.random() * 1000;
        await new Promise((resolve) => setTimeout(resolve, delay));
      }
    }
  };

  /**
   * Recover from connection errors
   */
  const recoverFromError = async () => {
    console.log("[Socket] Attempting to recover from error");

    try {
      // Try to reconnect if disconnected
      if (!connected) {
        await retryOperation(() => {
          if (socketRef.current) {
            socketRef.current.connect();
          }
        });
      }

      // Rejoin room if we were in one
      if (metaRef.current.currentRoom) {
        await retryOperation(() => {
          joinRoom(
            metaRef.current.currentRoom,
            metaRef.current.selectedRole,
            metaRef.current.roomMetadata
          );
        });
      }

      console.log("[Socket] Recovery successful");
    } catch (error) {
      console.error("[Socket] Recovery failed:", error);
      // Notify user of persistent connection issues
      if (typeof window !== "undefined" && window.alert) {
        window.alert("Connection lost. Please refresh the page to reconnect.");
      }
    }
  };

  /**
   * Leave current room
   */
  const leaveRoom = () => {
    const s = socketRef.current || socket;
    if (s && s.emit) {
      s.emit("leave-room");
      // clear stored room info
      metaRef.current.currentRoom = null;
      metaRef.current.selectedRole = null;
      metaRef.current.roomMetadata = null;

      // Clear persisted state
      localStorage.removeItem("gupshup-socket-state");
      console.log("[Socket] Cleared persisted state");
    }
  };

  /**
   * Send a message to the current room
   * @param {string} message - Message to send
   */
  const sendMessage = (message) => {
    const s = socketRef.current || socket;
    if (s && s.emit) {
      s.emit("message", message);
    }
  };

  /**
   * Signal ready to start discussion
   */
  const signalReady = () => {
    const s = socketRef.current || socket;
    if (s && s.emit) s.emit("user-ready");
  };

  /**
   * Change user role in current room
   * @param {string} userId - User identifier
   * @param {string} newRole - New role ('speaker' or 'listener')
   * @param {string} roomId - Optional room ID
   */
  const changeRole = (userId, newRole, roomId = null) => {
    const s = socketRef.current || socket;
    if (s && s.emit) s.emit("change-role", { userId, role: newRole, roomId });
  };

  /**
   * Request next speaker in the discussion
   */
  const requestNextSpeaker = () => {
    const s = socketRef.current || socket;
    if (s && s.emit) s.emit("next-speaker");
  };

  const value = {
    socket,
    connected,
    reconnectionState,
    joinRoom,
    leaveRoom,
    sendMessage,
    signalReady,
    requestNextSpeaker,
    changeRole,
    retryOperation,
    recoverFromError,
  };

  return (
    <SocketContext.Provider value={value}>{children}</SocketContext.Provider>
  );
}

/**
 * Custom hook to use socket context
 * @returns {Object} Socket context value
 */
export function useSocket() {
  const context = useContext(SocketContext);
  if (!context) {
    throw new Error("useSocket must be used within a SocketProvider");
  }
  return context;
}
