/**
 * Helper Utilities
 * Common utility functions used across the application
 */

/**
 * Generate a random room code
 * @param {number} length - Length of the code
 * @returns {string} Random room code
 */
export function generateRoomCode(length = 6) {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
  let code = ''
  for (let i = 0; i < length; i++) {
    code += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  return code
}

/**
 * Generate a random anonymous name
 * @returns {string} Random anonymous name (e.g., "Happy Tiger")
 */
export function generateAnonymousName() {
  const adjectives = [
    'Happy', 'Cheerful', 'Bright', 'Swift', 'Calm', 'Bold', 'Wise',
    'Clever', 'Kind', 'Gentle', 'Brave', 'Quick', 'Smart', 'Eager'
  ]
  const animals = [
    'Tiger', 'Eagle', 'Dolphin', 'Fox', 'Lion', 'Owl', 'Panda',
    'Wolf', 'Bear', 'Hawk', 'Deer', 'Rabbit', 'Falcon', 'Otter'
  ]
  
  const adjective = adjectives[Math.floor(Math.random() * adjectives.length)]
  const animal = animals[Math.floor(Math.random() * animals.length)]
  
  return `${adjective} ${animal}`
}

/**
 * Generate a random avatar color
 * @returns {string} Hex color code
 */
export function generateAvatarColor() {
  const colors = [
    '#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6',
    '#EC4899', '#14B8A6', '#F97316', '#6366F1', '#84CC16'
  ]
  return colors[Math.floor(Math.random() * colors.length)]
}

/**
 * Debounce function
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
export function debounce(func, wait = 300) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

/**
 * Throttle function
 * @param {Function} func - Function to throttle
 * @param {number} limit - Limit time in milliseconds
 * @returns {Function} Throttled function
 */
export function throttle(func, limit = 300) {
  let inThrottle
  return function executedFunction(...args) {
    if (!inThrottle) {
      func(...args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}

/**
 * Deep clone an object
 * @param {Object} obj - Object to clone
 * @returns {Object} Cloned object
 */
export function deepClone(obj) {
  if (obj === null || typeof obj !== 'object') return obj
  if (obj instanceof Date) return new Date(obj.getTime())
  if (obj instanceof Array) return obj.map(item => deepClone(item))
  if (obj instanceof Object) {
    const clonedObj = {}
    for (const key in obj) {
      if (Object.prototype.hasOwnProperty.call(obj, key)) {
        clonedObj[key] = deepClone(obj[key])
      }
    }
    return clonedObj
  }
}

/**
 * Check if object is empty
 * @param {Object} obj - Object to check
 * @returns {boolean} True if empty
 */
export function isEmpty(obj) {
  if (obj == null) return true
  if (Array.isArray(obj) || typeof obj === 'string') return obj.length === 0
  if (obj instanceof Map || obj instanceof Set) return obj.size === 0
  return Object.keys(obj).length === 0
}

/**
 * Get initials from name
 * @param {string} name - Full name
 * @returns {string} Initials (e.g., "John Doe" -> "JD")
 */
export function getInitials(name) {
  if (!name) return '?'
  return name
    .split(' ')
    .map(word => word.charAt(0).toUpperCase())
    .slice(0, 2)
    .join('')
}

/**
 * Sleep/delay function
 * @param {number} ms - Milliseconds to sleep
 * @returns {Promise} Promise that resolves after delay
 */
export function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

/**
 * Capitalize first letter of string
 * @param {string} str - String to capitalize
 * @returns {string} Capitalized string
 */
export function capitalize(str) {
  if (!str) return ''
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase()
}

/**
 * Truncate string to specified length
 * @param {string} str - String to truncate
 * @param {number} maxLength - Maximum length
 * @param {string} suffix - Suffix to add (default: '...')
 * @returns {string} Truncated string
 */
export function truncate(str, maxLength = 50, suffix = '...') {
  if (!str || str.length <= maxLength) return str
  return str.substring(0, maxLength - suffix.length) + suffix
}

/**
 * Check if code is running in development mode
 * @returns {boolean} True if in development
 */
export function isDevelopment() {
  return import.meta.env.MODE === 'development'
}

/**
 * Check if code is running in production mode
 * @returns {boolean} True if in production
 */
export function isProduction() {
  return import.meta.env.MODE === 'production'
}

export default {
  generateRoomCode,
  generateAnonymousName,
  generateAvatarColor,
  debounce,
  throttle,
  deepClone,
  isEmpty,
  getInitials,
  sleep,
  capitalize,
  truncate,
  isDevelopment,
  isProduction,
}
