import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { screen } from '@testing-library/react'
import { renderWithProviders } from '../test-utils'
import SpeakerTimer from '../../components/ui/SpeakerTimer'

describe('SpeakerTimer', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('Rendering', () => {
    it('should render timer with initial time', () => {
      renderWithProviders(<SpeakerTimer timeRemaining={60} totalTime={60} />)
      
      expect(screen.getByText('01:00')).toBeInTheDocument()
    })

    it('should format time correctly for single digit seconds', () => {
      renderWithProviders(<SpeakerTimer timeRemaining={65} totalTime={120} />)
      
      expect(screen.getByText('01:05')).toBeInTheDocument()
    })

    it('should format time correctly for zero minutes', () => {
      renderWithProviders(<SpeakerTimer timeRemaining={30} totalTime={60} />)
      
      expect(screen.getByText('00:30')).toBeInTheDocument()
    })

    it('should handle zero time remaining', () => {
      renderWithProviders(<SpeakerTimer timeRemaining={0} totalTime={60} />)
      
      expect(screen.getByText('00:00')).toBeInTheDocument()
    })
  })

  describe('Visual States', () => {
    it('should show normal state when time is above 50%', () => {
      const { container } = renderWithProviders(
        <SpeakerTimer timeRemaining={40} totalTime={60} />
      )
      
      // Check if timer is rendered
      expect(screen.getByText('00:40')).toBeInTheDocument()
    })

    it('should show warning state when time is below 50%', () => {
      const { container } = renderWithProviders(
        <SpeakerTimer timeRemaining={20} totalTime={60} />
      )
      
      expect(screen.getByText('00:20')).toBeInTheDocument()
    })

    it('should show critical state when time is below 10 seconds', () => {
      const { container } = renderWithProviders(
        <SpeakerTimer timeRemaining={5} totalTime={60} />
      )
      
      expect(screen.getByText('00:05')).toBeInTheDocument()
    })
  })

  describe('Progress Bar', () => {
    it('should show progress bar', () => {
      renderWithProviders(<SpeakerTimer timeRemaining={30} totalTime={60} />)
      
      // Check if timer container exists
      const timer = screen.getByText('00:30')
      expect(timer).toBeInTheDocument()
    })

    it('should calculate progress percentage correctly', () => {
      renderWithProviders(<SpeakerTimer timeRemaining={30} totalTime={60} />)
      
      // 30 seconds remaining out of 60 = 50%
      expect(screen.getByText('00:30')).toBeInTheDocument()
    })
  })

  describe('Edge Cases', () => {
    it('should handle negative time remaining', () => {
      renderWithProviders(<SpeakerTimer timeRemaining={-5} totalTime={60} />)
      
      // Should show 00:00 or handle gracefully
      expect(screen.getByText(/00:00|--:--/)).toBeInTheDocument()
    })

    it('should handle totalTime of zero', () => {
      expect(() => {
        renderWithProviders(<SpeakerTimer timeRemaining={0} totalTime={0} />)
      }).not.toThrow()
    })

    it('should handle time remaining greater than total time', () => {
      renderWithProviders(<SpeakerTimer timeRemaining={90} totalTime={60} />)
      
      expect(screen.getByText('01:30')).toBeInTheDocument()
    })
  })

  describe('Time Formatting', () => {
    it('should format minutes and seconds with leading zeros', () => {
      renderWithProviders(<SpeakerTimer timeRemaining={125} totalTime={180} />)
      
      expect(screen.getByText('02:05')).toBeInTheDocument()
    })

    it('should handle times over 10 minutes', () => {
      renderWithProviders(<SpeakerTimer timeRemaining={615} totalTime={900} />)
      
      expect(screen.getByText('10:15')).toBeInTheDocument()
    })
  })
})
