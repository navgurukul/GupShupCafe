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

describe('LoginPage', () => {
  beforeEach(() => {
    mockNavigate.mockClear()
    localStorage.clear()
  })

  describe('Rendering', () => {
    it('should render login form with all fields', () => {
      renderWithProviders(<LoginPage />)

      expect(screen.getByLabelText(/User ID/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/Full Name/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/Campus/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/Location/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/Anonymous Display Name/i)).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /Join Discussion/i })).toBeInTheDocument()
    })

    it('should render with AI branding', () => {
      renderWithProviders(<LoginPage />)

      expect(screen.getByText(/AI Roundtable Discussion/i)).toBeInTheDocument()
    })
  })

  describe('Form Validation', () => {
    it('should show error for empty user ID', async () => {
      const user = userEvent.setup()
      renderWithProviders(<LoginPage />)

      const submitButton = screen.getByRole('button', { name: /Join Discussion/i })
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText(/User ID is required/i)).toBeInTheDocument()
      })
    })

    it('should show error for empty name', async () => {
      const user = userEvent.setup()
      renderWithProviders(<LoginPage />)

      const idInput = screen.getByLabelText(/User ID/i)
      await user.type(idInput, 'test-id-123')

      const submitButton = screen.getByRole('button', { name: /Join Discussion/i })
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText(/Name is required/i)).toBeInTheDocument()
      })
    })

    it('should show error for empty campus', async () => {
      const user = userEvent.setup()
      renderWithProviders(<LoginPage />)

      const idInput = screen.getByLabelText(/User ID/i)
      const nameInput = screen.getByLabelText(/Full Name/i)
      
      await user.type(idInput, 'test-id-123')
      await user.type(nameInput, 'Test User')

      const submitButton = screen.getByRole('button', { name: /Join Discussion/i })
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText(/Campus is required/i)).toBeInTheDocument()
      })
    })

    it('should validate all fields before submission', async () => {
      const user = userEvent.setup()
      renderWithProviders(<LoginPage />)

      const submitButton = screen.getByRole('button', { name: /Join Discussion/i })
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText(/User ID is required/i)).toBeInTheDocument()
        expect(screen.getByText(/Name is required/i)).toBeInTheDocument()
        expect(screen.getByText(/Campus is required/i)).toBeInTheDocument()
      })
    })
  })

  describe('Form Interaction', () => {
    it('should allow user to fill in all fields', async () => {
      const user = userEvent.setup()
      renderWithProviders(<LoginPage />)

      const idInput = screen.getByLabelText(/User ID/i)
      const nameInput = screen.getByLabelText(/Full Name/i)
      const campusInput = screen.getByLabelText(/Campus/i)
      const locationInput = screen.getByLabelText(/Location/i)
      const anonymousNameInput = screen.getByLabelText(/Anonymous Display Name/i)

      await user.type(idInput, 'test-123')
      await user.type(nameInput, 'John Doe')
      await user.type(campusInput, 'Main Campus')
      await user.type(locationInput, 'New York')
      await user.type(anonymousNameInput, 'Happy Tiger')

      expect(idInput).toHaveValue('test-123')
      expect(nameInput).toHaveValue('John Doe')
      expect(campusInput).toHaveValue('Main Campus')
      expect(locationInput).toHaveValue('New York')
      expect(anonymousNameInput).toHaveValue('Happy Tiger')
    })

    it('should clear error when user starts typing', async () => {
      const user = userEvent.setup()
      renderWithProviders(<LoginPage />)

      const submitButton = screen.getByRole('button', { name: /Join Discussion/i })
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText(/User ID is required/i)).toBeInTheDocument()
      })

      const idInput = screen.getByLabelText(/User ID/i)
      await user.type(idInput, 'test-123')

      await waitFor(() => {
        expect(screen.queryByText(/User ID is required/i)).not.toBeInTheDocument()
      })
    })
  })

  describe('Anonymous Name Generation', () => {
    it('should display anonymous name suggestions', () => {
      renderWithProviders(<LoginPage />)

      expect(screen.getByText(/Suggestions:/i)).toBeInTheDocument()
      
      // Should have 3 suggestion buttons
      const suggestions = screen.getAllByRole('button', { name: /Thinker|Explorer|Scholar|Philosopher|Researcher|Learner|Discussant|Mind/i })
      expect(suggestions.length).toBeGreaterThanOrEqual(1)
    })

    it('should fill anonymous name when clicking suggestion', async () => {
      const user = userEvent.setup()
      renderWithProviders(<LoginPage />)

      const anonymousNameInput = screen.getByLabelText(/Anonymous Display Name/i)
      expect(anonymousNameInput.value).toBe('')

      // Click first suggestion
      const suggestions = screen.getAllByRole('button', { name: /Thinker|Explorer|Scholar|Philosopher|Researcher|Learner|Discussant|Mind/i })
      const firstSuggestion = suggestions[0]
      const suggestionText = firstSuggestion.textContent

      await user.click(firstSuggestion)

      await waitFor(() => {
        expect(anonymousNameInput.value).toBe(suggestionText)
      })
    })
  })

  describe('Form Submission', () => {
    it('should submit form with valid data', async () => {
      const user = userEvent.setup()
      renderWithProviders(<LoginPage />)

      const idInput = screen.getByLabelText(/User ID/i)
      const nameInput = screen.getByLabelText(/Full Name/i)
      const campusInput = screen.getByLabelText(/Campus/i)
      const locationInput = screen.getByLabelText(/Location/i)
      const anonymousNameInput = screen.getByLabelText(/Anonymous Display Name/i)

      await user.type(idInput, 'test-123')
      await user.type(nameInput, 'John Doe')
      await user.type(campusInput, 'Main Campus')
      await user.type(locationInput, 'New York')
      await user.type(anonymousNameInput, 'Happy Tiger')

      const submitButton = screen.getByRole('button', { name: /Join Discussion/i })
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/lobby')
      })
    })

    it('should disable submit button while submitting', async () => {
      const user = userEvent.setup()
      renderWithProviders(<LoginPage />)

      const idInput = screen.getByLabelText(/User ID/i)
      const nameInput = screen.getByLabelText(/Full Name/i)
      const campusInput = screen.getByLabelText(/Campus/i)
      const anonymousNameInput = screen.getByLabelText(/Anonymous Display Name/i)

      await user.type(idInput, 'test-123')
      await user.type(nameInput, 'John Doe')
      await user.type(campusInput, 'Main Campus')
      await user.type(anonymousNameInput, 'Happy Tiger')

      const submitButton = screen.getByRole('button', { name: /Join Discussion/i })
      
      await user.click(submitButton)
      
      // Button should be disabled during submission
      expect(submitButton).toBeDisabled()
    })
  })

  describe('Authentication Redirect', () => {
    it('should redirect to lobby if already authenticated', async () => {
      // Mock authenticated state
      localStorage.setItem('auth_user', JSON.stringify({
        id: 'test-123',
        name: 'Test User',
        campus: 'Test Campus',
        location: 'Test Location'
      }))
      localStorage.setItem('auth_anonymousName', 'Happy Tiger')

      renderWithProviders(<LoginPage />)

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/lobby')
      })
    })
  })
})
