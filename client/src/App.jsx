import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { SocketProvider } from './contexts/SocketContext'
import { AuthProvider } from './contexts/AuthContext'
import { AudioProvider } from './contexts/AudioContext'
import LoginPage from './pages/LoginPage'
import SignupPage from './pages/SignupPage'
import LobbyPage from './pages/LobbyPage'
import RoundtablePage from './pages/RoundtablePage'
import AudioTestPage from './pages/AudioTestPage'
import BroadcastTestPage from './pages/BroadcastTestPage'
import SpeechRecognitionTest from './pages/SpeechRecognitionTest'
import ProtectedRoute from './components/common/ProtectedRoute'

/**
 * Main App Component
 * Sets up routing and context providers for the entire application
 */
function App() {
  return (
    <Router>
      <AuthProvider>
        <SocketProvider>
          <AudioProvider>
            <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
              <Routes>
                {/* Public Routes */}
                <Route path="/" element={<LoginPage />} />
                <Route path="/signup" element={<SignupPage />} />
                
                {/* Protected Routes - Require Authentication */}
                <Route path="/lobby" element={
                  <ProtectedRoute>
                    <LobbyPage />
                  </ProtectedRoute>
                } />
                
                <Route path="/room-lobby" element={
                  <ProtectedRoute>
                    <LobbyPage />
                  </ProtectedRoute>
                } />
                
                <Route path="/roundtable" element={
                  <ProtectedRoute>
                    <RoundtablePage />
                  </ProtectedRoute>
                } />
                
                {/* Audio Test Route - For debugging audio issues */}
                <Route path="/audio-test" element={<AudioTestPage />} />
                
                {/* Broadcast Test Route - Simple broadcast audio test */}
                <Route path="/broadcast-test" element={<BroadcastTestPage />} />

                 {/* Broadcast Test Route - Simple broadcast audio test */}
                <Route path="/zoe" element={<SpeechRecognitionTest />} />
                
                {/* Fallback Route */}
                <Route path="*" element={<LoginPage />} />
              </Routes>
            </div>
          </AudioProvider>
        </SocketProvider>
      </AuthProvider>
    </Router>
  )
}

export default App
