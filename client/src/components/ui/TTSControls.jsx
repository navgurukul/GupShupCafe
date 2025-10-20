import React from 'react';
import { Volume2, VolumeX, MessageSquare, Square } from 'lucide-react';
import { useTTS } from '../../hooks/useTTS';

/**
 * TTS Controls Component
 * Provides UI controls for text-to-speech functionality
 */
function TTSControls({ className = "" }) {
  const {
    isSpeaking,
    currentText,
    isEnabled,
    volume,
    stopSpeaking,
    toggleEnabled,
    setTTSVolume,
    requestFacilitatorResponse,
    isAvailable,
  } = useTTS();

  if (!isAvailable()) {
    return null;
  }

  return (
    <div className={`bg-white rounded-lg shadow-md p-4 ${className}`}>
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-medium text-gray-700 flex items-center">
          <MessageSquare className="w-4 h-4 mr-2" />
          Facilitator Voice
        </h3>
        
        {/* TTS Status Indicator */}
        <div className="flex items-center space-x-2">
          {isSpeaking && (
            <div className="flex items-center text-green-600 text-xs">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse mr-1"></div>
              Speaking
            </div>
          )}
          
          {/* Enable/Disable Toggle */}
          <button
            onClick={toggleEnabled}
            className={`p-1 rounded transition-colors ${
              isEnabled 
                ? 'text-blue-600 hover:bg-blue-50' 
                : 'text-gray-400 hover:bg-gray-50'
            }`}
            title={isEnabled ? 'Disable TTS' : 'Enable TTS'}
          >
            {isEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Current Speech Display */}
      {isSpeaking && currentText && (
        <div className="mb-3 p-2 bg-blue-50 rounded text-xs text-blue-800 border-l-2 border-blue-200">
          <div className="font-medium mb-1">Currently speaking:</div>
          <div className="line-clamp-2">{currentText}</div>
        </div>
      )}

      {/* Controls */}
      <div className="flex items-center justify-between">
        {/* Request Facilitator Response */}
        <button
          onClick={requestFacilitatorResponse}
          disabled={isSpeaking || !isEnabled}
          className={`px-3 py-1 text-xs font-medium rounded transition-colors ${
            isSpeaking || !isEnabled
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
              : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
          }`}
          title="Request facilitator to provide guidance"
        >
          Ask Facilitator
        </button>

        {/* Stop Speaking Button */}
        {isSpeaking && (
          <button
            onClick={stopSpeaking}
            className="p-1 text-red-600 hover:bg-red-50 rounded transition-colors"
            title="Stop speaking"
          >
            <Square className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Volume Control (if supported) */}
      {isEnabled && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          <div className="flex items-center space-x-2">
            <VolumeX className="w-3 h-3 text-gray-400" />
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={volume}
              onChange={(e) => setTTSVolume(parseFloat(e.target.value))}
              className="flex-1 h-1 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              title="Adjust TTS volume"
            />
            <Volume2 className="w-3 h-3 text-gray-400" />
          </div>
        </div>
      )}
    </div>
  );
}

export default TTSControls;