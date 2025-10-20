"""
Socket.io Event Handlers
Manages real-time communication for the roundtable discussions
"""

import socketio
from typing import Dict, Any
from datetime import datetime
import uuid
import os
import asyncio

from .room_manager import room_manager
from .timer_manager import timer_manager
from ..ai.topic_generator import generate_discussion_topic
from ..database.database import db


async def process_transcript_for_english_feedback(room_id: str, transcript_id: str):
    """
    Process transcript with English feedback agent (async background task)
    """
    try:
        from ..services.agent_service import agent_service
        
        # Get English feedback agent for this room
        agents = await agent_service.get_agents_by_room(room_id)
        english_agent = next((a for a in agents if a.agent_type == "english"), None)
        
        if english_agent:
            # Process transcript for instant feedback
            await agent_service.process_transcript_for_feedback(
                english_agent.agent_id, 
                transcript_id, 
                "instant"
            )
            print(f"[Backend] Generated instant feedback for transcript {transcript_id}")
        else:
            print(f"[Backend] No English agent found for room {room_id}")
            
    except Exception as e:
        print(f"Error processing transcript for feedback: {str(e)}")


async def setup_socket_handlers(sio: socketio.AsyncServer):
    """
    Setup Socket.io event handlers
    Args:
        sio: Socket.io server instance
    """
    
    # In-memory map of active room ids per room
    active_rooms: Dict[str, str] = {}
    
    @sio.on('connection')
    async def connect(sid, environ, auth):
        """Handle client connection"""
        print(f"[Backend] Socket connected: {sid}")
        print(f"[Backend] Handshake auth: {auth}")
        try:
            # Log a small subset of environ for diagnostics
            headers = environ.get('headers') if isinstance(environ, dict) else None
            origin = None
            user_agent = None
            if headers and isinstance(headers, list):
                for k, v in headers:
                    if k.lower() == 'origin':
                        origin = v
                    if k.lower() == 'user-agent':
                        user_agent = v
            print(f"[Backend] Connect meta -> origin: {origin}, ua: {user_agent}")
        except Exception as e:
            print(f"[Backend] Error parsing connect environ: {e}")
        
        # Save auth data to session so it can be retrieved in join_room
        if auth:
            await sio.save_session(sid, {'auth': auth})

        # Emit a connection acknowledgement for quick client-side sanity checks
        try:
            await sio.emit(
                "connection-ack",
                {
                    "sid": sid,
                    "connectedAt": datetime.now().isoformat(),
                    "serverPid": os.getpid(),
                },
                room=sid,
            )
            print(f"[Backend] Sent connection-ack to {sid}")
        except Exception as e:
            print(f"[Backend] Failed to emit connection-ack to {sid}: {e}")
    
    @sio.on('disconnect')
    async def disconnect(sid):
        """Handle client disconnection"""
        print(f"👋 User disconnected: {sid}")
        
        # Find the room this socket was in
        rooms = sio.rooms(sid)
        for room_id in rooms:
            if room_id != sid:  # Skip the default room (socket's own room)
                # Get user data from room before removing
                room = room_manager.get_room(room_id)
                user = room.get_participant_by_socket(sid)
                
                if user:
                    user_id = user.id
                    anonymous_name = user.anonymous_name
                    room_manager.remove_user_from_room(room_id, user_id)
                    
                    # Get updated participants
                    participants = room_manager.get_room_participants(room_id)
                    
                    # Notify others
                    await sio.emit("participants-update", participants, room=room_id)
                    await sio.emit("participant-left", {
                        "participantId": user_id,
                        "anonymousName": anonymous_name
                    }, room=room_id)
                    
                    print(f"[Backend] {anonymous_name} disconnected from room {room_id}")
    
    @sio.on('join-room')
    async def join_room(sid, *args):
        """Handle user joining a room"""
        try:
            # Robustly extract roomId and clientUserData
            room_id = "general"
            client_user_data = None
            room_data = None  # Additional room metadata (e.g., room_name, topic_category, etc.)
            
            print(f"[Backend] join-room args: {args}")
            
            if len(args) > 0 and isinstance(args[0], str):
                room_id = args[0]
            if len(args) > 1 and isinstance(args[1], dict):
                client_user_data = args[1]
            if len(args) > 2 and isinstance(args[2], dict):
                room_data = args[2]
            
            # Get auth data from session
            try:
                session = await sio.get_session(sid)
                auth_data = session.get("auth", {}) if session else {}
            except:
                auth_data = {}
            
            # Use clientUserData if provided, else fallback to auth
            if client_user_data and client_user_data.get("userId"):
                # Validate that client-provided socketId matches server sid (security check)
                client_socket_id = client_user_data.get("socketId")
                if client_socket_id and client_socket_id != sid:
                    print(f"[Backend] Warning: Client socketId {client_socket_id} doesn't match server sid {sid}")
                
                effective_user_data = {
                    "id": client_user_data.get("userId"),
                    "socketId": sid,  # Always use server's authoritative socket ID
                    "name": client_user_data.get("name"),
                    "campus": client_user_data.get("campus"),
                    "location": client_user_data.get("location"),
                    "anonymousName": client_user_data.get("anonymousName"),
                    "role": client_user_data.get("role", "listener"),
                    "isReady": False,
                    "joinedAt": datetime.now().isoformat()
                }
            else:
                effective_user_data = {
                    "id": auth_data.get("userId", sid),
                    "socketId": sid,  # Always use server's authoritative socket ID
                    "name": auth_data.get("name"),
                    "campus": auth_data.get("campus"),
                    "location": auth_data.get("location"),
                    "anonymousName": auth_data.get("anonymousName"),
                    "role": auth_data.get("role", "listener"),
                    "isReady": False,
                    "joinedAt": datetime.now().isoformat()
                }
            
            print(f"[Backend] 📥 {effective_user_data['anonymousName']} joining room: {room_id} with socketId: {effective_user_data['socketId']}")
            
            # Leave any existing rooms
            current_rooms = sio.rooms(sid)
            for room in current_rooms:
                if room != sid:
                    print(f"[Backend] Leaving room: {room}")
                    await sio.leave_room(sid, room)
                    # Find and remove user from that room
                    old_room = room_manager.get_room(room)
                    old_user = old_room.get_participant_by_socket(sid)
                    if old_user:
                        room_manager.remove_user_from_room(room, old_user.id)
            
            # Join the new room
            await sio.enter_room(sid, room_id)
            print(f"[Backend] Joined new room: {room_id}")
            
            # Add user to room manager
            room_manager.add_user_to_room(room_id, effective_user_data)
            
            # Store room metadata if provided
            room = room_manager.get_room(room_id)
            if room_data:
                # Store room metadata for later use when creating room
                room.metadata = room_data
            
            # Get updated participants
            participants = room_manager.get_room_participants(room_id)
            
            # Emit participant-joined event
            await sio.emit("participant-joined", {
                "participant": participants[-1] if participants else None
            }, room=room_id)
            
            # Emit participants update to all users in the room
            await sio.emit("participants-update", participants, room=room_id)
            print("[Backend] Emitted participants-update")
            
            # Check if there's an active discussion and sync state
            room = room_manager.get_room(room_id)
            if room.status.value == "in_progress":
                print(f"[Backend] Syncing active discussion state with {effective_user_data['anonymousName']}")
                
                current_speaker = room.get_current_speaker()
                
                discussion_state = {
                    "topic": room.topic,
                    "firstSpeaker": current_speaker.to_dict() if current_speaker else None,
                    "duration": room.speaking_time,
                    "currentSpeakerIndex": room.current_speaker_index,
                    "round": room.current_round
                }
                
                await sio.emit("discussion-started", discussion_state, room=sid)
            
        except Exception as e:
            print(f"Error in join-room: {str(e)}")
            import traceback
            traceback.print_exc()
    
    @sio.on('user-ready')
    async def user_ready(sid, data=None):
        """Handle user ready status"""
        try:
            # Find room for this socket
            rooms = sio.rooms(sid)
            room_id = None
            for room in rooms:
                if room != sid:
                    room_id = room
                    break
            
            if not room_id:
                print(f"[Backend] No room found for user-ready from {sid}")
                return
            
            # Get user from room by socket ID
            room = room_manager.get_room(room_id)
            user = room.get_participant_by_socket(sid)
            
            if not user:
                print(f"[Backend] No user found for socket {sid} in room {room_id}")
                return
            
            # Get ready status from data or default to True
            is_ready = True
            if data and isinstance(data, dict):
                is_ready = data.get("isReady", True)
            
            # Update user ready status using the participant from room
            room_manager.update_user(room_id, user.id, {"isReady": is_ready})
            
            print(f"[Backend] {user.anonymous_name} marked as ready in room {room_id}")
            
            # Get updated participants
            participants = room_manager.get_room_participants(room_id)
            
            # Emit update to all in room
            await sio.emit("participants-update", participants, room=room_id)
            
            # Check if discussion can start
            await check_and_start_discussion(sio, room_id, active_rooms)
            
        except Exception as e:
            print(f"Error in user-ready: {str(e)}")
            import traceback
            traceback.print_exc()
    
    @sio.on('change-role')
    async def change_role(sid, data):
        """Handle role change request"""
        try:
            user_id = data.get("userId")
            new_role = data.get("role")
            
            # Find room for this socket
            rooms = sio.rooms(sid)
            room_id = None
            for room in rooms:
                if room != sid:
                    room_id = room
                    break
            
            if not room_id:
                return
            
            # Check if user can become speaker
            if new_role == "speaker" and not room_manager.can_become_speaker(room_id):
                await sio.emit("role-change-failed", {
                    "error": "Maximum number of speakers reached"
                }, room=sid)
                return
            
            # Change role
            success = room_manager.change_user_role(room_id, user_id, new_role)
            
            if success:
                # Get updated participants
                participants = room_manager.get_room_participants(room_id)
                await sio.emit("participants-update", participants, room=room_id)
                await sio.emit("role-changed", {
                    "userId": user_id,
                    "role": new_role
                }, room=room_id)
            
        except Exception as e:
            print(f"Error in change-role: {str(e)}")
    
    @sio.event
    async def message(sid, message_data):
        """Handle chat messages"""
        try:
            # Find room for this socket
            rooms = sio.rooms(sid)
            room_id = None
            for room in rooms:
                if room != sid:
                    room_id = room
                    break
            
            if not room_id:
                return
            
            # Get user data
            room = room_manager.get_room(room_id)
            user = next((p for p in room["participants"] if p["socketId"] == sid), None)
            
            if user:
                # Broadcast message to room
                await sio.emit("message", {
                    "id": str(uuid.uuid4()),
                    "userId": user["id"],
                    "anonymousName": user["anonymousName"],
                    "message": message_data,
                    "timestamp": datetime.now().isoformat()
                }, room=room_id, skip_sid=sid)
            
        except Exception as e:
            print(f"Error handling message: {str(e)}")
    
    @sio.event
    async def debug_ping(sid, data=None):
        """Roundtrip latency/debug check: client emits 'debug-ping', server responds 'debug-pong'"""
        try:
            print(f"[Backend] <- debug-ping from {sid}: {data}")
            await sio.emit(
                "debug-pong",
                {
                    "echo": data,
                    "serverTime": datetime.now().isoformat(),
                    "sid": sid,
                },
                room=sid,
            )
            print(f"[Backend] -> debug-pong to {sid}")
        except Exception as e:
            print(f"[Backend] Error in debug-ping handler: {e}")

    @sio.event
    async def debug_whoami(sid, data=None):
        """Return the current socket id and any saved auth session data"""
        try:
            session = await sio.get_session(sid)
            payload = {
                "sid": sid,
                "auth": (session.get("auth") if session else None),
                "serverTime": datetime.now().isoformat(),
            }
            await sio.emit("debug-whoami", payload, room=sid)
            print(f"[Backend] Provided whoami to {sid}")
        except Exception as e:
            print(f"[Backend] Error in debug-whoami handler: {e}")

    @sio.event
    async def debug_room_state(sid, data=None):
        """Emit the current room state for this socket (participants, status, timers)"""
        try:
            # Determine the room this socket is currently in (other than its own room)
            room_id = None
            try:
                for rid in sio.rooms(sid):
                    if rid != sid:
                        room_id = rid
                        break
            except Exception:
                room_id = None

            if not room_id:
                await sio.emit(
                    "debug-room-state",
                    {"error": "Socket not in any room", "sid": sid},
                    room=sid,
                )
                print(f"[Backend] debug-room-state requested by {sid} but socket not in room")
                return

            room = room_manager.get_room(room_id)
            participants = []
            try:
                participants = [
                    (p.to_dict() if hasattr(p, "to_dict") else {
                        "id": getattr(p, "id", None),
                        "socketId": getattr(p, "socket_id", None),
                        "anonymousName": getattr(p, "anonymous_name", None),
                        "role": getattr(getattr(p, "role", None), "value", getattr(p, "role", None)),
                        "isReady": getattr(p, "is_ready", None),
                    })
                    for p in getattr(room, "participants", [])
                ]
            except Exception as pe:
                print(f"[Backend] Error serializing participants for debug-room-state: {pe}")

            payload = {
                "roomId": room_id,
                "status": getattr(getattr(room, "status", None), "value", getattr(room, "status", None)),
                "topic": getattr(room, "topic", None),
                "participantsCount": len(participants),
                "participants": participants,
                "currentSpeakerIndex": getattr(room, "current_speaker_index", None),
                "currentRound": getattr(room, "current_round", None),
                "speakingTime": getattr(room, "speaking_time", None),
                "timeRemaining": getattr(room, "time_remaining", None),
                "activeRoomId": active_rooms.get(room_id),
                "serverTime": datetime.now().isoformat(),
            }

            await sio.emit("debug-room-state", payload, room=sid)
            print(f"[Backend] Sent debug-room-state to {sid} for room {room_id}")
        except Exception as e:
            print(f"[Backend] Error in debug-room-state handler: {e}")

    @sio.on('webrtc-offer')
    async def webrtc_offer(sid, data):
        """Relay WebRTC offer to target peer"""
        try:
            target_sid = data.get("to")
            sdp = data.get("sdp")
            
            if not target_sid or not sdp:
                print(f"[Backend] Invalid webrtc-offer data: {data}")
                return
            
            print(f"[Backend] Relaying WebRTC offer from {sid} to {target_sid}")
            await sio.emit("webrtc-offer", {
                "from": sid,
                "sdp": sdp
            }, room=target_sid)
            
        except Exception as e:
            print(f"Error handling webrtc-offer: {str(e)}")
            import traceback
            traceback.print_exc()
    
    @sio.on('webrtc-answer')
    async def webrtc_answer(sid, data):
        """Relay WebRTC answer to target peer"""
        try:
            target_sid = data.get("to")
            sdp = data.get("sdp")
            
            if not target_sid or not sdp:
                print(f"[Backend] Invalid webrtc-answer data: {data}")
                return
            
            print(f"[Backend] Relaying WebRTC answer from {sid} to {target_sid}")
            await sio.emit("webrtc-answer", {
                "from": sid,
                "sdp": sdp
            }, room=target_sid)
            
        except Exception as e:
            print(f"Error handling webrtc-answer: {str(e)}")
            import traceback
            traceback.print_exc()
    
    @sio.on('webrtc-ice-candidate')
    async def webrtc_ice_candidate(sid, data):
        """Relay ICE candidate to target peer"""
        try:
            target_sid = data.get("to")
            candidate = data.get("candidate")
            
            if not target_sid or not candidate:
                print(f"[Backend] Invalid webrtc-ice-candidate data: {data}")
                return
            
            print(f"[Backend] Relaying ICE candidate from {sid} to {target_sid}")
            await sio.emit("webrtc-ice-candidate", {
                "from": sid,
                "candidate": candidate
            }, room=target_sid)
            
        except Exception as e:
            print(f"Error handling webrtc-ice-candidate: {str(e)}")
            import traceback
            traceback.print_exc()
    
    @sio.event
    async def speech_transcript(sid, data):
        """Handle speech transcript from participant"""
        try:
            text = data.get("text", "")
            speaker_id = data.get("speakerId")
            
            # Find room for this socket
            rooms = sio.rooms(sid)
            room_id = None
            for room in rooms:
                if room != sid:
                    room_id = room
                    break
            
            if not room_id:
                print(f"[Backend] No room found for speech transcript from {sid}")
                return
            
            # Get room ID
            room_id = active_rooms.get(room_id)
            if not room_id:
                print(f"[Backend] No active room for room {room_id}")
                return
            
            # Save transcript to database
            transcript_id = str(uuid.uuid4())
            await db.save_transcript({
                "id": transcript_id,
                "roomId": room_id,
                "participantId": speaker_id,
                "text": text,
                "timestamp": datetime.now().isoformat()
            })
            
            print(f"[Backend] Saved transcript for room {room_id}: {text[:50]}...")
            
        except Exception as e:
            print(f"Error handling speech-transcript: {str(e)}")
            import traceback
            traceback.print_exc()
    
    @sio.event
    async def end_turn(sid, data):
        """Handle end of speaking turn"""
        try:
            # Find room for this socket
            rooms = sio.rooms(sid)
            room_id = None
            for room in rooms:
                if room != sid:
                    room_id = room
                    break
            
            if not room_id:
                print(f"[Backend] No room found for end-turn from {sid}")
                return
            
            # Cancel the current timer
            await timer_manager.cancel_timer(room_id)
            
            room = room_manager.get_room(room_id)
            
            # Get current speaker
            current_speaker = room.get_current_speaker()
            if not current_speaker:
                print(f"[Backend] No current speaker in room {room_id}")
                return
            
            # Emit turn-ended event
            await sio.emit("turn-ended", {
                "speaker": current_speaker.to_dict()
            }, room=room_id)
            
            # Advance to next speaker
            next_speaker = room.advance_turn()
            
            # Check if discussion is complete
            if room.status.value == "completed":
                print(f"[Backend] Discussion completed in room {room_id}")
                
                # Update room in database
                room_id = active_rooms.get(room_id)
                if room_id:
                    await db.update_room(room_id, {
                        "endedAt": datetime.now().isoformat(),
                        "roundsCompleted": room.current_round - 1
                    })
                    
                    # Remove from active rooms
                    del active_rooms[room_id]
                
                # Emit discussion-ended event
                await sio.emit("discussion-ended", {
                    "roomId": room_id,
                    "roundsCompleted": room.current_round - 1
                }, room=room_id)
                
                return
            
            # Check if round is complete
            if room.current_speaker_index == 0:
                await sio.emit("round-complete", {
                    "round": room.current_round - 1,
                    "next": room.current_round
                }, room=room_id)
            
            # Emit turn-started for next speaker
            if next_speaker:
                await sio.emit("turn-started", {
                    "speaker_index": room.current_speaker_index,
                    "speaker": next_speaker.to_dict(),
                    "timer": room.speaking_time
                }, room=room_id)
                
                print(f"[Backend] Next speaker: {next_speaker.anonymous_name}")
                
                # Start timer for next turn
                await start_turn_timer(sio, room_id, room.speaking_time, active_rooms)
            
        except Exception as e:
            print(f"Error handling end-turn: {str(e)}")
            import traceback
            traceback.print_exc()
    
    @sio.event
    async def next_speaker(sid, data):
        """Handle request for next speaker (manual progression)"""
        try:
            # Reuse end_turn logic
            await end_turn(sid, data)
        except Exception as e:
            print(f"Error handling next-speaker: {str(e)}")
    
    @sio.event
    async def leave_room(sid, data=None):
        """Handle user leaving room"""
        try:
            # Find room for this socket
            rooms = sio.rooms(sid)
            room_id = None
            for room in rooms:
                if room != sid:
                    room_id = room
                    break
            
            if not room_id:
                return
            
            # Get user data from room before removing
            room = room_manager.get_room(room_id)
            user = next((p for p in room.participants if p.socket_id == sid), None)
            
            if user:
                user_id = user.id
                room_manager.remove_user_from_room(room_id, user_id)
                
                # Leave socket.io room
                await sio.leave_room(sid, room_id)
                
                # Get updated participants
                participants = room_manager.get_room_participants(room_id)
                
                # Notify others
                await sio.emit("participants-update", participants, room=room_id)
                await sio.emit("participant-left", {
                    "participantId": user_id,
                    "anonymousName": user.anonymous_name
                }, room=room_id)
                
                print(f"[Backend] {user.anonymous_name} left room {room_id}")
            
        except Exception as e:
            print(f"Error handling leave-room: {str(e)}")
            import traceback
            traceback.print_exc()
    
    @sio.event
    async def ready_for_webrtc(sid, data=None):
        """Handle client ready for WebRTC connections"""
        try:
            # Find room for this socket
            rooms = sio.rooms(sid)
            room_id = None
            for room in rooms:
                if room != sid:
                    room_id = room
                    break
            
            if not room_id:
                return
            
            print(f"[Backend] Client {sid} is ready for WebRTC in room {room_id}")
            
            # Notify other participants that this user is ready
            await sio.emit("peer-ready", {
                "socketId": sid
            }, room=room_id, skip_sid=sid)
            
        except Exception as e:
            print(f"Error handling ready-for-webrtc: {str(e)}")

    @sio.event
    async def transcript_received(sid, data):
        """Handle speech transcript from participant and trigger agent processing"""
        try:
            transcript_text = data.get("text", "")
            participant_id = data.get("participantId")
            round_number = data.get("round", 1)
            turn_order = data.get("turnOrder", 0)
            
            # Find room for this socket
            rooms = sio.rooms(sid)
            room_id = None
            for room in rooms:
                if room != sid:
                    room_id = room
                    break
            
            if not room_id:
                print(f"[Backend] No room found for transcript from {sid}")
                return
            
            # Get room from room manager
            room = room_manager.get_room(room_id)
            user = room.get_participant_by_socket(sid)
            
            if not user:
                print(f"[Backend] No user found for socket {sid}")
                return
            
            # Save transcript to database
            transcript_id = str(uuid.uuid4())
            transcript_data = {
                "transcript_id": transcript_id,
                "room_id": room_id,
                "participant_id": participant_id or user.id,
                "user_id": user.id,
                "round_number": round_number,
                "turn_order": turn_order,
                "transcript_text": transcript_text,
                "language": "en",
                "stt_confidence": data.get("confidence", 0.9),
                "started_at": data.get("startedAt", datetime.now().isoformat()),
                "ended_at": data.get("endedAt", datetime.now().isoformat()),
                "duration_seconds": data.get("duration", 0),
                "word_count": len(transcript_text.split()),
                "speech_rate": len(transcript_text.split()) / max(data.get("duration", 1), 1),
                "is_processed": 0
            }
            
            await db.save_transcript(transcript_data)
            print(f"[Backend] Saved transcript for {user.anonymous_name}: {transcript_text[:50]}...")
            
            # Trigger English feedback agent processing (async)
            asyncio.create_task(process_transcript_for_english_feedback(room_id, transcript_id))
            
            # Emit transcript saved confirmation
            await sio.emit("transcript-saved", {
                "transcriptId": transcript_id,
                "participantId": participant_id or user.id
            }, room=sid)
            
        except Exception as e:
            print(f"Error handling transcript-received: {str(e)}")
            import traceback
            traceback.print_exc()

    @sio.event
    async def request_facilitator_response(sid, data):
        """Handle request for facilitator to speak (TTS)"""
        try:
            # Find room for this socket
            rooms = sio.rooms(sid)
            room_id = None
            for room in rooms:
                if room != sid:
                    room_id = room
                    break
            
            if not room_id:
                return
            
            print(f"[Backend] Facilitator response requested for room {room_id}")
            
            # Get recent transcripts and feedback for context
            recent_transcripts = await db.get_recent_transcripts(room_id, limit=5)
            feedback_summaries = await db.get_feedback_by_room(room_id, "instant")
            
            # Generate facilitator response
            from ..services.agent_service import agent_service
            facilitator_text = await agent_service.generate_facilitator_turn_response(
                room_id, recent_transcripts, feedback_summaries
            )
            
            # Emit facilitator response for TTS
            await sio.emit("facilitator-speaking", {
                "text": facilitator_text,
                "timestamp": datetime.now().isoformat()
            }, room=room_id)
            
            print(f"[Backend] Facilitator response: {facilitator_text[:100]}...")
            
        except Exception as e:
            print(f"Error handling request-facilitator-response: {str(e)}")
            import traceback
            traceback.print_exc()

    @sio.event
    async def get_instant_feedback(sid, data):
        """Handle request for instant feedback for a participant"""
        try:
            participant_id = data.get("participantId")
            
            # Find room for this socket
            rooms = sio.rooms(sid)
            room_id = None
            for room in rooms:
                if room != sid:
                    room_id = room
                    break
            
            if not room_id:
                return
            
            # Get recent feedback for this participant
            feedback_list = await db.get_feedback_by_room(room_id, "instant")
            participant_feedback = [
                f for f in feedback_list 
                if f.get("participant_id") == participant_id
            ]
            
            if participant_feedback:
                latest_feedback = participant_feedback[0]  # Most recent
                await sio.emit("instant-feedback", {
                    "participantId": participant_id,
                    "feedback": latest_feedback.get("display_message"),
                    "timestamp": latest_feedback.get("created_at")
                }, room=sid)
            else:
                await sio.emit("instant-feedback", {
                    "participantId": participant_id,
                    "feedback": "Keep up the great work!",
                    "timestamp": datetime.now().isoformat()
                }, room=sid)
            
        except Exception as e:
            print(f"Error handling get-instant-feedback: {str(e)}")
            import traceback
            traceback.print_exc()


