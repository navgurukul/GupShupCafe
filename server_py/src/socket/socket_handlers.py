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

from ..services.room_service import room_service
from .room_manager import room_manager
from .timer_manager import timer_manager
from ..ai.topic_generator import generate_discussion_topic
from ..database.database import db
from .room_manager import room_manager


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
        print(f"User disconnected: {sid}")
        
        # Find the room this socket was in
        rooms = sio.rooms(sid)
        for room_id in rooms:
            if room_id != sid:  # Skip the default room (socket's own room)
                # Get user data from room before removing
                room = room_manager.get_room(room_id)
                if not room:
                    continue
                user = room.get_participant_by_socket(sid)
                
                if user:
                    user_id = user.get("id")
                    anonymous_name = user.get("anonymousName")
                    was_host = room_manager.is_host(room_id, user_id)
                    was_current_speaker = room.is_current_speaker(user_id)
                    
                    # If current speaker disconnected, advance turn immediately
                    if was_current_speaker and room.status.value == "in_progress":
                        print(f"[Backend] Current speaker {anonymous_name} disconnected, advancing turn")
                        # Cancel current timer
                        await timer_manager.cancel_timer(room_id)
                        # Advance to next speaker
                        next_speaker = room.advance_turn()
                        if next_speaker:
                            await sio.emit("turn-started", {
                                "speaker_index": room.current_speaker_index,
                                "speaker": next_speaker,
                                "timer": room.speaking_time
                            }, room=room_id)
                            # Start timer for next speaker
                            await start_turn_timer(sio, room_id, room.speaking_time, active_rooms)
                        else:
                            # No more speakers, end discussion
                            await sio.emit("discussion-ended", {
                                "roomId": room_id,
                                "reason": "no_speakers_available"
                            }, room=room_id)
                    
                    # Preserve host state if this user was the host
                    if was_host:
                        room_service.preserve_host_state(room_id, user_id)
                        print(f"[Backend] Host {anonymous_name} disconnected, preserving host state")

                    room_service.remove_user_from_room(room_id, user_id)

                    # Get updated participants
                    participants = room_manager.get_room_participants(room_id)

                    # If the host left and there are still participants, assign a new host
                    new_host = None
                    if was_host and participants:
                        new_host = room_service.assign_new_host(room_id)
                        if new_host:
                            print(f"[Backend] Assigned new host: {new_host.get('anonymousName', 'Unknown')}")
                    
                    # Notify others
                    await sio.emit("participants-update", participants, room=room_id)
                    await sio.emit("participant-left", {
                        "participantId": user_id,
                        "anonymousName": anonymous_name,
                        "wasHost": was_host,
                        "newHost": new_host.get("id") if new_host else None
                    }, room=room_id)
                    
                    # If a new host was assigned, notify about host change
                    if new_host:
                        await sio.emit("host-changed", {
                            "newHost": new_host,
                            "previousHost": anonymous_name
                        }, room=room_id)
                    
                    print(f"[Backend] {anonymous_name} disconnected from room {room_id}")
                    
                    # Clean up empty rooms immediately
                    if len(participants) == 0:
                        print(f"[Backend] Room {room_id} is now empty, cleaning up...")
                        room_service.cleanup_room(room_id)
    
    @sio.on('join-room')
    async def join_room(sid, *args):
        """Handle user joining a room with atomic operations"""
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
            
            # Use room-level lock to prevent race conditions
            room_lock_key = f"room_lock_{room_id}"
            if not hasattr(join_room, '_locks'):
                join_room._locks = {}
            
            if room_lock_key not in join_room._locks:
                join_room._locks[room_lock_key] = asyncio.Lock()
            
            async with join_room._locks[room_lock_key]:
                # Get auth data from session
                try:
                    session = await sio.get_session(sid)
                    auth_data = session.get("auth", {}) if session else {}
                except:
                    auth_data = {}
                
                # Use clientUserData if provided, else fallback to auth
                if client_user_data and client_user_data.get("userId"):
                    effective_user_data = {
                        "id": client_user_data.get("userId"),
                        "socketId": sid,
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
                        "socketId": sid,
                        "name": auth_data.get("name"),
                        "campus": auth_data.get("campus"),
                        "location": auth_data.get("location"),
                        "anonymousName": auth_data.get("anonymousName"),
                        "role": auth_data.get("role", "listener"),
                        "isReady": False,
                        "joinedAt": datetime.now().isoformat()
                    }
                
                print(f"[Backend] {effective_user_data['anonymousName']} joining room: {room_id}")
                
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
                            room_manager.remove_user_from_room(room, old_user.get("id"))
                
                # Join the new room
                await sio.enter_room(sid, room_id)
                print(f"[Backend] Joined new room: {room_id}")
                
                # Check if user already exists in room (reconnection case)
                existing_user = room_manager.get_participant_by_id(room_id, effective_user_data["id"])
                
                if existing_user:
                    # Update existing user's socket ID and preserve their state
                    print(f"[Backend] User {effective_user_data['anonymousName']} reconnecting to room {room_id}")
                    print(f"[Backend] Old socket ID: {existing_user.get('socketId')}, New socket ID: {sid}")
                    
                    # Store previous state for comparison
                    previous_ready = existing_user.get("isReady", False)
                    previous_role = existing_user.get("role", "listener")
                    
                    # Update socket ID and user data
                    existing_user["socketId"] = sid
                    existing_user["name"] = effective_user_data["name"]
                    existing_user["campus"] = effective_user_data["campus"]
                    existing_user["location"] = effective_user_data["location"]
                    
                    # Preserve existing ready status and role
                    print(f"[Backend] Preserved user state - ready: {previous_ready}, role: {previous_role}")
                    
                    # Check if this user should have host privileges restored
                    host_restored = room_manager.restore_host_privileges(room_id, effective_user_data["id"])
                    if host_restored:
                        print(f"[Backend] Restored host privileges for {effective_user_data['anonymousName']}")
                    
                    # Emit reconnection event to the user
                    await sio.emit("user-reconnected", {
                        "userId": effective_user_data["id"],
                        "anonymousName": effective_user_data["anonymousName"],
                        "wasHost": host_restored,
                        "preservedState": {
                            "isReady": previous_ready,
                            "role": previous_role
                        }
                    }, room=sid)
                    
                else:
                    # Add new user to room manager
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
                        "firstSpeaker": current_speaker if current_speaker else None,
                        "duration": room.speaking_time,
                        "currentSpeakerIndex": room.current_speaker_index,
                        "round": room.current_round
                    }
                    
                    await sio.emit("discussion-started", discussion_state, room=sid)
            
        except Exception as e:
            print(f"Error in join-room: {str(e)}")
            import traceback
            traceback.print_exc()
    
    @sio.on('start-discussion')
    async def start_discussion(sid, data=None):
        """Handle host starting discussion manually"""
        try:
            # Find room for this socket
            rooms = sio.rooms(sid)
            room_id = None
            for room in rooms:
                if room != sid:
                    room_id = room
                    break
            
            if not room_id:
                print(f"[Backend] No room found for start-discussion from {sid}")
                return
            
            # Get user from room by socket ID using room manager
            room = room_manager.get_room(room_id)
            if not room:
                print(f"[Backend] Room {room_id} not found in room manager")
                return
            user = room.get_participant_by_socket(sid)
            
            if not user:
                print(f"[Backend] No user found for socket {sid} in room {room_id}")
                return
            
            # Check if user is host using the room manager
            is_host = room_manager.is_host(room_id, user.get("id"))
            
            if not is_host:
                print(f"[Backend] User {user.get('anonymousName', 'Unknown')} is not host, cannot start discussion")
                return
            
            # Check if all participants are ready
            participants = room_manager.get_room_participants(room_id)
            ready_participants = [p for p in participants if p.get("isReady", False)]
            if len(ready_participants) < len(participants):
                print(f"[Backend] Not all participants are ready, cannot start discussion")
                return
            
            print(f"[Backend] Host {user.get('anonymousName', 'Unknown')} manually starting discussion in room {room_id}")
            
            # Start the discussion (force start even if not all ready)
            room._rest_api_trigger = True  # Allow manual start
            await check_and_start_discussion(sio, room_id, active_rooms)
            
        except Exception as e:
            print(f"Error in start-discussion: {str(e)}")
            import traceback
            traceback.print_exc()
    
    @sio.on('user-reconnection-ack')
    async def user_reconnection_ack(sid, data=None):
        """Handle user acknowledgment of successful reconnection"""
        try:
            # Find room for this socket
            rooms = sio.rooms(sid)
            room_id = None
            for room in rooms:
                if room != sid:
                    room_id = room
                    break
            
            if not room_id:
                print(f"[Backend] No room found for reconnection ack from {sid}")
                return
            
            # Get user from room by socket ID using room manager
            room = room_manager.get_room(room_id)
            if not room:
                print(f"[Backend] Room {room_id} not found in room manager")
                return
            user = room.get_participant_by_socket(sid)
            
            if user:
                print(f"[Backend] User {user.get('anonymousName', 'Unknown')} acknowledged reconnection in room {room_id}")
                
                # Get updated participants and emit to all
                participants = room_manager.get_room_participants(room_id)
                await sio.emit("participants-update", participants, room=room_id)
                
                # Notify others that user has reconnected
                await sio.emit("participant-reconnected", {
                    "participantId": user.get("id"),
                    "anonymousName": user.get("anonymousName"),
                    "socketId": sid
                }, room=room_id, skip_sid=sid)
            
        except Exception as e:
            print(f"Error in user-reconnection-ack: {str(e)}")
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
            
            # Get user from room by socket ID using room manager
            room = room_manager.get_room(room_id)
            if not room:
                print(f"[Backend] Room {room_id} not found in room manager")
                return
            user = room.get_participant_by_socket(sid)
            
            if not user:
                print(f"[Backend] No user found for socket {sid} in room {room_id}")
                return
            
            # Get ready status from data or default to True
            is_ready = True
            if data and isinstance(data, dict):
                is_ready = data.get("isReady", True)
            
            # Update user ready status in room manager
            room_manager.update_user(room_id, user.get("id"), {"isReady": is_ready})
            
            print(f"[Backend] {user.get('anonymousName', 'Unknown')} marked as ready={is_ready} in room {room_id}")
            
            # Get updated participants
            participants = room_manager.get_room_participants(room_id)
            ready_count = len([p for p in participants if p.get("isReady", False)])
            print(f"[Backend] Room {room_id} now has {len(participants)} total participants, {ready_count} ready")
            
            # Emit update to all in room
            await sio.emit("participants-update", participants, room=room_id)
            
            # Check if discussion can start (only if not already in progress)
            if room.status.value != "in_progress":
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
            if new_role == "speaker" and not room_service.can_become_speaker(room_id):
                await sio.emit("role-change-failed", {
                    "error": "Maximum number of speakers reached"
                }, room=sid)
                return
            
            # Change role
            success = room_service.change_user_role(room_id, user_id, new_role)
            
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
            
            # Get user data from room manager
            room = room_manager.get_room(room_id)
            if not room:
                return
            user = room.get_participant_by_socket(sid)
            
            if user:
                # Check if it's the user's turn to speak
                current_speaker = room.get_current_speaker()
                if not current_speaker or current_speaker.get("id") != user.get("id"):
                    await sio.emit("message-error", {
                        "error": "It's not your turn to speak"
                    }, room=sid)
                    return
                
                message_id = str(uuid.uuid4())
                message_obj = {
                    "id": message_id,
                    "userId": user.get("id"),
                    "anonymousName": user.get("anonymousName"),
                    "message": message_data,
                    "timestamp": datetime.now().isoformat(),
                    "round": room.current_round,
                    "turnOrder": room.current_speaker_index
                }
                
                # Save message to database using transcripts table
                await db.save_transcript({
                    "transcript_id": message_id,
                    "room_id": room_id,
                    "participant_id": user.get("id"),
                    "user_id": user.get("id"),
                    "round_number": room.current_round,
                    "turn_order": room.current_speaker_index,
                    "transcript_text": message_data,
                    "language": "en",
                    "stt_confidence": 1.0,  # Chat messages have 100% confidence
                    "started_at": datetime.now().isoformat(),
                    "ended_at": datetime.now().isoformat(),
                    "duration_seconds": 0,  # Chat messages are instant
                    "word_count": len(message_data.split()),
                    "speech_rate": 0,  # Not applicable for chat
                    "is_processed": 0
                })
                
                # Broadcast message to room
                await sio.emit("message", message_obj, room=room_id)
                print(f"[Backend] Chat message from {user.get('anonymousName')}: {message_data[:50]}...")
            
        except Exception as e:
            print(f"Error handling message: {str(e)}")
            import traceback
            traceback.print_exc()

    @sio.event
    async def send_round_messages_to_ai(sid, data):
        """Send all messages from current round to AI for analysis"""
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
            
            room = room_manager.get_room(room_id)
            if not room:
                return
            
            # Get all messages from current round using transcripts table
            round_messages = await db.get_transcripts_by_round(room_id, room.current_round)
            
            if round_messages:
                # Send to AI facilitator for analysis
                from ..services.agent_service import agent_service
                
                # Get facilitator agent for this room
                agents = await agent_service.get_agents_by_room(room_id)
                facilitator_agent = next((a for a in agents if a.agent_type == "facilitator"), None)
                
                if facilitator_agent:
                    # Generate AI response based on round messages
                    ai_response = await agent_service.analyze_round_messages(
                        facilitator_agent.agent_id,
                        round_messages,
                        room.current_round
                    )
                    
                    # Broadcast AI analysis to room
                    await sio.emit("ai-round-analysis", {
                        "round": room.current_round,
                        "analysis": ai_response,
                        "messageCount": len(round_messages),
                        "timestamp": datetime.now().isoformat()
                    }, room=room_id)
                    
                    print(f"[Backend] AI analyzed {len(round_messages)} messages from round {room.current_round}")
            
        except Exception as e:
            print(f"Error sending round messages to AI: {str(e)}")
            import traceback
            traceback.print_exc()
    
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
            if room:
                try:
                    participants = room_manager.get_room_participants(room_id)
                except Exception as e:
                    print(f"[Backend] Error getting participants: {e}")
                    participants = []

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
            
            # Check if room is active
            if room_id not in active_rooms:
                print(f"[Backend] No active room for room {room_id}")
                return
            
            # Save transcript to database using original room_id
            transcript_id = str(uuid.uuid4())
            await db.save_transcript({
                "id": transcript_id,
                "roomId": room_id,  # Use original room_id
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
            if not room:
                print(f"[Backend] Room {room_id} not found in room manager")
                return
            
            # Get current speaker
            current_speaker = room.get_current_speaker()
            if not current_speaker:
                print(f"[Backend] No current speaker in room {room_id}")
                return
            
            # Emit turn-ended event
            await sio.emit("turn-ended", {
                "speaker": current_speaker,
                "reason": "manual_end"
            }, room=room_id)
            
            # Advance to next speaker
            next_speaker = room.advance_turn()
            
            # Check if discussion is complete
            if room.status.value == "completed":
                print(f"[Backend] Discussion completed in room {room_id} after {room.current_round - 1} rounds")
                
                # Update room in database using the original room_id
                if room_id in active_rooms:
                    await db.update_room(room_id, {
                        "ended_at": datetime.now().isoformat(),
                        "rounds_completed": room.current_round - 1,
                        "status": "completed"
                    })
                    
                    # Remove from active rooms
                    del active_rooms[room_id]
                
                # Emit discussion-ended event
                await sio.emit("discussion-ended", {
                    "roomId": room_id,
                    "roundsCompleted": room.current_round - 1,
                    "reason": "rounds_completed"
                }, room=room_id)
                
                return
            
            # Check if we just started a new round
            if room.current_speaker_index == 0 and room.current_round > 1:
                await sio.emit("round-complete", {
                    "round": room.current_round - 1,
                    "next": room.current_round
                }, room=room_id)
            
            # Emit turn-started for next speaker
            if next_speaker:
                await sio.emit("turn-started", {
                    "speaker_index": room.current_speaker_index,
                    "speaker": next_speaker,
                    "timer": room.speaking_time,
                    "round": room.current_round
                }, room=room_id)
                
                print(f"[Backend] Next speaker: {next_speaker.get('anonymousName', 'Unknown')} (Round {room.current_round})")
                
                # Start timer for next turn
                await start_turn_timer(sio, room_id, room.speaking_time, active_rooms)
            else:
                print(f"[Backend] No next speaker available in room {room_id}")
                await sio.emit("discussion-ended", {
                    "roomId": room_id,
                    "reason": "no_speakers_available"
                }, room=room_id)
            
        except Exception as e:
            print(f"Error handling end-turn: {str(e)}")
            import traceback
            traceback.print_exc()
    
    @sio.event
    async def next_speaker(sid, data):
        """Handle request for next speaker (manual progression)"""
        try:
            # Find room for this socket
            rooms = sio.rooms(sid)
            room_id = None
            for room in rooms:
                if room != sid:
                    room_id = room
                    break
            
            if not room_id:
                print(f"[Backend] No room found for next-speaker from {sid}")
                return
            
            # Get user from room by socket ID using room manager
            room = room_manager.get_room(room_id)
            if not room:
                print(f"[Backend] Room {room_id} not found in room manager")
                return
            user = room.get_participant_by_socket(sid)
            
            if not user:
                print(f"[Backend] No user found for socket {sid} in room {room_id}")
                return
            
            # Check if user is host or current speaker
            is_host = room_manager.is_host(room_id, user.get("id"))
            is_current_speaker = room.is_current_speaker(user.get("id"))
            
            if not (is_host or is_current_speaker):
                print(f"[Backend] User {user.get('anonymousName', 'Unknown')} cannot advance turn (not host or current speaker)")
                return
            
            print(f"[Backend] {user.get('anonymousName', 'Unknown')} manually advancing to next speaker")
            
            # Reuse end_turn logic
            await end_turn(sid, data)
        except Exception as e:
            print(f"Error handling next-speaker: {str(e)}")
            import traceback
            traceback.print_exc()
    
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
            if not room:
                print(f"[Backend] Room {room_id} not found in room manager")
                return
            user = room.get_participant_by_socket(sid)
            
            if user:
                user_id = user.get("id")
                anonymous_name = user.get("anonymousName")
                was_host = room_service.is_host(room_id, user_id)
                
                # Preserve host state if this user was the host
                if was_host:
                    room_service.preserve_host_state(room_id, user_id)
                    print(f"[Backend] Host {anonymous_name} left, preserving host state")
                
                room_service.remove_user_from_room(room_id, user_id)
                
                # Leave socket.io room
                await sio.leave_room(sid, room_id)
                
                # Get updated participants
                participants = room_manager.get_room_participants(room_id)
                
                # If the host left and there are still participants, assign a new host
                new_host = None
                if was_host and participants:
                    new_host = room_service.assign_new_host(room_id)
                    if new_host:
                        print(f"[Backend] Assigned new host: {new_host.get('anonymousName', 'Unknown')}")
                
                # Notify others
                await sio.emit("participants-update", participants, room=room_id)
                await sio.emit("participant-left", {
                    "participantId": user_id,
                    "anonymousName": anonymous_name,
                    "wasHost": was_host,
                    "newHost": new_host.get("id") if new_host else None
                }, room=room_id)
                
                # If a new host was assigned, notify about host change
                if new_host:
                    await sio.emit("host-changed", {
                        "newHost": new_host,
                        "previousHost": anonymous_name
                    }, room=room_id)
                
                print(f"[Backend] {anonymous_name} left room {room_id}")
                
                # Clean up empty rooms immediately
                if len(participants) == 0:
                    print(f"[Backend] Room {room_id} is now empty, cleaning up...")
                    room_service.cleanup_room(room_id)
            
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
            if not room:
                print(f"[Backend] Room {room_id} not found in room manager")
                return
            user = room.get_participant_by_socket(sid)
            
            if not user:
                print(f"[Backend] No user found for socket {sid}")
                return
            
            # Save transcript to database
            transcript_id = str(uuid.uuid4())
            transcript_data = {
                "transcript_id": transcript_id,
                "room_id": room_id,
                "participant_id": participant_id or user.get("id"),
                "user_id": user.get("id"),
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
                "participantId": participant_id or user.get("id")
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
        if not room:
            return
        
        # Don't start if already active, but allow if we're triggering from REST API
        if room.status.value == "in_progress":
            # Check if this is a REST API trigger by looking for a special flag
            if not getattr(room, '_rest_api_trigger', False):
                return
        
        # Check if we have minimum participants ready
        min_participants = int(os.getenv("MIN_PARTICIPANTS", "1"))
        participants = room_manager.get_room_participants(room_id)
        ready_participants = [p for p in participants if p.get("isReady", False)]
        
        print(f"[Backend] Discussion check - Total participants: {len(participants)}, Ready: {len(ready_participants)}, Min required: {min_participants}")
        print(f"[Backend] Participant ready statuses: {[(p.get('anonymousName', 'Unknown'), p.get('isReady', False)) for p in participants]}")
        
        if len(ready_participants) >= min_participants:
            print(f"[Backend] Starting discussion in room {room_id}")
            
            # Generate or get topic based on room metadata
            room_metadata = getattr(room, 'metadata', {}) or {}
            topic_category = room_metadata.get('topic_category')
            
            # Generate topic using MCP tools if category is provided, otherwise use fallback
            if topic_category:
                try:
                    # Use MCP tools to generate topic based on category
                    topic = await generate_discussion_topic(category=topic_category)
                except Exception as e:
                    print(f"[Backend] Error generating topic with MCP: {str(e)}, using fallback")
                    topic = await generate_discussion_topic()
            else:
                topic = await generate_discussion_topic()
            
            # Use the original room_id for database storage (no separate active_room_id)
            # This ensures the facilitator agent's room_id matches the room users joined
            active_rooms[room_id] = room_id  # Map to itself for consistency
            
            # Get room metadata (if available)
            room_name = room_metadata.get('name') or room_metadata.get('room_name') or room_id
            cefr_level = room_metadata.get('cefr_level', 'A1')
            
            # Convert CEFR level to string format if needed
            if isinstance(cefr_level, int):
                cefr_map = {1: 'A1', 2: 'A2', 3: 'B1', 4: 'B2', 5: 'C1', 6: 'C2'}
                cefr_level = cefr_map.get(cefr_level, 'A1')
            
            # Update room in database with discussion start information
            # Extract topic title from topic dictionary
            topic_title = topic.get("title", "General Discussion") if isinstance(topic, dict) else str(topic)
            
            await db.update_room(room_id, {
                "room_name": room_name,
                "topic_title": topic_title,
                "participant_count": len(ready_participants),
                "started_at": datetime.now().isoformat(),
                "ended_at": None,
                "duration_seconds": None,
                "rounds_completed": 0,
                "status": "active",
                "cefr_level": cefr_level
            })
            
            # Create agents for this room using the original room_id
            from ..services.agent_service import agent_service
            try:
                agent_ids = await agent_service.create_room_agents(room_id, topic)
                print(f"[Backend] Created agents for room {room_id}: {agent_ids}")
                
                # Update the room record with the facilitator agent_id
                if agent_ids.get('facilitator_agent_id'):
                    await db.update_room(room_id, {"facilitator_agent_id": agent_ids['facilitator_agent_id']})
                    print(f"[Backend] Updated room {room_id} with facilitator agent {agent_ids['facilitator_agent_id']}")
                    
            except Exception as e:
                print(f"[Backend] Error creating agents for room {room_id}: {str(e)}")
                # Continue without agents - discussion can still proceed
            
            # Save participants to database using the original room_id
            for participant in ready_participants:
                try:
                    participant_data = {
                        "room_id": room_id,  # Use original room_id
                        "user_id": participant.get("id"),
                        "anonymous_name": participant.get("anonymousName"),
                        "avatar_color": None,  # Will be generated if needed
                        "role": participant.get("role", "participant"),
                        "is_ready": participant.get("isReady", False),
                        "turn_order": 0,  # Will be set based on speaking order
                        "is_speaking": False,
                        "is_muted": False,
                        "socket_id": participant.get("socketId"),
                        "starting_cefr_level": "A1",  # Default, should be from user profile
                        "ending_cefr_level": None,
                        "joined_at": datetime.fromisoformat(participant.get("joinedAt", datetime.now().isoformat()).replace('Z', '+00:00')),
                        "left_at": None,
                        "campusOrLocation": participant.get("campus") or participant.get("location"),
                        "speaking_time_seconds": 0
                    }
                    await db.save_participant(participant_data)
                except Exception as e:
                    print(f"[Backend] Error saving participant {participant.get('anonymousName', 'Unknown')}: {str(e)}")
            
            # Record topic usage
            await db.record_topic_usage(topic)
            
            # Update room state
            from ..models.enums import RoomStatus
            room.status = RoomStatus.IN_PROGRESS
            room.topic = {"title": topic_title, "category": topic_category or "general"}
            room.current_speaker_index = 0
            room.current_round = 1
            room.started_at = datetime.now().isoformat()
            
            # Ensure we have speakers before starting
            speakers = room.get_speakers()
            if not speakers:
                print(f"[Backend] No speakers available in room {room_id}, cannot start discussion")
                return
            
            # Get first speaker
            first_speaker = room.get_current_speaker()
            duration = int(os.getenv("DEFAULT_SPEAKING_TIME", "60"))
            room.speaking_time = duration
            room.time_remaining = duration
            
            print(f"[Backend] First speaker: {first_speaker.get('anonymousName', 'Unknown') if first_speaker else 'None'}")
            
            # Emit discussion started
            await sio.emit("discussion-started", {
                "topic": topic_title,
                "firstSpeaker": first_speaker if first_speaker else None,
                "duration": duration
            }, room=room_id)
            
            # Emit participants update to ensure frontend has latest participant data
            participants = room_manager.get_room_participants(room_id)
            await sio.emit("participants-update", participants, room=room_id)
            print("[Backend] Emitted participants-update after discussion started")
            
            # Emit turn-started for the first speaker
            if first_speaker:
                await sio.emit("turn-started", {
                    "speaker_index": 0,
                    "speaker": first_speaker,
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
        
        room = room_manager.get_room(rid)
        if not room:
            print(f"[Backend] Room {rid} not found during timer completion")
            return
            
        # Get current speaker before advancing
        current_speaker = room.get_current_speaker()
        if current_speaker:
            print(f"[Backend] Current speaker {current_speaker.get('anonymousName', 'Unknown')} time expired")
            
            # Emit turn-ended event for current speaker
            await sio.emit("turn-ended", {
                "speaker": current_speaker,
                "reason": "time_expired"
            }, room=rid)
        
        # Advance to next speaker
        next_speaker = room.advance_turn()
        
        # Check if discussion is complete (room.advance_turn sets status to COMPLETED)
        if room.status.value == "completed":
            print(f"[Backend] Discussion completed in room {rid} after {room.current_round - 1} rounds")
            
            # Update room in database
            if rid in active_rooms:
                await db.update_room(rid, {
                    "ended_at": datetime.now().isoformat(),
                    "rounds_completed": room.current_round - 1,
                    "status": "completed"
                })
                
                # Remove from active rooms
                del active_rooms[rid]
            
            # Emit discussion-ended event
            await sio.emit("discussion-ended", {
                "roomId": rid,
                "roundsCompleted": room.current_round - 1,
                "reason": "rounds_completed"
            }, room=rid)
            
            return
        
        # Check if we just started a new round
        if room.current_speaker_index == 0 and room.current_round > 1:
            await sio.emit("round-complete", {
                "round": room.current_round - 1,
                "next": room.current_round
            }, room=rid)
        
        # Start next turn if we have a speaker
        if next_speaker:
            await sio.emit("turn-started", {
                "speaker_index": room.current_speaker_index,
                "speaker": next_speaker,
                "timer": room.speaking_time,
                "round": room.current_round
            }, room=rid)
            
            print(f"[Backend] Next speaker: {next_speaker.get('anonymousName', 'Unknown')} (Round {room.current_round})")
            
            # Start timer for next turn
            await start_turn_timer(sio, rid, room.speaking_time, active_rooms)
        else:
            print(f"[Backend] No next speaker available in room {rid}")
            await sio.emit("discussion-ended", {
                "roomId": rid,
                "reason": "no_speakers_available"
            }, room=rid)
    
    # Start the timer
    await timer_manager.start_timer(
        room_id=room_id,
        duration=duration,
        on_warning=on_warning,
        on_complete=on_complete,
        warning_threshold=10
    )

    # WebRTC Connection State Events
    @sio.on('webrtc-connection-state')
    async def webrtc_connection_state(sid, data):
        """Handle WebRTC connection state updates"""
        try:
            room_id = data.get('roomId')
            state = data.get('state')
            peer_id = data.get('peerId')
            
            if room_id:
                await sio.emit('webrtc-connection-state', {
                    'peerId': peer_id,
                    'state': state,
                    'timestamp': datetime.now().isoformat()
                }, room=room_id)
        except Exception as e:
            print(f"Error handling webrtc-connection-state: {str(e)}")

    @sio.on('webrtc-connection-failed')
    async def webrtc_connection_failed(sid, data):
        """Handle WebRTC connection failures"""
        try:
            room_id = data.get('roomId')
            peer_id = data.get('peerId')
            error = data.get('error')
            
            if room_id:
                await sio.emit('webrtc-connection-failed', {
                    'peerId': peer_id,
                    'error': error,
                    'timestamp': datetime.now().isoformat()
                }, room=room_id)
        except Exception as e:
            print(f"Error handling webrtc-connection-failed: {str(e)}")

    @sio.on('webrtc-connection-restored')
    async def webrtc_connection_restored(sid, data):
        """Handle WebRTC connection restoration"""
        try:
            room_id = data.get('roomId')
            peer_id = data.get('peerId')
            
            if room_id:
                await sio.emit('webrtc-connection-restored', {
                    'peerId': peer_id,
                    'timestamp': datetime.now().isoformat()
                }, room=room_id)
        except Exception as e:
            print(f"Error handling webrtc-connection-restored: {str(e)}")

    @sio.on('webrtc-connection-closed')
    async def webrtc_connection_closed(sid, data):
        """Handle WebRTC connection closure"""
        try:
            room_id = data.get('roomId')
            peer_id = data.get('peerId')
            
            if room_id:
                await sio.emit('webrtc-connection-closed', {
                    'peerId': peer_id,
                    'timestamp': datetime.now().isoformat()
                }, room=room_id)
        except Exception as e:
            print(f"Error handling webrtc-connection-closed: {str(e)}")

    @sio.on('webrtc-peer-disconnected')
    async def webrtc_peer_disconnected(sid, data):
        """Handle WebRTC peer disconnection"""
        try:
            room_id = data.get('roomId')
            peer_id = data.get('peerId')
            
            if room_id:
                await sio.emit('webrtc-peer-disconnected', {
                    'peerId': peer_id,
                    'timestamp': datetime.now().isoformat()
                }, room=room_id)
        except Exception as e:
            print(f"Error handling webrtc-peer-disconnected: {str(e)}")

    @sio.on('webrtc-cleanup-request')
    async def webrtc_cleanup_request(sid, data):
        """Handle WebRTC cleanup requests"""
        try:
            room_id = data.get('roomId')
            peer_id = data.get('peerId')
            
            if room_id:
                await sio.emit('webrtc-cleanup-request', {
                    'peerId': peer_id,
                    'timestamp': datetime.now().isoformat()
                }, room=room_id)
        except Exception as e:
            print(f"Error handling webrtc-cleanup-request: {str(e)}")

    @sio.on('webrtc-connection-test')
    async def webrtc_connection_test(sid, data):
        """Handle WebRTC connection testing"""
        try:
            room_id = data.get('roomId')
            peer_id = data.get('peerId')
            
            if room_id:
                await sio.emit('webrtc-connection-test', {
                    'peerId': peer_id,
                    'timestamp': datetime.now().isoformat()
                }, room=room_id)
        except Exception as e:
            print(f"Error handling webrtc-connection-test: {str(e)}")

    @sio.on('webrtc-connection-verified')
    async def webrtc_connection_verified(sid, data):
        """Handle WebRTC connection verification"""
        try:
            room_id = data.get('roomId')
            peer_id = data.get('peerId')
            
            if room_id:
                await sio.emit('webrtc-connection-verified', {
                    'peerId': peer_id,
                    'timestamp': datetime.now().isoformat()
                }, room=room_id)
        except Exception as e:
            print(f"Error handling webrtc-connection-verified: {str(e)}")

    @sio.on('webrtc-error')
    async def webrtc_error(sid, data):
        """Handle WebRTC errors"""
        try:
            room_id = data.get('roomId')
            peer_id = data.get('peerId')
            error = data.get('error')
            
            if room_id:
                await sio.emit('webrtc-error', {
                    'peerId': peer_id,
                    'error': error,
                    'timestamp': datetime.now().isoformat()
                }, room=room_id)
        except Exception as e:
            print(f"Error handling webrtc-error: {str(e)}")

    @sio.on('webrtc-stats-update')
    async def webrtc_stats_update(sid, data):
        """Handle WebRTC statistics updates"""
        try:
            room_id = data.get('roomId')
            peer_id = data.get('peerId')
            stats = data.get('stats')
            
            if room_id:
                await sio.emit('webrtc-stats-update', {
                    'peerId': peer_id,
                    'stats': stats,
                    'timestamp': datetime.now().isoformat()
                }, room=room_id)
        except Exception as e:
            print(f"Error handling webrtc-stats-update: {str(e)}")

    @sio.on('webrtc-quality-warning')
    async def webrtc_quality_warning(sid, data):
        """Handle WebRTC quality warnings"""
        try:
            room_id = data.get('roomId')
            peer_id = data.get('peerId')
            warning = data.get('warning')
            
            if room_id:
                await sio.emit('webrtc-quality-warning', {
                    'peerId': peer_id,
                    'warning': warning,
                    'timestamp': datetime.now().isoformat()
                }, room=room_id)
        except Exception as e:
            print(f"Error handling webrtc-quality-warning: {str(e)}")

    # Audio State Events
    @sio.on('audio-state-change')
    async def audio_state_change(sid, data):
        """Handle audio state changes"""
        try:
            room_id = data.get('roomId')
            state = data.get('state')
            user_id = data.get('userId')
            
            if room_id:
                await sio.emit('audio-state-change', {
                    'userId': user_id,
                    'state': state,
                    'timestamp': datetime.now().isoformat()
                }, room=room_id)
        except Exception as e:
            print(f"Error handling audio-state-change: {str(e)}")

    @sio.on('audio-level-update')
    async def audio_level_update(sid, data):
        """Handle audio level updates"""
        try:
            room_id = data.get('roomId')
            level = data.get('level')
            user_id = data.get('userId')
            
            if room_id:
                await sio.emit('audio-level-update', {
                    'userId': user_id,
                    'level': level,
                    'timestamp': datetime.now().isoformat()
                }, room=room_id)
        except Exception as e:
            print(f"Error handling audio-level-update: {str(e)}")

    @sio.on('microphone-permission-change')
    async def microphone_permission_change(sid, data):
        """Handle microphone permission changes"""
        try:
            room_id = data.get('roomId')
            permission = data.get('permission')
            user_id = data.get('userId')
            
            if room_id:
                await sio.emit('microphone-permission-change', {
                    'userId': user_id,
                    'permission': permission,
                    'timestamp': datetime.now().isoformat()
                }, room=room_id)
        except Exception as e:
            print(f"Error handling microphone-permission-change: {str(e)}")

    # WebRTC Acknowledgment Events
    @sio.on('webrtc-offer-ack')
    async def webrtc_offer_ack(sid, data):
        """Handle WebRTC offer acknowledgments"""
        try:
            room_id = data.get('roomId')
            peer_id = data.get('peerId')
            
            if room_id:
                await sio.emit('webrtc-offer-ack', {
                    'peerId': peer_id,
                    'timestamp': datetime.now().isoformat()
                }, room=room_id)
        except Exception as e:
            print(f"Error handling webrtc-offer-ack: {str(e)}")

    @sio.on('webrtc-answer-ack')
    async def webrtc_answer_ack(sid, data):
        """Handle WebRTC answer acknowledgments"""
        try:
            room_id = data.get('roomId')
            peer_id = data.get('peerId')
            
            if room_id:
                await sio.emit('webrtc-answer-ack', {
                    'peerId': peer_id,
                    'timestamp': datetime.now().isoformat()
                }, room=room_id)
        except Exception as e:
            print(f"Error handling webrtc-answer-ack: {str(e)}")

    @sio.on('webrtc-ice-ack')
    async def webrtc_ice_ack(sid, data):
        """Handle WebRTC ICE candidate acknowledgments"""
        try:
            room_id = data.get('roomId')
            peer_id = data.get('peerId')
            
            if room_id:
                await sio.emit('webrtc-ice-ack', {
                    'peerId': peer_id,
                    'timestamp': datetime.now().isoformat()
                }, room=room_id)
        except Exception as e:
            print(f"Error handling webrtc-ice-ack: {str(e)}")

    # WebRTC Lifecycle Events
    @sio.on('webrtc-connection-created')
    async def webrtc_connection_created(sid, data):
        """Handle WebRTC connection creation"""
        try:
            room_id = data.get('roomId')
            peer_id = data.get('peerId')
            
            if room_id:
                await sio.emit('webrtc-connection-created', {
                    'peerId': peer_id,
                    'timestamp': datetime.now().isoformat()
                }, room=room_id)
        except Exception as e:
            print(f"Error handling webrtc-connection-created: {str(e)}")

    @sio.on('webrtc-connection-destroyed')
    async def webrtc_connection_destroyed(sid, data):
        """Handle WebRTC connection destruction"""
        try:
            room_id = data.get('roomId')
            peer_id = data.get('peerId')
            
            if room_id:
                await sio.emit('webrtc-connection-destroyed', {
                    'peerId': peer_id,
                    'timestamp': datetime.now().isoformat()
                }, room=room_id)
        except Exception as e:
            print(f"Error handling webrtc-connection-destroyed: {str(e)}")

    @sio.on('webrtc-connection-paused')
    async def webrtc_connection_paused(sid, data):
        """Handle WebRTC connection pausing"""
        try:
            room_id = data.get('roomId')
            peer_id = data.get('peerId')
            
            if room_id:
                await sio.emit('webrtc-connection-paused', {
                    'peerId': peer_id,
                    'timestamp': datetime.now().isoformat()
                }, room=room_id)
        except Exception as e:
            print(f"Error handling webrtc-connection-paused: {str(e)}")

    @sio.on('webrtc-connection-resumed')
    async def webrtc_connection_resumed(sid, data):
        """Handle WebRTC connection resuming"""
        try:
            room_id = data.get('roomId')
            peer_id = data.get('peerId')
            
            if room_id:
                await sio.emit('webrtc-connection-resumed', {
                    'peerId': peer_id,
                    'timestamp': datetime.now().isoformat()
                }, room=room_id)
        except Exception as e:
            print(f"Error handling webrtc-connection-resumed: {str(e)}")
