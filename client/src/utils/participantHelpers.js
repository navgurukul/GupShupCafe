/**
 * Participant Helper Functions
 * Common functions for managing participant data across pages
 */

import { generateAvatarColor } from './helpers'

const getApiUrl = () => {
  return import.meta.env.VITE_API_URL || 'http://localhost:3003'
}

/**
 * Create a participant in the database
 * @param {Object} participantData - Participant data
 * @returns {Promise<Object>} API response
 */
export async function createParticipant(participantData) {
  const apiUrl = getApiUrl()
  
  try {
    const response = await fetch(`${apiUrl}/participants/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(participantData),
    })

    const result = await response.json()
    console.log('[ParticipantHelper] Participant created:', result)
    
    // Store participant data in localStorage
    if (result.status === 'success') {
      saveParticipantToLocalStorage({
        participantId: result.data,
        ...participantData
      })
    }
    
    return result
  } catch (error) {
    console.error('[ParticipantHelper] Error creating participant:', error)
    throw error
  }
}

/**
 * Save participant data to localStorage
 * @param {Object} participantData - Participant data to save
 */
export function saveParticipantToLocalStorage(participantData) {
  try {
    localStorage.setItem('participantData', JSON.stringify(participantData))
    console.log('[ParticipantHelper] Participant data saved to localStorage:', participantData)
  } catch (error) {
    console.error('[ParticipantHelper] Error saving to localStorage:', error)
  }
}

/**
 * Get participant data from localStorage
 * @returns {Object|null} Participant data or null
 */
export function getParticipantFromLocalStorage() {
  try {
    const data = localStorage.getItem('participantData')
    return data ? JSON.parse(data) : null
  } catch (error) {
    console.error('[ParticipantHelper] Error reading from localStorage:', error)
    return null
  }
}

/**
 * Clear participant data from localStorage
 */
export function clearParticipantFromLocalStorage() {
  try {
    localStorage.removeItem('participantData')
    console.log('[ParticipantHelper] Participant data cleared from localStorage')
  } catch (error) {
    console.error('[ParticipantHelper] Error clearing localStorage:', error)
  }
}

/**
 * Common function to create participant with user data
 * Extracts repeated logic from handleCreateRoom and handleJoinSubmit
 * @param {Object} params - Parameters for participant creation
 * @returns {Promise<Object>} Created participant result
 */
export async function createParticipantForRoom({
  userId,
  roomId,
  anonymousName,
  currentCefrLevel,
  campusOrLocation = null
}) {
  const participantPayload = {
    user_id: userId,
    room_id: roomId,
    avatar_color: generateAvatarColor(),
    anonymous_name: anonymousName,
    campusOrLocation: campusOrLocation,
    joined_at: new Date().toISOString(),
    starting_cefr_level: currentCefrLevel,
    ending_cefr_level: currentCefrLevel // Initially same as starting level
  }

  return await createParticipant(participantPayload)
}

export default {
  createParticipant,
  saveParticipantToLocalStorage,
  getParticipantFromLocalStorage,
  clearParticipantFromLocalStorage,
  createParticipantForRoom
}