async def check_and_start_discussion(sio: socketio.AsyncServer, room_id: str, active_rooms: Dict[str, str]):
    """
    Check if discussion can start
    Args:
        sio: Socket.io server instance
        room_id: Room identifier
        active_rooms: Active rooms map
    """
    try:
        room = room_manager.get_room(room_id)
        
        # Don't start if already active
        if room.status.value == "in_progress":
            return
        
        # Check if we have minimum participants ready
        min_participants = int(os.getenv("MIN_PARTICIPANTS", "1"))
        ready_participants = [p for p in room.participants if p.is_ready]
        
        if len(ready_participants) >= min_participants:
            print(f"[Backend] Starting discussion in room {room_id}")
            
            # Generate or get topic
            topic = await generate_discussion_topic()
            
            # Create room
            room_id = str(uuid.uuid4())
            active_rooms[room_id] = room_id
            
            # Create agents for this room
            from ..services.agent_service import agent_service
            try:
                agent_ids = await agent_service.create_room_agents(room_id, topic)
                print(f"[Backend] Created agents for room {room_id}: {agent_ids}")
            except Exception as e:
                print(f"[Backend] Error creating agents for room {room_id}: {str(e)}")
            
            # Get room metadata (if available)
            room_metadata = getattr(room, 'metadata', {})
            room_name = room_metadata.get('name') or room_metadata.get('room_name') or room_id
            topic_category = room_metadata.get('topic_category') or topic.get("category")
            cefr_level = room_metadata.get('cefr_level', 0)
            
            # Convert CEFR level string to integer if needed
            if isinstance(cefr_level, str):
                cefr_map = {'A1': 1, 'A2': 2, 'B1': 3, 'B2': 4, 'C1': 5, 'C2': 6}
                cefr_level = cefr_map.get(cefr_level, 0)
            
            # Save room to database
            await db.save_room({
                "room_id": room_id,
                "room_name": room_name,
                "topic": topic,
                "participantCount": len(ready_participants),
                "startedAt": datetime.now().isoformat(),
                "endedAt": None,
                "durationSeconds": None,
                "roundsCompleted": 0,
                "status": "active",
                "cefr_level": cefr_level
            })
            
            # Save participants to database
            for participant in ready_participants:
                try:
                    await db.save_participant({
                        "user_id": participant.id,
                        "room_id": room_id,
                        "anonymousName": participant.anonymous_name,
                        "campus": participant.campus if hasattr(participant, 'campus') else None,
                        "location": participant.location if hasattr(participant, 'location') else None,
                        "joinedAt": participant.joined_at if hasattr(participant, 'joined_at') else datetime.now().isoformat(),
                        "leftAt": None,
                        "speakingTimeSeconds": 0
                    })
                except Exception as e:
                    print(f"[Backend] Error saving participant {participant.anonymous_name}: {str(e)}")
            
            # Record topic usage
            await db.record_topic_usage(topic)
            
            # Update room state
            from ..models.enums import RoomStatus
            room.status = RoomStatus.IN_PROGRESS
            room.topic = topic
            room.current_speaker_index = 0
            room.current_round = 1
            room.started_at = datetime.now().isoformat()
            
            # Get first speaker
            first_speaker = room.get_current_speaker()
            duration = int(os.getenv("DEFAULT_SPEAKING_TIME", "60"))
            room.speaking_time = duration
            room.time_remaining = duration
            
            # Emit discussion started
            await sio.emit("discussion-started", {
                "topic": topic,
                "firstSpeaker": first_speaker.to_dict() if first_speaker else None,
                "duration": duration
            }, room=room_id)
            
            # Emit turn-started for the first speaker
            if first_speaker:
                await sio.emit("turn-started", {
                    "speaker_index": 0,
                    "speaker": first_speaker.to_dict(),
                    "timer": duration
                }, room=room_id)
            
            # Start timer for the turn
            await start_turn_timer(sio, room_id, duration, active_rooms)
            
            print(f"[Backend] Discussion started with topic: {topic['title']}")
        else:
            print(f"[Backend] Discussion not ready yet - need {min_participants} participants, {len(ready_participants)} ready")
    except Exception as e:
        print(f"Error checking discussion start: {str(e)}")
        import traceback
        traceback.print_exc()


