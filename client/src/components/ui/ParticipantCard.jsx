import React from 'react'
import AudioLevelBar from './AudioLevelBar'

/**
 * ParticipantCard Component
 * Displays individual participant information in the roundtable view
 */
function ParticipantCard({ 
  participant, 
  isCurrentSpeaker, 
  position,
  remoteStream 
}) {
  /**
   * Get card styling based on participant state
   */
  const getCardStyle = () => {
    const baseClasses = 'absolute w-14 h-14 rounded-full border-4 transition-all duration-300 ' +
                       'flex items-center justify-center font-semibold text-white text-sm ' +
                       'shadow-lg cursor-pointer chair-enter'
    
    if (isCurrentSpeaker) {
      return `${baseClasses} border-green-500 bg-green-500 shadow-green-300 shadow-xl scale-110 ` +
             'animate-pulse-active ring-4 ring-green-200'
    }
    
    return `${baseClasses} border-primary-600 bg-primary-600 hover:scale-105`
  }

  /**
   * Display participant avatar (first letter of name)
   */
  const displayAvatar = () => {
    return participant.anonymousName.charAt(0).toUpperCase()
  }

  /**
   * Display participant name below avatar
   */
  const displayName = () => {
    return (
      <div className="absolute -bottom-12 left-1/2 transform -translate-x-1/2 
                      bg-white px-2 py-1 rounded-md shadow-sm border text-xs font-medium 
                      text-gray-700 whitespace-nowrap">
        {participant.anonymousName}
        <div className={`text-xs ${
          participant.role === 'speaker' ? 'text-blue-600' : 'text-gray-500'
        }`}>
          {participant.role === 'speaker' ? 'Speaker' : 'Listener'}
        </div>
      </div>
    )
  }

  /**
   * Display ready status indicator
   */
  const displayReadyStatus = () => {
    if (!participant.isReady) {
      return (
        <div className="absolute -top-2 -left-2 w-5 h-5 bg-yellow-400 rounded-full 
                        border-2 border-white flex items-center justify-center">
          <div className="w-2 h-2 bg-white rounded-full"></div>
        </div>
      )
    }
    return null
  }

  /**
   * Display speaking indicator when participant is currently speaking
   */
  const displaySpeakingIndicator = () => {
    if (isCurrentSpeaker) {
      return (
        <div className="absolute -top-2 -right-2 w-6 h-6 bg-green-400 rounded-full 
                        border-2 border-white flex items-center justify-center animate-bounce">
          <div className="w-2 h-2 bg-white rounded-full"></div>
        </div>
      )
    }
    return null
  }

  return (
    <div
      className={getCardStyle()}
      style={position}
      title={`${participant.anonymousName}${isCurrentSpeaker ? ' (Speaking)' : ''}`}
    >
      {/* Participant Initial */}
      {displayAvatar()}
      
      {/* Speaking Indicator */}
      {displaySpeakingIndicator()}
      
      {/* Ready Status */}
      {displayReadyStatus()}
      
      {/* Role Indicator */}
      <div className={`absolute -top-1 -left-1 w-4 h-4 rounded-full border-2 border-white text-xs flex items-center justify-center ${
        participant.role === 'speaker' 
          ? 'bg-blue-500 text-white' 
          : 'bg-gray-400 text-white'
      }`}>
        {participant.role === 'speaker' ? '🎤' : '👂'}
      </div>

      {/* Audio Level Indicator (if remote stream available) */}
      {remoteStream && (
        <div className="absolute left-1/2 -bottom-6 -translate-x-1/2 w-10">
          <AudioLevelBar stream={remoteStream} showLabel={false} />
        </div>
      )}

      {/* Name Label */}
      {displayName()}
    </div>
  )
}

export default ParticipantCard
