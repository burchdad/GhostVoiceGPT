"""FastAPI application and API routes"""

from fastapi import FastAPI, Request, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any, Optional
import json
import uvicorn

logger = logging.getLogger(__name__)


class VoiceAPI:
    """FastAPI application for GhostVoiceGPT"""
    
    def __init__(self, orchestrator, config):
        self.orchestrator = orchestrator
        self.config = config
        self.app = FastAPI(
            title="GhostVoiceGPT API",
            description="Multi-carrier AI voice system",
            version="0.1.0"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=config.app.allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        self.setup_routes()
        self.active_websockets: Dict[str, WebSocket] = {}
    
    def setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/")
        async def root():
            return {"message": "GhostVoiceGPT API", "version": "0.1.0", "status": "running"}
        
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}
        
        @self.app.post("/calls/outbound")
        async def make_outbound_call(request: Dict[str, Any]):
            """Initiate an outbound AI voice call"""
            try:
                to_number = request.get("to_number")
                from_number = request.get("from_number")
                persona = request.get("persona", "stephen")
                
                if not to_number or not from_number:
                    raise HTTPException(status_code=400, detail="to_number and from_number are required")
                
                result = await self.orchestrator.initiate_call(to_number, from_number, persona)
                
                if result.get("status") == "success":
                    return JSONResponse(content=result, status_code=200)
                else:
                    return JSONResponse(content=result, status_code=400)
                    
            except Exception as e:
                logger.error(f"Outbound call API failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/webhooks/twilio")
        async def twilio_webhook(request: Request):
            """Handle Twilio webhooks"""
            try:
                # Get form data from Twilio
                form_data = await request.form()
                payload = dict(form_data)
                headers = dict(request.headers)
                
                # Extract call information
                call_sid = payload.get("CallSid")
                call_status = payload.get("CallStatus")
                
                if not call_sid:
                    raise HTTPException(status_code=400, detail="CallSid missing")
                
                # Determine event type
                event_type = "call_answered" if call_status == "in-progress" else "status_update"
                
                # Handle the event
                result = await self.orchestrator.handle_call_event(call_sid, event_type, payload)
                
                # Return TwiML response
                if event_type == "call_answered":
                    return """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>Hello! Please hold while I connect you to our AI assistant.</Say>
    <Start>
        <Stream url="wss://your-domain.com/stream/twilio" />
    </Start>
</Response>"""
                else:
                    return """<?xml version="1.0" encoding="UTF-8"?>
<Response></Response>"""
                    
            except Exception as e:
                logger.error(f"Twilio webhook failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/webhooks/telnyx")
        async def telnyx_webhook(request: Request):
            """Handle Telnyx webhooks"""
            try:
                payload = await request.json()
                headers = dict(request.headers)
                
                # Extract call information
                data = payload.get("data", {})
                call_control_id = data.get("call_control_id")
                event_type = data.get("event_type")
                
                if not call_control_id:
                    raise HTTPException(status_code=400, detail="call_control_id missing")
                
                # Handle the event
                result = await self.orchestrator.handle_call_event(call_control_id, event_type, data)
                
                return JSONResponse(content={"status": "received"})
                
            except Exception as e:
                logger.error(f"Telnyx webhook failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/calls/{call_sid}")
        async def get_call_info(call_sid: str):
            """Get information about a specific call"""
            try:
                session_info = await self.orchestrator.get_session_info(call_sid)
                
                if session_info:
                    return JSONResponse(content=session_info)
                else:
                    raise HTTPException(status_code=404, detail="Call not found")
                    
            except Exception as e:
                logger.error(f"Get call info failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.delete("/calls/{call_sid}")
        async def end_call(call_sid: str):
            """End an active call"""
            try:
                result = await self.orchestrator.end_call(call_sid)
                return JSONResponse(content=result)
                
            except Exception as e:
                logger.error(f"End call failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.websocket("/stream/twilio")
        async def twilio_media_stream(websocket: WebSocket):
            """Handle Twilio media stream WebSocket"""
            await websocket.accept()
            call_sid = None
            
            try:
                while True:
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    
                    if message.get("event") == "start":
                        call_sid = message["start"]["callSid"]
                        self.active_websockets[call_sid] = websocket
                        logger.info(f"Media stream started for call {call_sid}")
                    
                    elif message.get("event") == "media":
                        # Handle incoming audio
                        if call_sid:
                            # Decode base64 audio and process
                            audio_data = message["media"]["payload"]  # base64 encoded
                            # In real implementation, would decode and process
                            await self.orchestrator.handle_call_event(call_sid, "audio_received", {
                                "audio_data": audio_data
                            })
                    
                    elif message.get("event") == "stop":
                        logger.info(f"Media stream stopped for call {call_sid}")
                        if call_sid in self.active_websockets:
                            del self.active_websockets[call_sid]
                        break
                        
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for call {call_sid}")
                if call_sid and call_sid in self.active_websockets:
                    del self.active_websockets[call_sid]
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
    
    def run(self, host: str = "0.0.0.0", port: int = 8000, debug: bool = False):
        """Run the FastAPI application"""
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            debug=debug,
            log_level="info" if not debug else "debug"
        )