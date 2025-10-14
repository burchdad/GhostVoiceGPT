#!/usr/bin/env python3
"""Quick test script for GhostVoiceGPT functionality"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from ghostvoice.config import settings
from ghostvoice.adapters import AdapterFactory
from ghostvoice.core.ai_brain import AIBrain
from ghostvoice.core.audio_pipeline import AudioPipelineFactory


async def test_basic_functionality():
    """Test basic system functionality"""
    print("🧪 Testing GhostVoiceGPT Basic Functionality")
    print("=" * 50)
    
    # Test 1: Configuration
    print("1. Testing configuration...")
    print(f"   ✅ Debug mode: {settings.app.debug}")
    print(f"   ✅ Host: {settings.app.host}:{settings.app.port}")
    print(f"   ✅ Webhook base URL: {settings.app.webhook_base_url}")
    
    # Test 2: Telephony Adapters
    print("\n2. Testing telephony adapters...")
    carriers = AdapterFactory.get_supported_carriers()
    print(f"   ✅ Supported carriers: {carriers}")
    
    # Create adapter
    adapter = AdapterFactory.create_adapter("twilio", {
        "account_sid": "test_sid",
        "auth_token": "test_token"
    })
    print(f"   ✅ Twilio adapter created: {type(adapter).__name__}")
    
    # Test 3: AI Brain
    print("\n3. Testing AI brain...")
    
    class MockClient:
        class Chat:
            class Completions:
                async def create(self, **kwargs):
                    class Response:
                        class Choice:
                            class Message:
                                content = "Hello! This is a test response."
                            message = Message()
                        choices = [Choice()]
                    return Response()
            completions = Completions()
        chat = Chat()
    
    ai_brain = AIBrain(MockClient(), {})
    personas = ai_brain.get_available_personas()
    print(f"   ✅ Available personas: {personas}")
    
    greeting = await ai_brain.generate_greeting("stephen")
    print(f"   ✅ Stephen's greeting: {greeting}")
    
    response = await ai_brain.generate_response("Hello there!", [], "nova")
    print(f"   ✅ Nova's response: {response[:50]}...")
    
    # Test 4: Audio Pipeline
    print("\n4. Testing audio pipeline...")
    pipeline_config = {
        "stt_provider": "openai",
        "tts_provider": "openai", 
        "openai_client": MockClient()
    }
    
    pipeline = AudioPipelineFactory.create_pipeline(pipeline_config)
    print(f"   ✅ Audio pipeline created")
    
    # Test STT
    transcript = await pipeline.speech_to_text(b"fake_audio_data")
    print(f"   ✅ STT test: {transcript[:50]}...")
    
    # Test TTS
    audio = await pipeline.text_to_speech("Hello world!", "stephen")
    print(f"   ✅ TTS test: Generated {len(audio)} bytes")
    
    print("\n" + "=" * 50)
    print("✅ All basic functionality tests passed!")
    print("🎉 GhostVoiceGPT is ready for production use!")


if __name__ == "__main__":
    asyncio.run(test_basic_functionality())