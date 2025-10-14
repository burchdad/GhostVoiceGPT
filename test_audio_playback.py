#!/usr/bin/env python3
"""Test different audio formats and players"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


async def test_audio_formats():
    """Test generating different audio formats"""
    print("🎵 Testing Different Audio Formats")
    print("=" * 50)
    
    try:
        from elevenlabs import generate, set_api_key
        
        # Set API key
        api_key = "sk_14163aaea3cbf2f09141089320b9af8b03fb108eaa971f33"
        set_api_key(api_key)
        
        test_text = "This is a test. Can you hear me now?"
        voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel
        
        print(f"🎤 Generating test audio...")
        print(f"   Text: '{test_text}'")
        
        # Generate audio
        audio = generate(
            text=test_text,
            voice=voice_id,
            model="eleven_monolingual_v1"
        )
        
        # Convert to bytes
        if hasattr(audio, '__iter__') and not isinstance(audio, (str, bytes)):
            audio_bytes = b''.join(
                chunk if isinstance(chunk, (bytes, bytearray, memoryview))
                else b''  # skip unsupported types
                for chunk in audio
                if isinstance(chunk, (bytes, bytearray, memoryview))
            )
        else:
            if isinstance(audio, bytes):
                audio_bytes = audio
            elif isinstance(audio, (bytearray, memoryview)):
                audio_bytes = bytes(audio)
            elif hasattr(audio, '__iter__') and not isinstance(audio, (str, bytes, bytearray, memoryview)):
                audio_bytes = b''.join(chunk for chunk in audio if isinstance(chunk, (bytes, bytearray, memoryview)))
            else:
                raise TypeError(f"Unsupported audio type: {type(audio)}")
        
        # Save as MP3
        mp3_file = "quick_test.mp3"
        with open(mp3_file, "wb") as f:
            f.write(audio_bytes)
        
        print(f"✅ Generated {len(audio_bytes)} bytes")
        print(f"💾 Saved as {mp3_file}")
        
        # Try to open with Windows Media Player explicitly
        print(f"\n🎵 Attempting to play with different methods...")
        
        try:
            import subprocess
            
            # Method 1: Default association
            print("   1. Opening with default player...")
            subprocess.run(["cmd", "/c", "start", mp3_file], check=False, shell=True)
            
            # Method 2: Try wmplayer explicitly
            print("   2. Trying Windows Media Player...")
            subprocess.run(["wmplayer", mp3_file], check=False)
            
        except Exception as e:
            print(f"   ⚠️  Player launch error: {e}")
        
        # Create a simple HTML player
        html_player = f"""
<!DOCTYPE html>
<html>
<head>
    <title>GhostVoiceGPT Audio Test</title>
</head>
<body>
    <h2>🎤 GhostVoiceGPT Audio Test</h2>
    <p>Click play to test the generated voice:</p>
    <audio controls>
        <source src="{mp3_file}" type="audio/mpeg">
        Your browser does not support the audio element.
    </audio>
    <br><br>
    <p>Text: "{test_text}"</p>
    <p>Voice: Rachel (Stephen persona)</p>
</body>
</html>
"""
        
        with open("audio_test.html", "w") as f:
            f.write(html_player)
        
        print(f"   3. Created HTML player: audio_test.html")
        print(f"      Open this file in your web browser to test audio")
        
        # Try opening HTML in browser
        try:
            import webbrowser
            webbrowser.open("audio_test.html")
            print(f"   4. Opened HTML player in default browser")
        except Exception as e:
            print(f"   ⚠️  Browser open error: {e}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🔧 Troubleshooting Steps:")
    print("1. Check if audio_test.html opens and plays in your browser")
    print("2. Verify system volume is up and speakers/headphones work")
    print("3. Try right-clicking quick_test.mp3 → 'Open with' → choose media player")
    print("4. Test with VLC Media Player if available")
    print("5. Check Windows audio settings (output device)")


if __name__ == "__main__":
    asyncio.run(test_audio_formats())