import { describe, it, expect, beforeEach, vi } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { renderWithProviders } from '../test-utils'
import RoomLobbyPage from '../../pages/RoomLobbyPage'

// Mock useParams to return a test room ID
const mockRoomId = 'test-room-123'
const mockNavigate = vi.fn()

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useParams: () => ({ roomId: mockRoomId }),
    useNavigate: () => mockNavigate,
    useLocation: () => ({ pathname: `/lobby/${mockRoomId}`, search: '?role=speaker' })
  }
})

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

describe('RoomLobbyPage - Dynamic Room Routing', () => {
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
    
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ status: 'success', data: [] })
    })
  })

  describe('Room ID from URL', () => {
    it('should display room lobby interface', async () => {
      renderWithProviders(<RoomLobbyPage />)

      expect(screen.getByRole('heading', { name: /Lobby/i })).toBeInTheDocument()
      // Check for "Welcome" text which should be present
      expect(screen.getByText(/Welcome/i)).toBeInTheDocument()
    })

    it('should have share room button', async () => {
      renderWithProviders(<RoomLobbyPage />)

      const shareButton = screen.getByTitle(/Share Room/i)
      expect(shareButton).toBeInTheDocument()
    })

    it('should generate correct shareable link with room ID', async () => {
      const user = userEvent.setup()
      renderWithProviders(<RoomLobbyPage />)

      const shareButton = screen.getByTitle(/Share Room/i)
      await user.click(shareButton)

      await waitFor(() => {
        const linkInput = screen.getByDisplayValue(new RegExp(mockRoomId))
        expect(linkInput.value).toContain(`/lobby/${mockRoomId}`)
        expect(linkInput.value).toContain('role=speaker')
      })
    })
  })

  describe('Share Modal', () => {
    it('should open share modal when share button clicked', async () => {
      const user = userEvent.setup()
      renderWithProviders(<RoomLobbyPage />)

      const shareButton = screen.getByTitle(/Share Room/i)
      await user.click(shareButton)

      await waitFor(() => {
        expect(screen.getByText(/Share Room Link/i)).toBeInTheDocument()
      })
    })

    it('should display copy button in share modal', async () => {
      const user = userEvent.setup()
      renderWithProviders(<RoomLobbyPage />)

      const shareButton = screen.getByTitle(/Share Room/i)
      await user.click(shareButton)

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Copy/i })).toBeInTheDocument()
      })
    })

    it('should close modal when close button clicked', async () => {
      const user = userEvent.setup()
      renderWithProviders(<RoomLobbyPage />)

      const shareButton = screen.getByTitle(/Share Room/i)
      await user.click(shareButton)

      await waitFor(() => {
        expect(screen.getByText(/Share Room Link/i)).toBeInTheDocument()
      })

      const closeButton = screen.getByRole('button', { name: /Close/i })
      await user.click(closeButton)

      await waitFor(() => {
        expect(screen.queryByText(/Share Room Link/i)).not.toBeInTheDocument()
      })
    })
  })
})
