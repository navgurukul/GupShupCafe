import React, { createContext, useContext, useState, useEffect } from 'react'
import { useSocket } from './SocketContext'

/**
 * Audio Context for managing WebRTC audio communication
 * Handles microphone access, audio streams, and peer connections
 */

const AudioContext = createContext()

/**
 * AudioProvider Component
 * Manages audio state and WebRTC functionality
 */
export function AudioProvider({ children }) {
  const { socket, connected } = useSocket()
  // Track if we have already signaled WebRTC readiness
  const [webrtcReadySignaled, setWebrtcReadySignaled] = useState(false)

  useEffect(() => {
    if (socket) {
      console.log('[Audio][Debug] Socket object available', socket)
      socket.on('connect', () => {
        console.log('[Audio][Debug] Socket connected:', socket.id)
      })
      socket.on('disconnect', () => {
        console.log('[Audio][Debug] Socket disconnected')
      })
    }
  }, [socket])

  const [audioEnabled, setAudioEnabled] = useState(false)
  const [micPermission, setMicPermission] = useState(null) // null, 'granted', 'denied'
  const [localStream, setLocalStream] = useState(null)
  const [isMuted, setIsMuted] = useState(true)
  const [audioLevel, setAudioLevel] = useState(0)
  const [peers, setPeers] = useState({}) // map socketId -> RTCPeerConnection
  const [remoteStreams, setRemoteStreams] = useState({}) // map socketId -> MediaStream
  const [userRole, setUserRole] = useState('listener') // Track user's current role
  const localStreamRef = React.useRef(null)

  /**
   * Request microphone permission and get audio stream
   * Only allowed for speakers
   */
  // Request microphone access and set up local stream ONCE per session
  const requestMicrophoneAccess = async () => {
    console.log('[Audio] requestMicrophoneAccess called');
    
    if (localStreamRef.current) {
      console.log('[Audio] Using existing local stream');
      setMicPermission('granted')
      setAudioEnabled(true)
      return localStreamRef.current
    }
    
    try {
      console.log('[Audio] Requesting microphone access from browser');
      const audioConstraints = {
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 48000,
          sampleSize: 16,
          channelCount: 1,
          latency: 0.01,
          googEchoCancellation: true,
          googAutoGainControl: true,
          googNoiseSuppression: true,
          googHighpassFilter: true,
          googTypingNoiseDetection: true,
          googAudioMirroring: false
        }
      }
      const stream = await navigator.mediaDevices.getUserMedia(audioConstraints)
      console.log('[Audio] Microphone access granted, stream:', stream);
      localStreamRef.current = stream
      setLocalStream(stream)
      setMicPermission('granted')
      setAudioEnabled(true)
      setupAudioLevelMonitoring(stream)
      // Do not emit 'ready-for-webrtc' here; emit only after both localStream and participants-update are ready
      return stream
    } catch (error) {
      console.error('Error accessing microphone:', error)
      setMicPermission('denied')
      setAudioEnabled(false)
      return null
    }
  }

  /**
   * Update user role and handle audio stream accordingly
   * @param {string} newRole - New role ('speaker' or 'listener')
   */
  // Only update role, do not destroy local stream
  const updateUserRole = async (newRole) => {
    console.log(`[Audio] Updating user role from ${userRole} to ${newRole}`)
    setUserRole(newRole)
    if (newRole === 'speaker') {
      await requestMicrophoneAccess()
    }
    // Do not stop or destroy the local stream on demotion
  }

  /**
   * Set up audio level monitoring for visual feedback
   * @param {MediaStream} stream - Audio stream to monitor
   */
  const setupAudioLevelMonitoring = (stream) => {
    try {
      const audioContext = new (window.AudioContext || window.webkitAudioContext)()
      const analyser = audioContext.createAnalyser()
      const microphone = audioContext.createMediaStreamSource(stream)
      const dataArray = new Uint8Array(analyser.frequencyBinCount)

      microphone.connect(analyser)
      analyser.fftSize = 256

      const updateAudioLevel = () => {
        analyser.getByteFrequencyData(dataArray)
        const average = dataArray.reduce((a, b) => a + b) / dataArray.length
        setAudioLevel(average)
        
        if (audioEnabled) {
          requestAnimationFrame(updateAudioLevel)
        }
      }

      updateAudioLevel()
    } catch (error) {
      console.error('Error setting up audio level monitoring:', error)
    }
  }

  /**
   * Mute/unmute the microphone (always available if mic is granted)
   */
  const toggleMute = () => {
    const stream = localStreamRef.current || localStream
    if (stream) {
      const audioTracks = stream.getAudioTracks()
      audioTracks.forEach(track => {
        track.enabled = isMuted
      })
      setIsMuted(!isMuted)
    }
  }

  /**
   * Optimize SDP for audio-only communication
   * @param {RTCSessionDescription} sessionDescription - Original SDP
   * @returns {RTCSessionDescription} Optimized SDP
   */
  const optimizeAudioSDP = (sessionDescription) => {
    let sdp = sessionDescription.sdp
    
    // Remove video-related lines
    sdp = sdp.replace(/m=video.*\r?\n/g, '')
    sdp = sdp.replace(/a=rtcp-fb:.*\r?\n/g, '')
    sdp = sdp.replace(/a=fmtp:.*profile-level-id.*\r?\n/g, '')
    
    // Prioritize Opus codec for better voice quality
    const opusCodecRegex = /a=rtpmap:(\d+) opus\/48000\/2\r?\n/
    const opusMatch = sdp.match(opusCodecRegex)
    
    if (opusMatch) {
      const opusPayloadType = opusMatch[1]
      
      // Find and modify m=audio line to prioritize Opus
      const audioLineRegex = /m=audio \d+ UDP\/TLS\/RTP\/SAVPF (.+)\r?\n/
      const audioMatch = sdp.match(audioLineRegex)
      
      if (audioMatch) {
        const payloadTypes = audioMatch[1].split(' ')
        const reorderedTypes = [opusPayloadType, ...payloadTypes.filter(pt => pt !== opusPayloadType)]
        const port = audioMatch[0].split(' ')[1]
        sdp = sdp.replace(audioLineRegex, `m=audio ${port} UDP/TLS/RTP/SAVPF ${reorderedTypes.join(' ')}\r\n`)
      }
      
      // Add Opus-specific optimizations
      const opusSettings = `a=fmtp:${opusPayloadType} minptime=10;useinbandfec=1;usedtx=1\r\n`
      if (!sdp.includes(opusSettings)) {
        sdp = sdp.replace(opusMatch[0], opusMatch[0] + opusSettings)
      }
    }
    
    // Add audio quality settings
    sdp += 'a=extmap:1 urn:ietf:params:rtp-hdrext:ssrc-audio-level\r\n'
    
    return new RTCSessionDescription({
      type: sessionDescription.type,
      sdp: sdp
    })
  }

  const createPeerConnection = (peerSocketId, socket) => {
    const iceServers = [
      { urls: 'stun:stun.l.google.com:19302' },
      { urls: 'stun:stun1.l.google.com:19302' }
    ]
    
    // Audio-optimized peer connection configuration
    const config = {
      iceServers,
      iceCandidatePoolSize: 10,
      bundlePolicy: 'balanced',
      rtcpMuxPolicy: 'require',
      // Audio-specific optimizations
      sdpSemantics: 'unified-plan'
    }
    
    const pc = new RTCPeerConnection(config)

    // send local ICE candidates to the peer via server
    pc.onicecandidate = (event) => {
      if (event.candidate) {
        socket.emit('webrtc-ice-candidate', { to: peerSocketId, candidate: event.candidate })
      }
    }

    // Handle incoming remote streams (from broadcast test pattern)
    pc.ontrack = (event) => {
      try {
        console.log(`[Audio][Debug] ontrack event for peer: ${peerSocketId}`)
        const remoteStream = event.streams[0]
        if (remoteStream) {
          // Store remote stream in state for UI components
          setRemoteStreams(prev => ({ ...prev, [peerSocketId]: remoteStream }))
          // Optionally, also play audio for debugging (hidden)
          const audioElement = document.createElement('audio')
          audioElement.srcObject = remoteStream
          audioElement.autoplay = true
          audioElement.controls = false
          audioElement.id = `remote-audio-${peerSocketId}`
          audioElement.volume = 1.0
          let container = document.getElementById('remote-audio-container')
          if (!container) {
            container = document.createElement('div')
            container.id = 'remote-audio-container'
            container.style.display = 'none'
            document.body.appendChild(container)
          }
          const oldElement = document.getElementById(`remote-audio-${peerSocketId}`)
          if (oldElement) {
            oldElement.remove()
          }
          container.appendChild(audioElement)
        } else {
          console.warn(`[Audio][Debug] No remoteStream found in ontrack for peer: ${peerSocketId}`)
        }
      } catch (err) {
        console.error(`[Audio][Debug] Error handling ontrack event for ${peerSocketId}:`, err)
      }
    }

    // Add connection state change logging
    pc.onconnectionstatechange = () => {
      console.log(`Peer ${peerSocketId} connection state:`, pc.connectionState)
    }

    // store pc
    setPeers(prev => ({ ...prev, [peerSocketId]: pc }))
    return pc
  }


  /**
   * Stop audio stream and cleanup
   */
  const stopAudio = () => {
    if (localStreamRef.current) {
      localStreamRef.current.getTracks().forEach(track => track.stop())
      localStreamRef.current = null
      setLocalStream(null)
    }
    setAudioEnabled(false)
    setIsMuted(true)
    setAudioLevel(0)
  }

  /**
   * Enable audio for speaking (unmute)
   */
  const enableSpeaking = async () => {
    console.log('[Audio] enableSpeaking called');
    console.log('[Audio] Current state:', { localStream: !!localStream, isMuted, userRole });
    
    // Request microphone access if we don't have a local stream yet
    if (!localStream) {
      console.log('[Audio] Requesting microphone access for speaking')
      await requestMicrophoneAccess()
    }
    
    // Update user role to speaker
    updateUserRole('speaker')
    
    // Unmute if we're muted
    if (isMuted) {
      console.log('[Audio] Unmuting microphone');
      toggleMute()
    }
    
    console.log('[Audio] enableSpeaking completed');
  }

  /**
   * Disable audio for speaking (mute)
   */
  const disableSpeaking = () => {
    if (localStream && !isMuted) {
      toggleMute()
    }
  }

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopAudio()
    }
  }, [])

  // On mount, set up local stream ONCE if user is speaker
  useEffect(() => {
    if (userRole === 'speaker' && !localStreamRef.current) {
      requestMicrophoneAccess()
    }
  }, [userRole])

  // Setup peer signaling when socket is available
  useEffect(() => {
    if (!socket || !connected) return
    
    console.log('[Audio] Setting up peer signaling handlers')
    
    // Define handlers
    const handleOffer = async ({ from, sdp }) => {
      try {
        console.log(`[Audio] Received WebRTC offer from ${from}`)
        
        // Check if connection already exists
        let pc = peers[from]
        if (!pc) {
          console.log(`[Audio] Creating new peer connection for ${from}`)
          pc = createPeerConnection(from, socket)
        } else {
          console.log(`[Audio] Using existing peer connection for ${from}`)
        }
        
        // Add local stream tracks if we're a speaker
        // This allows speakers to send audio to each other (bidirectional)
        const currentStream = localStreamRef.current || localStream
        if (currentStream && userRole === 'speaker') {
          console.log(`[Audio] Adding ${currentStream.getTracks().length} tracks to peer ${from}`)
          currentStream.getTracks().forEach(track => {
            pc.addTrack(track, currentStream)
          })
        } else {
          console.log(`[Audio] Not adding tracks - Role: ${userRole}, Stream: ${!!currentStream}`)
        }
        
        await pc.setRemoteDescription({ type: 'offer', sdp })
        
        // Create answer with audio-only constraints
        const answerOptions = {
          offerToReceiveAudio: true,
          offerToReceiveVideo: false,
          voiceActivityDetection: true
        }
        
        const answer = await pc.createAnswer(answerOptions)
        await pc.setLocalDescription(answer)
        
        console.log(`[Audio] Sending WebRTC answer to ${from}`)
        socket.emit('webrtc-answer', { to: from, sdp: answer.sdp })
      } catch (err) {
        console.error('[Audio] Error handling webrtc-offer:', err)
      }
    }
    
    const handleAnswer = async ({ from, sdp }) => {
      try {
        const pc = peers[from]
        if (!pc) return
        await pc.setRemoteDescription({ type: 'answer', sdp })
      } catch (err) {
        console.error('[Audio] Error handling webrtc-answer:', err)
      }
    }
    
    const handleIceCandidate = async ({ from, candidate }) => {
      try {
        const pc = peers[from]
        if (!pc || !candidate) return
        await pc.addIceCandidate(candidate)
      } catch (err) {
        console.error('[Audio] Error adding remote ICE candidate:', err)
      }
    }
    
    const handleParticipantsUpdate = (updatedParticipants) => {
      try {
        console.log(`[Audio] Participants update received. Total: ${updatedParticipants.length}, My role: ${userRole}, Local stream: ${!!localStreamRef.current}`)
        // Only emit 'ready-for-webrtc' after both localStream and participants-update are ready, and only once
        if (localStreamRef.current && !webrtcReadySignaled) {
          setWebrtcReadySignaled(true)
          console.log('[Audio] Emitting ready-for-webrtc after both localStream and participants-update')
          socket.emit('ready-for-webrtc')
        }
        
        const otherPeers = updatedParticipants.filter(p => p.socketId && p.socketId !== socket.id)
        console.log(`[Audio] Other peers: ${otherPeers.length}`)
        
        // Only speakers initiate connections (send offers)
        // Listeners wait to receive offers from speakers
        const currentStream = localStreamRef.current
        if (userRole === 'speaker' && currentStream) {
          console.log(`[Audio] I am a speaker, initiating connections to all peers`)
          otherPeers.forEach(p => {
            console.log(`[Audio] Processing peer ${p.socketId}, role: ${p.role || 'unknown'}`)
            
            // Check if connection already exists
            if (!peers[p.socketId]) {
              console.log(`[Audio] Creating new connection to ${p.socketId}`)
              const pc = createPeerConnection(p.socketId, socket)
              
              // Add our audio tracks to the connection
              console.log(`[Audio] Adding ${currentStream.getTracks().length} tracks to peer ${p.socketId}`)
              currentStream.getTracks().forEach(track => {
                pc.addTrack(track, currentStream)
              })
              
              // Create and send offer with audio-only constraints
              const offerOptions = {
                offerToReceiveAudio: true,
                offerToReceiveVideo: false,
                voiceActivityDetection: true
              }
              
              pc.createOffer(offerOptions)
                .then(offer => {
                  return pc.setLocalDescription(offer)
                })
                .then(() => {
                  console.log(`[Audio] Sending WebRTC offer to ${p.socketId}`)
                  socket.emit('webrtc-offer', { to: p.socketId, sdp: pc.localDescription.sdp })
                })
                .catch(err => console.error(`[Audio] Error creating/sending offer to ${p.socketId}:`, err))
            } else {
              console.log(`[Audio] Connection to ${p.socketId} already exists`)
            }
          })
        } else {
          console.log(`[Audio] I am a listener, waiting for offers from speakers`)
        }
      } catch (err) {
        console.error('[Audio] Error during participants-update handling for WebRTC:', err)
      }
    }
    
    const handleRoleChanged = ({ userId, newRole, participants }) => {
      try {
        // If this is our role change, update our audio capabilities
        if (socket.id && participants) {
          const ourParticipant = participants.find(p => p.socketId === socket.id)
          if (ourParticipant && ourParticipant.role !== userRole) {
            console.log(`[Audio] Role changed to ${ourParticipant.role}`)
            updateUserRole(ourParticipant.role)
          }
        }
      } catch (err) {
        console.error('[Audio] Error handling role change:', err)
      }
    }
    
    const handleRoleChangeSuccess = ({ newRole }) => {
      console.log(`[Audio] Role change confirmed: ${newRole}`)
      updateUserRole(newRole)
    }
    
    const handleRoleChangeError = ({ message }) => {
      console.error(`[Audio] Role change failed: ${message}`)
    }
    
    // Register handlers
    socket.on('webrtc-offer', handleOffer)
    socket.on('webrtc-answer', handleAnswer)
    socket.on('webrtc-ice-candidate', handleIceCandidate)
    socket.on('participants-update', handleParticipantsUpdate)
    socket.on('role-changed', handleRoleChanged)
    socket.on('role-change-success', handleRoleChangeSuccess)
    socket.on('role-change-error', handleRoleChangeError)
    
    // Cleanup function to remove handlers
    return () => {
      console.log('[Audio] Cleaning up peer signaling handlers')
      socket.off('webrtc-offer', handleOffer)
      socket.off('webrtc-answer', handleAnswer)
      socket.off('webrtc-ice-candidate', handleIceCandidate)
      socket.off('participants-update', handleParticipantsUpdate)
      socket.off('role-changed', handleRoleChanged)
      socket.off('role-change-success', handleRoleChangeSuccess)
      socket.off('role-change-error', handleRoleChangeError)
    }
  }, [socket, connected, userRole, localStream, peers, webrtcReadySignaled])

  // Check for browser support
  const isWebRTCSupported = () => {
    return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia)
  }

  // Enable audio playback for all remote streams (call this on user interaction)
  const enableAudioPlayback = () => {
    const audioElements = document.querySelectorAll('audio[data-peer]')
    audioElements.forEach(audioEl => {
      audioEl.play().catch(console.error)
    })
  }

  const value = {
    audioEnabled,
    micPermission,
    localStream,
    isMuted,
    audioLevel,
    userRole,
    remoteStreams,
    isWebRTCSupported: isWebRTCSupported(),
    requestMicrophoneAccess,
    updateUserRole,
    toggleMute,
    stopAudio,
    enableSpeaking,
    disableSpeaking,
    enableAudioPlayback
  }

  return (
    <AudioContext.Provider value={value}>
      {children}
    </AudioContext.Provider>
  )
}

/**
 * Custom hook to use audio context
 * @returns {Object} Audio context value
 */
export function useAudio() {
  const context = useContext(AudioContext)
  if (!context) {
    // Return default values instead of throwing error to prevent crashes
    console.warn('useAudio called outside AudioProvider, returning defaults')
    return {
      audioEnabled: false,
      micPermission: null,
      localStream: null,
      isMuted: true,
      audioLevel: 0,
      userRole: 'listener',
      isWebRTCSupported: false,
      requestMicrophoneAccess: () => Promise.resolve(null),
      updateUserRole: () => {},
      toggleMute: () => {},
      stopAudio: () => {},
      enableSpeaking: () => {},
      disableSpeaking: () => {},
      enableAudioPlayback: () => {}
    }
  }
  return context
}
