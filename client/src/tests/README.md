# Test Documentation

## Overview
This directory contains comprehensive regression tests for the GupShupCafe frontend application covering core features.

## Test Structure

### `/tests/contexts/`
Tests for React context providers that manage application state:
- **AuthContext.test.jsx** - Authentication state management, login/logout, session persistence
- **AudioContext.test.jsx** - Audio stream management, microphone permissions, mute/unmute functionality

### `/tests/pages/`
Tests for main page components:
- **LoginPage.test.jsx** - Login form, validation, anonymous name suggestions, form submission

### `/tests/components/`
Tests for reusable UI components:
- **LiveAudioLevelBar.test.jsx** - Audio level visualization
- **ProtectedRoute.test.jsx** - Route protection based on authentication
- **SpeakerTimer.test.jsx** - Timer display and formatting

### `/tests/integration/`
End-to-end integration tests:
- **LoginFlow.test.jsx** - Complete user journey from login to navigation

## Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run with coverage
npm test:coverage

# Run specific test file
npm test -- LoginPage.test.jsx
```

## Test Coverage

### Authentication Flow
- ✅ Login form validation
- ✅ Input error handling
- ✅ Anonymous name generation
- ✅ Session persistence
- ✅ Protected route access

### Audio Features
- ✅ Microphone permission requests
- ✅ Audio stream initialization
- ✅ Mute/unmute functionality
- ✅ WebRTC support detection
- ✅ Audio level monitoring
- ✅ Resource cleanup

### Components
- ✅ Live audio level bar rendering
- ✅ Speaker timer display
- ✅ Protected route guards
- ✅ Form field interactions

### Integration Tests
- ✅ Complete login flow
- ✅ Form validation workflow
- ✅ Session persistence across reloads
- ✅ Incremental error clearing

## Writing New Tests

### Test File Template

```javascript
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { renderWithProviders } from '../test-utils'
import YourComponent from '../../components/YourComponent'

describe('YourComponent', () => {
  beforeEach(() => {
    // Setup code
  })

  describe('Feature Group', () => {
    it('should do something specific', async () => {
      // Arrange
      const user = userEvent.setup()
      renderWithProviders(<YourComponent />)

      // Act
      await user.click(screen.getByRole('button'))

      // Assert
      await waitFor(() => {
        expect(screen.getByText(/expected/i)).toBeInTheDocument()
      })
    })
  })
})
```

## Test Utilities

### `renderWithProviders()`
Wraps components with all necessary context providers (Auth, Socket, Audio) and Router.

```javascript
import { renderWithProviders } from '../test-utils'

renderWithProviders(<YourComponent />)
```

### Mock Helpers
- `createMockUser()` - Creates a mock user object
- `createMockAnonymousName()` - Generates a random anonymous name
- `mockLocalStorage()` - Provides localStorage mock
- `waitForAsync()` - Helper for async operations

## Continuous Integration

Tests are automatically run on:
- Pull requests
- Commits to main branch
- Pre-deployment checks

## Best Practices

1. **Test user behavior, not implementation details**
2. **Use accessible queries** (getByRole, getByLabelText)
3. **Test error states and edge cases**
4. **Keep tests independent and isolated**
5. **Mock external dependencies** (WebRTC, localStorage, etc.)
6. **Clean up after tests** (unmount, restore mocks)

## Known Issues

- Some tests may need adjustments based on actual component implementation
- WebRTC APIs are mocked for testing environment
- Socket connections are mocked to avoid real network calls

## Future Enhancements

- Add E2E tests with Playwright
- Increase coverage for LobbyPage and RoundtablePage
- Add visual regression tests
- Performance testing for audio processing
- Accessibility (a11y) automated tests
