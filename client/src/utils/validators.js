/**
 * Validator Utilities
 * Functions for validating user input and data
 */

/**
 * Validate email address
 * @param {string} email - Email to validate
 * @returns {boolean} True if valid email
 */
export function isValidEmail(email) {
  if (!email || typeof email !== 'string') return false
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email.trim())
}

/**
 * Validate room code format
 * @param {string} code - Room code to validate
 * @returns {boolean} True if valid code
 */
export function isValidRoomCode(code) {
  if (!code || typeof code !== 'string') return false
  
  // Room codes should be 4-8 alphanumeric characters
  const codeRegex = /^[A-Z0-9]{4,8}$/
  return codeRegex.test(code.toUpperCase())
}

/**
 * Validate username
 * @param {string} username - Username to validate
 * @returns {Object} Validation result with isValid and error message
 */
export function validateUsername(username) {
  if (!username || typeof username !== 'string') {
    return { isValid: false, error: 'Username is required' }
  }
  
  const trimmed = username.trim()
  
  if (trimmed.length < 2) {
    return { isValid: false, error: 'Username must be at least 2 characters' }
  }
  
  if (trimmed.length > 50) {
    return { isValid: false, error: 'Username must be less than 50 characters' }
  }
  
  return { isValid: true, error: null }
}

/**
 * Validate password strength
 * @param {string} password - Password to validate
 * @returns {Object} Validation result with isValid, strength, and error message
 */
export function validatePassword(password) {
  if (!password || typeof password !== 'string') {
    return { isValid: false, strength: 'weak', error: 'Password is required' }
  }
  
  if (password.length < 6) {
    return { 
      isValid: false, 
      strength: 'weak', 
      error: 'Password must be at least 6 characters' 
    }
  }
  
  // Calculate strength
  let strength = 'weak'
  const hasLower = /[a-z]/.test(password)
  const hasUpper = /[A-Z]/.test(password)
  const hasNumber = /\d/.test(password)
  const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(password)
  
  const criteriaCount = [hasLower, hasUpper, hasNumber, hasSpecial].filter(Boolean).length
  
  if (password.length >= 12 && criteriaCount >= 3) {
    strength = 'strong'
  } else if (password.length >= 8 && criteriaCount >= 2) {
    strength = 'medium'
  }
  
  return { isValid: true, strength, error: null }
}

/**
 * Validate URL
 * @param {string} url - URL to validate
 * @returns {boolean} True if valid URL
 */
export function isValidURL(url) {
  if (!url || typeof url !== 'string') return false
  
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

/**
 * Validate CEFR level
 * @param {string} level - CEFR level to validate
 * @returns {boolean} True if valid CEFR level
 */
export function isValidCEFRLevel(level) {
  if (!level || typeof level !== 'string') return false
  
  const validLevels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
  return validLevels.includes(level.toUpperCase())
}

/**
 * Validate speaking time
 * @param {number} seconds - Speaking time in seconds
 * @returns {Object} Validation result
 */
export function validateSpeakingTime(seconds) {
  if (isNaN(seconds)) {
    return { isValid: false, error: 'Speaking time must be a number' }
  }
  
  if (seconds < 30) {
    return { isValid: false, error: 'Speaking time must be at least 30 seconds' }
  }
  
  if (seconds > 300) {
    return { isValid: false, error: 'Speaking time cannot exceed 5 minutes' }
  }
  
  return { isValid: true, error: null }
}

/**
 * Validate participant count
 * @param {number} count - Number of participants
 * @returns {Object} Validation result
 */
export function validateParticipantCount(count) {
  if (isNaN(count)) {
    return { isValid: false, error: 'Participant count must be a number' }
  }
  
  if (count < 2) {
    return { isValid: false, error: 'At least 2 participants required' }
  }
  
  if (count > 8) {
    return { isValid: false, error: 'Maximum 8 participants allowed' }
  }
  
  return { isValid: true, error: null }
}

/**
 * Validate round count
 * @param {number} rounds - Number of rounds
 * @returns {Object} Validation result
 */
export function validateRoundCount(rounds) {
  if (isNaN(rounds)) {
    return { isValid: false, error: 'Round count must be a number' }
  }
  
  if (rounds < 1) {
    return { isValid: false, error: 'At least 1 round required' }
  }
  
  if (rounds > 10) {
    return { isValid: false, error: 'Maximum 10 rounds allowed' }
  }
  
  return { isValid: true, error: null }
}

/**
 * Sanitize user input to prevent XSS
 * @param {string} input - User input to sanitize
 * @returns {string} Sanitized input
 */
export function sanitizeInput(input) {
  if (!input || typeof input !== 'string') return ''
  
  return input
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/\//g, '&#x2F;')
}

/**
 * Validate required field
 * @param {any} value - Value to validate
 * @param {string} fieldName - Name of the field
 * @returns {Object} Validation result
 */
export function validateRequired(value, fieldName = 'Field') {
  if (value === null || value === undefined || value === '') {
    return { isValid: false, error: `${fieldName} is required` }
  }
  
  if (typeof value === 'string' && value.trim() === '') {
    return { isValid: false, error: `${fieldName} cannot be empty` }
  }
  
  return { isValid: true, error: null }
}

export default {
  isValidEmail,
  isValidRoomCode,
  validateUsername,
  validatePassword,
  isValidURL,
  isValidCEFRLevel,
  validateSpeakingTime,
  validateParticipantCount,
  validateRoundCount,
  sanitizeInput,
  validateRequired,
}
