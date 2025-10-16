import { useState, useEffect } from 'react'
import { useSocket } from '../contexts/SocketContext'

/**
 * useRoomState Hook
 * Manages room state including participants, current speaker, and room metadata
 */
export function useRoomState() {
  const { socket, connected } = useSocket()
  const [roomState, setRoomState] = useState({
    roomCode: null,
    topic: null,
    status: 'waiting', // 'waiting', 'in-progress', 'ended'
    currentSpeakerIndex: 0,
    currentRound: 0,
    maxRounds: 3,
    speakingTime: 60
  })
  const [participants, setParticipants] = useState([])
  const [currentSpeaker, setCurrentSpeaker] = useState(null)

  useEffect(() => {
    if (!socket || !connected) return

    // Listen for room state updates
    const handleRoomUpdate = (data) => {
      console.log('[RoomState] Room update:', data)
      if (data.roomCode) {
        setRoomState(prev => ({
          ...prev,
          roomCode: data.roomCode,
          topic: data.topic || prev.topic,
          status: data.status || prev.status,
          currentSpeakerIndex: data.currentSpeakerIndex ?? prev.currentSpeakerIndex,
          currentRound: data.currentRound ?? prev.currentRound,
          maxRounds: data.maxRounds ?? prev.maxRounds,
          speakingTime: data.speakingTime ?? prev.speakingTime
        }))
      }
    }

    // Listen for participants updates
    const handleParticipantsUpdate = (data) => {
      console.log('[RoomState] Participants update:', data)
      if (data.participants && Array.isArray(data.participants)) {
        setParticipants(data.participants)
        
        // Update current speaker based on currentSpeakerIndex
        if (data.currentSpeakerIndex !== undefined && data.participants[data.currentSpeakerIndex]) {
          setCurrentSpeaker(data.participants[data.currentSpeakerIndex])
        }
      }
    }

    // Listen for speaker change
    const handleSpeakerChange = (data) => {
      console.log('[RoomState] Speaker change:', data)
      setRoomState(prev => ({
        ...prev,
        currentSpeakerIndex: data.index
      }))
      if (data.speaker) {
        setCurrentSpeaker(data.speaker)
      }
    }

    // Listen for discussion start
    const handleDiscussionStart = (data) => {
      console.log('[RoomState] Discussion started:', data)
      setRoomState(prev => ({
        ...prev,
        status: 'in-progress',
        topic: data.topic || prev.topic
      }))
    }

    // Listen for discussion end
    const handleDiscussionEnd = () => {
      console.log('[RoomState] Discussion ended')
      setRoomState(prev => ({
        ...prev,
        status: 'ended'
      }))
    }

    // Register event listeners
    socket.on('room-update', handleRoomUpdate)
    socket.on('participants-update', handleParticipantsUpdate)
    socket.on('speaker-change', handleSpeakerChange)
    socket.on('discussion-started', handleDiscussionStart)
    socket.on('discussion-ended', handleDiscussionEnd)

    // Cleanup listeners
    return () => {
      socket.off('room-update', handleRoomUpdate)
      socket.off('participants-update', handleParticipantsUpdate)
      socket.off('speaker-change', handleSpeakerChange)
      socket.off('discussion-started', handleDiscussionStart)
      socket.off('discussion-ended', handleDiscussionEnd)
    }
  }, [socket, connected])

  /**
   * Update room state with new data
   */
  const updateRoomState = (updates) => {
    setRoomState(prev => ({
      ...prev,
      ...updates
    }))
  }

  return {
    roomState,
    participants,
    currentSpeaker,
    updateRoomState
  }
}
