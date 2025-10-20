import React, { createContext, useContext, useEffect, useState } from 'react'
import { io } from 'socket.io-client'
import { useAuth } from './AuthContext'
import { visibilityManager } from '../utils/visibilityManager'

/**
 * Socket Context for managing real-time communication
 * Handles connection to the backend via Socket.io
 */

const SocketContext = createContext()

/**
 * SocketProvider Component
 * Manages socket connection and provides socket instance to children
 */
export function SocketProvider({ children }) {
  const socketRef = React.useRef(null)
  // metaRef holds plain metadata so we never overwrite the socket instance
  const metaRef = React.useRef({ currentRoom: null, selectedRole: null, roomMetadata: null })
  const [socket, setSocket] = useState(null)
  const [connected, setConnected] = useState(false)
  const { isAuthenticated, user: userData } = useAuth()

  useEffect(() => {
    // Only connect if user is authenticated
    // Only initialize socket once when auth becomes available
    // Development bypass: allow connection without auth in development
    const isDevelopment = import.meta.env.DEV || window.location.hostname === 'localhost'
    const shouldConnect = (isAuthenticated && userData) || isDevelopment

    console.log('[Socket] Connection check:', {
      isAuthenticated,
      hasUserData: !!userData,
      isDevelopment,
      shouldConnect,
      hasSocket: !!socketRef.current
    })

    if (shouldConnect && !socketRef.current) {
      const isProd = import.meta.env.MODE === 'production';
      const socketUrl = import.meta.env.VITE_SOCKET_URL || (isProd ? undefined : 'http://localhost:3003');

      // Get stored user data from localStorage
      const storedUserData = JSON.parse(localStorage.getItem('userData') || '{}');

      // For development: create mock data if no user data exists
      if (isDevelopment && !storedUserData.userId && !userData?.userId) {
        const mockUserData = {
          userId: 'dev-user-' + Math.random().toString(36).substring(2, 11),
          name: 'Dev User',
          campusOrLocation: 'Development'
        };
        localStorage.setItem('userData', JSON.stringify(mockUserData));
        localStorage.setItem('participantData', JSON.stringify({
          anonymous_name: 'DevUser' + Math.random().toString(36).substring(2, 6)
        }));
        console.log('[Socket] Created mock user data for development:', mockUserData);
      }

      // Restore room state from localStorage if available
      const storedRoomState = JSON.parse(localStorage.getItem('socketRoomState') || '{}');
      if (storedRoomState.currentRoom) {
        metaRef.current = storedRoomState;
        console.log('[Socket] Restored room state from localStorage:', storedRoomState);
      }

      console.log('[Socket] Creating socket connection to:', socketUrl)
      console.log('[Socket] Auth data:', {
        storedUserId: storedUserData.userId,
        userDataUserId: userData?.userId,
        storedName: storedUserData.name,
        userDataName: userData?.name
      })

      // Create socket with enhanced reconnection options
      const newSocket = io(socketUrl, {
        auth: {
          userId: storedUserData.userId || userData?.userId || 'anonymous-' + Math.random().toString(36).substring(2, 11),
          name: storedUserData.name || userData?.name || 'Anonymous User',
          campusOrLocation: storedUserData.campusOrLocation || userData?.campusOrLocation || null,
        },
        transports: ['polling', 'websocket'], // Try polling first, then upgrade to websocket
        reconnection: true,
        reconnectionAttempts: 20, // Increased attempts
        reconnectionDelay: 1000,
        reconnectionDelayMax: 5000, // Max delay between attempts
        maxReconnectionAttempts: 20,
        timeout: 20000, // Connection timeout
        autoConnect: true,
        upgrade: true, // Allow transport upgrade
        forceNew: false // Reuse existing connection if possible
      })

      console.log('[Socket] Setting up socket event listeners')

      newSocket.on('connect', () => {
        console.log('[Socket] Connected to server:', newSocket.id)
        setConnected(true)
        
        // Auto-rejoin room if we were in one before disconnect
        if (metaRef.current.currentRoom && metaRef.current.selectedRole) {
          console.log('[Socket] Auto-rejoining room after reconnect:', metaRef.current.currentRoom)
          
          // Get stored data from localStorage
          const storedUserData = JSON.parse(localStorage.getItem('userData') || '{}');
          const storedParticipantData = JSON.parse(localStorage.getItem('participantData') || '{}');

          const reconnectUserData = {
            userId: storedUserData.userId || userData?.userId || 'anonymous-user',
            name: storedUserData.name || userData?.name || 'Anonymous User',
            campusOrLocation: storedUserData.campusOrLocation || userData?.campusOrLocation || null,
            anonymousName: storedParticipantData.anonymous_name || storedUserData.name || userData?.name || 'Anonymous',
            role: metaRef.current.selectedRole,
            isReconnecting: true // Flag to indicate this is a reconnection
          }
          
          if (metaRef.current.roomMetadata) {
            newSocket.emit('join-room', metaRef.current.currentRoom, reconnectUserData, metaRef.current.roomMetadata)
          } else {
            newSocket.emit('join-room', metaRef.current.currentRoom, reconnectUserData)
          }
        }
      })

      newSocket.on('disconnect', (reason) => {
        console.log('[Socket] Disconnected from server:', reason)
        setConnected(false)
        
        // Don't clear room state on disconnect - keep it for reconnection
        if (reason === 'io server disconnect') {
          // Server initiated disconnect, might be intentional
          console.log('[Socket] Server initiated disconnect')
        } else {
          // Client side disconnect or network issue, prepare for reconnection
          console.log('[Socket] Client/network disconnect, will attempt reconnection')
        }
      })

      newSocket.on('reconnect', (attemptNumber) => {
        console.log(`[Socket] Reconnected after ${attemptNumber} attempts`)
        setConnected(true)
      })

      newSocket.on('reconnect_attempt', (attemptNumber) => {
        console.log(`[Socket] Reconnection attempt ${attemptNumber}`)
      })

      newSocket.on('reconnect_error', (error) => {
        console.error('[Socket] Reconnection error:', error)
      })

      newSocket.on('reconnect_failed', () => {
        console.error('[Socket] Reconnection failed after all attempts')
        setConnected(false)
      })

      newSocket.on('connect_error', (error) => {
        console.error('[Socket] Connection error:', error)
        setConnected(false)
      })

      // Add heartbeat to detect connection issues
      let heartbeatInterval;
      newSocket.on('connect', () => {
        heartbeatInterval = setInterval(() => {
          if (newSocket.connected) {
            newSocket.emit('heartbeat', { timestamp: Date.now() });
          }
        }, 30000); // Send heartbeat every 30 seconds
      });

      newSocket.on('disconnect', () => {
        if (heartbeatInterval) {
          clearInterval(heartbeatInterval);
        }
      });

      socketRef.current = newSocket
      setSocket(newSocket)

      console.log('[Socket] Socket instance created and stored')
    }

    // Handle page visibility changes for connection optimization
    const handleVisibilityChange = (isVisible, event) => {
      const socket = socketRef.current
      if (!socket) return

      if (isVisible) {
        console.log('[Socket] Page became visible, ensuring connection')
        if (!socket.connected) {
          socket.connect()
        }
      } else if (event === 'beforeunload') {
        console.log('[Socket] Page unloading, saving state')
        // State is already saved in localStorage, just log
      } else {
        console.log('[Socket] Page became hidden, connection will be maintained')
        // Keep connection alive but reduce activity
      }
    }

    // Add visibility listener
    const removeVisibilityListener = visibilityManager.addListener(handleVisibilityChange)

    // Cleanup visibility listener
    return () => {
      removeVisibilityListener()
      if (!isAuthenticated && socketRef.current) {
        try {
          socketRef.current.close()
        } catch (e) {
          console.warn('[Socket] Error closing socket during cleanup', e)
        }
        socketRef.current = null
        metaRef.current = { currentRoom: null, selectedRole: null, roomMetadata: null }
        localStorage.removeItem('socketRoomState')
        setSocket(null)
        setConnected(false)
      }
    }



  }, [isAuthenticated, userData])

  /**
   * Join a room
   * @param {string} roomId - Room identifier
   * @param {string} role - User role ('speaker' or 'listener')
   * @param {object} roomMetadata - Optional room metadata (name, topic_category, cefr_level, etc.)
   */
  const joinRoom = (roomId, role = 'listener', roomMetadata = null) => {
    const s = socketRef.current || socket
    if (s && s.emit) {
      // store current room/role in metaRef so reconnects can rejoin
      metaRef.current.currentRoom = roomId
      metaRef.current.selectedRole = role
      metaRef.current.roomMetadata = roomMetadata

      // Persist room state to localStorage for reconnection
      localStorage.setItem('socketRoomState', JSON.stringify({
        currentRoom: roomId,
        selectedRole: role,
        roomMetadata: roomMetadata,
        joinedAt: new Date().toISOString()
      }))

      // Get stored data from localStorage
      const storedUserData = JSON.parse(localStorage.getItem('userData') || '{}');
      const storedParticipantData = JSON.parse(localStorage.getItem('participantData') || '{}');
      const anonymousName = storedParticipantData.anonymous_name || 'Anonymous'

      const joinUserData = {
        userId: storedUserData.userId || userData?.userId || 'anonymous-user',
        name: storedUserData.name || userData?.name || 'Anonymous User',
        campusOrLocation: storedUserData.campusOrLocation || userData?.campusOrLocation || null,
        anonymousName: anonymousName,
        role: role
      }

      console.log('[Socket] Joining room:', roomId, 'with role:', role)

      // Emit with room metadata as third parameter if provided
      if (roomMetadata) {
        s.emit('join-room', roomId, joinUserData, roomMetadata)
      } else {
        s.emit('join-room', roomId, joinUserData)
      }
    }
  }

  /**
   * Leave current room
   */
  const leaveRoom = () => {
    const s = socketRef.current || socket
    if (s && s.emit) {
      s.emit('leave-room')
      // clear stored room info
      metaRef.current.currentRoom = null
      metaRef.current.selectedRole = null
      metaRef.current.roomMetadata = null
      
      // Clear persisted room state
      localStorage.removeItem('socketRoomState')
      
      console.log('[Socket] Left room and cleared state')
    }
  }

  /**
   * Send a message to the current room
   * @param {string} message - Message to send
   */
  const sendMessage = (message) => {
    const s = socketRef.current || socket
    if (s && s.emit) {
      s.emit('message', message)
    }
  }

  /**
   * Signal ready to start discussion
   */
  const signalReady = () => {
    const s = socketRef.current || socket
    if (s && s.emit) s.emit('user-ready')
  }

  /**
   * Change user role in current room
   * @param {string} userId - User identifier
   * @param {string} newRole - New role ('speaker' or 'listener')
   * @param {string} roomId - Optional room ID
   */
  const changeRole = (userId, newRole, roomId = null) => {
    const s = socketRef.current || socket
    if (s && s.emit) s.emit('role-change', { userId, newRole, roomId })
  }

  /**
   * Request next speaker in the discussion
   */
  const requestNextSpeaker = () => {
    const s = socketRef.current || socket
    if (s && s.emit) s.emit('next-speaker')
  }

  const value = {
    socket,
    connected,
    joinRoom,
    leaveRoom,
    sendMessage,
    signalReady,
    requestNextSpeaker,
    changeRole
  }

  return (
    <SocketContext.Provider value={value}>
      {children}
    </SocketContext.Provider>
  )
}

/**
 * Custom hook to use socket context
 * @returns {Object} Socket context value
 */
export function useSocket() {
  const context = useContext(SocketContext)
  if (!context) {
    throw new Error('useSocket must be used within a SocketProvider')
  }
  return context
}
