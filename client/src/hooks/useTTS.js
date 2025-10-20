import { useContext } from 'react';
import { TTSContext } from '../contexts/TTSContext';

/**
 * Custom hook to use TTS functionality
 * Re-exports the TTS context for easier importing
 */
export function useTTS() {
  const context = useContext(TTSContext);
  if (!context) {
    throw new Error('useTTS must be used within a TTSProvider');
  }
  return context;
}

export default useTTS;