async def start_turn_timer(sio: socketio.AsyncServer, room_id: str, duration: int, active_rooms: Dict[str, str]):
    """
    Start a timer for the current turn
    Args:
        sio: Socket.io server instance
        room_id: Room identifier
        duration: Timer duration in seconds
        active_rooms: Active rooms map
    """
    
    async def on_warning(rid: str, time_remaining: int):
        """Called when warning threshold is reached"""
        await sio.emit("timer-warning", {
            "remaining": time_remaining
        }, room=rid)
        print(f"[Backend] Timer warning sent for room {rid}: {time_remaining}s remaining")
    
    async def on_complete(rid: str):
        """Called when timer completes"""
        print(f"[Backend] Timer completed for room {rid}, advancing turn")
        
        # Find the socket ID of any participant to trigger end_turn
        room = room_manager.get_room(rid)
        if room.participants:
            # Get current speaker
            current_speaker = room.get_current_speaker()
            if not current_speaker:
                return
            
            # Emit turn-ended event
            await sio.emit("turn-ended", {
                "speaker": current_speaker.to_dict()
            }, room=rid)
            
            # Advance to next speaker
            next_speaker = room.advance_turn()
            
            # Check if discussion is complete
            if room.status.value == "completed":
                print(f"[Backend] Discussion completed in room {rid}")
                
                # Update room in database
                room_id = active_rooms.get(rid)
                if room_id:
                    await db.update_room(room_id, {
                        "endedAt": datetime.now().isoformat(),
                        "roundsCompleted": room.current_round - 1
                    })
                    
                    # Remove from active rooms
                    del active_rooms[rid]
                
                # Emit discussion-ended event
                await sio.emit("discussion-ended", {
                    "roomId": room_id,
                    "roundsCompleted": room.current_round - 1
                }, room=rid)
                
                return
            
            # Check if round is complete
            if room.current_speaker_index == 0:
                await sio.emit("round-complete", {
                    "round": room.current_round - 1,
                    "next": room.current_round
                }, room=rid)
            
            # Emit turn-started for next speaker
            if next_speaker:
                await sio.emit("turn-started", {
                    "speaker_index": room.current_speaker_index,
                    "speaker": next_speaker.to_dict(),
                    "timer": room.speaking_time
                }, room=rid)
                
                print(f"[Backend] Next speaker: {next_speaker.anonymous_name}")
                
                # Start timer for next turn
                await start_turn_timer(sio, rid, room.speaking_time, active_rooms)
    
    # Start the timer
    await timer_manager.start_timer(
        room_id=room_id,
        duration=duration,
        on_warning=on_warning,
        on_complete=on_complete,
        warning_threshold=10
    )
