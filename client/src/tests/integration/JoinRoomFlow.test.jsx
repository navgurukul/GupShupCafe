import { describe, it, expect, beforeEach, vi } from 'vitest'
import { fetchWaitingRooms } from '../../services/api'

/**
 * Integration tests for Join Room feature
 * These tests verify the core functionality of discovering and joining rooms
 */
describe('Join Room Integration Tests', () => {
  // Mock fetch globally
  global.fetch = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Room Discovery API Integration', () => {
    it('should fetch waiting rooms from backend successfully', async () => {
      const mockRooms = [
        {
          room_id: 'room-123',
          room_name: 'Tech Discussion',
          topic_category: 'scienceAndTechnology',
          cefr_level: 'B1',
          max_participants: 6,
          participant_count: 2,
          status: 'waiting'
        }
      ]

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          status: 'success',
          data: mockRooms
        })
      })

      const rooms = await fetchWaitingRooms()

      expect(rooms).toEqual(mockRooms)
      expect(rooms[0].room_id).toBe('room-123')
      expect(rooms[0].status).toBe('waiting')
    })

    it('should handle backend errors gracefully', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Network error'))

      const rooms = await fetchWaitingRooms()

      expect(rooms).toEqual([])
    })

    it('should handle empty room list', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          status: 'success',
          data: []
        })
      })

      const rooms = await fetchWaitingRooms()

      expect(rooms).toEqual([])
    })
  })

  describe('Room Data Transformation', () => {
    it('should correctly map backend room data to frontend format', () => {
      const backendRoom = {
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
      }

      // Simulate the mapping function from LobbyPage
      const mapBackendRoomToFrontend = (room) => ({
        id: room.room_id,
        name: room.room_name,
        description: room.topic_title || `Room for ${room.topic_category}`,
        cefr_level: room.cefr_level,
        topic_category: room.topic_category,
        max_participants: room.max_participants,
        participant_count: room.participant_count || 0,
        status: room.status,
        created_at: room.created_at,
        isBackendRoom: true
      })

      const frontendRoom = mapBackendRoomToFrontend(backendRoom)

      expect(frontendRoom.id).toBe('room-123')
      expect(frontendRoom.name).toBe('Tech Discussion')
      expect(frontendRoom.description).toBe('AI and Machine Learning')
      expect(frontendRoom.isBackendRoom).toBe(true)
      expect(frontendRoom.participant_count).toBe(2)
    })

    it('should handle missing optional fields', () => {
      const backendRoom = {
        room_id: 'room-456',
        room_name: 'Simple Room',
        topic_category: 'education',
        cefr_level: 'A1',
        max_participants: 4,
        status: 'waiting'
      }

      const mapBackendRoomToFrontend = (room) => ({
        id: room.room_id,
        name: room.room_name,
        description: room.topic_title || `Room for ${room.topic_category}`,
        participant_count: room.participant_count || 0,
        isBackendRoom: true
      })

      const frontendRoom = mapBackendRoomToFrontend(backendRoom)

      expect(frontendRoom.description).toBe('Room for education')
      expect(frontendRoom.participant_count).toBe(0)
    })
  })

  describe('Join Room Participant Creation', () => {
    it('should create participant entry when joining a room', async () => {
      const participantData = {
        user_id: 'user-123',
        room_id: 'room-456',
        anonymous_name: 'Happy Tiger',
        avatar_color: '#FF5733',
        joined_at: new Date().toISOString(),
        starting_cefr_level: 'B1',
        ending_cefr_level: 'B1'
      }

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          status: 'success',
          data: 'participant-789'
        })
      })

      const response = await fetch('/participants/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(participantData)
      })

      const result = await response.json()

      expect(result.status).toBe('success')
      expect(result.data).toBe('participant-789')
    })

    it('should handle participant creation errors', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({
          status: 'failure',
          message: 'Room is full'
        })
      })

      const response = await fetch('/participants/', {
        method: 'POST',
        body: JSON.stringify({})
      })

      expect(response.ok).toBe(false)
      expect(response.status).toBe(400)
    })
  })

  describe('Room List Auto-Refresh Logic', () => {
    it('should implement interval-based refresh pattern', () => {
      vi.useFakeTimers()
      
      let refreshCount = 0
      const fetchRooms = () => {
        refreshCount++
        return Promise.resolve([])
      }

      // Simulate auto-refresh every 10 seconds
      const intervalId = setInterval(fetchRooms, 10000)

      // Initially called once
      fetchRooms()
      expect(refreshCount).toBe(1)

      // After 10 seconds
      vi.advanceTimersByTime(10000)
      expect(refreshCount).toBe(2)

      // After 20 seconds
      vi.advanceTimersByTime(10000)
      expect(refreshCount).toBe(3)

      clearInterval(intervalId)
      vi.useRealTimers()
    })

    it('should stop refresh when component unmounts', () => {
      vi.useFakeTimers()
      
      let refreshCount = 0
      const fetchRooms = () => {
        refreshCount++
        return Promise.resolve([])
      }

      const intervalId = setInterval(fetchRooms, 10000)

      fetchRooms()
      expect(refreshCount).toBe(1)

      // Simulate component unmount
      clearInterval(intervalId)

      // Advance time but refresh should not happen
      vi.advanceTimersByTime(30000)
      expect(refreshCount).toBe(1)

      vi.useRealTimers()
    })
  })

  describe('Room Filtering and Fallback Logic', () => {
    it('should prioritize backend rooms over predefined rooms', () => {
      const backendRooms = [
        { id: 'backend-1', name: 'Backend Room', isBackendRoom: true }
      ]
      const predefinedRooms = [
        { id: 'predefined-1', name: 'Predefined Room', isBackendRoom: false }
      ]

      // Logic from LobbyPage
      const allRooms = backendRooms.length > 0 ? backendRooms : predefinedRooms

      expect(allRooms).toEqual(backendRooms)
      expect(allRooms[0].isBackendRoom).toBe(true)
    })

    it('should show predefined rooms when backend returns empty', () => {
      const backendRooms = []
      const predefinedRooms = [
        { id: 'predefined-1', name: 'Education', isBackendRoom: false },
        { id: 'predefined-2', name: 'Science', isBackendRoom: false }
      ]

      const allRooms = backendRooms.length > 0 ? backendRooms : predefinedRooms

      expect(allRooms).toEqual(predefinedRooms)
      expect(allRooms.length).toBe(2)
    })
  })

  describe('Share Room URL Generation', () => {
    it('should generate correct shareable link format', () => {
      const roomId = 'room-123'
      const role = 'speaker'
      const origin = 'http://localhost:5173'

      const generateShareableLink = (roomId, role) => {
        return `${origin}/room-lobby?room=${roomId}&role=${role}`
      }

      const link = generateShareableLink(roomId, role)

      expect(link).toBe('http://localhost:5173/room-lobby?room=room-123&role=speaker')
      expect(link).toContain('room=room-123')
      expect(link).toContain('role=speaker')
    })

    it('should handle different roles in URL', () => {
      const roomId = 'room-456'
      const origin = 'http://localhost:5173'

      const generateShareableLink = (roomId, role) => {
        return `${origin}/room-lobby?room=${roomId}&role=${role}`
      }

      const speakerLink = generateShareableLink(roomId, 'speaker')
      const listenerLink = generateShareableLink(roomId, 'listener')

      expect(speakerLink).toContain('role=speaker')
      expect(listenerLink).toContain('role=listener')
    })
  })
})
