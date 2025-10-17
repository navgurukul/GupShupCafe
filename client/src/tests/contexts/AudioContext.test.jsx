import { describe, it, expect, beforeEach, vi } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { AudioProvider, useAudio } from '../../contexts/AudioContext'

describe('AudioContext', () => {
  let mockMediaStream
  let mockGetUserMedia

  beforeEach(() => {
    // Create mock media stream
    mockMediaStream = {
      getTracks: vi.fn(() => [{
        stop: vi.fn(),
        enabled: true,
        id: 'test-track-1'
      }]),
      getAudioTracks: vi.fn(() => [{
        stop: vi.fn(),
        enabled: true,
        id: 'audio-track-1'
      }]),
      id: 'test-stream-1'
    }

    // Mock getUserMedia
    mockGetUserMedia = vi.fn(() => Promise.resolve(mockMediaStream))
    global.navigator.mediaDevices.getUserMedia = mockGetUserMedia
  })

  describe('Initial State', () => {
    it('should initialize with default audio state', () => {
      const { result } = renderHook(() => useAudio(), {
        wrapper: AudioProvider
      })

      expect(result.current.audioEnabled).toBe(false)
      expect(result.current.audioStream).toBeNull()
      expect(result.current.micPermission).toBe('prompt')
      expect(result.current.isMuted).toBe(false)
    })

    it('should detect WebRTC support', () => {
      const { result } = renderHook(() => useAudio(), {
        wrapper: AudioProvider
      })

      expect(result.current.isWebRTCSupported).toBe(true)
    })
  })

  describe('Microphone Access', () => {
    it('should request microphone access successfully', async () => {
      const { result } = renderHook(() => useAudio(), {
        wrapper: AudioProvider
      })

      await act(async () => {
        await result.current.requestMicrophoneAccess()
      })

      await waitFor(() => {
        expect(mockGetUserMedia).toHaveBeenCalledWith({
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true
          }
        })
        expect(result.current.audioEnabled).toBe(true)
        expect(result.current.audioStream).toBe(mockMediaStream)
        expect(result.current.micPermission).toBe('granted')
      })
    })

    it('should handle microphone access denial', async () => {
      mockGetUserMedia.mockRejectedValueOnce(
        new DOMException('Permission denied', 'NotAllowedError')
      )

      const { result } = renderHook(() => useAudio(), {
        wrapper: AudioProvider
      })

      await act(async () => {
        await result.current.requestMicrophoneAccess()
      })

      await waitFor(() => {
        expect(result.current.audioEnabled).toBe(false)
        expect(result.current.audioStream).toBeNull()
        expect(result.current.micPermission).toBe('denied')
      })
    })

    it('should handle microphone not found error', async () => {
      mockGetUserMedia.mockRejectedValueOnce(
        new DOMException('Device not found', 'NotFoundError')
      )

      const { result } = renderHook(() => useAudio(), {
        wrapper: AudioProvider
      })

      await act(async () => {
        await result.current.requestMicrophoneAccess()
      })

      await waitFor(() => {
        expect(result.current.audioEnabled).toBe(false)
        expect(result.current.micPermission).toBe('denied')
      })
    })
  })

  describe('Mute/Unmute Functionality', () => {
    it('should mute microphone', async () => {
      const { result } = renderHook(() => useAudio(), {
        wrapper: AudioProvider
      })

      // First get microphone access
      await act(async () => {
        await result.current.requestMicrophoneAccess()
      })

      await waitFor(() => {
        expect(result.current.audioEnabled).toBe(true)
      })

      // Then mute
      act(() => {
        result.current.toggleMute()
      })

      await waitFor(() => {
        expect(result.current.isMuted).toBe(true)
        const tracks = mockMediaStream.getAudioTracks()
        tracks.forEach(track => {
          expect(track.enabled).toBe(false)
        })
      })
    })

    it('should unmute microphone', async () => {
      const { result } = renderHook(() => useAudio(), {
        wrapper: AudioProvider
      })

      // Get microphone access and mute
      await act(async () => {
        await result.current.requestMicrophoneAccess()
      })

      act(() => {
        result.current.toggleMute()
      })

      await waitFor(() => {
        expect(result.current.isMuted).toBe(true)
      })

      // Unmute
      act(() => {
        result.current.toggleMute()
      })

      await waitFor(() => {
        expect(result.current.isMuted).toBe(false)
      })
    })
  })

  describe('Stop Audio Stream', () => {
    it('should stop audio stream and release microphone', async () => {
      const { result } = renderHook(() => useAudio(), {
        wrapper: AudioProvider
      })

      await act(async () => {
        await result.current.requestMicrophoneAccess()
      })

      await waitFor(() => {
        expect(result.current.audioEnabled).toBe(true)
      })

      act(() => {
        result.current.stopAudioStream()
      })

      await waitFor(() => {
        expect(result.current.audioEnabled).toBe(false)
        expect(result.current.audioStream).toBeNull()
        const tracks = mockMediaStream.getTracks()
        tracks.forEach(track => {
          expect(track.stop).toHaveBeenCalled()
        })
      })
    })

    it('should handle stopping when no stream exists', () => {
      const { result } = renderHook(() => useAudio(), {
        wrapper: AudioProvider
      })

      expect(() => {
        act(() => {
          result.current.stopAudioStream()
        })
      }).not.toThrow()

      expect(result.current.audioStream).toBeNull()
    })
  })

  describe('User Role Management', () => {
    it('should update user role', () => {
      const { result } = renderHook(() => useAudio(), {
        wrapper: AudioProvider
      })

      act(() => {
        result.current.updateUserRole('speaker')
      })

      expect(result.current.userRole).toBe('speaker')

      act(() => {
        result.current.updateUserRole('listener')
      })

      expect(result.current.userRole).toBe('listener')
    })
  })

  describe('WebRTC Support Detection', () => {
    it('should detect when WebRTC is not supported', () => {
      const originalGetUserMedia = global.navigator.mediaDevices.getUserMedia
      delete global.navigator.mediaDevices.getUserMedia

      const { result } = renderHook(() => useAudio(), {
        wrapper: AudioProvider
      })

      expect(result.current.isWebRTCSupported).toBe(false)

      // Restore
      global.navigator.mediaDevices.getUserMedia = originalGetUserMedia
    })
  })

  describe('Edge Cases', () => {
    it('should handle multiple microphone access requests', async () => {
      const { result } = renderHook(() => useAudio(), {
        wrapper: AudioProvider
      })

      await act(async () => {
        await result.current.requestMicrophoneAccess()
        await result.current.requestMicrophoneAccess()
      })

      // Should only call getUserMedia once or handle gracefully
      expect(result.current.audioEnabled).toBe(true)
    })

    it('should clean up on unmount', async () => {
      const { result, unmount } = renderHook(() => useAudio(), {
        wrapper: AudioProvider
      })

      await act(async () => {
        await result.current.requestMicrophoneAccess()
      })

      await waitFor(() => {
        expect(result.current.audioEnabled).toBe(true)
      })

      unmount()

      // Tracks should be stopped on unmount
      const tracks = mockMediaStream.getTracks()
      tracks.forEach(track => {
        expect(track.stop).toHaveBeenCalled()
      })
    })
  })
})
