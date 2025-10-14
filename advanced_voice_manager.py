"""
ElevenLabs Voice Library & Multilingual System
Enhanced voice management for GhostVoiceGPT
"""

import os
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass

# Handle ElevenLabs imports with proper typing
try:
    import elevenlabs
    from elevenlabs import ElevenLabs, Voice, VoiceSettings
    ELEVENLABS_AVAILABLE = True
    
    # Use the actual types when available  
    ElevenLabsType = ElevenLabs  # type: ignore
    VoiceType = Voice  # type: ignore
    VoiceSettingsType = VoiceSettings  # type: ignore
    
except ImportError:
    print("ElevenLabs package not found. Install with: pip install elevenlabs")
    ELEVENLABS_AVAILABLE = False
    
    # Create dummy types for when package not available
    class ElevenLabsType:  # type: ignore
        def __init__(self, api_key: str): pass
        def generate(self, **kwargs) -> List[bytes]: return []
    
    class VoiceType:  # type: ignore
        def __init__(self, voice_id: str, settings: Any = None): pass
    
    class VoiceSettingsType:  # type: ignore
        def __init__(self, **kwargs): pass

@dataclass
class VoiceConfig:
    """Configuration for a voice including settings and metadata"""
    voice_id: str
    name: str
    gender: str
    accent: str
    age_range: str
    personality: str
    languages: List[str]
    recommended_for: List[str]
    
    # Voice settings
    stability: float = 0.5
    similarity_boost: float = 0.75
    style: float = 0.0
    use_speaker_boost: bool = True

