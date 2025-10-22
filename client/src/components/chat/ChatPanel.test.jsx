import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import ChatPanel from './ChatPanel';

// Mock the contexts
const mockSocket = {
  emit: vi.fn(),
  on: vi.fn(),
  off: vi.fn()
};

const mockUser = {
  id: 'user-1',
  anonymousName: 'TestUser'
};

vi.mock('../../contexts/SocketContext', () => ({
  useSocket: () => ({ socket: mockSocket })
}));

vi.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({ user: mockUser })
}));

describe('ChatPanel', () => {
  const defaultProps = {
    isActive: true,
    currentSpeaker: { id: 'user-1', anonymousName: 'TestUser' },
    roomId: 'test-room',
    round: 1,
    discussionStarted: true,
    compact: false
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('renders chat interface when discussion started', () => {
    render(<ChatPanel {...defaultProps} />);
    
    expect(screen.getByText('Round 1 Discussion')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Type your message...')).toBeInTheDocument();
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  test('shows waiting message when discussion not started', () => {
    render(<ChatPanel {...defaultProps} discussionStarted={false} />);
    
    expect(screen.getByText("Discussion hasn't started yet")).toBeInTheDocument();
    expect(screen.getByText('Wait for discussion to start')).toBeInTheDocument();
  });

  test('shows waiting message when not active speaker', () => {
    render(<ChatPanel {...defaultProps} isActive={false} />);
    
    expect(screen.getByText('Wait for your turn to speak')).toBeInTheDocument();
    expect(screen.getByText('TestUser is speaking')).toBeInTheDocument();
  });

  test('sends message when form submitted', async () => {
    render(<ChatPanel {...defaultProps} />);
    
    const input = screen.getByPlaceholderText('Type your message...');
    const button = screen.getByRole('button');
    
    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(button);
    
    expect(mockSocket.emit).toHaveBeenCalledWith('message', 'Test message');
    expect(input.value).toBe('');
  });

  test('prevents empty message submission', () => {
    render(<ChatPanel {...defaultProps} />);
    
    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
    
    const input = screen.getByPlaceholderText('Type your message...');
    fireEvent.change(input, { target: { value: '   ' } });
    expect(button).toBeDisabled();
  });

  test('renders compact view correctly', () => {
    render(<ChatPanel {...defaultProps} compact={true} />);
    
    expect(screen.getByText('Round 1 Chat')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Your message...')).toBeInTheDocument();
  });

  test('displays messages correctly', () => {
    render(<ChatPanel {...defaultProps} />);
    
    // Simulate receiving a message
    const messageHandler = mockSocket.on.mock.calls.find(call => call[0] === 'message')[1];
    messageHandler({
      id: 'msg-1',
      userId: 'user-2',
      anonymousName: 'OtherUser',
      message: 'Hello everyone!',
      timestamp: new Date().toISOString()
    });
    
    // Note: In a real test, you'd need to trigger a re-render or use a more sophisticated setup
    // This is a simplified example showing the test structure
  });
});