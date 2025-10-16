import React, { useState, useEffect, useRef } from 'react'
import { Mic } from 'lucide-react'

/**
 * SpeechToText Component
 * Displays live transcription using Web Speech API when user is speaking
 */
function SpeechToText({ isActive, speakerName }) {
  const [transcript, setTranscript] = useState('')
  const [interimTranscript, setInterimTranscript] = useState('')
  const [isListening, setIsListening] = useState(false)
  const [isSupported, setIsSupported] = useState(true)
  const recognitionRef = useRef(null)

  useEffect(() => {
    // Check if browser supports Web Speech API
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SpeechRecognition) {
      console.warn('[SpeechToText] Web Speech API not supported')
      setIsSupported(false)
      return
    }

    // Initialize speech recognition
    const recognition = new SpeechRecognition()
    recognition.continuous = true
    recognition.interimResults = true
    recognition.lang = 'en-US'

    recognition.onstart = () => {
      console.log('[SpeechToText] Speech recognition started')
      setIsListening(true)
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
        setTranscript(prev => prev + final)
      }
      setInterimTranscript(interim)
    }

    recognition.onerror = (event) => {
      console.error('[SpeechToText] Speech recognition error:', event.error)
      if (event.error === 'no-speech') {
        // This is normal, just continue
        return
      }
      setIsListening(false)
    }

    recognition.onend = () => {
      console.log('[SpeechToText] Speech recognition ended')
      setIsListening(false)
      
      // Restart if still active
      if (isActive && recognitionRef.current) {
        try {
          recognition.start()
        } catch (error) {
          console.error('[SpeechToText] Error restarting recognition:', error)
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
  }, [])

  // Start/stop recognition based on isActive prop
  useEffect(() => {
    if (!isSupported || !recognitionRef.current) return

    if (isActive && !isListening) {
      // Clear previous transcript when starting new session
      setTranscript('')
      setInterimTranscript('')
      
      try {
        recognitionRef.current.start()
      } catch (error) {
        if (error.message.includes('already started')) {
          console.log('[SpeechToText] Recognition already running')
        } else {
          console.error('[SpeechToText] Error starting recognition:', error)
        }
      }
    } else if (!isActive && isListening) {
      try {
        recognitionRef.current.stop()
      } catch (error) {
        console.error('[SpeechToText] Error stopping recognition:', error)
      }
    }
  }, [isActive, isListening, isSupported])

  if (!isSupported) {
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

  const displayText = transcript + interimTranscript

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
