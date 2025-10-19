import React, { createContext, useContext, useReducer, useEffect } from 'react'

/**
 * Authentication Context for managing user login state
 * Handles user email, name, password, and interest categories
 */

const AuthContext = createContext()

// Action types for auth reducer
const AUTH_ACTIONS = {
  LOGIN: 'LOGIN',
  LOGOUT: 'LOGOUT',
  UPDATE_PROFILE: 'UPDATE_PROFILE'
}

// Initial authentication state
const initialState = {
  isAuthenticated: false,
  user: null,
  anonymousName: null
}

// Authentication reducer
function authReducer(state, action) {
  switch (action.type) {
    case AUTH_ACTIONS.LOGIN:
      return {
        isAuthenticated: true,
        user: action.payload.user || action.payload,
        anonymousName: action.payload.anonymousName || null
      }
    case AUTH_ACTIONS.LOGOUT:
      return initialState
    case AUTH_ACTIONS.UPDATE_PROFILE:
      return {
        ...state,
        user: { ...state.user, ...action.payload }
      }
    default:
      return state
  }
}

/**
 * AuthProvider Component
 * Provides authentication context to the application
 */
export function AuthProvider({ children }) {
  const [state, dispatch] = useReducer(authReducer, initialState)

  // Load authentication state from localStorage on mount
  useEffect(() => {
    const savedUser = localStorage.getItem('auth_user')
    
    if (savedUser) {
      try {
        const user = JSON.parse(savedUser)
        if (user && user.email) {
          dispatch({
            type: AUTH_ACTIONS.LOGIN,
            payload: {
              user
            }
          })
        }
      } catch (error) {
        console.error('Error loading saved auth:', error)
        localStorage.removeItem('auth_user')
        localStorage.removeItem('auth_anonymousName')
      }
    }
  }, [])

  // Save authentication state to localStorage
  useEffect(() => {
    if (state.isAuthenticated) {
      localStorage.setItem('auth_user', JSON.stringify(state.user))
    } else {
      localStorage.removeItem('auth_user')
    }
  }, [state.isAuthenticated, state.user, state.anonymousName])

  /**
   * Login function
   * @param {Object} userData - User data (email, name, interests, etc.)
   * @param {String} anonymousName - Optional anonymous name for the user
   */
  const login = (userData) => {
    dispatch({
      type: AUTH_ACTIONS.LOGIN,
      payload: {
        user: userData,
      }
    })
  }

  /**
   * Logout function
   * Clears all authentication data
   */
  const logout = () => {
    dispatch({ type: AUTH_ACTIONS.LOGOUT })
  }

  /**
   * Update user profile
   * @param {Object} updates - Fields to update
   */
  const updateProfile = (updates) => {
    dispatch({
      type: AUTH_ACTIONS.UPDATE_PROFILE,
      payload: updates
    })
  }

  const value = {
    ...state,
    login,
    logout,
    updateProfile
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

/**
 * Custom hook to use authentication context
 * @returns {Object} Authentication context value
 */
export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
