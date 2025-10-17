/**
 * Speech Service
 * Wrapper for Web Speech API for speech recognition
 */

/**
 * Check if Web Speech API is supported
 * @returns {boolean} True if supported
 */
export function isSupported() {
  return !!(window.SpeechRecognition || window.webkitSpeechRecognition)
}

/**
 * Create a new speech recognition instance
 * @param {Object} options - Configuration options
 * @returns {SpeechRecognition} Speech recognition instance
 */
export function createRecognition(options = {}) {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
  
  if (!SpeechRecognition) {
    throw new Error('Web Speech API not supported in this browser')
  }

  const recognition = new SpeechRecognition()
  
  // Default configuration
  recognition.continuous = options.continuous ?? true
  recognition.interimResults = options.interimResults ?? true
  recognition.lang = options.lang || detectLanguage()
  recognition.maxAlternatives = options.maxAlternatives || 1

  console.log('[Speech] Recognition instance created with language:', recognition.lang)
  
  return recognition
}

/**
 * Start speech recognition
 * @param {SpeechRecognition} recognition - Speech recognition instance
 * @param {Function} onResult - Callback for results
 * @param {Function} onError - Callback for errors
 * @param {Function} onEnd - Callback when recognition ends
 */
export function startRecognition(recognition, { onResult, onError, onEnd } = {}) {
  if (!recognition) {
    console.error('[Speech] No recognition instance provided')
    return
  }

  try {
    // Set up event handlers
    if (onResult) {
      recognition.onresult = (event) => {
        let interim = ''
        let final = ''

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript
          if (event.results[i].isFinal) {
            final += transcript + ' '
          } else {
            interim += transcript
          }
        }

        onResult({ final, interim })
      }
    }

    if (onError) {
      recognition.onerror = (event) => {
        console.error('[Speech] Recognition error:', event.error)
        onError(event.error)
      }
    }

    if (onEnd) {
      recognition.onend = () => {
        console.log('[Speech] Recognition ended')
        onEnd()
      }
    }

    recognition.start()
    console.log('[Speech] Recognition started')
  } catch (error) {
    console.error('[Speech] Error starting recognition:', error)
    if (onError) onError(error)
  }
}

/**
 * Stop speech recognition
 * @param {SpeechRecognition} recognition - Speech recognition instance
 */
export function stopRecognition(recognition) {
  if (!recognition) {
    console.error('[Speech] No recognition instance provided')
    return
  }

  try {
    recognition.stop()
    console.log('[Speech] Recognition stopped')
  } catch (error) {
    console.error('[Speech] Error stopping recognition:', error)
  }
}

/**
 * Detect browser language for speech recognition
 * @returns {string} Language code (e.g., 'en-US')
 */
export function detectLanguage() {
  // Try to get language from various sources
  const browserLang = navigator.language || navigator.userLanguage
  
  // Default to English if language detection fails
  if (!browserLang) {
    return 'en-US'
  }

  // Map common language codes to supported speech recognition codes
  const langMap = {
    'en': 'en-US',
    'es': 'es-ES',
    'fr': 'fr-FR',
    'de': 'de-DE',
    'it': 'it-IT',
    'pt': 'pt-PT',
    'ru': 'ru-RU',
    'ja': 'ja-JP',
    'ko': 'ko-KR',
    'zh': 'zh-CN',
    'hi': 'hi-IN'
  }

  // Extract base language code (e.g., 'en' from 'en-US')
  const baseLang = browserLang.split('-')[0].toLowerCase()
  
  // Return mapped language or use browser language as-is
  return langMap[baseLang] || browserLang
}

/**
 * Get supported languages for speech recognition
 * Note: This is a subset of commonly supported languages
 * @returns {Array} List of supported language codes
 */
export function getSupportedLanguages() {
  return [
    { code: 'en-US', name: 'English (US)' },
    { code: 'en-GB', name: 'English (UK)' },
    { code: 'es-ES', name: 'Spanish' },
    { code: 'fr-FR', name: 'French' },
    { code: 'de-DE', name: 'German' },
    { code: 'it-IT', name: 'Italian' },
    { code: 'pt-PT', name: 'Portuguese' },
    { code: 'ru-RU', name: 'Russian' },
    { code: 'ja-JP', name: 'Japanese' },
    { code: 'ko-KR', name: 'Korean' },
    { code: 'zh-CN', name: 'Chinese (Simplified)' },
    { code: 'hi-IN', name: 'Hindi' }
  ]
}

export default {
  isSupported,
  createRecognition,
  startRecognition,
  stopRecognition,
  detectLanguage,
  getSupportedLanguages
}
