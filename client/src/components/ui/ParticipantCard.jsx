import AudioLevelBar from "./AudioLevelBar";
import SpeechToTextPanel from "../feedback/SpeechToTextPanel";
import { Bot } from "lucide-react";
import { useParams } from "react-router-dom";

/**
 * ParticipantCard Component
 * Displays individual participant information in the roundtable view
 */
function ParticipantCard({
  participant,
  isCurrentSpeaker,
  position,
  remoteStream,
  showTranscription = false,
}) {
  const { roomId } = useParams();
  /**
   * Get card styling based on participant state
   */
  const getCardStyle = () => {
    const baseClasses =
      "absolute w-14 h-14 rounded-full border-4 transition-all duration-300 " +
      "flex items-center justify-center font-semibold text-white text-sm " +
      "shadow-lg cursor-pointer chair-enter";

    if (participant.isAgent) {
      // Agent styling
      if (isCurrentSpeaker) {
        return (
          `${baseClasses} border-blue-500 bg-blue-500 shadow-blue-300 shadow-xl scale-110 ` +
          "animate-pulse-active ring-4 ring-blue-200"
        );
      }
      return `${baseClasses} border-blue-600 bg-blue-600 hover:scale-105`;
    }

    // Regular participant styling
    if (isCurrentSpeaker) {
      return (
        `${baseClasses} border-green-500 bg-green-500 shadow-green-300 shadow-xl scale-110 ` +
        "animate-pulse-active ring-4 ring-green-200"
      );
    }

    return `${baseClasses} border-primary-600 bg-primary-600 hover:scale-105`;
  };

  /**
   * Display participant avatar (first letter of name or bot icon)
   */
  const displayAvatar = () => {
    if (participant.isAgent) {
      return <Bot className="w-6 h-6" />;
    }
    return (participant.anonymousName || "A").charAt(0).toUpperCase();
  };

  /**
   * Display participant name below avatar
   */
  const displayName = () => {
    return (
      <div
        className="absolute -bottom-12 left-1/2 transform -translate-x-1/2 
                      bg-white px-2 py-1 rounded-md shadow-sm border text-xs font-medium 
                      text-gray-700 whitespace-nowrap"
      >
        {participant.anonymousName || "Anonymous"}
        <div
          className={`text-xs ${
            participant.isAgent
              ? "text-blue-600"
              : participant.role === "speaker"
              ? "text-blue-600"
              : "text-gray-500"
          }`}
        >
          {participant.isAgent
            ? "AI Facilitator"
            : participant.role === "speaker"
            ? "Speaker"
            : "Listener"}
        </div>
      </div>
    );
  };

  /**
   * Display ready status indicator
   */
  const displayReadyStatus = () => {
    if (!participant.isReady) {
      return (
        <div
          className="absolute -top-2 -left-2 w-5 h-5 bg-yellow-400 rounded-full 
                        border-2 border-white flex items-center justify-center"
        >
          <div className="w-2 h-2 bg-white rounded-full"></div>
        </div>
      );
    }
    return null;
  };

  /**
   * Display speaking indicator when participant is currently speaking
   */
  const displaySpeakingIndicator = () => {
    if (isCurrentSpeaker) {
      const bgColor = participant.isAgent ? "bg-blue-400" : "bg-green-400";
      return (
        <div
          className={`absolute -top-2 -right-2 w-6 h-6 ${bgColor} rounded-full 
                        border-2 border-white flex items-center justify-center animate-bounce`}
        >
          <div className="w-2 h-2 bg-white rounded-full"></div>
        </div>
      );
    }
    return null;
  };

  return (
    <div
      className={getCardStyle()}
      style={position}
      title={`${participant.anonymousName || "Anonymous"}${
        isCurrentSpeaker ? " (Speaking)" : ""
      }`}
    >
      {/* Participant Initial */}
      {displayAvatar()}

      {/* Speaking Indicator */}
      {displaySpeakingIndicator()}

      {/* Ready Status */}
      {displayReadyStatus()}

      {/* Role Indicator */}
      <div
        className={`absolute -top-1 -left-1 w-4 h-4 rounded-full border-2 border-white text-xs flex items-center justify-center ${
          participant.isAgent
            ? "bg-blue-500 text-white"
            : participant.role === "speaker"
            ? "bg-blue-500 text-white"
            : "bg-gray-400 text-white"
        }`}
      >
        {participant.isAgent
          ? "🤖"
          : participant.role === "speaker"
          ? "🎤"
          : "👂"}
      </div>

      {/* Audio Level Indicator (if remote stream available and not an agent) */}
      {remoteStream && !participant.isAgent && (
        <div className="absolute left-1/2 -bottom-6 -translate-x-1/2 w-10">
          <AudioLevelBar stream={remoteStream} showLabel={false} />
        </div>
      )}

      {/* Name Label */}
      {displayName()}

      {/* Speech-to-Text Panel (compact version for current speaker) */}
      {showTranscription && isCurrentSpeaker && !participant.isAgent && (
        <div className="absolute top-16 left-1/2 transform -translate-x-1/2 w-48 z-10">
          <SpeechToTextPanel
            isActive={isCurrentSpeaker}
            speakerName={participant.anonymousName}
            participantId={participant.id}
            roomId={roomId}
            compact={true}
          />
        </div>
      )}
    </div>
  );
}

export default ParticipantCard;
