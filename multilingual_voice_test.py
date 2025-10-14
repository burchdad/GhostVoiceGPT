"""
Multilingual Voice Testing for GhostVoiceGPT
Test different voices with multiple languages
"""

import os
import sys
import asyncio
sys.path.append('.')

# Import our existing audio pipeline
from ghostvoice.core.audio_pipeline import ElevenLabsTTSEngine

# Extended voice library with more options
EXTENDED_VOICE_LIBRARY = {
    # Current working voices
    "stephen": "21m00Tcm4TlvDq8ikWAM",    # Rachel - for Stephen persona
    "nova": "EXAVITQu4vr4xnSDxMaL",       # Bella - for Nova persona  
    "sugar": "MF3mGyEYCl7XYWbV9V6O",      # Elli - for Sugar persona
    
    # Additional male voices
    "adam": "pNInz6obpgDQGcFmaJgB",       # Deep, authoritative
    "antoni": "ErXwobaYiN019PkySvjV",     # Warm, conversational
    "arnold": "VR6AewLTigWG4xSOukaG",     # Strong, confident
    "josh": "TxGEqnHWrfWFTfGW9XjX",       # Calm, steady
    "sam": "yoZ06aMxZJJ28mfd3POQ",        # Casual, friendly
    
    # Additional female voices  
    "domi": "AZnzlk1XvdvUeBnXmlld",       # Strong, confident female
    "alice": "Xb7hH8MSUJpSbSDYk0k2",      # British accent
    "dorothy": "ThT5KcBeYPX3keUQqHPh",    # Pleasant, clear
    
    # International/Multilingual voices
    "giovanni": "zcAOhNBS3c14rBihAFp1",   # Italian accent, great for romance languages
    "matilda": "XrExE9yKIg1WjnnlVkGX",     # Clear, good for multiple languages
    
    # Professional/Narrator voices
    "daniel": "onwK4e9ZLuTAKqWW03F9",     # British narrator
    "lily": "pFZP5JQG7iQjIQuC4Bku",       # Professional female
    "sarah": "EXAVITQu4vr4xnSDxMaL",      # Clear, professional
}

# Voice metadata for selection
VOICE_PROFILES = {
    "adam": {"gender": "male", "accent": "american", "style": "deep_authoritative", "languages": ["en-US", "en-GB"]},
    "antoni": {"gender": "male", "accent": "american", "style": "warm_conversational", "languages": ["en-US"]},
    "arnold": {"gender": "male", "accent": "american", "style": "strong_confident", "languages": ["en-US"]},
    "josh": {"gender": "male", "accent": "american", "style": "calm_narrator", "languages": ["en-US"]},
    "sam": {"gender": "male", "accent": "american", "style": "casual_friendly", "languages": ["en-US"]},
    "domi": {"gender": "female", "accent": "american", "style": "strong_confident", "languages": ["en-US"]},
    "alice": {"gender": "female", "accent": "british", "style": "refined_elegant", "languages": ["en-GB", "en-US"]},
    "dorothy": {"gender": "female", "accent": "american", "style": "pleasant_clear", "languages": ["en-US"]},
    "giovanni": {"gender": "male", "accent": "italian", "style": "warm_expressive", "languages": ["it-IT", "en-US", "es-ES"]},
    "matilda": {"gender": "female", "accent": "american", "style": "clear_multilingual", "languages": ["en-US", "es-ES", "fr-FR", "de-DE"]},
    "daniel": {"gender": "male", "accent": "british", "style": "professional_narrator", "languages": ["en-GB", "en-US"]},
    "lily": {"gender": "female", "accent": "american", "style": "professional_clear", "languages": ["en-US"]},
}

# Test phrases in different languages
MULTILINGUAL_TEST_PHRASES = {
    "en-US": "Hello! I'm your AI assistant, ready to help you with anything you need.",
    "en-GB": "Good day! I'm your AI assistant, and I'm here to help you with whatever you require.",
    "es-ES": "¡Hola! Soy tu asistente de inteligencia artificial, listo para ayudarte con lo que necesites.",
    "fr-FR": "Bonjour! Je suis votre assistant IA, prêt à vous aider avec tout ce dont vous avez besoin.",
    "de-DE": "Hallo! Ich bin Ihr KI-Assistent und bereit, Ihnen bei allem zu helfen, was Sie brauchen.",
    "it-IT": "Ciao! Sono il tuo assistente AI, pronto ad aiutarti con tutto ciò di cui hai bisogno.",
    "pt-BR": "Olá! Sou seu assistente de IA, pronto para ajudá-lo com tudo o que precisar.",
    "ja-JP": "こんにちは！私はあなたのAIアシスタントです。必要なことは何でもお手伝いします。",
    "ko-KR": "안녕하세요! 저는 당신의 AI 어시스턴트입니다. 필요한 모든 것을 도와드릴 준비가 되어 있습니다.",
    "zh-CN": "你好！我是你的AI助手，随时准备帮助你解决任何需要。"
}

