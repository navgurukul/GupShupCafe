import React from 'react'
import { useSocket } from '../../contexts/SocketContext'

/**
 * ConnectionStatus Component
 * Shows the current socket connection status with visual indicator
 */
export function ConnectionStatus() {
  const { connected } = useSocket()

  return (
    <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm ${
      connected 
        ? 'bg-green-100 text-green-800 border border-green-200' 
        : 'bg-red-100 text-red-800 border border-red-200'
    }`}>
      <div className={`w-2 h-2 rounded-full ${
        connected ? 'bg-green-500' : 'bg-red-500'
      } ${connected ? 'animate-pulse' : ''}`} />
      <span className="font-medium">
        {connected ? 'Connected' : 'Disconnected'}
      </span>
    </div>
  )
}

export default ConnectionStatus