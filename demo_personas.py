#!/usr/bin/env python3
"""Demo script showing ElevenLabs voices for each persona"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from ghostvoice.core.audio_pipeline import AudioPipelineFactory


async def demo_personas():
    """Demo each persona with ElevenLabs voices"""
    print("🎭 GhostVoiceGPT Persona Voice Demo")
    print("=" * 50)
    
    # Mock OpenAI client
    class MockOpenAIClient:
        pass
    
    # Create pipeline with ElevenLabs
    pipeline_config = {
        "stt_provider": "openai",
        "tts_provider": "elevenlabs",
        "openai_client": MockOpenAIClient(),
        "elevenlabs_api_key": "sk_14163aaea3cbf2f09141089320b9af8b03fb108eaa971f33"
    }
    
    pipeline = AudioPipelineFactory.create_pipeline(pipeline_config)
    
    # Demo scripts for each persona
    demos = {
        "stephen": "Hey there! I'm Stephen. I'm confident, knowledgeable, and ready to help you build amazing things. What can I assist you with today?",
        "nova": "Hi! I'm Nova. I'm here to provide warm, empathetic support. I care about your experience and want to make sure you feel heard and understood.",
        "sugar": "Hey there, sweetie! I'm Sugar and I'm super excited to chat with you! I bring energy and enthusiasm to everything we do together!"
    }
    
    # Generate audio for each persona
    for persona, text in demos.items():
        print(f"\n🎤 Generating voice for {persona.title()}...")
        audio_data = await pipeline.text_to_speech(text, persona)
        
        if audio_data:
            filename = f"demo_{persona}.mp3"
            with open(filename, "wb") as f:
                f.write(audio_data)
            print(f"   ✅ {len(audio_data)} bytes generated")
            print(f"   💾 Saved as {filename}")
            print(f"   🗣️  \"{text[:50]}...\"")
        else:
            print(f"   ❌ Failed to generate audio for {persona}")
    
    print("\n" + "=" * 50)
    print("🎉 Persona demo complete!")
    print("🎧 Play the demo_*.mp3 files to hear each persona")
    print("\n📝 Persona Characteristics:")
    print("   • Stephen: Confident, knowledgeable (Rachel voice)")
    print("   • Nova: Warm, empathetic (Bella voice)")
    print("   • Sugar: Bubbly, energetic (Elli voice)")


if __name__ == "__main__":
    asyncio.run(demo_personas())