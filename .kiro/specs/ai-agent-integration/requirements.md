Backend Plan: Integrating Conversational Agents

This document outlines the backend architecture and implementation plan for integrating a Facilitator Agent and an English Feedback Agent into the turn-based conversational application.

1. Core Objectives

Automated Facilitation: A facilitator agent will vocally guide the conversation in each room using TTS.

Real-time Feedback: An English feedback agent will provide private, text-based feedback to each participant on their spoken English.

Seamless Integration: The agents will be registered as participants and interact with the existing transcripts and feedback tables.

Turn-Based Optimization: The system will leverage the turn-based nature of the conversation to manage processing delays effectively.

2. Database Schema

We will introduce a new agents table to manage the identity and state of each agent instance per room.

agents Table Schema

CREATE TABLE agents (
    agent_id TEXT PRIMARY KEY,
    room_id TEXT NOT NULL,
    agent_model TEXT NOT NULL, -- e.g., 'gemini-1.5-pro', 'bedrock-claude-v2'
    agent_type TEXT NOT NULL CHECK(agent_type IN ('facilitator', 'english_feedback')),
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'inactive', 'processing')),
    system_prompt TEXT,
    total_interactions INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    FOREIGN KEY (room_id) REFERENCES rooms (room_id)
);


Required Modifications to Existing Tables

transcripts table: Needs a participant_id column to associate a transcript with either a human participant or an agent.

feedback table: Needs agent_id, participant_id, and transcript_id columns to link the feedback to the agent that generated it, the participant who received it, and the specific transcript it's based on.

3. System Architecture & Data Flow

The interaction will be managed through a combination of REST APIs for state creation and WebSockets for real-time, turn-based communication.

+-----------+      (1) Speech-to-Text      +----------------+      (2) POST /transcript      +-----------------+
|           | ---------------------------> |                | ----------------------------> |                 |
|  Client   |      (via browser API)       |  Client-side   |                               |  Backend Server |
| (Browser) |                              |      App       | <---------------------------  | (Node.js/Express)|
|           | <--------------------------- |                |   (6) Private Feedback        |                 |
+-----------+   (via WebSocket)            +----------------+   (WebSocket Event)           +--------+--------+
                                                                                                    |
                                                                                                    | (3) Save to DB
                                                                                                    v
                                                                                           +-----------------+
                                                                                           |    Database     |
                                                                                           | (transcripts)   |
                                                                                           +--------+--------+
                                                                                                    |
                                                                                                    | (4) Trigger Agents
                                                                                                    v
+-----------------------------+     (5) Generate & Save Feedback     +-------------------------------+
|                             | <------------------------------------ |                               |
| English Feedback Agent      |       (LLM call -> Save to DB)        |      Turn Management Logic    |
| (Processes asynchronously)  |                                       | (Handles turn scheduling)     |
|                             | -------------------------------------> |                               |
+-----------------------------+       (7) Synthesize Turn Data       +-------------------------------+
                                                                     |
+-----------------------------+                                      | (8) Generate Script & TTS
|                             | <------------------------------------ |
|   Facilitator Agent         |                                       |
| (Processes 15s pre-turn)    | ------------------------------------->|
|                             |    (9) Audio Ready                    |
+-----------------------------+                                       |
                                                                      v
                                                         +-----------------+
                                                         |   Client-side   |
                                                         | (via WebSocket) |
                                                         +-----------------+


4. Agent Interaction Workflow (Turn-by-Turn)

Step 1: Room Initialization

When a new room is created, the backend server automatically creates two entries in the agents table: one facilitator and one english_feedback, both linked to the room_id.

Clients in the room are notified via a agents_joined socket event, and the agents appear in the participant list.

Step 2: Participant's Speaking Turn

The client application uses the browser's SpeechRecognition API to capture the participant's speech and convert it to a transcript in real-time.

At the end of the participant's turn, the final transcript is sent to the backend via a send_transcript socket event.

The backend saves the transcript to the transcripts table, associating it with the participant_id.

Step 3: English Feedback Agent (Asynchronous)

The send_transcript event handler triggers the English feedback agent's logic asynchronously.

The agent retrieves the newly saved transcript.

It calls the specified LLM (Gemini/Bedrock) with a system prompt to analyze the transcript for grammar, clarity, and fluency.

The generated feedback is saved to the feedback table.

The backend emits a private_feedback socket event only to the specific participant's socket ID, delivering the feedback text.

Step 4: Facilitator Agent (Pre-computation)

Our turn management system knows when the facilitator's turn is approaching.

15 seconds before the facilitator's turn begins, a scheduled job or a setTimeout triggers the facilitator agent.

The agent queries the database for all transcripts and feedback generated since its last turn.

It uses an LLM to process this data to:

Acknowledge points made by participants.

Identify common themes or disagreements.

Reflect on key areas for improvement based on the English agent's feedback.

Generate a script to guide the conversation forward.

This generated script is immediately sent to the TTS service (@zoe-ng/tts wrapper) to generate an audio stream/file.

When the facilitator's turn officially starts, the backend broadcasts a facilitator_turn socket event to all clients, containing the URL or data of the pre-generated audio. Clients then play this audio.

Step 5: End of Session Summary

When the session ends, a final trigger invokes the English feedback agent.

The agent queries all feedback it has generated for the room.

It synthesizes this feedback into a comprehensive, personalized summary for each participant.

The agent generates a concluding script.

This script is converted to audio via TTS, and the audio is broadcast to the room for all participants to hear as a final wrap-up.

5. API and WebSocket Endpoints

REST API

POST /api/rooms/:roomId/agents

Purpose: Internal endpoint called upon room creation to register the facilitator and feedback agents.

Body: None. Logic is handled internally.

Response: 201 Created with the details of the created agents.

WebSocket (Socket.IO) Events

Client -> Server

join_room({ roomId, participantId }): User joins a room.

send_transcript({ roomId, participantId, transcript }): A participant sends their final transcript for their turn.

Server -> Client

agents_joined({ facilitatorAgent, feedbackAgent }): (Broadcast) Informs clients that the agents have been added to the room.

new_turn({ participantId, turnDuration }): (Broadcast) Announces the start of the next turn. participantId can be a human or an agent ID.

private_feedback({ feedbackText, fromAgentId }): (Private message to one client) Delivers feedback from the English agent.

facilitator_speech({ audioUrl, transcript }): (Broadcast) Sent when it's the facilitator's turn. Clients will fetch and play the audioUrl.

session_summary({ audioUrl, transcript }): (Broadcast) Sent at the end of the meeting with the final summary audio.

6. Implementation Strategy

Database Migration: Add the agents table and update the transcripts and feedback tables with the new foreign key columns.

Agent Service: Create a service module (agentService.js) responsible for creating, retrieving, and managing agent records in the database.

Room Logic Integration: Modify the room creation logic to call the agentService and register the two default agents.

WebSocket Handlers: Implement the server-side listeners for join_room and send_transcript.

LLM Integration: Create a generic LLM service that can interact with Gemini and/or Bedrock based on the agent_model field. This service will handle API calls and system prompt formatting.

Feedback Agent Logic: Implement the asynchronous workflow for the English feedback agent.

Turn Management & Facilitator Logic:

Develop a robust turn management system. A simple queue-based system would work well.

Implement the 15-second pre-computation trigger for the facilitator agent.

Integrate the TTS service to convert the facilitator's generated text into speech.

Final Summary: Implement the end-of-session logic to generate and deliver the final summary.