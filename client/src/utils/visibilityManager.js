/**
 * Visibility Manager
 * Handles page visibility changes to optimize socket connection
 */

class VisibilityManager {
  constructor() {
    this.listeners = new Set()
    this.isVisible = !document.hidden
    this.setupEventListeners()
  }

  setupEventListeners() {
    // Handle page visibility changes
    document.addEventListener('visibilitychange', () => {
      this.isVisible = !document.hidden
      this.notifyListeners(this.isVisible)
    })

    // Handle window focus/blur
    window.addEventListener('focus', () => {
      this.isVisible = true
      this.notifyListeners(true)
    })

    window.addEventListener('blur', () => {
      this.isVisible = false
      this.notifyListeners(false)
    })

    // Handle beforeunload to save state
    window.addEventListener('beforeunload', () => {
      this.notifyListeners(false, 'beforeunload')
    })
  }

  addListener(callback) {
    this.listeners.add(callback)
    return () => this.listeners.delete(callback)
  }

  notifyListeners(isVisible, event = 'visibility') {
    this.listeners.forEach(callback => {
      try {
        callback(isVisible, event)
      } catch (error) {
        console.error('Error in visibility listener:', error)
      }
    })
  }

  getVisibility() {
    return this.isVisible
  }
}

// Singleton instance
export const visibilityManager = new VisibilityManager()

export default visibilityManager