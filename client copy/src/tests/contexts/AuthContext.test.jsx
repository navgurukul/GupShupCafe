import { describe, it, expect, beforeEach, vi } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { AuthProvider, useAuth } from '../../contexts/AuthContext'
import { createMockUser } from '../test-utils'

describe('AuthContext', () => {
  let localStorageMock

  beforeEach(() => {
    // Mock localStorage
    localStorageMock = {
      getItem: vi.fn(),
      setItem: vi.fn(),
      removeItem: vi.fn(),
      clear: vi.fn()
    }
    global.localStorage = localStorageMock
  })

  describe('Initial State', () => {
    it('should initialize with unauthenticated state', () => {
      localStorageMock.getItem.mockReturnValue(null)
      
      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider
      })

      expect(result.current.isAuthenticated).toBe(false)
      expect(result.current.user).toBeNull()
      expect(result.current.anonymousName).toBeNull()
    })

    it('should restore authentication from localStorage', () => {
      const mockUser = createMockUser()
      const mockAnonymousName = 'Happy Tiger'
      
      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'auth_user') return JSON.stringify(mockUser)
        if (key === 'auth_anonymousName') return mockAnonymousName
        return null
      })

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider
      })

      expect(result.current.isAuthenticated).toBe(true)
      expect(result.current.user).toEqual(mockUser)
      expect(result.current.anonymousName).toBe(mockAnonymousName)
    })
  })

  describe('Login Functionality', () => {
    it('should successfully log in a user', async () => {
      localStorageMock.getItem.mockReturnValue(null)
      
      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider
      })

      const mockUser = createMockUser()
      const mockAnonymousName = 'Clever Eagle'

      act(() => {
        result.current.login(mockUser, mockAnonymousName)
      })

      await waitFor(() => {
        expect(result.current.isAuthenticated).toBe(true)
        expect(result.current.user).toEqual(mockUser)
        expect(result.current.anonymousName).toBe(mockAnonymousName)
      })

      // Verify localStorage was called
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'auth_user',
        JSON.stringify(mockUser)
      )
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'auth_anonymousName',
        mockAnonymousName
      )
    })

    it('should handle login with missing fields', async () => {
      localStorageMock.getItem.mockReturnValue(null)
      
      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider
      })

      const incompleteUser = {
        id: 'test-123',
        name: 'Test User'
      }

      act(() => {
        result.current.login(incompleteUser, 'Happy Tiger')
      })

      await waitFor(() => {
        expect(result.current.isAuthenticated).toBe(true)
        expect(result.current.user).toEqual(incompleteUser)
      })
    })
  })

  describe('Logout Functionality', () => {
    it('should successfully log out a user', async () => {
      const mockUser = createMockUser()
      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'auth_user') return JSON.stringify(mockUser)
        if (key === 'auth_anonymousName') return 'Happy Tiger'
        return null
      })

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider
      })

      expect(result.current.isAuthenticated).toBe(true)

      act(() => {
        result.current.logout()
      })

      await waitFor(() => {
        expect(result.current.isAuthenticated).toBe(false)
        expect(result.current.user).toBeNull()
        expect(result.current.anonymousName).toBeNull()
      })

      // Verify localStorage was cleared
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_user')
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_anonymousName')
    })
  })

  describe('Update Profile', () => {
    it('should update user profile', async () => {
      const mockUser = createMockUser()
      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'auth_user') return JSON.stringify(mockUser)
        if (key === 'auth_anonymousName') return 'Happy Tiger'
        return null
      })

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider
      })

      const updates = { campus: 'New Campus', location: 'New Location' }

      act(() => {
        result.current.updateProfile(updates)
      })

      await waitFor(() => {
        expect(result.current.user.campus).toBe('New Campus')
        expect(result.current.user.location).toBe('New Location')
        expect(result.current.user.id).toBe(mockUser.id)
        expect(result.current.user.name).toBe(mockUser.name)
      })
    })
  })

  describe('Edge Cases', () => {
    it('should handle corrupted localStorage data', () => {
      localStorageMock.getItem.mockReturnValue('invalid-json')

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider
      })

      // Should fall back to unauthenticated state
      expect(result.current.isAuthenticated).toBe(false)
    })

    it('should handle null user during login', async () => {
      localStorageMock.getItem.mockReturnValue(null)
      
      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider
      })

      act(() => {
        result.current.login(null, 'Happy Tiger')
      })

      // Should handle gracefully
      await waitFor(() => {
        expect(result.current.user).toBeNull()
      })
    })
  })
})
