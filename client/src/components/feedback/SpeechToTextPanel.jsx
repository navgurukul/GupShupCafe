import React, { useState, useEffect, useRef } from 'react'
import { Mic, MicOff } from 'lucide-react'
import { useSocket } from '../../contexts/SocketContext'

/**
 * SpeechToText Component
 * Displays live transcription using Web Speech API when user is speaking
 */
function SpeechToText({ isActive, speakerName, participantId, roomId, compact = false }) {
  const [transcript, setTranscript] = useState('')
  const [interimTranscript, setInterimTranscript] = useState('')
  const [isListening, setIsListening] = useState(false)
  const [isSupported, setIsSupported] = useState(true)
  const [error, setError] = useState(null)
  const recognitionRef = useRef(null)
  const { socket } = useSocket()

  useEffect(() => {
    // Check if browser supports Web Speech API
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SpeechRecognition) {
      console.warn('[SpeechToText] Web Speech API not supported')
      setIsSupported(false)
      setError('Speech recognition not supported in this browser')
      return
    }

    // Initialize speech recognition
    const recognition = new SpeechRecognition()
    recognition.continuous = true
    recognition.interimResults = true
    recognition.lang = 'en-US'

    recognition.onstart = () => {
      console.log(`[SpeechToText] Speech recognition started for ${speakerName}`)
      setIsListening(true)
      setError(null)
    }

    recognition.onresult = (event) => {
      let interim = ''
      let final = ''

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcriptPart = event.results[i][0].transcript
        if (event.results[i].isFinal) {
          final += transcriptPart + ' '
        } else {
          interim += transcriptPart
        }
      }

      if (final) {
        const newTranscript = final.trim()
        setTranscript(prev => prev + (prev ? ' ' : '') + newTranscript)
        
        // Send transcript to server if we have socket connection
        if (socket && participantId && roomId && newTranscript) {
          socket.emit('transcript-received', {
            text: newTranscript,
            participantId: participantId,
            roomId: roomId,
            timestamp: new Date().toISOString(),
            confidence: event.results[event.resultIndex][0].confidence || 0.9
          })
          console.log(`[SpeechToText] Sent transcript to server: ${newTranscript.substring(0, 50)}...`)
        }
      }
      setInterimTranscript(interim)
    }

    recognition.onerror = (event) => {
      console.error(`[SpeechToText] Speech recognition error for ${speakerName}:`, event.error)
      
      if (event.error === 'no-speech') {
        // This is normal, just continue
        return
      }
      
      if (event.error === 'not-allowed') {
        setError('Microphone access denied')
      } else if (event.error === 'network') {
        setError('Network error occurred')
      } else {
        setError(`Recognition error: ${event.error}`)
      }
      
      setIsListening(false)
    }

    recognition.onend = () => {
      console.log(`[SpeechToText] Speech recognition ended for ${speakerName}`)
      setIsListening(false)
      
      // Restart if still active and no error
      if (isActive && recognitionRef.current && !error) {
        try {
          setTimeout(() => {
            if (recognitionRef.current && isActive) {
              recognition.start()
            }
          }, 100) // Small delay to prevent rapid restart issues
        } catch (error) {
          console.error('[SpeechToText] Error restarting recognition:', error)
          setError('Failed to restart recognition')
        }
      }
    }

    recognitionRef.current = recognition

    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop()
        } catch (error) {
          console.error('[SpeechToText] Error stopping recognition:', error)
        }
        recognitionRef.current = null
      }
    }
  }, [speakerName, socket, participantId, roomId, error])

  // Start/stop recognition based on isActive prop
  useEffect(() => {
    if (!isSupported || !recognitionRef.current) return

    if (isActive && !isListening && !error) {
      // Clear previous transcript when starting new session
      setTranscript('')
      setInterimTranscript('')
      setError(null)
      
      try {
        recognitionRef.current.start()
      } catch (error) {
        if (error.message.includes('already started')) {
          console.log(`[SpeechToText] Recognition already running for ${speakerName}`)
        } else {
          console.error(`[SpeechToText] Error starting recognition for ${speakerName}:`, error)
          setError('Failed to start recognition')
        }
      }
    } else if (!isActive && isListening) {
      try {
        recognitionRef.current.stop()
      } catch (error) {
        console.error(`[SpeechToText] Error stopping recognition for ${speakerName}:`, error)
      }
    }
  }, [isActive, isListening, isSupported, error, speakerName])

  if (!isSupported) {
    if (compact) {
      return (
        <div className="bg-yellow-50 border border-yellow-200 rounded p-2">
          <div className="flex items-center space-x-1">
            <MicOff className="w-3 h-3 text-yellow-600" />
            <span className="text-xs text-yellow-800">Speech recognition not supported</span>
          </div>
        </div>
      )
    }
    
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div className="flex items-start space-x-2">
          <div className="text-yellow-600">⚠️</div>
          <div>
            <p className="text-sm font-medium text-yellow-800">Speech recognition not supported</p>
            <p className="text-xs text-yellow-700 mt-1">
              Your browser doesn't support the Web Speech API. Try using Chrome or Edge.
            </p>
          </div>
        </div>
      </div>
    )
  }

  if (!isActive) {
    return null
  }

  if (error) {
    if (compact) {
      return (
        <div className="bg-red-50 border border-red-200 rounded p-2">
          <div className="flex items-center space-x-1">
            <MicOff className="w-3 h-3 text-red-600" />
            <span className="text-xs text-red-800">{error}</span>
          </div>
        </div>
      )
    }
    
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-start space-x-2">
          <MicOff className="w-4 h-4 text-red-600 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-red-800">Transcription Error</p>
            <p className="text-xs text-red-700 mt-1">{error}</p>
          </div>
        </div>
      </div>
    )
  }

  const displayText = transcript + interimTranscript

  if (compact) {
    return (
      <div className="bg-white border border-blue-200 rounded p-2">
        <div className="flex items-center justify-between mb-1">
          <div className="flex items-center space-x-1">
            <Mic className={`w-3 h-3 ${isListening ? 'text-green-600 animate-pulse' : 'text-gray-400'}`} />
            <span className="text-xs font-medium text-gray-700">
              {speakerName ? `${speakerName}` : 'Live Transcription'}
            </span>
          </div>
          <div className={`px-1 py-0.5 text-xs rounded ${
            isListening ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
          }`}>
            {isListening ? '🎤' : '⏸️'}
          </div>
        </div>
        
        <div className="min-h-[40px] max-h-[80px] overflow-y-auto bg-gray-50 rounded p-2">
          {displayText ? (
            <p className="text-xs text-gray-800 leading-relaxed">
              {transcript}
              {interimTranscript && (
                <span className="text-gray-500 italic">{interimTranscript}</span>
              )}
            </p>
          ) : (
            <p className="text-xs text-gray-400 italic">
              {isListening ? 'Listening...' : 'Waiting...'}
            </p>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white border-2 border-blue-200 rounded-lg shadow-sm p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <Mic className={`w-5 h-5 ${isListening ? 'text-green-600 animate-pulse' : 'text-gray-400'}`} />
          <h3 className="text-sm font-semibold text-gray-900">
            Live Transcription
            {speakerName && ` - ${speakerName}`}
          </h3>
        </div>
        <div className={`px-2 py-1 text-xs rounded-full ${
          isListening ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
        }`}>
          {isListening ? '🎤 Listening' : '⏸️ Paused'}
        </div>
      </div>
      
      <div className="min-h-[100px] max-h-[200px] overflow-y-auto bg-gray-50 rounded-md p-3">
        {displayText ? (
          <p className="text-sm text-gray-800 leading-relaxed">
            {transcript}
            {interimTranscript && (
              <span className="text-gray-500 italic">{interimTranscript}</span>
            )}
          </p>
        ) : (
          <p className="text-sm text-gray-400 italic">
            {isListening ? 'Waiting for speech...' : 'Start speaking to see transcription'}
          </p>
        )}
      </div>
      
      <div className="mt-2 text-xs text-gray-500">
        💡 Tip: Speak clearly for better transcription accuracy
      </div>
    </div>
  )
}

export default SpeechToText
