import React, { useState, useEffect, useRef } from 'react';
import { Send, MessageCircle, Users } from 'lucide-react';
import { useSocket } from '../../contexts/SocketContext';
import { useAuth } from '../../contexts/AuthContext';

/**
 * ChatPanel Component
 * Turn-based chat interface for roundtable discussions
 */
function ChatPanel({ 
  isActive, 
  currentSpeaker, 
  roomId, 
  round, 
  discussionStarted,
  compact = false 
}) {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const messagesEndRef = useRef(null);
  const { socket } = useSocket();
  const { user } = useAuth();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (!socket) return;

    const handleMessage = (messageData) => {
      console.log('[Chat] Received message:', messageData);
      setMessages(prev => [...prev, messageData]);
    };

    const handleMessageError = (error) => {
      console.error('[Chat] Message error:', error);
      alert(error.error || 'Failed to send message');
      setIsSubmitting(false);
    };

    const handleAiAnalysis = (analysisData) => {
      console.log('[Chat] Received AI analysis:', analysisData);
      setAiAnalysis(analysisData);
      
      // Clear analysis after 10 seconds
      setTimeout(() => {
        setAiAnalysis(null);
      }, 10000);
    };

    const handleRoundComplete = () => {
      // Trigger AI analysis when round completes
      if (socket && roomId) {
        socket.emit('send-round-messages-to-ai', { roomId });
      }
    };

    socket.on('message', handleMessage);
    socket.on('message-error', handleMessageError);
    socket.on('ai-round-analysis', handleAiAnalysis);
    socket.on('round-complete', handleRoundComplete);

    return () => {
      socket.off('message', handleMessage);
      socket.off('message-error', handleMessageError);
      socket.off('ai-round-analysis', handleAiAnalysis);
      socket.off('round-complete', handleRoundComplete);
    };
  }, [socket, roomId]);

  // Clear messages when round changes
  useEffect(() => {
    setMessages([]);
    setAiAnalysis(null);
  }, [round]);

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!message.trim() || !socket || isSubmitting) return;
    
    if (!isActive) {
      alert("It's not your turn to speak!");
      return;
    }

    setIsSubmitting(true);
    
    // Add message optimistically
    const tempMessage = {
      id: `temp-${Date.now()}`,
      userId: user?.id,
      anonymousName: user?.anonymousName || 'You',
      message: message.trim(),
      timestamp: new Date().toISOString(),
      round,
      turnOrder: currentSpeaker?.turnOrder || 0
    };
    
    setMessages(prev => [...prev, tempMessage]);
    
    // Send to server
    socket.emit('message', message.trim());
    
    setMessage('');
    setIsSubmitting(false);
  };

  const isCurrentUserSpeaking = currentSpeaker && currentSpeaker.id === user?.id;

  if (compact) {
    return (
      <div className="bg-white border border-gray-200 rounded-lg p-3">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <MessageCircle className="w-4 h-4 text-blue-600" />
            <span className="text-sm font-medium text-gray-700">
              Round {round} Chat
            </span>
          </div>
          <div className="text-xs text-gray-500">
            {messages.length} messages
          </div>
        </div>
        
        {messages.length > 0 && (
          <div className="max-h-32 overflow-y-auto mb-2 space-y-1">
            {messages.slice(-3).map((msg) => (
              <div key={msg.id} className="text-xs">
                <span className="font-medium text-gray-700">
                  {msg.anonymousName}:
                </span>
                <span className="text-gray-600 ml-1">
                  {msg.message}
                </span>
              </div>
            ))}
          </div>
        )}
        
        {isCurrentUserSpeaking && (
          <form onSubmit={handleSubmit} className="flex space-x-1">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Your message..."
              className="flex-1 text-xs px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
              disabled={isSubmitting}
            />
            <button
              type="submit"
              disabled={!message.trim() || isSubmitting}
              className="px-2 py-1 bg-blue-600 text-white rounded text-xs hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send className="w-3 h-3" />
            </button>
          </form>
        )}
      </div>
    );
  }

  return (
    <div className="bg-white border-2 border-blue-200 rounded-lg shadow-sm flex flex-col h-96">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center space-x-2">
          <MessageCircle className="w-5 h-5 text-blue-600" />
          <h3 className="text-sm font-semibold text-gray-900">
            Round {round} Discussion
          </h3>
        </div>
        <div className="flex items-center space-x-2 text-xs text-gray-500">
          <Users className="w-4 h-4" />
          <span>{messages.length} messages</span>
        </div>
      </div>

      {/* AI Analysis Banner */}
      {aiAnalysis && (
        <div className="bg-blue-50 border-b border-blue-200 p-3">
          <div className="flex items-start space-x-2">
            <div className="text-blue-600">🤖</div>
            <div>
              <p className="text-sm font-medium text-blue-900">AI Analysis</p>
              <p className="text-xs text-blue-800 mt-1">{aiAnalysis.analysis}</p>
            </div>
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {!discussionStarted ? (
          <div className="text-center text-gray-500 text-sm py-8">
            <MessageCircle className="w-8 h-8 mx-auto mb-2 text-gray-400" />
            <p>Discussion hasn't started yet</p>
            <p className="text-xs mt-1">Messages will appear here during turns</p>
          </div>
        ) : messages.length === 0 ? (
          <div className="text-center text-gray-500 text-sm py-8">
            <MessageCircle className="w-8 h-8 mx-auto mb-2 text-gray-400" />
            <p>No messages yet this round</p>
            <p className="text-xs mt-1">Participants can chat during their turns</p>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${
                msg.userId === user?.id ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-3 py-2 rounded-lg ${
                  msg.userId === user?.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-900'
                }`}
              >
                <div className="flex items-center space-x-2 mb-1">
                  <span className="text-xs font-medium opacity-75">
                    {msg.anonymousName}
                  </span>
                  <span className="text-xs opacity-50">
                    {new Date(msg.timestamp).toLocaleTimeString([], {
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </span>
                </div>
                <p className="text-sm">{msg.message}</p>
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-200 p-4">
        {!discussionStarted ? (
          <div className="text-center text-gray-500 text-sm">
            Wait for discussion to start
          </div>
        ) : !isCurrentUserSpeaking ? (
          <div className="text-center text-gray-500 text-sm">
            Wait for your turn to speak
            {currentSpeaker && (
              <div className="mt-1">
                <span className="font-medium">{currentSpeaker.anonymousName}</span> is speaking
              </div>
            )}
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="flex space-x-2">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isSubmitting}
            />
            <button
              type="submit"
              disabled={!message.trim() || isSubmitting}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        )}
      </div>
    </div>
  );
}

export default ChatPanel;