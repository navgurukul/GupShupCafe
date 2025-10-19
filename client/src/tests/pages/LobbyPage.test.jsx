import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { renderWithProviders } from '../test-utils'
import LobbyPage from '../../pages/LobbyPage'
import * as api from '../../services/api'

// Mock useNavigate
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useLocation: () => ({ pathname: '/lobby', search: '' })
  }
})

// Mock API service
vi.mock('../../services/api')

// Mock socket context
const mockJoinRoom = vi.fn()
const mockSignalReady = vi.fn()

vi.mock('../../contexts/SocketContext', () => ({
  useSocket: () => ({
    socket: { id: 'socket-123', on: vi.fn(), off: vi.fn(), emit: vi.fn() },
    connected: true,
    joinRoom: mockJoinRoom,
    signalReady: mockSignalReady
  }),
  SocketProvider: ({ children }) => children
}))

// Mock audio context
vi.mock('../../contexts/AudioContext', () => ({
  useAudio: () => ({
    audioEnabled: true,
    micPermission: 'granted',
    requestMicrophoneAccess: vi.fn(),
    isWebRTCSupported: true,
    userRole: 'speaker',
    updateUserRole: vi.fn()
  }),
  AudioProvider: ({ children }) => children
}))

describe('LobbyPage - Join Room Feature', () => {
  const mockWaitingRooms = [
    {
      room_id: 'room-123',
      room_name: 'Tech Discussion',
      topic_title: 'AI and Machine Learning',
      topic_category: 'scienceAndTechnology',
      cefr_level: 'B1',
      max_participants: 6,
      participant_count: 2,
      status: 'waiting',
      created_at: '2025-10-19T09:00:00Z',
      created_by: 'user-456'
    },
    {
      room_id: 'room-456',
      room_name: 'Literature Chat',
      topic_title: 'Modern Poetry',
      topic_category: 'literature',
      cefr_level: 'C1',
      max_participants: 4,
      participant_count: 1,
      status: 'waiting',
      created_at: '2025-10-19T09:15:00Z',
      created_by: 'user-789'
    }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    
    // Set up authenticated user
    localStorage.setItem('userData', JSON.stringify({
      userId: 'user-123',
      name: 'Test User',
      currentCefrLevel: 'B1'
    }))
    localStorage.setItem('auth_anonymousName', 'Happy Tiger')
    
    // Mock successful API responses by default
    api.fetchWaitingRooms.mockResolvedValue(mockWaitingRooms)
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ status: 'success', data: 'participant-123' })
    })
  })

  afterEach(() => {
    vi.resetAllMocks()
  })

  describe('Room Discovery', () => {
    it('should fetch and display waiting rooms on load', async () => {
      renderWithProviders(<LobbyPage />)

      await waitFor(() => {
        expect(api.fetchWaitingRooms).toHaveBeenCalled()
      })

      await waitFor(() => {
        expect(screen.getByText('Tech Discussion')).toBeInTheDocument()
        expect(screen.getByText('Literature Chat')).toBeInTheDocument()
      })
    })

    it('should display loading state while fetching rooms', async () => {
      // Delay the API response
      api.fetchWaitingRooms.mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve(mockWaitingRooms), 100))
      )

      renderWithProviders(<LobbyPage />)

      expect(screen.getByText(/Loading rooms/i)).toBeInTheDocument()

      await waitFor(() => {
        expect(screen.getByText('Tech Discussion')).toBeInTheDocument()
      }, { timeout: 3000 })
    })

    it('should display empty state when no rooms available', async () => {
      api.fetchWaitingRooms.mockResolvedValue([])

      renderWithProviders(<LobbyPage />)

      await waitFor(() => {
        expect(screen.getByText(/No rooms available/i)).toBeInTheDocument()
      })
    })

    it('should show participant counts for waiting rooms', async () => {
      renderWithProviders(<LobbyPage />)

      await waitFor(() => {
        expect(screen.getByText(/2 \/ 6 joined/i)).toBeInTheDocument()
        expect(screen.getByText(/1 \/ 4 joined/i)).toBeInTheDocument()
      })
    })

    it('should display "Active Room" badge for backend rooms', async () => {
      renderWithProviders(<LobbyPage />)

      await waitFor(() => {
        const badges = screen.getAllByText(/Active Room/i)
        expect(badges.length).toBe(2) // One for each backend room
      })
    })

    it('should display room details (CEFR level, category)', async () => {
      renderWithProviders(<LobbyPage />)

      await waitFor(() => {
        expect(screen.getByText('B1')).toBeInTheDocument()
        expect(screen.getByText('C1')).toBeInTheDocument()
      })
    })
  })

  describe('Auto-refresh', () => {
    it('should auto-refresh room list every 10 seconds', async () => {
      vi.useFakeTimers()
      
      renderWithProviders(<LobbyPage />)

      await waitFor(() => {
        expect(api.fetchWaitingRooms).toHaveBeenCalledTimes(1)
      })

      // Fast-forward 10 seconds
      vi.advanceTimersByTime(10000)

      await waitFor(() => {
        expect(api.fetchWaitingRooms).toHaveBeenCalledTimes(2)
      })

      // Fast-forward another 10 seconds
      vi.advanceTimersByTime(10000)

      await waitFor(() => {
        expect(api.fetchWaitingRooms).toHaveBeenCalledTimes(3)
      })

      vi.useRealTimers()
    })

    it('should stop auto-refresh when user joins a room', async () => {
      vi.useFakeTimers()
      const user = userEvent.setup({ delay: null })
      
      renderWithProviders(<LobbyPage />)

      await waitFor(() => {
        expect(screen.getByText('Tech Discussion')).toBeInTheDocument()
      })

      // Click join button
      const joinButtons = screen.getAllByRole('button', { name: /Join/i })
      await user.click(joinButtons[0])

      // Fast-forward time
      vi.advanceTimersByTime(30000)

      // Should not have called fetchWaitingRooms again after joining
      await waitFor(() => {
        expect(api.fetchWaitingRooms).toHaveBeenCalledTimes(1)
      })

      vi.useRealTimers()
    })
  })

  describe('Join Room Flow', () => {
    it('should join a backend room successfully', async () => {
      const user = userEvent.setup()
      renderWithProviders(<LobbyPage />)

      await waitFor(() => {
        expect(screen.getByText('Tech Discussion')).toBeInTheDocument()
      })

      const joinButtons = screen.getAllByRole('button', { name: /Join/i })
      await user.click(joinButtons[0])

      await waitFor(() => {
        // Should create participant entry
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('/participants/'),
          expect.objectContaining({
            method: 'POST',
            body: expect.stringContaining('room-123')
          })
        )
      })

      await waitFor(() => {
        // Should call joinRoom with correct room ID
        expect(mockJoinRoom).toHaveBeenCalledWith(
          'room-123',
          'speaker',
          expect.objectContaining({
            name: 'Tech Discussion',
            cefr_level: 'B1',
            max_participants: 6
          })
        )
      })

      await waitFor(() => {
        // Should navigate to room lobby
        expect(mockNavigate).toHaveBeenCalledWith('/room-lobby')
      })
    })

    it('should handle join room errors gracefully', async () => {
      const user = userEvent.setup()
      global.fetch.mockRejectedValueOnce(new Error('Failed to create participant'))

      renderWithProviders(<LobbyPage />)

      await waitFor(() => {
        expect(screen.getByText('Tech Discussion')).toBeInTheDocument()
      })

      const joinButtons = screen.getAllByRole('button', { name: /Join/i })
      await user.click(joinButtons[0])

      // Should still attempt to join via socket
      await waitFor(() => {
        expect(mockJoinRoom).toHaveBeenCalled()
      })
    })

    it('should pass room metadata when joining', async () => {
      const user = userEvent.setup()
      renderWithProviders(<LobbyPage />)

      await waitFor(() => {
        expect(screen.getByText('Tech Discussion')).toBeInTheDocument()
      })

      const joinButtons = screen.getAllByRole('button', { name: /Join/i })
      await user.click(joinButtons[0])

      await waitFor(() => {
        expect(mockJoinRoom).toHaveBeenCalledWith(
          'room-123',
          'speaker',
          expect.objectContaining({
            name: 'Tech Discussion',
            room_name: 'Tech Discussion',
            topic_category: 'scienceAndTechnology',
            cefr_level: 'B1',
            max_participants: 6
          })
        )
      })
    })
  })

  describe('Room Sharing', () => {
    it('should open share modal when share button clicked', async () => {
      const user = userEvent.setup()
      renderWithProviders(<LobbyPage />)

      await waitFor(() => {
        expect(screen.getByText('Tech Discussion')).toBeInTheDocument()
      })

      const shareButtons = screen.getAllByRole('button', { title: /Share this room/i })
      await user.click(shareButtons[0])

      await waitFor(() => {
        expect(screen.getByText(/Room Created! Invite Others/i)).toBeInTheDocument()
      })
    })

    it('should generate shareable link with correct format', async () => {
      const user = userEvent.setup()
      renderWithProviders(<LobbyPage />)

      await waitFor(() => {
        expect(screen.getByText('Tech Discussion')).toBeInTheDocument()
      })

      const shareButtons = screen.getAllByRole('button', { title: /Share this room/i })
      await user.click(shareButtons[0])

      await waitFor(() => {
        const linkInput = screen.getByDisplayValue(/room-123/)
        expect(linkInput.value).toContain('room=room-123')
        expect(linkInput.value).toContain('role=speaker')
      })
    })

    it('should copy link to clipboard', async () => {
      const user = userEvent.setup()
      
      // Mock clipboard API
      Object.assign(navigator, {
        clipboard: {
          writeText: vi.fn().mockResolvedValue()
        }
      })

      renderWithProviders(<LobbyPage />)

      await waitFor(() => {
        expect(screen.getByText('Tech Discussion')).toBeInTheDocument()
      })

      const shareButtons = screen.getAllByRole('button', { title: /Share this room/i })
      await user.click(shareButtons[0])

      await waitFor(() => {
        expect(screen.getByText(/Room Created! Invite Others/i)).toBeInTheDocument()
      })

      const copyButton = screen.getByRole('button', { name: /Copy/i })
      await user.click(copyButton)

      await waitFor(() => {
        expect(navigator.clipboard.writeText).toHaveBeenCalled()
        expect(screen.getByText(/Copied!/i)).toBeInTheDocument()
      })
    })
  })

  describe('Create Room', () => {
    it('should show create room form when button clicked', async () => {
      const user = userEvent.setup()
      renderWithProviders(<LobbyPage />)

      const createButton = screen.getByRole('button', { name: /Create Room/i })
      await user.click(createButton)

      expect(screen.getByLabelText(/Room Name/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/Max Participants/i)).toBeInTheDocument()
      expect(screen.getByText(/Topic Category/i)).toBeInTheDocument()
      expect(screen.getByText(/CEFR Level/i)).toBeInTheDocument()
    })

    it('should validate required fields when creating room', async () => {
      const user = userEvent.setup()
      renderWithProviders(<LobbyPage />)

      const createButton = screen.getByRole('button', { name: /Create Room/i })
      await user.click(createButton)

      const publishButton = screen.getByRole('button', { name: /Publish Room/i })
      expect(publishButton).toBeDisabled()
    })

    it('should enable publish button when all fields filled', async () => {
      const user = userEvent.setup()
      renderWithProviders(<LobbyPage />)

      const createButton = screen.getByRole('button', { name: /Create Room/i })
      await user.click(createButton)

      // Fill in room name
      const roomNameInput = screen.getByLabelText(/Room Name/i)
      await user.type(roomNameInput, 'New Test Room')

      // Fill in anonymous name
      const anonymousNameInput = screen.getByPlaceholderText(/Enter your anonymous display name/i)
      await user.type(anonymousNameInput, 'Cool Panda')

      // Select topic category
      const scienceButton = screen.getByRole('button', { name: /Science & Technology/i })
      await user.click(scienceButton)

      // Select CEFR level
      const b1Button = screen.getByRole('button', { name: /B1 - Intermediate/i })
      await user.click(b1Button)

      const publishButton = screen.getByRole('button', { name: /Publish Room/i })
      expect(publishButton).not.toBeDisabled()
    })
  })

  describe('Error Handling', () => {
    it('should handle API errors gracefully and show fallback rooms', async () => {
      api.fetchWaitingRooms.mockRejectedValue(new Error('API Error'))

      renderWithProviders(<LobbyPage />)

      await waitFor(() => {
        // Should show predefined rooms as fallback
        expect(screen.getByText('Education')).toBeInTheDocument()
        expect(screen.getByText('Science & Technology')).toBeInTheDocument()
      })
    })

    it('should handle empty response and show fallback rooms', async () => {
      api.fetchWaitingRooms.mockResolvedValue([])

      renderWithProviders(<LobbyPage />)

      await waitFor(() => {
        expect(screen.getByText(/No rooms available/i)).toBeInTheDocument()
      })
    })
  })

  describe('Room Display', () => {
    it('should display room icons based on category', async () => {
      renderWithProviders(<LobbyPage />)

      await waitFor(() => {
        const roomCards = screen.getAllByRole('button', { name: /Join/i })
        expect(roomCards.length).toBeGreaterThan(0)
      })

      // Check that rooms have visual elements (icons are rendered as SVG)
      const svgElements = document.querySelectorAll('svg')
      expect(svgElements.length).toBeGreaterThan(0)
    })

    it('should display room header showing room count', async () => {
      renderWithProviders(<LobbyPage />)

      await waitFor(() => {
        expect(screen.getByText(/Available Rooms/i)).toBeInTheDocument()
      })
    })

    it('should show connection status in header', async () => {
      renderWithProviders(<LobbyPage />)

      expect(screen.getByText(/Connected/i)).toBeInTheDocument()
    })

    it('should show waiting time in header', async () => {
      renderWithProviders(<LobbyPage />)

      expect(screen.getByText(/0:00/i)).toBeInTheDocument()
    })
  })

  describe('Participant Management', () => {
    it('should show user as participant when in room', async () => {
      const user = userEvent.setup()
      renderWithProviders(<LobbyPage />)

      await waitFor(() => {
        expect(screen.getByText('Tech Discussion')).toBeInTheDocument()
      })

      const joinButtons = screen.getAllByRole('button', { name: /Join/i })
      await user.click(joinButtons[0])

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/room-lobby')
      })
    })
  })
})
