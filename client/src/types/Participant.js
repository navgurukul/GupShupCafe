/**
 * @typedef {Object} Participant
 * @property {string} id - Unique participant identifier
 * @property {string} socketId - Socket.io connection ID
 * @property {string} anonymousName - Anonymous display name (e.g., "Happy Tiger")
 * @property {string} avatarColor - Color for participant avatar
 * @property {string} role - Participant role ('speaker' or 'listener')
 * @property {boolean} isReady - Ready status for discussion start
 * @property {boolean} isSpeaking - Currently speaking indicator
 * @property {boolean} isMuted - Microphone muted status
 * @property {string} cefrLevel - CEFR English proficiency level
 */

/**
 * Participant type definition for roundtable discussions
 */
export const ParticipantType = {}
