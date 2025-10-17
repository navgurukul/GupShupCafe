import { describe, it, expect, beforeEach, vi } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { renderWithProviders } from '../test-utils'
import LoginPage from '../../pages/LoginPage'

// Mock useNavigate
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate
  }
})

describe('Integration Tests: Login Flow', () => {
  beforeEach(() => {
    mockNavigate.mockClear()
    localStorage.clear()
  })

  describe('Complete Login Flow', () => {
    it('should complete full login flow from empty form to navigation', async () => {
      const user = userEvent.setup()
      renderWithProviders(<LoginPage />)

      // Step 1: Verify initial state
      expect(screen.getByRole('button', { name: /Join Discussion/i })).toBeEnabled()

      // Step 2: Fill in all required fields
      await user.type(screen.getByLabelText(/User ID/i), 'student-001')
      await user.type(screen.getByLabelText(/Full Name/i), 'Alice Johnson')
      await user.type(screen.getByLabelText(/Campus/i), 'Mumbai Campus')
      await user.type(screen.getByLabelText(/Location/i), 'Mumbai')

      // Step 3: Use a suggestion for anonymous name
      const suggestions = screen.getAllByRole('button', { name: /Thinker|Explorer|Scholar|Philosopher|Researcher|Learner|Discussant|Mind/i })
      await user.click(suggestions[0])

      const anonymousNameInput = screen.getByLabelText(/Anonymous Display Name/i)
      await waitFor(() => {
        expect(anonymousNameInput.value).not.toBe('')
      })

      // Step 4: Submit form
      const submitButton = screen.getByRole('button', { name: /Join Discussion/i })
      await user.click(submitButton)

      // Step 5: Verify navigation
      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/lobby')
      })

      // Step 6: Verify data was stored in localStorage
      const storedUser = JSON.parse(localStorage.getItem('auth_user'))
      expect(storedUser).toMatchObject({
        id: 'student-001',
        name: 'Alice Johnson',
        campus: 'Mumbai Campus',
        location: 'Mumbai'
      })

      const storedAnonymousName = localStorage.getItem('auth_anonymousName')
      expect(storedAnonymousName).toBeTruthy()
    })

    it('should prevent submission with incomplete form', async () => {
      const user = userEvent.setup()
      renderWithProviders(<LoginPage />)

      // Fill only some fields
      await user.type(screen.getByLabelText(/User ID/i), 'student-001')
      await user.type(screen.getByLabelText(/Full Name/i), 'Alice Johnson')
      // Leave campus and other fields empty

      const submitButton = screen.getByRole('button', { name: /Join Discussion/i })
      await user.click(submitButton)

      // Should show validation errors
      await waitFor(() => {
        expect(screen.getByText(/Campus is required/i)).toBeInTheDocument()
      })

      // Should NOT navigate
      expect(mockNavigate).not.toHaveBeenCalled()
    })

    it('should allow form correction after validation error', async () => {
      const user = userEvent.setup()
      renderWithProviders(<LoginPage />)

      // Try to submit empty form
      const submitButton = screen.getByRole('button', { name: /Join Discussion/i })
      await user.click(submitButton)

      // Verify errors
      await waitFor(() => {
        expect(screen.getByText(/User ID is required/i)).toBeInTheDocument()
      })

      // Fill in all fields
      await user.type(screen.getByLabelText(/User ID/i), 'student-002')
      await user.type(screen.getByLabelText(/Full Name/i), 'Bob Smith')
      await user.type(screen.getByLabelText(/Campus/i), 'Delhi Campus')
      await user.type(screen.getByLabelText(/Location/i), 'Delhi')
      await user.type(screen.getByLabelText(/Anonymous Display Name/i), 'Swift Eagle')

      // Resubmit
      await user.click(submitButton)

      // Should now navigate
      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/lobby')
      })
    })
  })

  describe('Session Persistence', () => {
    it('should persist login across page reloads', async () => {
      const user = userEvent.setup()
      
      // First render - login
      const { unmount } = renderWithProviders(<LoginPage />)

      await user.type(screen.getByLabelText(/User ID/i), 'student-003')
      await user.type(screen.getByLabelText(/Full Name/i), 'Charlie Brown')
      await user.type(screen.getByLabelText(/Campus/i), 'Bangalore Campus')
      await user.type(screen.getByLabelText(/Location/i), 'Bangalore')
      await user.type(screen.getByLabelText(/Anonymous Display Name/i), 'Clever Lion')

      const submitButton = screen.getByRole('button', { name: /Join Discussion/i })
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/lobby')
      })

      unmount()
      mockNavigate.mockClear()

      // Second render - should redirect immediately
      renderWithProviders(<LoginPage />)

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/lobby')
      })
    })
  })

  describe('User Experience', () => {
    it('should allow selection of different anonymous name suggestions', async () => {
      const user = userEvent.setup()
      renderWithProviders(<LoginPage />)

      const anonymousNameInput = screen.getByLabelText(/Anonymous Display Name/i)
      const suggestions = screen.getAllByRole('button', { name: /Thinker|Explorer|Scholar|Philosopher|Researcher|Learner|Discussant|Mind/i })

      expect(suggestions.length).toBeGreaterThanOrEqual(1)

      // Click first suggestion
      await user.click(suggestions[0])
      const firstName = anonymousNameInput.value

      // Click second suggestion if it exists
      if (suggestions.length > 1) {
        await user.click(suggestions[1])
        const secondName = anonymousNameInput.value

        // Names should be different
        expect(firstName).toBeTruthy()
        expect(secondName).toBeTruthy()
        expect(firstName).not.toBe(secondName)
      }
    })

    it('should clear validation errors incrementally', async () => {
      const user = userEvent.setup()
      renderWithProviders(<LoginPage />)

      // Submit empty form to trigger all errors
      await user.click(screen.getByRole('button', { name: /Join Discussion/i }))

      await waitFor(() => {
        expect(screen.getByText(/User ID is required/i)).toBeInTheDocument()
        expect(screen.getByText(/Name is required/i)).toBeInTheDocument()
        expect(screen.getByText(/Campus is required/i)).toBeInTheDocument()
      })

      // Fix User ID error
      await user.type(screen.getByLabelText(/User ID/i), 'student-004')
      await waitFor(() => {
        expect(screen.queryByText(/User ID is required/i)).not.toBeInTheDocument()
      })

      // Other errors should still be present
      expect(screen.getByText(/Name is required/i)).toBeInTheDocument()
      expect(screen.getByText(/Campus is required/i)).toBeInTheDocument()

      // Fix Name error
      await user.type(screen.getByLabelText(/Full Name/i), 'David Lee')
      await waitFor(() => {
        expect(screen.queryByText(/Name is required/i)).not.toBeInTheDocument()
      })

      // Campus error should still be present
      expect(screen.getByText(/Campus is required/i)).toBeInTheDocument()
    })
  })
})
