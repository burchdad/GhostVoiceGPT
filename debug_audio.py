#!/usr/bin/env python3
"""Debug ElevenLabs audio output to troubleshoot playback issues"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


async def debug_elevenlabs_audio():
    """Debug ElevenLabs audio generation"""
    print("🔍 Debugging ElevenLabs Audio Output")
    print("=" * 50)
    
    try:
        from elevenlabs import generate, set_api_key
        
        # Set API key
        api_key = "sk_14163aaea3cbf2f09141089320b9af8b03fb108eaa971f33"
        set_api_key(api_key)
        print("✅ ElevenLabs API key set")
        
        # Test with different output formats
        test_text = "Hello, this is a test of the ElevenLabs audio system."
        voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel
        
        print(f"\n🎤 Testing voice generation...")
        print(f"   Text: {test_text}")
        print(f"   Voice ID: {voice_id}")
        
        # Test with different models and formats
        configs = [
            {"model": "eleven_monolingual_v1", "format": "mp3_22050_32"},
            {"model": "eleven_monolingual_v1", "format": "mp3_44100_32"},
            {"model": "eleven_multilingual_v2", "format": "mp3_22050_32"},
        ]
        
        for i, config in enumerate(configs):
            try:
                print(f"\n🧪 Test {i+1}: {config['model']} with {config['format']}")
                
                # Generate audio with specific format
                audio = generate(
                    text=test_text,
                    voice=voice_id,
                    model=config["model"]
                )
                
                # Handle the audio data
                if hasattr(audio, '__iter__') and not isinstance(audio, (str, bytes, bytearray, memoryview)):
                    audio_bytes = b''.join(audio)
                elif isinstance(audio, (bytearray, memoryview)):
                    audio_bytes = bytes(audio)
                else:
                    audio_bytes = audio if isinstance(audio, bytes) else b''.join(audio)
                
                print(f"   ✅ Generated {len(audio_bytes)} bytes")
                
                # Save with different filename
                filename = f"debug_test_{i+1}.mp3"
                with open(filename, "wb") as f:
                    f.write(audio_bytes)
                
                print(f"   💾 Saved as {filename}")
                
                # Check file header to verify it's a valid MP3
                if len(audio_bytes) > 10:
                    header = audio_bytes[:10]
                    print(f"   🔍 File header: {header}")
                    
                    # Check for MP3 signature
                    if header.startswith(b'ID3') or header[0:2] == b'\xff\xfb' or header[0:2] == b'\xff\xf3':
                        print(f"   ✅ Valid MP3 format detected")
                    else:
                        print(f"   ⚠️  Unusual MP3 format - may need different player")
                
            except Exception as e:
                print(f"   ❌ Test {i+1} failed: {e}")
        
        # Try with a very simple approach using requests directly
        print(f"\n🔧 Testing direct API approach...")
        try:
            import requests
            
            url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": api_key
            }
            data = {
                "text": "Hello, this is a direct API test.",
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                audio_content = response.content
                print(f"   ✅ Direct API: {len(audio_content)} bytes")
                
                with open("debug_direct_api.mp3", "wb") as f:
                    f.write(audio_content)
                print(f"   💾 Saved as debug_direct_api.mp3")
                
                # Check header
                if len(audio_content) > 10:
                    header = audio_content[:10]
                    print(f"   🔍 Direct API header: {header}")
            else:
                print(f"   ❌ Direct API failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Direct API test failed: {e}")
        
    except ImportError:
        print("❌ ElevenLabs not available")
    except Exception as e:
        print(f"❌ Debug failed: {e}")
    
    print("\n" + "=" * 50)
    print("🔍 Debug complete!")
    print("\n💡 Troubleshooting tips:")
    print("   1. Try playing debug_*.mp3 files with different media players")
    print("   2. Try VLC Media Player if Windows Media Player doesn't work")
    print("   3. Check if your speakers/headphones are working")
    print("   4. Try opening the files in a web browser")


if __name__ == "__main__":
    asyncio.run(debug_elevenlabs_audio())