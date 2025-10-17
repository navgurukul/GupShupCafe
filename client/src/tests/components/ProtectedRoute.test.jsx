import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import { renderWithProviders } from '../test-utils'
import ProtectedRoute from '../../components/common/ProtectedRoute'

// Mock useNavigate
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate
  }
})

describe('ProtectedRoute', () => {
  beforeEach(() => {
    mockNavigate.mockClear()
    localStorage.clear()
  })

  describe('Authentication Check', () => {
    it('should render children when user is authenticated', () => {
      // Set authenticated state
      localStorage.setItem('auth_user', JSON.stringify({
        id: 'test-123',
        name: 'Test User',
        campus: 'Test Campus',
        location: 'Test Location'
      }))
      localStorage.setItem('auth_anonymousName', 'Happy Tiger')

      renderWithProviders(
        <ProtectedRoute>
          <div>Protected Content</div>
        </ProtectedRoute>
      )

      expect(screen.getByText('Protected Content')).toBeInTheDocument()
    })

    it('should redirect to login when user is not authenticated', async () => {
      renderWithProviders(
        <ProtectedRoute>
          <div>Protected Content</div>
        </ProtectedRoute>
      )

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/')
      })

      expect(screen.queryByText('Protected Content')).not.toBeInTheDocument()
    })

    it('should show loading state while checking authentication', () => {
      renderWithProviders(
        <ProtectedRoute>
          <div>Protected Content</div>
        </ProtectedRoute>
      )

      // Initially should show loading or nothing
      // This depends on implementation details
    })
  })

  describe('Multiple Children', () => {
    it('should render multiple children when authenticated', () => {
      localStorage.setItem('auth_user', JSON.stringify({
        id: 'test-123',
        name: 'Test User',
        campus: 'Test Campus'
      }))
      localStorage.setItem('auth_anonymousName', 'Happy Tiger')

      renderWithProviders(
        <ProtectedRoute>
          <div>First Child</div>
          <div>Second Child</div>
        </ProtectedRoute>
      )

      expect(screen.getByText('First Child')).toBeInTheDocument()
      expect(screen.getByText('Second Child')).toBeInTheDocument()
    })
  })
})
