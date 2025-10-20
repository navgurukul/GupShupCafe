import React, { createContext, useContext, useEffect, useState } from 'react'
import { io } from 'socket.io-client'
import { useAuth } from './AuthContext'

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
    // TEMP: Allow connection without auth for testing
    if ((isAuthenticated && userData) && !socketRef.current) {
      const isProd = import.meta.env.MODE === 'production';
      const socketUrl = import.meta.env.VITE_SOCKET_URL || (isProd ? undefined : 'http://localhost:3003');

      // Get stored user data from localStorage
      const storedUserData = JSON.parse(localStorage.getItem('userData') || '{}');

      // Create socket with sensible reconnection options
      const newSocket = io(socketUrl, {
        auth: {
          userId: storedUserData.userId || userData.userId,
          name: storedUserData.name || userData.name,
          campusOrLocation: storedUserData?.campusOrLocation || userData?.campusOrLocation || null,
        },
        transports: ['polling', 'websocket'], // Try polling first, then upgrade to websocket
        reconnection: true,
        reconnectionAttempts: 10,
        reconnectionDelay: 1000,
        autoConnect: true,
        upgrade: true, // Allow transport upgrade
        forceNew: true // Force new connection
      })

      newSocket.on('connect', () => {
        console.log('[Socket] Connected to server:', newSocket.id)
        setConnected(true)
        // re-join room if needed after reconnect using metaRef
        if (metaRef.current.currentRoom && metaRef.current.selectedRole) {
          // Get stored data from localStorage
          const storedUserData = JSON.parse(localStorage.getItem('userData') || '{}');
          const storedParticipantData = JSON.parse(localStorage.getItem('participantData') || '{}');

          const reconnectUserData = {
            userId: storedUserData.userId || userData?.userId,
            name: storedUserData.name || userData?.name,
            campusOrLocation: storedUserData?.campusOrLocation || userData?.campusOrLocation || null,
            anonymousName: storedParticipantData.anonymous_name || storedUserData.name || userData?.name || 'Anonymous',
            role: metaRef.current.selectedRole
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
      })

      newSocket.on('connect_error', (error) => {
        console.error('[Socket] Connection error:', error)
        setConnected(false)
      })

      socketRef.current = newSocket
      setSocket(newSocket)
    }

    // Cleanup when auth is removed entirely
    return () => {
      if (!isAuthenticated && socketRef.current) {
        try {
          socketRef.current.close()
        } catch (e) {
          console.warn('[Socket] Error closing socket during cleanup', e)
        }
        socketRef.current = null
        metaRef.current = { currentRoom: null, selectedRole: null, roomMetadata: null }
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

      // Get stored data from localStorage
      const storedUserData = JSON.parse(localStorage.getItem('userData') || '{}');
      const storedParticipantData = JSON.parse(localStorage.getItem('participantData') || '{}');
      const anonymousName = storedParticipantData.anonymous_name || 'Anonymous'

      const joinUserData = {
        userId: storedUserData.userId || userData?.userId,
        name: storedUserData.name || userData?.name,
        campusOrLocation: storedUserData?.campusOrLocation || userData?.campusOrLocation || null,
        anonymousName: anonymousName,
        role: role
      }

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
