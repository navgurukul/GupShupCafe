import React, { createContext, useContext, useState, useEffect, useRef } from "react";
import { ZoeTTS } from "@zoe-ng/tts";
import { useSocket } from "./SocketContext";

/**
 * TTS Context for managing text-to-speech functionality
 * Handles facilitator agent speech and other TTS needs
 */

const TTSContext = createContext();

/**
 * TTSProvider Component
 * Manages TTS state and functionality using @zoe-ng/tts
 */
export function TTSProvider({ children }) {
  const { socket } = useSocket();
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [currentText, setCurrentText] = useState("");
  const [isEnabled, setIsEnabled] = useState(true);
  const [volume, setVolume] = useState(1.0);
  const ttsRef = useRef(null);

  // Initialize TTS instance
  useEffect(() => {
    try {
      ttsRef.current = new ZoeTTS();
      console.log("[TTS] Zoe TTS initialized successfully");
    } catch (error) {
      console.error("[TTS] Error initializing Zoe TTS:", error);
    }
  }, []);

  // Listen for facilitator-speaking events from socket
  useEffect(() => {
    if (!socket) return;

    const handleFacilitatorSpeaking = async (data) => {
      try {
        const { text, timestamp } = data;
        console.log("[TTS] Facilitator speaking:", text);
        
        if (isEnabled && text && text.trim()) {
          await speakText(text, { isFacilitator: true });
        }
      } catch (error) {
        console.error("[TTS] Error handling facilitator speech:", error);
      }
    };

    socket.on("facilitator-speaking", handleFacilitatorSpeaking);

    return () => {
      socket.off("facilitator-speaking", handleFacilitatorSpeaking);
    };
  }, [socket, isEnabled]);

  /**
   * Speak text using TTS
   * @param {string} text - Text to speak
   * @param {object} options - Speaking options
   */
  const speakText = async (text, options = {}) => {
    if (!ttsRef.current || !text || !text.trim()) {
      console.warn("[TTS] Cannot speak: no TTS instance or empty text");
      return;
    }

    if (isSpeaking) {
      console.log("[TTS] Already speaking, stopping current speech");
      await stopSpeaking();
    }

    try {
      setIsSpeaking(true);
      setCurrentText(text);

      console.log(`[TTS] Speaking${options.isFacilitator ? ' (Facilitator)' : ''}: ${text.substring(0, 50)}...`);
      
      // Configure TTS options if needed
      // Note: @zoe-ng/tts may have different configuration options
      // Check the package documentation for available settings
      
      await ttsRef.current.speak(text);
      
      console.log("[TTS] Speech completed");
    } catch (error) {
      console.error("[TTS] Error during speech:", error);
    } finally {
      setIsSpeaking(false);
      setCurrentText("");
    }
  };

  /**
   * Stop current speech
   */
  const stopSpeaking = async () => {
    if (!ttsRef.current) return;

    try {
      // Check if ZoeTTS has a stop method
      if (typeof ttsRef.current.stop === 'function') {
        await ttsRef.current.stop();
      } else if (typeof ttsRef.current.cancel === 'function') {
        await ttsRef.current.cancel();
      }
      
      setIsSpeaking(false);
      setCurrentText("");
      console.log("[TTS] Speech stopped");
    } catch (error) {
      console.error("[TTS] Error stopping speech:", error);
    }
  };

  /**
   * Toggle TTS enabled/disabled
   */
  const toggleEnabled = () => {
    const newEnabled = !isEnabled;
    setIsEnabled(newEnabled);
    
    if (!newEnabled && isSpeaking) {
      stopSpeaking();
    }
    
    console.log(`[TTS] TTS ${newEnabled ? 'enabled' : 'disabled'}`);
  };

  /**
   * Set TTS volume (if supported by the TTS engine)
   * @param {number} newVolume - Volume level (0.0 to 1.0)
   */
  const setTTSVolume = (newVolume) => {
    const clampedVolume = Math.max(0, Math.min(1, newVolume));
    setVolume(clampedVolume);
    
    // Note: @zoe-ng/tts may not support volume control directly
    // This is a placeholder for future enhancement
    console.log(`[TTS] Volume set to ${clampedVolume}`);
  };

  /**
   * Request facilitator to speak (triggers backend to generate response)
   */
  const requestFacilitatorResponse = () => {
    if (socket) {
      console.log("[TTS] Requesting facilitator response");
      socket.emit("request-facilitator-response");
    }
  };

  /**
   * Check if TTS is available
   */
  const isAvailable = () => {
    return !!ttsRef.current;
  };

  const value = {
    isSpeaking,
    currentText,
    isEnabled,
    volume,
    speakText,
    stopSpeaking,
    toggleEnabled,
    setTTSVolume,
    requestFacilitatorResponse,
    isAvailable,
  };

  return (
    <TTSContext.Provider value={value}>
      {children}
    </TTSContext.Provider>
  );
}

/**
 * Custom hook to use TTS context
 * @returns {Object} TTS context value
 */
export function useTTS() {
  const context = useContext(TTSContext);
  if (!context) {
    throw new Error("useTTS must be used within a TTSProvider");
  }
  return context;
}