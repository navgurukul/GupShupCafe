/**
 * @typedef {Object} RoomState
 * @property {string} roomCode - Unique room identifier/code
 * @property {string} topic - Discussion topic
 * @property {string} status - Room status ('waiting', 'in-progress', 'ended')
 * @property {Participant[]} participants - List of participants in the room
 * @property {number} currentSpeakerIndex - Index of current speaker
 * @property {number} currentRound - Current discussion round
 * @property {number} maxRounds - Maximum number of rounds
 * @property {number} speakingTime - Time allocated per speaker (in seconds)
 */

import { ParticipantType } from './Participant.js'

/**
 * Room state type definition for managing discussion rooms
 */
export const RoomStateType = {}
