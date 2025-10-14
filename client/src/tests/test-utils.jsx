import React from 'react'
import { render } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { AuthProvider } from '../contexts/AuthContext'
import { SocketProvider } from '../contexts/SocketContext'
import { AudioProvider } from '../contexts/AudioContext'

/**
 * Custom render function that wraps components with all necessary providers
 */
export function renderWithProviders(ui, options = {}) {
  const {
    initialAuthState = {},
    ...renderOptions
  } = options

  function Wrapper({ children }) {
    return (
      <BrowserRouter>
        <AuthProvider initialState={initialAuthState}>
          <SocketProvider>
            <AudioProvider>
              {children}
            </AudioProvider>
          </SocketProvider>
        </AuthProvider>
      </BrowserRouter>
    )
  }

  return render(ui, { wrapper: Wrapper, ...renderOptions })
}

/**
 * Create a mock user object for testing
 */
export function createMockUser(overrides = {}) {
  return {
    id: 'test-user-123',
    name: 'Test User',
    campus: 'Test Campus',
    location: 'Test Location',
    ...overrides
  }
}

/**
 * Create a mock anonymous name
 */
export function createMockAnonymousName() {
  const adjectives = ['Happy', 'Clever', 'Swift']
  const nouns = ['Tiger', 'Eagle', 'Lion']
  const adjective = adjectives[Math.floor(Math.random() * adjectives.length)]
  const noun = nouns[Math.floor(Math.random() * nouns.length)]
  return `${adjective} ${noun}`
}

/**
 * Mock localStorage for testing
 */
export function mockLocalStorage() {
  const store = {}
  
  return {
    getItem: (key) => store[key] || null,
    setItem: (key, value) => {
      store[key] = value.toString()
    },
    removeItem: (key) => {
      delete store[key]
    },
    clear: () => {
      Object.keys(store).forEach(key => delete store[key])
    }
  }
}

/**
 * Wait for async operations to complete
 */
export function waitForAsync() {
  return new Promise(resolve => setTimeout(resolve, 0))
}

// Re-export testing library utilities
export * from '@testing-library/react'
export { default as userEvent } from '@testing-library/user-event'
