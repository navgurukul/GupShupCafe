import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { fetchWaitingRooms, fetchActiveRooms, createRoom } from '../../services/api'

// Mock fetch globally
global.fetch = vi.fn()

describe('API Service - Room Functions', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.resetAllMocks()
  })

  describe('fetchWaitingRooms', () => {
    it('should fetch waiting rooms successfully', async () => {
      const mockRooms = [
        {
          room_id: 'room-123',
          room_name: 'Tech Discussion',
          topic_category: 'scienceAndTechnology',
          cefr_level: 'B1',
          max_participants: 6,
          participant_count: 2,
          status: 'waiting',
          created_at: '2025-10-19T09:00:00Z'
        },
        {
          room_id: 'room-456',
          room_name: 'Literature Chat',
          topic_category: 'literature',
          cefr_level: 'C1',
          max_participants: 4,
          participant_count: 1,
          status: 'waiting',
          created_at: '2025-10-19T09:15:00Z'
        }
      ]

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          status: 'success',
          data: mockRooms,
          message: "Rooms listed for status='waiting'"
        })
      })

      const result = await fetchWaitingRooms()

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/rooms/waiting'),
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          })
        })
      )
      expect(result).toEqual(mockRooms)
      expect(result).toHaveLength(2)
      expect(result[0].room_id).toBe('room-123')
      expect(result[1].room_id).toBe('room-456')
    })

    it('should return empty array when no waiting rooms exist', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          status: 'success',
          data: [],
          message: "Rooms listed for status='waiting'"
        })
      })

      const result = await fetchWaitingRooms()

      expect(result).toEqual([])
      expect(result).toHaveLength(0)
    })

    it('should return empty array on API failure status', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          status: 'failure',
          data: [],
          message: 'Failed to list rooms by status'
        })
      })

      const result = await fetchWaitingRooms()

      expect(result).toEqual([])
    })

    it('should return empty array on network error', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Network error'))

      const result = await fetchWaitingRooms()

      expect(result).toEqual([])
    })

    it('should handle malformed response gracefully', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          status: 'success',
          // Missing 'data' field
          message: "Rooms listed"
        })
      })

      const result = await fetchWaitingRooms()

      expect(result).toEqual([])
    })

    it('should handle HTTP error responses', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error'
      })

      const result = await fetchWaitingRooms()

      expect(result).toEqual([])
    })
  })

  describe('fetchActiveRooms', () => {
    it('should fetch active rooms successfully', async () => {
      const mockRooms = [
        {
          room_id: 'room-789',
          room_name: 'Active Discussion',
          status: 'in_progress'
        }
      ]

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          rooms: mockRooms
        })
      })

      const result = await fetchActiveRooms()

      expect(result).toEqual(mockRooms)
    })

    it('should return empty array on error', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Network error'))

      const result = await fetchActiveRooms()

      expect(result).toEqual([])
    })
  })

  describe('createRoom', () => {
    it('should create a room successfully', async () => {
      const roomConfig = {
        room_name: 'New Discussion',
        topic_category: 'education',
        cefr_level: 'B2',
        max_participants: 5
      }

      const mockResponse = {
        data: {
          room_id: 'room-new-123',
          ...roomConfig
        }
      }

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      })

      const result = await createRoom(roomConfig)

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/rooms'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(roomConfig)
        })
      )
      expect(result).toEqual(mockResponse.data)
    })

    it('should handle room creation error', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Failed to create room'))

      await expect(createRoom({})).rejects.toThrow()
    })
  })
})