async def test_new_voices():
    """Test the new voices with English phrases"""
    
    # Set up API key
    api_key = "sk_14163aaea3cbf2f09141089320b9af8b03fb108eaa971f33"
    
    # Create TTS engine
    tts_engine = ElevenLabsTTSEngine(api_key=api_key)
    
    # Test phrase
    test_text = "Hello! This is a test of my voice. I hope you like how I sound!"
    
    # Test new voices
    new_voices_to_test = ["adam", "antoni", "domi", "alice", "giovanni", "daniel"]
    
    print("🎤 Testing New Voices...")
    print("=" * 50)
    
    for voice_name in new_voices_to_test:
        if voice_name in EXTENDED_VOICE_LIBRARY:
            voice_id = EXTENDED_VOICE_LIBRARY[voice_name]
            profile = VOICE_PROFILES.get(voice_name, {})
            
            print(f"\n🔊 Testing: {voice_name.title()}")
            print(f"   Gender: {profile.get('gender', 'unknown')}")
            print(f"   Accent: {profile.get('accent', 'unknown')}")
            print(f"   Style: {profile.get('style', 'unknown')}")
            
            try:
                # Temporarily override the voice mapping
                original_mapping = tts_engine.voice_mapping.copy()
                tts_engine.voice_mapping[voice_name] = voice_id
                
                # Generate audio using synthesize method
                audio_data = await tts_engine.synthesize(test_text, voice_name)
                
                # Save file
                filename = f"test_voice_{voice_name}.mp3"
                with open(filename, 'wb') as f:
                    f.write(audio_data)
                
                print(f"   ✅ Generated: {filename}")
                
                # Restore original mapping
                tts_engine.voice_mapping = original_mapping
                
            except Exception as e:
                print(f"   ❌ Error: {e}")

async def test_multilingual_capability():
    """Test multilingual capabilities with different voices"""
    
    # Set up API key
    api_key = "sk_14163aaea3cbf2f09141089320b9af8b03fb108eaa971f33"
    
    # Create TTS engine
    tts_engine = ElevenLabsTTSEngine(api_key=api_key)
    
    # Test multilingual voices
    multilingual_voices = ["giovanni", "matilda", "alice"]
    
    print("\n🌍 Testing Multilingual Capabilities...")
    print("=" * 50)
    
    for voice_name in multilingual_voices:
        if voice_name in EXTENDED_VOICE_LIBRARY:
            voice_id = EXTENDED_VOICE_LIBRARY[voice_name]
            profile = VOICE_PROFILES.get(voice_name, {})
            supported_languages = profile.get('languages', ['en-US'])
            
            print(f"\n🎭 Voice: {voice_name.title()}")
            print(f"   Supported Languages: {', '.join(supported_languages)}")
            
            # Test with supported languages
            for lang in supported_languages:
                if lang in MULTILINGUAL_TEST_PHRASES:
                    try:
                        # Temporarily override the voice mapping
                        original_mapping = tts_engine.voice_mapping.copy()
                        tts_engine.voice_mapping[voice_name] = voice_id
                        
                        # Generate audio using synthesize method
                        text = MULTILINGUAL_TEST_PHRASES[lang]
                        audio_data = await tts_engine.synthesize(text, voice_name)
                        
                        # Save file
                        filename = f"test_{voice_name}_{lang.replace('-', '_')}.mp3"
                        with open(filename, 'wb') as f:
                            f.write(audio_data)
                        
                        print(f"   ✅ {lang}: {filename}")
                        
                        # Restore original mapping
                        tts_engine.voice_mapping = original_mapping
                        
                    except Exception as e:
                        print(f"   ❌ {lang}: {e}")

async def create_voice_samples_for_client_demo():
    """Create a comprehensive demo of all available voices"""
    
    api_key = "sk_14163aaea3cbf2f09141089320b9af8b03fb108eaa971f33"
    tts_engine = ElevenLabsTTSEngine(api_key=api_key)
    
    demo_text = "Hello, I'm one of your available AI voices. You can choose me for your personal assistant, business applications, or any other project you have in mind."
    
    print("\n🎯 Creating Client Demo Voice Samples...")
    print("=" * 50)
    
    # Create samples for all voices
    all_voices = {**EXTENDED_VOICE_LIBRARY}
    
    demo_files = []
    
    for voice_name, voice_id in all_voices.items():
        try:
            # Skip if we already have samples for current personas
            if voice_name in ["stephen", "nova", "sugar"]:
                continue
                
            profile = VOICE_PROFILES.get(voice_name, {})
            
            print(f"🎙️  Creating sample: {voice_name.title()}")
            print(f"    {profile.get('gender', '?')} | {profile.get('accent', '?')} | {profile.get('style', '?')}")
            
            # Temporarily override the voice mapping
            original_mapping = tts_engine.voice_mapping.copy()
            tts_engine.voice_mapping[voice_name] = voice_id
            
            # Generate audio using synthesize method
            audio_data = await tts_engine.synthesize(demo_text, voice_name)
            
            # Save file
            filename = f"client_demo_{voice_name}.mp3"
            with open(filename, 'wb') as f:
                f.write(audio_data)
            
            demo_files.append(filename)
            print(f"    ✅ Created: {filename}")
            
            # Restore original mapping
            tts_engine.voice_mapping = original_mapping
            
        except Exception as e:
            print(f"    ❌ Failed: {e}")
    
    print(f"\n🎉 Created {len(demo_files)} voice demo files!")
    return demo_files

async def main():
    """Main async function to run all tests"""
    print("🚀 Advanced Voice Testing System")
    print("================================\n")
    
    # Test 1: New voices in English
    await test_new_voices()
    
    # Test 2: Multilingual capabilities
    await test_multilingual_capability()
    
    # Test 3: Client demo samples
    await create_voice_samples_for_client_demo()
    
    print("\n✨ Voice testing complete!")
    print("Check the generated MP3 files to hear all the new voices.")
    print("You can now offer clients a wide variety of voice options!")

if __name__ == "__main__":
    asyncio.run(main())