class AdvancedVoiceManager:
    """Advanced voice management with multilingual support"""
    
    def __init__(self, api_key: str):
        # Initialize ElevenLabs client
        self.client = ElevenLabsType(api_key=api_key)
        self.voice_library = self._initialize_voice_library()
        
    def _initialize_voice_library(self) -> Dict[str, VoiceConfig]:
        """Initialize comprehensive voice library"""
        return {
            # Current voices (tested and working)
            "rachel": VoiceConfig(
                voice_id="21m00Tcm4TlvDq8ikWAM",
                name="Rachel",
                gender="female",
                accent="american",
                age_range="young_adult",
                personality="calm_professional",
                languages=["en-US", "en-GB", "en-AU"],
                recommended_for=["business", "narration", "assistant"]
            ),
            
            "bella": VoiceConfig(
                voice_id="EXAVITQu4vr4xnSDxMaL",
                name="Bella",
                gender="female", 
                accent="american",
                age_range="adult",
                personality="warm_friendly",
                languages=["en-US", "en-CA"],
                recommended_for=["conversational", "marketing", "storytelling"]
            ),
            
            "elli": VoiceConfig(
                voice_id="MF3mGyEYCl7XYWbV9V6O",
                name="Elli",
                gender="female",
                accent="american",
                age_range="young",
                personality="energetic_bubbly",
                languages=["en-US"],
                recommended_for=["youth", "entertainment", "casual"]
            ),
            
            # Additional popular ElevenLabs voices
            "adam": VoiceConfig(
                voice_id="pNInz6obpgDQGcFmaJgB",
                name="Adam",
                gender="male",
                accent="american",
                age_range="adult",
                personality="deep_authoritative",
                languages=["en-US", "en-GB"],
                recommended_for=["professional", "narration", "announcements"]
            ),
            
            "antoni": VoiceConfig(
                voice_id="ErXwobaYiN019PkySvjV",
                name="Antoni",
                gender="male",
                accent="american",
                age_range="young_adult",
                personality="warm_conversational",
                languages=["en-US"],
                recommended_for=["podcasts", "conversational", "friendly"]
            ),
            
            "arnold": VoiceConfig(
                voice_id="VR6AewLTigWG4xSOukaG",
                name="Arnold",
                gender="male",
                accent="american",
                age_range="middle_aged",
                personality="strong_confident",
                languages=["en-US"],
                recommended_for=["action", "tough_guy", "authoritative"]
            ),
            
            "domi": VoiceConfig(
                voice_id="AZnzlk1XvdvUeBnXmlld",
                name="Domi",
                gender="female",
                accent="american",
                age_range="young_adult",
                personality="strong_confident",
                languages=["en-US"],
                recommended_for=["leadership", "powerful", "assertive"]
            ),
            
            "josh": VoiceConfig(
                voice_id="TxGEqnHWrfWFTfGW9XjX",
                name="Josh",
                gender="male",
                accent="american",
                age_range="adult",
                personality="calm_steady",
                languages=["en-US"],
                recommended_for=["narration", "professional", "reliable"]
            ),
            
            "sam": VoiceConfig(
                voice_id="yoZ06aMxZJJ28mfd3POQ",
                name="Sam",
                gender="male",
                accent="american",
                age_range="young_adult",
                personality="casual_friendly",
                languages=["en-US"],
                recommended_for=["casual", "approachable", "everyday"]
            ),
            
            # International voices for multilingual support
            "giovanni": VoiceConfig(
                voice_id="zcAOhNBS3c14rBihAFp1",
                name="Giovanni",
                gender="male",
                accent="italian",
                age_range="adult",
                personality="warm_expressive",
                languages=["it-IT", "en-US"],
                recommended_for=["italian", "romantic", "expressive"]
            ),
            
            "alice": VoiceConfig(
                voice_id="Xb7hH8MSUJpSbSDYk0k2",
                name="Alice",
                gender="female",
                accent="british",
                age_range="adult",
                personality="refined_elegant",
                languages=["en-GB", "en-US"],
                recommended_for=["british", "elegant", "sophisticated"]
            )
        }
    
    def get_voice_by_criteria(self, 
                            gender: Optional[str] = None,
                            accent: Optional[str] = None,
                            personality: Optional[str] = None,
                            language: Optional[str] = None) -> List[VoiceConfig]:
        """Find voices matching specific criteria"""
        matches = []
        
        for voice_config in self.voice_library.values():
            if gender and voice_config.gender != gender:
                continue
            if accent and voice_config.accent != accent:
                continue
            if personality and personality not in voice_config.personality:
                continue
            if language and language not in voice_config.languages:
                continue
                
            matches.append(voice_config)
        
        return matches
    
    def generate_with_language(self, 
                             text: str, 
                             voice_key: str,
                             language: str = "en-US",
                             custom_settings: Optional[Dict] = None) -> bytes:
        """Generate speech with language specification"""
        
        if voice_key not in self.voice_library:
            raise ValueError(f"Voice '{voice_key}' not found in library")
        
        voice_config = self.voice_library[voice_key]
        
        # Check language support
        if language not in voice_config.languages:
            print(f"Warning: {language} not officially supported by {voice_config.name}")
            print(f"Supported languages: {voice_config.languages}")
        
        # Apply custom settings or use defaults
        settings = VoiceSettingsType(
            stability=custom_settings.get('stability', voice_config.stability) if custom_settings else voice_config.stability,
            similarity_boost=custom_settings.get('similarity_boost', voice_config.similarity_boost) if custom_settings else voice_config.similarity_boost,
            style=custom_settings.get('style', voice_config.style) if custom_settings else voice_config.style,
            use_speaker_boost=custom_settings.get('use_speaker_boost', voice_config.use_speaker_boost) if custom_settings else voice_config.use_speaker_boost
        )
        
        # Add language hint to text if needed
        if language != "en-US":
            # You might want to add language markers or instructions here
            pass
        
        audio = self.client.generate(
            text=text,
            voice=VoiceType(voice_id=voice_config.voice_id, settings=settings),
            model="eleven_multilingual_v2"  # Use multilingual model
        )
        
        return b"".join(audio)
    
    def list_voices_by_language(self, language: str) -> List[Tuple[str, VoiceConfig]]:
        """Get all voices that support a specific language"""
        return [(key, config) for key, config in self.voice_library.items() 
                if language in config.languages]
    
    def get_voice_recommendations(self, use_case: str) -> List[Tuple[str, VoiceConfig]]:
        """Get voice recommendations for specific use cases"""
        return [(key, config) for key, config in self.voice_library.items() 
                if use_case in config.recommended_for]

def test_multilingual_voices():
    """Test script for multilingual capabilities"""
    api_key = os.getenv('ELEVENLABS_API_KEY')
    if not api_key:
        print("Please set ELEVENLABS_API_KEY environment variable")
        return
    
    voice_manager = AdvancedVoiceManager(api_key)
    
    # Test different languages
    test_phrases = {
        "en-US": "Hello, this is a test in American English.",
        "en-GB": "Hello, this is a test in British English.",
        "es-ES": "Hola, esta es una prueba en español.",
        "fr-FR": "Bonjour, ceci est un test en français.",
        "de-DE": "Hallo, das ist ein Test auf Deutsch.",
        "it-IT": "Ciao, questo è un test in italiano."
    }
    
    # Test with different voices
    test_voices = ["rachel", "adam", "alice", "giovanni"]
    
    for voice_key in test_voices:
        print(f"\n=== Testing {voice_key} ===")
        for lang, phrase in test_phrases.items():
            try:
                filename = f"test_{voice_key}_{lang.replace('-', '_')}.mp3"
                
                audio_data = voice_manager.generate_with_language(
                    text=phrase,
                    voice_key=voice_key,
                    language=lang
                )
                
                with open(filename, 'wb') as f:
                    f.write(audio_data)
                
                print(f"✅ Generated: {filename}")
                
            except Exception as e:
                print(f"❌ Failed {lang}: {e}")

if __name__ == "__main__":
    test_multilingual_voices()