#!/usr/bin/env python3
"""Test ElevenLabs TTS integration with GhostVoiceGPT"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from ghostvoice.core.audio_pipeline import ElevenLabsTTSEngine, AudioPipelineFactory


async def test_elevenlabs_integration():
    """Test ElevenLabs TTS functionality"""
    print("🎤 Testing ElevenLabs TTS Integration")
    print("=" * 50)
    
    # Check if ElevenLabs API key is provided
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("⚠️  No ELEVENLABS_API_KEY found in environment")
        print("   To test with real ElevenLabs voices, set your API key:")
        print("   export ELEVENLABS_API_KEY=your_key_here")
        print("\n🧪 Testing with mock configuration instead...")
        api_key = "mock_key_for_testing"
    else:
        print(f"✅ ElevenLabs API key found: {api_key[:8]}...")
    
    # Test 1: Create ElevenLabs TTS Engine
    print("\n1. Testing ElevenLabs TTS Engine creation...")
    tts_engine = ElevenLabsTTSEngine(api_key)
    print(f"   ✅ Engine created with voice mappings:")
    for persona, voice_id in tts_engine.voice_mapping.items():
        print(f"      - {persona}: {voice_id}")
    
    # Test 2: Test voice synthesis for each persona
    print("\n2. Testing voice synthesis for each persona...")
    test_text = "Hello! This is a test of the ElevenLabs text-to-speech integration."
    
    personas = ["stephen_voice", "nova_voice", "sugar_voice", "default"]
    
    for persona in personas:
        try:
            print(f"\n   Testing {persona}...")
            audio_data = await tts_engine.synthesize(test_text, persona)
            
            if audio_data and len(audio_data) > 0:
                print(f"   ✅ {persona}: Generated {len(audio_data)} bytes of audio")
                
                # Save sample to file for testing
                output_file = f"test_output_{persona}.mp3"
                with open(output_file, "wb") as f:
                    f.write(audio_data)
                print(f"      💾 Saved sample to {output_file}")
            else:
                print(f"   ⚠️  {persona}: No audio generated (likely due to mock API key)")
                
        except Exception as e:
            print(f"   ❌ {persona}: Error - {e}")
    
    # Test 3: Test with AudioPipelineFactory
    print("\n3. Testing integration with AudioPipelineFactory...")
    
    try:
        # Mock OpenAI client for the factory
        class MockOpenAIClient:
            pass
        
        pipeline_config = {
            "stt_provider": "openai",
            "tts_provider": "elevenlabs",
            "openai_client": MockOpenAIClient(),
            "elevenlabs_api_key": api_key
        }
        
        pipeline = AudioPipelineFactory.create_pipeline(pipeline_config)
        print("   ✅ Audio pipeline created with ElevenLabs TTS")
        
        # Test TTS through pipeline
        test_personas = ["stephen", "nova", "sugar"]
        for persona in test_personas:
            audio = await pipeline.text_to_speech("Testing pipeline integration", persona)
            if audio:
                print(f"   ✅ Pipeline TTS for {persona}: {len(audio)} bytes")
            else:
                print(f"   ⚠️  Pipeline TTS for {persona}: No audio (mock mode)")
                
    except Exception as e:
        print(f"   ❌ Pipeline integration error: {e}")
    
    # Test 4: Voice ID validation
    print("\n4. Testing voice ID mappings...")
    expected_voices = {
        "stephen_voice": "21m00Tcm4TlvDq8ikWAM",  # Rachel
        "nova_voice": "EXAVITQu4vr4xnSDxMaL",     # Bella  
        "sugar_voice": "MF3mGyEYCl7XYWbV9V6O",    # Elli
        "default": "21m00Tcm4TlvDq8ikWAM"         # Rachel
    }
    
    for persona, expected_id in expected_voices.items():
        actual_id = tts_engine.voice_mapping.get(persona)
        if actual_id == expected_id:
            print(f"   ✅ {persona}: {actual_id}")
        else:
            print(f"   ❌ {persona}: Expected {expected_id}, got {actual_id}")
    
    print("\n" + "=" * 50)
    
    if api_key != "mock_key_for_testing":
        print("✅ ElevenLabs integration test completed!")
        print("🎉 Real voices should be generated and saved as test_output_*.mp3")
        print("\n💡 Tips:")
        print("   - Play the generated .mp3 files to hear the different voices")
        print("   - Each persona has a distinct ElevenLabs voice")
        print("   - Stephen: Rachel (confident)")
        print("   - Nova: Bella (warm, empathetic)")  
        print("   - Sugar: Elli (bubbly, energetic)")
    else:
        print("⚠️  ElevenLabs integration test completed in MOCK mode")
        print("🔑 To test with real voices, set ELEVENLABS_API_KEY environment variable")
        print("\n💡 To get an ElevenLabs API key:")
        print("   1. Sign up at https://elevenlabs.io")
        print("   2. Go to your profile settings")
        print("   3. Copy your API key")
        print("   4. Set: export ELEVENLABS_API_KEY=your_key")


if __name__ == "__main__":
    asyncio.run(test_elevenlabs_integration())