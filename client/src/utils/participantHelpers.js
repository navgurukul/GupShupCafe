/**
 * Participant Helper Functions
 * Common functions for managing participant data across pages
 */

import { generateAvatarColor } from "./helpers";

const getApiUrl = () => {
  return import.meta.env.VITE_API_URL || "http://localhost:3003";
};

/**
 * Create a participant in the database
 * @param {Object} participantData - Participant data
 * @returns {Promise<Object>} API response
 */
export async function createParticipant(participantData) {
  const apiUrl = getApiUrl();

  try {
    const response = await fetch(`${apiUrl}/participants/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(participantData),
    });

    const result = await response.json();
    console.log("[ParticipantHelper] Participant created:", result);

    // Store participant data in localStorage
    if (result.status === "success" && result.data) {
      // result.data is now a full ParticipantModel object
      const participantModel = result.data;
      saveParticipantToLocalStorage({
        participantId: participantModel.participant_id,
        user_id: participantModel.user_id,
        room_id: participantModel.room_id,
        avatar_color: participantModel.avatar_color,
        anonymous_name: participantModel.anonymous_name,
        role: participantModel.role,
        is_ready: participantModel.is_ready,
        turn_order: participantModel.turn_order,
        is_speaking: participantModel.is_speaking,
        is_muted: participantModel.is_muted,
        socket_id: participantModel.socket_id,
        starting_cefr_level: participantModel.starting_cefr_level,
        ending_cefr_level: participantModel.ending_cefr_level,
        joined_at: participantModel.joined_at,
        left_at: participantModel.left_at,
        campusOrLocation: participantModel.campusOrLocation,
        speaking_time_seconds: participantModel.speaking_time_seconds,
        created_at: participantModel.created_at,
      });
    }

    return result;
  } catch (error) {
    console.error("[ParticipantHelper] Error creating participant:", error);
    throw error;
  }
}

/**
 * Save participant data to localStorage
 * @param {Object} participantData - Participant data to save
 */
export function saveParticipantToLocalStorage(participantData) {
  try {
    console.log(
      "[ParticipantHelper] Saving participant data to localStorage:",
      participantData
    );
    localStorage.setItem("participantData", JSON.stringify(participantData));
    console.log(
      "[ParticipantHelper] Participant data saved to localStorage successfully"
    );
  } catch (error) {
    console.error("[ParticipantHelper] Error saving to localStorage:", error);
  }
}

/**
 * Get participant data from localStorage
 * @returns {Object|null} Participant data or null
 */
export function getParticipantFromLocalStorage() {
  try {
    const data = localStorage.getItem("participantData");
    return data ? JSON.parse(data) : null;
  } catch (error) {
    console.error(
      "[ParticipantHelper] Error reading from localStorage:",
      error
    );
    return null;
  }
}

/**
 * Clear participant data from localStorage
 */
export function clearParticipantFromLocalStorage() {
  try {
    localStorage.removeItem("participantData");
    console.log(
      "[ParticipantHelper] Participant data cleared from localStorage"
    );
  } catch (error) {
    console.error("[ParticipantHelper] Error clearing localStorage:", error);
  }
}

/**
 * Common function to create participant with user data
 * Extracts repeated logic from handleCreateRoom and handleJoinSubmit
 * @param {Object} params - Parameters for participant creation
 * @returns {Promise<Object>} Created participant result
 */
export async function createParticipantForRoom({
  userId,
  roomId,
  anonymousName,
  currentCefrLevel,
  campusOrLocation = null,
}) {
  console.log(
    "[ParticipantHelper] Creating participant with name:",
    anonymousName
  );

  const participantPayload = {
    user_id: userId,
    room_id: roomId,
    avatar_color: generateAvatarColor(),
    anonymous_name: anonymousName,
    campusOrLocation: campusOrLocation,
    joined_at: new Date().toISOString(),
    starting_cefr_level: currentCefrLevel,
    ending_cefr_level: currentCefrLevel, // Initially same as starting level
  };

  console.log("[ParticipantHelper] Participant payload:", participantPayload);
  return await createParticipant(participantPayload);
}

export default {
  createParticipant,
  saveParticipantToLocalStorage,
  getParticipantFromLocalStorage,
  clearParticipantFromLocalStorage,
  createParticipantForRoom,
};
