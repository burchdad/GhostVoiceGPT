"""Core orchestrator for AI voice conversations"""

import asyncio
import json
import logging
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum

logger = logging.getLogger(__name__)


class CallState(Enum):
    """Call state enumeration"""
    INITIATED = "initiated"
    RINGING = "ringing"
    ANSWERED = "answered"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class CallSession:
    """Represents an active call session"""
    call_sid: str
    carrier: str
    from_number: str
    to_number: str
    state: CallState = CallState.INITIATED
    persona: str = "stephen"
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class VoiceOrchestrator:
    """Main orchestrator for AI voice conversations"""
    
    def __init__(self, telephony_adapter, audio_pipeline, ai_brain):
        self.telephony_adapter = telephony_adapter
        self.audio_pipeline = audio_pipeline
        self.ai_brain = ai_brain
        self.active_sessions: Dict[str, CallSession] = {}
        self.logger = logging.getLogger(__name__)
    
    async def initiate_call(self, to_number: str, from_number: str, persona: str = "stephen") -> Dict[str, Any]:
        """Initiate an outbound AI voice call"""
        try:
            # Create webhook URL for this call
            webhook_url = f"https://your-domain.com/webhooks/voice"
            
            # Make the call via telephony adapter
            result = await self.telephony_adapter.make_call(to_number, from_number, webhook_url)
            
            if result.get("status") == "success":
                # Create call session
                call_sid = result["call_sid"]
                session = CallSession(
                    call_sid=call_sid,
                    carrier=result.get("carrier", "unknown"),
                    from_number=from_number,
                    to_number=to_number,
                    persona=persona
                )
                
                self.active_sessions[call_sid] = session
                self.logger.info(f"Call initiated: {call_sid}")
                
                return {"status": "success", "call_sid": call_sid, "session": session}
            else:
                return result
                
        except Exception as e:
            self.logger.error(f"Call initiation failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def handle_call_event(self, call_sid: str, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming call events from telephony carrier"""
        try:
            session = self.active_sessions.get(call_sid)
            if not session:
                self.logger.warning(f"No session found for call {call_sid}")
                return {"status": "error", "message": "Session not found"}
            
            self.logger.info(f"Handling {event_type} for call {call_sid}")
            
            if event_type == "call_answered":
                session.state = CallState.ANSWERED
                # Start the conversation
                greeting = await self.ai_brain.generate_greeting(session.persona)
                await self.speak_to_caller(call_sid, greeting)
                
            elif event_type == "audio_received":
                # Process incoming audio
                audio_data = data.get("audio_data")
                if audio_data:
                    await self.process_incoming_audio(call_sid, audio_data)
                    
            elif event_type == "call_ended":
                session.state = CallState.COMPLETED
                session.end_time = datetime.now()
                # Clean up session after some time
                asyncio.create_task(self._cleanup_session(call_sid, delay=300))
            
            return {"status": "success", "session_state": session.state.value}
            
        except Exception as e:
            self.logger.error(f"Call event handling failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def process_incoming_audio(self, call_sid: str, audio_data: bytes) -> None:
        """Process incoming audio from caller"""
        try:
            session = self.active_sessions.get(call_sid)
            if not session:
                return
            
            # Convert speech to text
            transcript = await self.audio_pipeline.speech_to_text(audio_data)
            
            if transcript and transcript.strip():
                self.logger.info(f"Caller said: {transcript}")
                
                # Add to conversation history
                session.conversation_history.append({
                    "role": "user",
                    "content": transcript,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Generate AI response
                response = await self.ai_brain.generate_response(
                    transcript, 
                    session.conversation_history, 
                    session.persona
                )
                
                # Convert response to speech and send
                await self.speak_to_caller(call_sid, response)
                
                # Add AI response to history
                session.conversation_history.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now().isoformat()
                })
                
        except Exception as e:
            self.logger.error(f"Audio processing failed: {e}")
    
    async def speak_to_caller(self, call_sid: str, text: str) -> bool:
        """Convert text to speech and send to caller"""
        try:
            session = self.active_sessions.get(call_sid)
            if not session:
                return False
            
            # Convert text to speech
            audio_data = await self.audio_pipeline.text_to_speech(text, session.persona)
            
            # Stream audio to caller
            success = await self.telephony_adapter.stream_audio(call_sid, audio_data)
            
            if success:
                self.logger.info(f"Spoke to caller: {text[:100]}...")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Speaking to caller failed: {e}")
            return False
    
    async def get_session_info(self, call_sid: str) -> Optional[Dict[str, Any]]:
        """Get information about a call session"""
        session = self.active_sessions.get(call_sid)
        if not session:
            return None
        
        return {
            "call_sid": session.call_sid,
            "carrier": session.carrier,
            "from_number": session.from_number,
            "to_number": session.to_number,
            "state": session.state.value,
            "persona": session.persona,
            "start_time": session.start_time.isoformat(),
            "end_time": session.end_time.isoformat() if session.end_time else None,
            "conversation_length": len(session.conversation_history),
            "metadata": session.metadata
        }
    
    async def end_call(self, call_sid: str) -> Dict[str, Any]:
        """End an active call"""
        try:
            session = self.active_sessions.get(call_sid)
            if not session:
                return {"status": "error", "message": "Session not found"}
            
            session.state = CallState.COMPLETED
            session.end_time = datetime.now()
            
            # Clean up session
            await self._cleanup_session(call_sid)
            
            return {"status": "success", "message": "Call ended"}
            
        except Exception as e:
            self.logger.error(f"Ending call failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _cleanup_session(self, call_sid: str, delay: int = 0) -> None:
        """Clean up call session after delay"""
        if delay > 0:
            await asyncio.sleep(delay)
        
        if call_sid in self.active_sessions:
            session = self.active_sessions.pop(call_sid)
            self.logger.info(f"Cleaned up session for call {call_sid}")
            
            # Save session to database if needed
            # await self.save_session_to_db(session)