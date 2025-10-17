import React, { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'

import { useSocket } from '../contexts/SocketContext'
import { useAuth } from '../contexts/AuthContext'
import { useAudio } from '../contexts/AudioContext'
import { Users, Clock, Mic, MicOff, LogOut, Settings, Plus, BookOpen, Atom, PenTool, Brain } from 'lucide-react'

// Global flag to prevent multiple late join checks (accessible across components)
if (typeof window !== 'undefined') {
  window.lateJoinCheckInProgress = window.lateJoinCheckInProgress || false
}

/**
 * Lobby Page Component
 * Waiting area until minimum participants (1+) join the session
 */
function LobbyPage() {
  const navigate = useNavigate()
  const { socket, connected, joinRoom, signalReady } = useSocket()
  const { user, anonymousName, logout } = useAuth()
  const { 
    audioEnabled, 
    micPermission, 
    requestMicrophoneAccess, 
    isWebRTCSupported,
    userRole,
    updateUserRole
  } = useAudio()
  
  const [participants, setParticipants] = useState([])
  const [roomId, setRoomId] = useState('general')
  const [selectedRole, setSelectedRole] = useState('speaker') // Default to speaker
  const [minParticipants, setMinParticipants] = useState(1) // Default to 1 for solo testing
  const [isReady, setIsReady] = useState(false)
  const [waitingTime, setWaitingTime] = useState(0)
  const [systemMessage, setSystemMessage] = useState('Connecting to lobby...')
  const [isNavigating, setIsNavigating] = useState(false)
  
  // New state for room management
  const [showCreateRoom, setShowCreateRoom] = useState(false)
  const [newRoomId, setNewRoomId] = useState('')
  const [currentRoom, setCurrentRoom] = useState(null)
  const [inRoom, setInRoom] = useState(false)

  // Predefined rooms
  const predefinedRooms = [
    {
      id: 'education',
      name: 'Education',
      icon: BookOpen,
      color: 'bg-blue-500',
      description: 'Discuss educational topics and learning methodologies'
    },
    {
      id: 'science-technology',
      name: 'Science & Technology',
      icon: Atom,
      color: 'bg-green-500',
      description: 'Explore the latest in science and tech innovations'
    },
    {
      id: 'literature',
      name: 'Literature',
      icon: PenTool,
      color: 'bg-purple-500',
      description: 'Share thoughts on books, poetry, and creative writing'
    },
    {
      id: 'generative-ai',
      name: 'Generative AI',
      icon: Brain,
      color: 'bg-orange-500',
      description: 'Discuss AI, machine learning, and future technology'
    }
  ]

  // Room management functions
  const handleCreateRoom = () => {
    if (newRoomId.trim()) {
      const roomData = {
        id: newRoomId.trim(),
        name: newRoomId.trim(),
        isCustom: true
      }
      joinRoom(roomData.id, selectedRole)
      setCurrentRoom(roomData)
      setInRoom(true)
      setShowCreateRoom(false)
      setNewRoomId('')
    }
  }

  const handleJoinPredefinedRoom = (room) => {
    joinRoom(room.id, selectedRole)
    setCurrentRoom(room)
    setInRoom(true)
  }

  const handleLeaveRoom = () => {
    if (socket) {
      socket.emit('leave-room', { roomId: currentRoom?.id })
    }
    setCurrentRoom(null)
    setInRoom(false)
    setParticipants([])
  }

  // Timer for waiting time and late join check
  useEffect(() => {
    // Disable late join check in development to prevent loops
    const isDevelopment = import.meta.env.DEV || window.location.hostname === 'localhost'
    if (isDevelopment) {
      console.log('[Lobby][Debug] Development mode - disabling auto late join navigation')
      // Just start the timer, skip late join check
      const timer = setInterval(() => {
        setWaitingTime(prev => prev + 1)
      }, 1000)
      return () => clearInterval(timer)
    }

    // Production late join logic
    let isMounted = true; // Flag to check if component is still mounted

    const checkDiscussionState = async () => {
      // Check if a discussion is already active for late joiners
      try {
        const apiUrl = import.meta.env.VITE_API_URL || '';
        const res = await fetch(`${apiUrl}/api/room/${roomId}/state`);
        const json = await res.json();
        
        if (isMounted && json?.discussion?.active) {
          console.log('[Lobby][Debug] Late join detected - navigating to /roundtable');
          // Use a session flag to indicate a late join is in progress
          sessionStorage.setItem('late-join-navigating', 'true');
          navigate('/roundtable', { replace: true });
        }
      } catch (err) {
        console.warn('[Lobby][Debug] Failed to check room state for late join', err);
      }
    };

    // If not in development, and not already joining, check the state
    if (!isDevelopment && !sessionStorage.getItem('late-join-navigating')) {
      checkDiscussionState();
    }

    const timer = setInterval(() => {
      if (isMounted) {
        setWaitingTime(prev => prev + 1);
      }
    }, 1000);

    return () => {
      isMounted = false;
      clearInterval(timer);
    };
  }, [roomId, isNavigating, navigate])

  // Socket event handlers
  useEffect(() => {
    if (!socket || isNavigating) {
      console.log('[Lobby][Debug] Socket not available or navigating')
      return
    }

    console.log('[Lobby][Debug] Socket available, connected:', connected)
    // Socket connect/disconnect events
    socket.on('connect', () => {
      if (!isNavigating) {
        console.log('[Lobby][Debug] Socket connected:', socket.id)
        console.log(`[Lobby][Debug] Calling joinRoom with roomId: ${roomId}, role: ${selectedRole} (on connect)`)
        joinRoom(roomId, selectedRole)
      }
    })
    socket.on('disconnect', () => {
      console.log('[Lobby][Debug] Socket disconnected')
    })

    // Handle participants update
    socket.on('participants-update', (updatedParticipants) => {
      console.log('[Lobby][Debug] Received participants-update:', updatedParticipants)
      setParticipants(updatedParticipants)
      // Enhanced debug: print all roles and readiness
      console.log('[Lobby][Debug] Participants array:', updatedParticipants.map(p => ({name: p.anonymousName, role: p.role, isReady: p.isReady, id: p.id, socketId: p.socketId})))
      console.log('[Lobby][Debug] Local userRole:', userRole, 'selectedRole:', selectedRole)
      // Find local participant in the update
      const local = updatedParticipants.find(p => p.socketId === socket.id)
      if (local) {
        console.log('[Lobby][Debug] Local participant from update:', local)
      } else {
        console.log('[Lobby][Debug] Local participant not found in update. Socket ID:', socket.id)
      }
      if (updatedParticipants.length >= 1) {
        setSystemMessage('Ready to start! Click "Ready" when you want to begin.')
      } else {
        setSystemMessage('Connecting to discussion room...')
      }
    })

    // Handle discussion start
    socket.on('discussion-started', () => {
      console.log('[Lobby][Debug] Received discussion-started event - navigating to /roundtable')
      if (!isNavigating) {
        setIsNavigating(true)
        setSystemMessage('Discussion starting! Redirecting to roundtable...')
        console.log('[Lobby][Debug] Navigating to /roundtable now')
        navigate('/roundtable', { replace: true })
      }
    })

    // Handle user ready status
    socket.on('user-ready-update', (readyUsers) => {
      console.log('[Lobby][Debug] Received user-ready-update:', readyUsers)
      // Update UI to show who's ready
      console.log('[Lobby][Debug] Ready users:', readyUsers)
    })

    // Handle system messages
    socket.on('system-message', (message) => {
      console.log('[Lobby][Debug] Received system message:', message)
      setSystemMessage(message)
    })

    // Cleanup event listeners
    return () => {
      socket.off('connect')
      socket.off('disconnect')
      socket.off('participants-update')
      socket.off('discussion-started')
      socket.off('user-ready-update')
      socket.off('system-message')
    }
  }, [socket, connected, isNavigating, navigate, joinRoom, roomId, selectedRole, userRole])

  // Audio permission management
  const handleMicrophoneSetup = async () => {
    console.log('[Lobby][Debug] Setting up microphone')
    await requestMicrophoneAccess()
  }

  // User actions
  const handleLogout = () => {
    console.log('[Lobby][Debug] Logout clicked')
    logout()
  }

  const handleReady = () => {
    console.log('[Lobby][Debug] Ready button clicked')
    signalReady()
    setIsReady(true)
  }

  // Derived state
  const canStart = participants.length >= minParticipants && 
                   (selectedRole === 'listener' || audioEnabled)

  // Format time display
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  // Check if ready button should be disabled
  const isReadyButtonDisabled = !canStart

  // Early return for development debugging
  if (import.meta.env.DEV && participants.length === 0) {
    // In development, show the interface even with no participants
    console.log('[Lobby][Debug] Development mode - showing interface with 0 participants')
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
    )
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
            <div className={`flex items-center space-x-1 text-sm ${
              connected ? 'text-green-600' : 'text-red-600'
            }`}>
              <div className={`w-2 h-2 rounded-full ${
                connected ? 'bg-green-600' : 'bg-red-600'
              }`}></div>
              <span>{connected ? 'Connected' : 'Disconnected'}</span>
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
        {!inRoom ? (
          // Room Selection View
          <div className="space-y-8">
            {/* Header */}
            <div className="text-center space-y-4">
              <h2 className="text-3xl font-bold text-gray-900">Welcome to GupShup Cafe</h2>
              <p className="text-lg text-gray-600">Join a discussion room or create your own</p>
            </div>

            {/* Create New Room Card */}
            <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-dashed border-gray-300 hover:border-blue-400 transition-colors">
              <div className="text-center space-y-4">
                <div className="w-16 h-16 bg-blue-100 rounded-full mx-auto flex items-center justify-center">
                  <Plus className="w-8 h-8 text-blue-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900">Create New Room</h3>
                <p className="text-gray-600">Start your own discussion room with a custom topic</p>
                
                {!showCreateRoom ? (
                  <button
                    onClick={() => setShowCreateRoom(true)}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Create Room
                  </button>
                ) : (
                  <div className="space-y-4">
                    <input
                      type="text"
                      value={newRoomId}
                      onChange={(e) => setNewRoomId(e.target.value)}
                      placeholder="Enter room name..."
                      className="w-full max-w-md mx-auto px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      onKeyPress={(e) => e.key === 'Enter' && handleCreateRoom()}
                    />
                    <div className="flex justify-center space-x-3">
                      <button
                        onClick={handleCreateRoom}
                        disabled={!newRoomId.trim()}
                        className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                      >
                        Create
                      </button>
                      <button
                        onClick={() => {
                          setShowCreateRoom(false)
                          setNewRoomId('')
                        }}
                        className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
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
              <h3 className="text-2xl font-bold text-gray-900 text-center">Existing Rooms</h3>
              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                {predefinedRooms.map((room) => {
                  const IconComponent = room.icon
                  return (
                    <div
                      key={room.id}
                      className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-all duration-300 transform hover:scale-105"
                    >
                      <div className="text-center space-y-4">
                        <div className={`w-16 h-16 ${room.color} rounded-full mx-auto flex items-center justify-center`}>
                          <IconComponent className="w-8 h-8 text-white" />
                        </div>
                        <div>
                          <h4 className="text-lg font-semibold text-gray-900">{room.name}</h4>
                          <p className="text-sm text-gray-600 mt-2">{room.description}</p>
                        </div>
                        <button
                          onClick={() => handleJoinPredefinedRoom(room)}
                          className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
                        >
                          Join
                        </button>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        ) : (
          // In Room View
          <div className="space-y-8">
            {/* Room Header */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  {currentRoom?.icon && !currentRoom?.isCustom && (
                    <div className={`w-12 h-12 ${predefinedRooms.find(r => r.id === currentRoom.id)?.color} rounded-full flex items-center justify-center`}>
                      {React.createElement(predefinedRooms.find(r => r.id === currentRoom.id)?.icon, { className: "w-6 h-6 text-white" })}
                    </div>
                  )}
                  {currentRoom?.isCustom && (
                    <div className="w-12 h-12 bg-gray-500 rounded-full flex items-center justify-center">
                      <Users className="w-6 h-6 text-white" />
                    </div>
                  )}
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">{currentRoom?.name}</h2>
                    <p className="text-gray-600">
                      {currentRoom?.isCustom ? 'Custom Room' : predefinedRooms.find(r => r.id === currentRoom.id)?.description}
                    </p>
                  </div>
                </div>
                <button
                  onClick={handleLeaveRoom}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                >
                  Leave Room
                </button>
              </div>
            </div>

            {/* Participants */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Participants ({participants.length})
              </h3>
              
              {participants.length > 0 ? (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {participants.map((participant) => (
                    <div 
                      key={participant.id} 
                      className="flex items-center space-x-3 p-4 bg-gray-50 rounded-lg"
                    >
                      <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-semibold">
                        {participant.anonymousName.charAt(0).toUpperCase()}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-gray-900 truncate">{participant.anonymousName}</p>
                        <div className="flex items-center space-x-2">
                          <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                            participant.role === 'speaker' 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-blue-100 text-blue-800'
                          }`}>
                            {participant.role === 'speaker' ? '🎤' : '👂'}
                          </span>
                          {participant.isReady && (
                            <span className="text-xs text-green-600 font-medium">Ready</span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Users className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>You're the first one here! Others will join soon.</p>
                </div>
              )}
            </div>

            {/* Ready Button */}
            <div className="text-center">
              {!isReady ? (
                <button
                  onClick={() => {
                    if (socket && currentRoom) {
                      console.log('[Lobby][Debug] Signaling ready for room:', currentRoom.id)
                      signalReady()
                      setIsReady(true)
                    }
                  }}
                  className="px-8 py-4 bg-green-600 text-white text-lg font-semibold rounded-xl hover:bg-green-700 transition-colors shadow-lg hover:shadow-xl transform hover:scale-105"
                >
                  Ready
                </button>
              ) : (
                <div className="inline-flex items-center space-x-3 px-6 py-3 bg-green-100 text-green-800 rounded-xl">
                  <div className="w-3 h-3 bg-green-600 rounded-full animate-pulse"></div>
                  <span className="font-semibold">You're Ready! Waiting for others...</span>
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default LobbyPage
