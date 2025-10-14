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
from ..ai.topic_generator import generate_discussion_topic
from ..ai.llm_agent_service import llm_agent_service
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
                user = next((p for p in room["participants"] if p["socketId"] == sid), None)
                
                if user:
                    user_id = user["id"]
                    room_manager.remove_user_from_room(room_id, user_id)
                    
                    # Get updated participants
                    participants = room_manager.get_room_participants(room_id)
                    
                    # Notify others
                    await sio.emit("participants-update", participants, room=room_id)
                    await sio.emit("user-left", {
                        "userId": user_id,
                        "anonymousName": user.get("anonymousName")
                    }, room=room_id)
    
    @sio.event
    async def join_room(sid, *args):
        """Handle user joining a room"""
        try:
            # Robustly extract roomId and clientUserData
            room_id = "general"
            client_user_data = None
            
            print(f"[Backend] join-room args: {args}")
            
            if len(args) > 0 and isinstance(args[0], str):
                room_id = args[0]
            if len(args) > 1 and isinstance(args[1], dict):
                client_user_data = args[1]
            
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
                    old_user = next((p for p in old_room["participants"] if p["socketId"] == sid), None)
                    if old_user:
                        room_manager.remove_user_from_room(room, old_user["id"])
            
            # Join the new room
            await sio.enter_room(sid, room_id)
            print(f"[Backend] Joined new room: {room_id}")
            
            # Add user to room manager
            room_manager.add_user_to_room(room_id, effective_user_data)
            
            # Get updated participants
            participants = room_manager.get_room_participants(room_id)
            
            # Emit participants update to all users in the room
            await sio.emit("participants-update", participants, room=room_id)
            print("[Backend] Emitted participants-update")
            
            # Check if there's an active discussion and sync state
            room = room_manager.get_room(room_id)
            if room["discussion"]["active"]:
                print(f"[Backend] Syncing active discussion state with {effective_user_data['anonymousName']}")
                
                discussion = room["discussion"]
                first_speaker = None
                if room["participants"]:
                    speaker_idx = discussion.get("currentSpeakerIndex", 0)
                    if 0 <= speaker_idx < len(room["participants"]):
                        first_speaker = room["participants"][speaker_idx]
                
                discussion_state = {
                    "topic": discussion["topic"],
                    "firstSpeaker": first_speaker,
                    "duration": discussion["speakingTime"],
                    "currentSpeakerIndex": discussion.get("currentSpeakerIndex", 0),
                    "round": discussion.get("round", 1)
                }
                
                await sio.emit("discussion-started", discussion_state, room=sid)
            
        except Exception as e:
            print(f"Error in join-room: {str(e)}")
            import traceback
            traceback.print_exc()
    
    @sio.event
    async def user_ready(sid, data):
        """Handle user ready status"""
        try:
            user_id = data.get("userId")
            is_ready = data.get("isReady", True)
            
            # Find room for this socket
            rooms = sio.rooms(sid)
            room_id = None
            for room in rooms:
                if room != sid:
                    room_id = room
                    break
            
            if not room_id:
                return
            
            # Update user ready status
            room_manager.update_user(room_id, user_id, {"isReady": is_ready})
            
            # Get updated participants
            participants = room_manager.get_room_participants(room_id)
            
            # Emit update to all in room
            await sio.emit("participants-update", participants, room=room_id)
            
            # Check if discussion can start
            await check_and_start_discussion(sio, room_id, active_sessions)
            
        except Exception as e:
            print(f"Error in user-ready: {str(e)}")
    
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
                # Record statement for LLM agent if enabled
                if llm_agent_service.is_enabled():
                    llm_agent_service.add_statement(
                        room_id,
                        user["anonymousName"],
                        message_data
                    )
                
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
    async def request_agent_response(sid, data):
        """Handle request for LLM agent response"""
        try:
            if not llm_agent_service.is_enabled():
                await sio.emit("agent-response-error", {
                    "error": "LLM Agent is not enabled"
                }, room=sid)
                return
            
            # Find room for this socket
            rooms = sio.rooms(sid)
            room_id = None
            for room in rooms:
                if room != sid:
                    room_id = room
                    break
            
            if not room_id:
                return
            
            # Get room data
            room = room_manager.get_room(room_id)
            topic = room["discussion"].get("topic")
            
            if not topic:
                return
            
            # Generate agent response
            response = await llm_agent_service.generate_response(room_id, topic)
            
            # Broadcast agent response to room
            await sio.emit("agent-response", response, room=room_id)
            
            print(f"[Backend] 🤖 LLM Agent responded in room {room_id}")
            
        except Exception as e:
            print(f"Error generating agent response: {str(e)}")
            import traceback
            traceback.print_exc()
    
    @sio.event
    async def speaker_turn_changed(sid, data):
        """Handle when speaker turn changes - trigger agent if it's their turn"""
        try:
            if not llm_agent_service.is_enabled():
                return
            
            current_speaker = data.get("currentSpeaker")
            if not current_speaker:
                return
            
            # Check if it's the agent's turn
            if current_speaker.get("isAgent"):
                # Find room
                rooms = sio.rooms(sid)
                room_id = None
                for room in rooms:
                    if room != sid:
                        room_id = room
                        break
                
                if not room_id:
                    return
                
                # Get room data
                room = room_manager.get_room(room_id)
                topic = room["discussion"].get("topic")
                
                if not topic:
                    return
                
                # Generate and send agent response automatically
                response = await llm_agent_service.generate_response(room_id, topic)
                
                # Broadcast agent response
                await sio.emit("agent-response", response, room=room_id)
                
                print(f"[Backend] 🤖 LLM Agent spoke in room {room_id}")
        
        except Exception as e:
            print(f"Error in speaker turn change: {str(e)}")
            import traceback
            traceback.print_exc()



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
        if room["discussion"]["active"]:
            return
        
        # Check if we have minimum participants ready
        min_participants = int(os.getenv("MIN_PARTICIPANTS", "1"))
        ready_participants = [p for p in room["participants"] if p.get("isReady") and not p.get("isAgent")]
        
        if len(ready_participants) >= min_participants and len(ready_participants) >= min_participants:
            print(f"[Backend] Starting discussion in room {room_id}")
            
            # Generate or get topic
            topic = await generate_discussion_topic()
            
            # Add LLM Agent as participant if enabled
            if llm_agent_service.is_enabled():
                agent_participant = llm_agent_service.get_agent_participant()
                room_manager.add_user_to_room(room_id, agent_participant)
                print(f"[Backend] 🤖 Added LLM Agent to room {room_id}")
                
                # Initialize agent for this room
                llm_agent_service.initialize_room(room_id, topic, ready_participants)
            
            # Get all participants including agent
            all_participants = room_manager.get_room_participants(room_id)
            ready_all = [p for p in all_participants if p.get("isReady")]
            
            # Create session
            session_id = str(uuid.uuid4())
            active_sessions[room_id] = session_id
            
            # Save session to database
            await db.save_session({
                "id": session_id,
                "roomId": room_id,
                "topic": topic,
                "participantCount": len(ready_participants),  # Count human participants only
                "startedAt": datetime.now().isoformat(),
                "endedAt": None,
                "durationSeconds": None,
                "roundsCompleted": 0
            })
            
            # Record topic usage
            await db.record_topic_usage(topic)
            
            # Update room state
            room["discussion"]["active"] = True
            room["discussion"]["topic"] = topic
            room["discussion"]["currentSpeakerIndex"] = 0
            room["discussion"]["round"] = 1
            room["discussion"]["startedAt"] = datetime.now().isoformat()
            
            # Notify all participants including agent
            await sio.emit("participants-update", all_participants, room=room_id)
            
            # Emit discussion started
            first_speaker = ready_all[0] if ready_all else None
            duration = int(os.getenv("DEFAULT_SPEAKING_TIME", "60"))
            
            await sio.emit("discussion-started", {
                "topic": topic,
                "firstSpeaker": first_speaker,
                "duration": duration
            }, room=room_id)
            
            print(f"[Backend] Discussion started with topic: {topic['title']}")
        else:
            print(f"[Backend] Discussion not ready yet - need {min_participants} participants, {len(ready_participants)} ready")
    except Exception as e:
        print(f"Error checking discussion start: {str(e)}")
        import traceback
        traceback.print_exc()
