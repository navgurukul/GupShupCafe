/**
 * Formatter Utilities
 * Functions for formatting data for display
 */

/**
 * Format time in seconds to MM:SS format
 * @param {number} seconds - Time in seconds
 * @returns {string} Formatted time (e.g., "02:30")
 */
export function formatTime(seconds) {
  if (isNaN(seconds) || seconds < 0) return '00:00'
  
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

/**
 * Format date to readable string
 * @param {Date|string|number} date - Date object, ISO string, or timestamp
 * @param {Object} options - Intl.DateTimeFormat options
 * @returns {string} Formatted date
 */
export function formatDate(date, options = {}) {
  if (!date) return ''
  
  const dateObj = date instanceof Date ? date : new Date(date)
  
  if (isNaN(dateObj.getTime())) return ''
  
  const defaultOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    ...options
  }
  
  return dateObj.toLocaleDateString('en-US', defaultOptions)
}

/**
 * Format date and time to readable string
 * @param {Date|string|number} date - Date object, ISO string, or timestamp
 * @returns {string} Formatted date and time
 */
export function formatDateTime(date) {
  if (!date) return ''
  
  const dateObj = date instanceof Date ? date : new Date(date)
  
  if (isNaN(dateObj.getTime())) return ''
  
  return dateObj.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

/**
 * Format relative time (e.g., "2 hours ago")
 * @param {Date|string|number} date - Date object, ISO string, or timestamp
 * @returns {string} Relative time string
 */
export function formatRelativeTime(date) {
  if (!date) return ''
  
  const dateObj = date instanceof Date ? date : new Date(date)
  
  if (isNaN(dateObj.getTime())) return ''
  
  const now = new Date()
  const diffMs = now - dateObj
  const diffSecs = Math.floor(diffMs / 1000)
  const diffMins = Math.floor(diffSecs / 60)
  const diffHours = Math.floor(diffMins / 60)
  const diffDays = Math.floor(diffHours / 24)
  
  if (diffSecs < 60) return 'just now'
  if (diffMins < 60) return `${diffMins} ${diffMins === 1 ? 'minute' : 'minutes'} ago`
  if (diffHours < 24) return `${diffHours} ${diffHours === 1 ? 'hour' : 'hours'} ago`
  if (diffDays < 30) return `${diffDays} ${diffDays === 1 ? 'day' : 'days'} ago`
  
  return formatDate(dateObj)
}

/**
 * Format number with commas (e.g., 1000 -> "1,000")
 * @param {number} num - Number to format
 * @returns {string} Formatted number
 */
export function formatNumber(num) {
  if (isNaN(num)) return '0'
  return num.toLocaleString('en-US')
}

/**
 * Format percentage
 * @param {number} value - Value to format as percentage
 * @param {number} decimals - Number of decimal places
 * @returns {string} Formatted percentage (e.g., "75.5%")
 */
export function formatPercentage(value, decimals = 0) {
  if (isNaN(value)) return '0%'
  return `${value.toFixed(decimals)}%`
}

/**
 * Format CEFR level with full name
 * @param {string} level - CEFR level code (A1, A2, B1, B2, C1, C2)
 * @returns {string} Formatted level (e.g., "B2 - Upper Intermediate")
 */
export function formatCEFRLevel(level) {
  const levels = {
    'A1': 'A1 - Beginner',
    'A2': 'A2 - Elementary',
    'B1': 'B1 - Intermediate',
    'B2': 'B2 - Upper Intermediate',
    'C1': 'C1 - Advanced',
    'C2': 'C2 - Proficient'
  }
  return levels[level] || level
}

/**
 * Format duration in seconds to human-readable string
 * @param {number} seconds - Duration in seconds
 * @returns {string} Formatted duration (e.g., "2h 30m" or "45s")
 */
export function formatDuration(seconds) {
  if (isNaN(seconds) || seconds < 0) return '0s'
  
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)
  
  const parts = []
  if (hours > 0) parts.push(`${hours}h`)
  if (minutes > 0) parts.push(`${minutes}m`)
  if (secs > 0 || parts.length === 0) parts.push(`${secs}s`)
  
  return parts.join(' ')
}

/**
 * Format file size in bytes to human-readable string
 * @param {number} bytes - File size in bytes
 * @returns {string} Formatted size (e.g., "1.5 MB")
 */
export function formatFileSize(bytes) {
  if (isNaN(bytes) || bytes < 0) return '0 B'
  
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let size = bytes
  let unitIndex = 0
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  
  return `${size.toFixed(unitIndex === 0 ? 0 : 1)} ${units[unitIndex]}`
}

/**
 * Format score with color coding
 * @param {number} score - Score value (0-100)
 * @returns {Object} Object with formatted score and color class
 */
export function formatScore(score) {
  if (isNaN(score)) {
    return { text: 'N/A', color: 'text-gray-500' }
  }
  
  const text = `${Math.round(score)}%`
  
  if (score >= 80) return { text, color: 'text-green-600' }
  if (score >= 60) return { text, color: 'text-yellow-600' }
  return { text, color: 'text-red-600' }
}

export default {
  formatTime,
  formatDate,
  formatDateTime,
  formatRelativeTime,
  formatNumber,
  formatPercentage,
  formatCEFRLevel,
  formatDuration,
  formatFileSize,
  formatScore,
}
