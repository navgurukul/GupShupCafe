import { describe, it, expect, beforeEach, vi } from 'vitest'
import { screen } from '@testing-library/react'
import { renderWithProviders } from '../test-utils'
import AudioLevelBar from '../../components/ui/AudioLevelBar'

describe('AudioLevelBar', () => {
  let mockAudioContext
  let mockAnalyser
  let mockMediaStreamSource
  let mockStream

  beforeEach(() => {
    // Mock AnalyserNode
    mockAnalyser = {
      connect: vi.fn(),
      disconnect: vi.fn(),
      fftSize: 2048,
      frequencyBinCount: 1024,
      getByteFrequencyData: vi.fn((dataArray) => {
        // Simulate some audio data
        for (let i = 0; i < dataArray.length; i++) {
          dataArray[i] = Math.random() * 255
        }
      })
    }

    // Mock MediaStreamSource
    mockMediaStreamSource = {
      connect: vi.fn(),
      disconnect: vi.fn()
    }

    // Mock AudioContext
    mockAudioContext = {
      createAnalyser: vi.fn(() => mockAnalyser),
      createMediaStreamSource: vi.fn(() => mockMediaStreamSource),
      close: vi.fn(),
      resume: vi.fn()
    }

    global.AudioContext = vi.fn(() => mockAudioContext)

    // Mock MediaStream
    mockStream = {
      getTracks: vi.fn(() => [{ id: 'test-track', enabled: true }]),
      id: 'test-stream'
    }
  })

  describe('Rendering', () => {
    it('should render without crashing', () => {
      const { container } = renderWithProviders(<AudioLevelBar stream={null} />)
      expect(container).toBeTruthy()
    })

    it('should render with label when showLabel is true', () => {
      renderWithProviders(<AudioLevelBar stream={null} showLabel={true} />)
      expect(screen.getByText(/Audio Level/i)).toBeInTheDocument()
    })

    it('should not render label when showLabel is false', () => {
      renderWithProviders(<AudioLevelBar stream={null} showLabel={false} />)
      expect(screen.queryByText(/Audio Level/i)).not.toBeInTheDocument()
    })
  })

  describe('Audio Stream Processing', () => {
    it('should initialize AudioContext when stream is provided', () => {
      renderWithProviders(<AudioLevelBar stream={mockStream} />)

      expect(global.AudioContext).toHaveBeenCalled()
      expect(mockAudioContext.createAnalyser).toHaveBeenCalled()
      expect(mockAudioContext.createMediaStreamSource).toHaveBeenCalledWith(mockStream)
    })

    it('should connect audio nodes correctly', () => {
      renderWithProviders(<AudioLevelBar stream={mockStream} />)

      expect(mockMediaStreamSource.connect).toHaveBeenCalledWith(mockAnalyser)
    })

    it('should handle null stream gracefully', () => {
      expect(() => {
        renderWithProviders(<AudioLevelBar stream={null} />)
      }).not.toThrow()
    })
  })

  describe('Visual Feedback', () => {
    it('should display audio level bar component', () => {
      const { container } = renderWithProviders(<AudioLevelBar stream={mockStream} />)
      
      expect(container).toBeTruthy()
    })

    it('should render correctly with stream', async () => {
      const { container } = renderWithProviders(<AudioLevelBar stream={mockStream} />)
      
      expect(container.firstChild).toBeTruthy()
    })
  })

  describe('Cleanup', () => {
    it('should cleanup audio context on unmount', () => {
      const { unmount } = renderWithProviders(<AudioLevelBar stream={mockStream} />)

      unmount()

      expect(mockMediaStreamSource.disconnect).toHaveBeenCalled()
      expect(mockAudioContext.close).toHaveBeenCalled()
    })

    it('should cleanup when stream changes', () => {
      const { rerender } = renderWithProviders(<AudioLevelBar stream={mockStream} />)

      const newStream = {
        getTracks: vi.fn(() => [{ id: 'new-track', enabled: true }]),
        id: 'new-stream'
      }

      rerender(<AudioLevelBar stream={newStream} />)

      // Old context should be cleaned up
      expect(mockMediaStreamSource.disconnect).toHaveBeenCalled()
    })
  })
})
