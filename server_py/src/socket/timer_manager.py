"""
Timer Manager
Manages speaking timers for discussions
"""

import asyncio
from typing import Dict, Optional, Callable
from datetime import datetime


class TimerManager:
    """Manages turn-based speaking timers"""
    
    def __init__(self):
        self.active_timers: Dict[str, asyncio.Task] = {}
        self.timer_callbacks: Dict[str, Callable] = {}
    
    async def start_timer(
        self,
        room_id: str,
        duration: int,
        on_tick: Optional[Callable] = None,
        on_warning: Optional[Callable] = None,
        on_complete: Optional[Callable] = None,
        warning_threshold: int = 10
    ):
        """
        Start a timer for a room
        Args:
            room_id: Room identifier
            duration: Timer duration in seconds
            on_tick: Callback for each second (optional)
            on_warning: Callback when warning threshold is reached
            on_complete: Callback when timer completes
            warning_threshold: Seconds remaining to trigger warning (default: 10)
        """
        # Validate inputs
        if not room_id or not isinstance(room_id, str):
            raise ValueError("room_id must be a non-empty string")
        if not isinstance(duration, int) or duration <= 0:
            raise ValueError("duration must be a positive integer")
        if not isinstance(warning_threshold, int) or warning_threshold < 0:
            raise ValueError("warning_threshold must be a non-negative integer")
        if warning_threshold >= duration:
            raise ValueError("warning_threshold must be less than duration")
        
        # Cancel existing timer if any
        await self.cancel_timer(room_id)
        
        # Validate room exists and has participants before starting timer
        from .room_manager import room_manager
        room = room_manager.get_room(room_id)
        if not room or not room.participants:
            print(f"[TimerManager] Cannot start timer for room {room_id}: room empty or not found")
            return
        
        async def timer_task():
            try:
                time_remaining = duration
                warning_sent = False
                
                while time_remaining > 0:
                    await asyncio.sleep(1)
                    time_remaining -= 1
                    
                    # Call tick callback
                    if on_tick:
                        await on_tick(room_id, time_remaining)
                    
                    # Send warning at threshold
                    if time_remaining <= warning_threshold and not warning_sent:
                        warning_sent = True
                        if on_warning:
                            await on_warning(room_id, time_remaining)
                    
                    # Check if timer was cancelled
                    if room_id not in self.active_timers:
                        print(f"[TimerManager] Timer for room {room_id} was cancelled")
                        return
                
                # Timer completed
                if on_complete:
                    await on_complete(room_id)
                
                # Clean up
                if room_id in self.active_timers:
                    del self.active_timers[room_id]
                    
            except asyncio.CancelledError:
                print(f"[TimerManager] Timer task for room {room_id} cancelled")
            except Exception as e:
                print(f"[TimerManager] Error in timer task for room {room_id}: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Create and store the timer task
        task = asyncio.create_task(timer_task())
        self.active_timers[room_id] = task
        
        print(f"[TimerManager] Started timer for room {room_id}: {duration} seconds")
    
    async def cancel_timer(self, room_id: str) -> bool:
        """
        Cancel the timer for a room
        Args:
            room_id: Room identifier
        Returns: True if timer was cancelled, False if no timer was active
        """
        if room_id in self.active_timers:
            task = self.active_timers[room_id]
            task.cancel()
            
            try:
                await task
            except asyncio.CancelledError:
                pass
            
            del self.active_timers[room_id]
            print(f"[TimerManager] Cancelled timer for room {room_id}")
            return True
        
        return False
    
    def is_timer_active(self, room_id: str) -> bool:
        """
        Check if a timer is active for a room
        Args:
            room_id: Room identifier
        Returns: True if timer is active
        """
        return room_id in self.active_timers
    
    async def cancel_all_timers(self):
        """Cancel all active timers"""
        room_ids = list(self.active_timers.keys())
        for room_id in room_ids:
            await self.cancel_timer(room_id)
        
        print(f"[TimerManager] Cancelled all timers ({len(room_ids)} total)")
    
    async def cleanup_orphaned_timers(self):
        """Clean up any orphaned timers that are no longer valid"""
        orphaned_rooms = []
        for room_id, timer_task in self.active_timers.items():
            if timer_task.done():
                orphaned_rooms.append(room_id)

        for room_id in orphaned_rooms:
            del self.active_timers[room_id]
            print(f"[TimerManager] Cleaned up orphaned timer for room {room_id}")
    
    async def validate_timer_room(self, room_id: str) -> bool:
        """
        Validate that a room still exists and has participants
        Args:
            room_id: Room identifier
        Returns: True if room is valid for timer
        """
        from .room_manager import room_manager
        room = room_manager.get_room(room_id)
        return room is not None and len(room.participants) > 0
    
    async def cleanup_invalid_timers(self):
        """Clean up timers for rooms that no longer exist or are empty"""
        invalid_rooms = []
        for room_id in self.active_timers.keys():
            if not await self.validate_timer_room(room_id):
                invalid_rooms.append(room_id)
        
        for room_id in invalid_rooms:
            await self.cancel_timer(room_id)
            print(f"[TimerManager] Cleaned up invalid timer for room {room_id}")
    
    def get_timer_status(self, room_id: str) -> Optional[Dict]:
        """Get timer status for a room"""
        if not self.is_timer_active(room_id):
            return None
        
        return {
            "room_id": room_id,
            "active": True,
            "remaining_time": "unknown"  # Would need to track this properly
        }


# Singleton instance
timer_manager = TimerManager()
