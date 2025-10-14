#!/usr/bin/env python3
"""Simple audio verification script"""

import os

def analyze_mp3_file(filename):
    """Analyze MP3 file to check if it contains audio data"""
    if not os.path.exists(filename):
        return f"❌ File {filename} not found"
    
    file_size = os.path.getsize(filename)
    
    with open(filename, 'rb') as f:
        # Read first 100 bytes to check header
        header = f.read(100)
        
        # Read some data from middle
        f.seek(file_size // 2)
        middle = f.read(100)
        
        # Read last 100 bytes
        f.seek(-100, 2)
        tail = f.read(100)
    
    # Check for MP3 patterns
    has_id3 = header.startswith(b'ID3')
    has_mp3_frame = b'\xff\xfb' in header or b'\xff\xf3' in header
    has_audio_data = len(set(middle)) > 10  # Check for data variety (not just zeros)
    
    result = f"📁 {filename} ({file_size} bytes)\n"
    result += f"   ID3 tag: {'✅' if has_id3 else '❌'}\n"
    result += f"   MP3 frame: {'✅' if has_mp3_frame else '❌'}\n"
    result += f"   Audio data variety: {'✅' if has_audio_data else '❌'}\n"
    result += f"   Header: {header[:20]}\n"
    
    return result

if __name__ == "__main__":
    print("🔍 MP3 File Analysis")
    print("=" * 50)
    
    mp3_files = [
        "demo_stephen.mp3",
        "demo_nova.mp3", 
        "demo_sugar.mp3",
        "debug_test_1.mp3",
        "debug_direct_api.mp3"
    ]
    
    for filename in mp3_files:
        print(analyze_mp3_file(filename))
    
    print("💡 All files should have ID3 tags and audio data variety.")
    print("💡 If files look good but no sound, check:")
    print("   1. Volume levels (system and media player)")
    print("   2. Try VLC Media Player")
    print("   3. Try playing in web browser")
    print("   4. Check default audio device")