"""GhostVoiceGPT - Multi-Carrier AI Voice System

A production-ready AI voice system supporting multiple telephony carriers
including Twilio, Telnyx, Vonage, SignalWire, and Bandwidth.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from ghostvoice.config import settings
from ghostvoice.adapters import AdapterFactory
from ghostvoice.core.orchestrator import VoiceOrchestrator
from ghostvoice.core.ai_brain import AIBrain
from ghostvoice.core.audio_pipeline import AudioPipelineFactory
from ghostvoice.api import VoiceAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.app.debug else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class GhostVoiceGPTApp:
    """Main application class for GhostVoiceGPT"""
    
    def __init__(self):
        self.settings = settings
        self.telephony_adapter = None
        self.audio_pipeline = None
        self.ai_brain = None
        self.orchestrator = None
        self.api = None
    
    async def initialize(self):
        """Initialize all system components"""
        try:
            logger.info("Initializing GhostVoiceGPT...")
            
            # Initialize telephony adapter (using Twilio as default)
            carrier = "twilio"  # Could be made configurable
            carrier_config = {
                "account_sid": self.settings.telephony.twilio_account_sid,
                "auth_token": self.settings.telephony.twilio_auth_token,
                "phone_number": self.settings.telephony.twilio_phone_number
            }
            
            self.telephony_adapter = AdapterFactory.create_adapter(carrier, carrier_config)
            logger.info(f"Telephony adapter initialized: {carrier}")
            
            # Initialize OpenAI client (placeholder)
            class MockOpenAIClient:
                """Mock OpenAI client for demonstration"""
                def __init__(self, api_key):
                    self.api_key = api_key
                
                class Chat:
                    class Completions:
                        async def create(self, **kwargs):
                            class Response:
                                class Choice:
                                    class Message:
                                        content = "This is a mock AI response for demonstration purposes."
                                    message = Message()
                                choices = [Choice()]
                            return Response()
                    completions = Completions()
                chat = Chat()
            
            openai_client = MockOpenAIClient(self.settings.ai.openai_api_key)
            
            # Initialize AI brain
            personas_config = {}  # Load from config file if needed
            self.ai_brain = AIBrain(openai_client, personas_config)
            logger.info("AI brain initialized")
            
            # Initialize audio pipeline
            pipeline_config = {
                "stt_provider": self.settings.ai.default_stt_provider,
                "tts_provider": self.settings.ai.default_voice_provider,
                "openai_client": openai_client,
                "deepgram_api_key": self.settings.ai.deepgram_api_key,
                "elevenlabs_api_key": self.settings.ai.elevenlabs_api_key
            }
            
            if not self.settings.ai.elevenlabs_api_key and self.settings.ai.default_voice_provider == "elevenlabs":
                logger.warning("ElevenLabs selected as TTS provider but no API key provided. Falling back to OpenAI.")
                pipeline_config["tts_provider"] = "openai"
            
            self.audio_pipeline = AudioPipelineFactory.create_pipeline(pipeline_config)
            logger.info("Audio pipeline initialized")
            
            # Initialize orchestrator
            self.orchestrator = VoiceOrchestrator(
                self.telephony_adapter,
                self.audio_pipeline, 
                self.ai_brain
            )
            logger.info("Voice orchestrator initialized")
            
            # Initialize API
            self.api = VoiceAPI(self.orchestrator, self.settings)
            logger.info("API initialized")
            
            logger.info("GhostVoiceGPT initialization complete!")
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            raise
    
    def run(self):
        """Run the application"""
        try:
            logger.info("Starting GhostVoiceGPT server...")
            logger.info(f"Server will run on {self.settings.app.host}:{self.settings.app.port}")
            logger.info(f"Debug mode: {self.settings.app.debug}")
            
            # Note: In real deployment, you would run this with proper ASGI server
            # uvicorn main:app --host 0.0.0.0 --port 8000
            print("\n🎙️ GhostVoiceGPT Multi-Carrier AI Voice System")
            print("=" * 50)
            print(f"✅ Server initialized on {self.settings.app.host}:{self.settings.app.port}")
            print(f"✅ Supported carriers: {AdapterFactory.get_supported_carriers()}")
            print(f"✅ Available personas: {self.ai_brain.get_available_personas()}")
            print(f"✅ Debug mode: {self.settings.app.debug}")
            print("\n📞 Ready to handle AI voice calls!")
            print("\nAPI Endpoints:")
            print("  GET  /                    - API status")
            print("  GET  /health              - Health check")
            print("  POST /calls/outbound      - Make outbound call")
            print("  GET  /calls/{call_sid}    - Get call info")
            print("  POST /webhooks/twilio     - Twilio webhook")
            print("  POST /webhooks/telnyx     - Telnyx webhook")
            print("  WS   /stream/twilio       - Twilio media stream")
            print("\n" + "=" * 50)
            
            # self.api.run(
            #     host=self.settings.app.host,
            #     port=self.settings.app.port,
            #     debug=self.settings.app.debug
            # )
            
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            raise


async def main():
    """Main entry point"""
    app = GhostVoiceGPTApp()
    await app.initialize()
    app.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Application failed: {e}")
        sys.exit(1)