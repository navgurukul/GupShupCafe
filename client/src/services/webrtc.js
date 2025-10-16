/**
 * WebRTC Service
 * Handles WebRTC peer connection logic and configuration
 */

// STUN server configuration for NAT traversal
const STUN_SERVERS = {
  iceServers: [
    { urls: 'stun:stun.l.google.com:19302' },
    { urls: 'stun:stun1.l.google.com:19302' },
    { urls: 'stun:stun2.l.google.com:19302' }
  ]
}

// Codec preferences for audio-only communication
const CODEC_PREFERENCES = {
  preferOpus: true,
  opusStereo: false,
  opusDtx: true, // Discontinuous Transmission
  opusFec: true, // Forward Error Correction
  opusMaxAverageBitrate: 510000
}

/**
 * Create a new RTCPeerConnection with optimal audio settings
 * @param {MediaStream} localStream - Local audio stream
 * @returns {RTCPeerConnection} Configured peer connection
 */
export function createPeerConnection(localStream = null) {
  try {
    const peerConnection = new RTCPeerConnection(STUN_SERVERS)

    // Add local stream tracks if provided
    if (localStream) {
      localStream.getTracks().forEach(track => {
        peerConnection.addTrack(track, localStream)
        console.log('[WebRTC] Added local track to peer connection:', track.kind)
      })
    }

    // Set codec preferences for audio optimization
    const transceivers = peerConnection.getTransceivers()
    transceivers.forEach(transceiver => {
      if (transceiver.sender.track?.kind === 'audio') {
        const capabilities = RTCRtpSender.getCapabilities('audio')
        if (capabilities && capabilities.codecs) {
          // Prioritize Opus codec
          const preferredCodecs = capabilities.codecs.filter(codec => 
            codec.mimeType.includes('opus')
          )
          const otherCodecs = capabilities.codecs.filter(codec => 
            !codec.mimeType.includes('opus')
          )
          transceiver.setCodecPreferences([...preferredCodecs, ...otherCodecs])
          console.log('[WebRTC] Codec preferences set, Opus prioritized')
        }
      }
    })

    console.log('[WebRTC] Peer connection created successfully')
    return peerConnection
  } catch (error) {
    console.error('[WebRTC] Error creating peer connection:', error)
    throw error
  }
}

/**
 * Create an offer for initiating WebRTC connection
 * @param {RTCPeerConnection} peerConnection - Peer connection instance
 * @returns {Promise<RTCSessionDescription>} SDP offer
 */
export async function createOffer(peerConnection) {
  try {
    const offer = await peerConnection.createOffer({
      offerToReceiveAudio: true,
      offerToReceiveVideo: false
    })
    
    await peerConnection.setLocalDescription(offer)
    console.log('[WebRTC] Offer created and set as local description')
    
    return offer
  } catch (error) {
    console.error('[WebRTC] Error creating offer:', error)
    throw error
  }
}

/**
 * Handle incoming offer and create answer
 * @param {RTCPeerConnection} peerConnection - Peer connection instance
 * @param {RTCSessionDescription} offer - Incoming SDP offer
 * @returns {Promise<RTCSessionDescription>} SDP answer
 */
export async function handleOffer(peerConnection, offer) {
  try {
    await peerConnection.setRemoteDescription(new RTCSessionDescription(offer))
    console.log('[WebRTC] Remote description set from offer')
    
    const answer = await peerConnection.createAnswer()
    await peerConnection.setLocalDescription(answer)
    console.log('[WebRTC] Answer created and set as local description')
    
    return answer
  } catch (error) {
    console.error('[WebRTC] Error handling offer:', error)
    throw error
  }
}

/**
 * Handle incoming answer
 * @param {RTCPeerConnection} peerConnection - Peer connection instance
 * @param {RTCSessionDescription} answer - Incoming SDP answer
 */
export async function handleAnswer(peerConnection, answer) {
  try {
    await peerConnection.setRemoteDescription(new RTCSessionDescription(answer))
    console.log('[WebRTC] Remote description set from answer')
  } catch (error) {
    console.error('[WebRTC] Error handling answer:', error)
    throw error
  }
}

/**
 * Handle incoming ICE candidate
 * @param {RTCPeerConnection} peerConnection - Peer connection instance
 * @param {RTCIceCandidate} candidate - ICE candidate
 */
export async function handleICECandidate(peerConnection, candidate) {
  try {
    if (candidate) {
      await peerConnection.addIceCandidate(new RTCIceCandidate(candidate))
      console.log('[WebRTC] ICE candidate added successfully')
    }
  } catch (error) {
    console.error('[WebRTC] Error handling ICE candidate:', error)
    throw error
  }
}

/**
 * Close peer connection and cleanup
 * @param {RTCPeerConnection} peerConnection - Peer connection to close
 */
export function closePeerConnection(peerConnection) {
  try {
    if (peerConnection) {
      peerConnection.close()
      console.log('[WebRTC] Peer connection closed')
    }
  } catch (error) {
    console.error('[WebRTC] Error closing peer connection:', error)
  }
}

export default {
  createPeerConnection,
  createOffer,
  handleOffer,
  handleAnswer,
  handleICECandidate,
  closePeerConnection,
  STUN_SERVERS,
  CODEC_PREFERENCES
}
