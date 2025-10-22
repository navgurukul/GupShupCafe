import React, { useContext } from 'react'
import ParticipantCard from './ParticipantCard'
import { useAudio } from '../../contexts/AudioContext'
import { Brain, Bot } from 'lucide-react'

/**
 * RoundtableView Component
 * Visual representation of the roundtable with participants arranged in a circle
 */
function RoundtableView({ 
  participants, 
  currentSpeaker, 
  currentTopic, 
  discussionStarted, 
  facilitatorResponse, 
  facilitatorTurnActive 
}) {
  // Get audio context using custom hook
  const audioCtx = useAudio()
  // You may need to adjust this depending on how remote streams are tracked in AudioContext
  const remoteStreams = audioCtx?.remoteStreams || {}
  /**
   * Calculate position for each chair around the circle
   * @param {number} index - Participant index
   * @param {number} total - Total number of participants
   */
  const getChairPosition = (index, total) => {
    // Distribute chairs evenly around the circle
    const angle = (index * 360) / total
    const radius = 140 // Distance from center
    
    // Convert angle to radians and calculate x, y coordinates
    const radians = (angle - 90) * (Math.PI / 180) // -90 to start from top
    const x = radius * Math.cos(radians)
    const y = radius * Math.sin(radians)
    
    return {
      left: `calc(50% + ${x}px)`,
      top: `calc(50% + ${y}px)`,
      transform: 'translate(-50%, -50%)'
    }
  }

  /**
   * Render participant chair using ParticipantCard component
   */
  const renderChair = (participant, index) => {
    const position = getChairPosition(index, participants.length)
    const isCurrentSpeaker = currentSpeaker && currentSpeaker.id === participant.id
    const remoteStream = remoteStreams[participant.socketId] || null
    
    return (
      <ParticipantCard
        key={participant.id}
        participant={participant}
        isCurrentSpeaker={isCurrentSpeaker}
        position={position}
        remoteStream={remoteStream}
      />
    )
  }

  return (
    <div className="relative flex items-center justify-center min-h-[500px]">
      {/* Roundtable Surface */}
      <div className="relative w-96 h-96 bg-gradient-to-br from-amber-800 to-amber-900 
                      rounded-full shadow-2xl border-8 border-amber-700">
        
        {/* Wood grain effect */}
        <div className="absolute inset-2 bg-gradient-to-br from-amber-700 to-amber-800 
                        rounded-full opacity-60"></div>
        <div className="absolute inset-4 bg-gradient-to-br from-amber-600 to-amber-700 
                        rounded-full opacity-40"></div>
        
        {/* Center Topic Area */}
        <div className="absolute inset-8 bg-white rounded-full shadow-inner border-4 
                        border-gray-200 flex items-center justify-center p-4">
          {discussionStarted && currentTopic ? (
            <div className="text-center">
              <Brain className="w-8 h-8 text-primary-600 mx-auto mb-2" />
              <h3 className="text-lg font-bold text-gray-900 leading-tight">
                {currentTopic.title}
              </h3>
              {currentTopic.category && (
                <span className="inline-block mt-2 px-2 py-1 bg-primary-100 text-primary-800 
                               text-xs font-medium rounded-full">
                  {currentTopic.category}
                </span>
              )}
            </div>
          ) : (
            <div className="text-center">
              <Brain className="w-12 h-12 text-gray-400 mx-auto mb-2" />
              <p className="text-gray-500 text-sm">
                {participants.length < 1 
                  ? 'Waiting for participants...' 
                  : 'Preparing discussion...'}
              </p>
            </div>
          )}
        </div>

        {/* Participants as chairs around the table */}
        {participants.map((participant, index) => renderChair(participant, index))}
        
        {/* Empty chair indicators for visual balance */}
        {participants.length > 0 && participants.length < 8 && (
          <>
            {Array.from({ length: Math.max(0, 4 - participants.length) }, (_, index) => {
              const totalSlots = Math.max(4, participants.length + 1)
              const emptyIndex = participants.length + index
              const position = getChairPosition(emptyIndex, totalSlots)
              
              return (
                <div
                  key={`empty-${index}`}
                  className="absolute w-12 h-12 rounded-full border-4 border-dashed 
                           border-gray-300 bg-gray-100 opacity-50 transition-all duration-300"
                  style={position}
                  title="Waiting for participant"
                >
                  <div className="w-full h-full flex items-center justify-center text-gray-400 text-xs">
                    +
                  </div>
                </div>
              )
            })}
          </>
        )}
      </div>

      {/* Discussion Status */}
      <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 
                      bg-white px-4 py-2 rounded-full shadow-lg border">
        <div className="flex items-center space-x-2 text-sm">
          <div className={`w-2 h-2 rounded-full ${
            discussionStarted ? 'bg-green-500 animate-pulse' : 'bg-gray-400'
          }`}></div>
          <span className={discussionStarted ? 'text-green-700' : 'text-gray-600'}>
            {discussionStarted 
              ? `Discussion Active • ${participants.length} participants`
              : `Preparing • ${participants.length} joined`}
          </span>
        </div>
      </div>

      {/* Current Speaker Highlight */}
      {discussionStarted && currentSpeaker && (
        <div className={`absolute top-4 left-1/2 transform -translate-x-1/2 px-4 py-2 rounded-full ${
          currentSpeaker.isAgent 
            ? 'bg-blue-100 border border-blue-200' 
            : 'bg-green-100 border border-green-200'
        }`}>
          <div className="flex items-center space-x-2 text-sm">
            <div className={`w-2 h-2 rounded-full animate-pulse ${
              currentSpeaker.isAgent ? 'bg-blue-500' : 'bg-green-500'
            }`}></div>
            {currentSpeaker.isAgent && <Bot className="w-4 h-4 text-blue-600" />}
            <span className={`font-medium ${
              currentSpeaker.isAgent ? 'text-blue-800' : 'text-green-800'
            }`}>
              {currentSpeaker.anonymousName} is {currentSpeaker.isAgent ? 'facilitating' : 'speaking'}
            </span>
          </div>
        </div>
      )}

      {/* Facilitator Response Bubble */}
      {facilitatorTurnActive && facilitatorResponse && (
        <div className="absolute top-16 left-1/2 transform -translate-x-1/2 max-w-md">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 shadow-lg">
            <div className="flex items-start space-x-2">
              <Bot className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-sm text-blue-900 font-medium mb-1">AI Facilitator</p>
                <p className="text-sm text-gray-800 leading-relaxed">
                  {facilitatorResponse}
                </p>
              </div>
            </div>
            {/* Speech bubble pointer */}
            <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-full">
              <div className="w-0 h-0 border-l-8 border-r-8 border-t-8 border-transparent border-t-blue-200"></div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default RoundtableView
