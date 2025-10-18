"""
Socket.io Event Handlers
Manages real-time communication for the roundtable discussions
"""

import socketio
from typing import Dict, Any
from datetime import datetime
import uuid
import os

from .room_manager import room_manager
from .timer_manager import timer_manager
from ..ai.topic_generator import generate_discussion_topic
from ..database.database import db


async def setup_socket_handlers(sio: socketio.AsyncServer):
    """
    Setup Socket.io event handlers
    Args:
        sio: Socket.io server instance
    """
    
    # In-memory map of active session ids per room
    active_sessions: Dict[str, str] = {}
    
    @sio.event
    async def connect(sid, environ, auth):
        """Handle client connection"""
        print(f"[Backend] Socket connected: {sid}")
        print(f"[Backend] Handshake auth: {auth}")
        
        # Save auth data to session so it can be retrieved in join_room
        if auth:
            await sio.save_session(sid, {'auth': auth})
    
    @sio.event
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
    
    @sio.event
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
            session = await sio.get_session(sid)
            auth_data = session.get("auth", {}) if session else {}
            
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
            
            print(f"[Backend] 📥 {effective_user_data['anonymousName']} joining room: {room_id}")
            
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
                # Store room metadata for later use when creating session
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
    
    @sio.event
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
            await check_and_start_discussion(sio, room_id, active_sessions)
            
        except Exception as e:
            print(f"Error in user-ready: {str(e)}")
            import traceback
            traceback.print_exc()
    
    @sio.event
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
            
            # Get session ID
            session_id = active_sessions.get(room_id)
            if not session_id:
                print(f"[Backend] No active session for room {room_id}")
                return
            
            # Save transcript to database
            transcript_id = str(uuid.uuid4())
            await db.save_transcript({
                "id": transcript_id,
                "sessionId": session_id,
                "participantId": speaker_id,
                "text": text,
                "timestamp": datetime.now().isoformat()
            })
            
            print(f"[Backend] Saved transcript for session {session_id}: {text[:50]}...")
            
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
                
                # Update session in database
                session_id = active_sessions.get(room_id)
                if session_id:
                    await db.update_session(session_id, {
                        "endedAt": datetime.now().isoformat(),
                        "roundsCompleted": room.current_round - 1
                    })
                    
                    # Remove from active sessions
                    del active_sessions[room_id]
                
                # Emit discussion-ended event
                await sio.emit("discussion-ended", {
                    "sessionId": session_id,
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
                await start_turn_timer(sio, room_id, room.speaking_time, active_sessions)
            
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


async def check_and_start_discussion(sio: socketio.AsyncServer, room_id: str, active_sessions: Dict[str, str]):
    """
    Check if discussion can start
    Args:
        sio: Socket.io server instance
        room_id: Room identifier
        active_sessions: Active sessions map
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
            
            # Create session
            session_id = str(uuid.uuid4())
            active_sessions[room_id] = session_id
            
            # Get room metadata (if available)
            room_metadata = getattr(room, 'metadata', {})
            room_name = room_metadata.get('name') or room_metadata.get('room_name') or room_id
            topic_category = room_metadata.get('topic_category') or topic.get("category")
            cefr_level = room_metadata.get('cefr_level', 0)
            
            # Convert CEFR level string to integer if needed
            if isinstance(cefr_level, str):
                cefr_map = {'A1': 1, 'A2': 2, 'B1': 3, 'B2': 4, 'C1': 5, 'C2': 6}
                cefr_level = cefr_map.get(cefr_level, 0)
            
            # Save session to database
            await db.save_session({
                "session_id": session_id,
                "room_id": room_id,
                "room_name": room_name,
                "topic": topic,
                "participantCount": len(ready_participants),
                "startedAt": datetime.now().isoformat(),
                "endedAt": None,
                "durationSeconds": None,
                "roundsCompleted": 0,
                "status": "active",
                "crf_level": cefr_level
            })
            
            # Save participants to database
            for participant in ready_participants:
                try:
                    await db.save_participant({
                        "user_id": participant.id,
                        "session_id": session_id,
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
            await start_turn_timer(sio, room_id, duration, active_sessions)
            
            print(f"[Backend] Discussion started with topic: {topic['title']}")
        else:
            print(f"[Backend] Discussion not ready yet - need {min_participants} participants, {len(ready_participants)} ready")
    except Exception as e:
        print(f"Error checking discussion start: {str(e)}")
        import traceback
        traceback.print_exc()


async def start_turn_timer(sio: socketio.AsyncServer, room_id: str, duration: int, active_sessions: Dict[str, str]):
    """
    Start a timer for the current turn
    Args:
        sio: Socket.io server instance
        room_id: Room identifier
        duration: Timer duration in seconds
        active_sessions: Active sessions map
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
                
                # Update session in database
                session_id = active_sessions.get(rid)
                if session_id:
                    await db.update_session(session_id, {
                        "endedAt": datetime.now().isoformat(),
                        "roundsCompleted": room.current_round - 1
                    })
                    
                    # Remove from active sessions
                    del active_sessions[rid]
                
                # Emit discussion-ended event
                await sio.emit("discussion-ended", {
                    "sessionId": session_id,
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
                await start_turn_timer(sio, rid, room.speaking_time, active_sessions)
    
    # Start the timer
    await timer_manager.start_timer(
        room_id=room_id,
        duration=duration,
        on_warning=on_warning,
        on_complete=on_complete,
        warning_threshold=10
    )
