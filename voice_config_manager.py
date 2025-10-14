"""
Voice Configuration Management System
Easy interface for clients to customize voice settings and multilingual support
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

@dataclass
class VoiceSettings:
    """Voice configuration settings"""
    stability: float = 0.5          # 0.0-1.0: Higher = more stable, lower = more variable
    similarity_boost: float = 0.75  # 0.0-1.0: Higher = closer to original voice
    style: float = 0.0              # 0.0-1.0: Style exaggeration 
    use_speaker_boost: bool = True   # Boost speaker similarity
    
    def to_dict(self) -> dict:
        return asdict(self)

@dataclass
class VoiceProfile:
    """Complete voice profile with metadata and settings"""
    voice_id: str
    name: str
    gender: str
    accent: str
    personality: str
    languages: List[str]
    recommended_for: List[str]
    settings: VoiceSettings
    
    def to_dict(self) -> dict:
        data = asdict(self)
        data['settings'] = self.settings.to_dict()
        return data

class VoiceConfigManager:
    """Manage voice configurations for GhostVoiceGPT"""
    
    def __init__(self, config_file: str = "voice_config.json"):
        self.config_file = config_file
        self.voice_profiles = self._load_default_profiles()
        self.load_config()
    
    def _load_default_profiles(self) -> Dict[str, VoiceProfile]:
        """Load default voice profiles"""
        return {
            # Male Voices
            "adam": VoiceProfile(
                voice_id="pNInz6obpgDQGcFmaJgB",
                name="Adam",
                gender="male",
                accent="american",
                personality="deep_authoritative_confident",
                languages=["en-US", "en-GB"],
                recommended_for=["business", "professional", "narrator", "authoritative"],
                settings=VoiceSettings(stability=0.7, similarity_boost=0.8, style=0.1)
            ),
            
            "antoni": VoiceProfile(
                voice_id="ErXwobaYiN019PkySvjV",
                name="Antoni",
                gender="male",
                accent="american",
                personality="warm_conversational_friendly",
                languages=["en-US"],
                recommended_for=["conversational", "casual", "podcasts", "friendly"],
                settings=VoiceSettings(stability=0.5, similarity_boost=0.75, style=0.2)
            ),
            
            "daniel": VoiceProfile(
                voice_id="onwK4e9ZLuTAKqWW03F9",
                name="Daniel",
                gender="male",
                accent="british",
                personality="refined_professional_narrator",
                languages=["en-GB", "en-US"],
                recommended_for=["british", "narrator", "educational", "sophisticated"],
                settings=VoiceSettings(stability=0.8, similarity_boost=0.85, style=0.0)
            ),
            
            "giovanni": VoiceProfile(
                voice_id="zcAOhNBS3c14rBihAFp1",
                name="Giovanni",
                gender="male",
                accent="italian",
                personality="warm_expressive_romantic",
                languages=["it-IT", "en-US", "es-ES", "fr-FR"],
                recommended_for=["multilingual", "romantic", "expressive", "italian"],
                settings=VoiceSettings(stability=0.6, similarity_boost=0.8, style=0.3)
            ),
            
            "josh": VoiceProfile(
                voice_id="TxGEqnHWrfWFTfGW9XjX",
                name="Josh",
                gender="male",
                accent="american",
                personality="calm_steady_reliable",
                languages=["en-US"],
                recommended_for=["narrator", "calm", "educational", "reliable"],
                settings=VoiceSettings(stability=0.8, similarity_boost=0.75, style=0.1)
            ),
            
            "sam": VoiceProfile(
                voice_id="yoZ06aMxZJJ28mfd3POQ",
                name="Sam",
                gender="male",
                accent="american",
                personality="casual_friendly_everyday",
                languages=["en-US"],
                recommended_for=["casual", "friendly", "everyday", "approachable"],
                settings=VoiceSettings(stability=0.5, similarity_boost=0.7, style=0.2)
            ),
            
            # Female Voices
            "rachel": VoiceProfile(
                voice_id="21m00Tcm4TlvDq8ikWAM",
                name="Rachel",
                gender="female",
                accent="american",
                personality="calm_professional_confident",
                languages=["en-US", "en-GB", "en-AU"],
                recommended_for=["business", "professional", "assistant", "confident"],
                settings=VoiceSettings(stability=0.6, similarity_boost=0.8, style=0.1)
            ),
            
            "bella": VoiceProfile(
                voice_id="EXAVITQu4vr4xnSDxMaL",
                name="Bella",
                gender="female",
                accent="american",
                personality="warm_friendly_empathetic",
                languages=["en-US", "en-CA"],
                recommended_for=["conversational", "friendly", "warm", "empathetic"],
                settings=VoiceSettings(stability=0.5, similarity_boost=0.75, style=0.2)
            ),
            
            "elli": VoiceProfile(
                voice_id="MF3mGyEYCl7XYWbV9V6O",
                name="Elli",
                gender="female",
                accent="american",
                personality="energetic_bubbly_youthful",
                languages=["en-US"],
                recommended_for=["youth", "energetic", "bubbly", "entertainment"],
                settings=VoiceSettings(stability=0.4, similarity_boost=0.7, style=0.3)
            ),
            
            "alice": VoiceProfile(
                voice_id="Xb7hH8MSUJpSbSDYk0k2",
                name="Alice",
                gender="female",
                accent="british",
                personality="refined_elegant_sophisticated",
                languages=["en-GB", "en-US"],
                recommended_for=["british", "elegant", "sophisticated", "refined"],
                settings=VoiceSettings(stability=0.7, similarity_boost=0.8, style=0.1)
            ),
            
            "domi": VoiceProfile(
                voice_id="AZnzlk1XvdvUeBnXmlld",
                name="Domi",
                gender="female",
                accent="american",
                personality="strong_confident_assertive",
                languages=["en-US"],
                recommended_for=["leadership", "confident", "strong", "assertive"],
                settings=VoiceSettings(stability=0.6, similarity_boost=0.8, style=0.2)
            ),
            
            "matilda": VoiceProfile(
                voice_id="XrExE9yKIg1WjnnlVkGX",
                name="Matilda",
                gender="female",
                accent="american",
                personality="clear_versatile_multilingual",
                languages=["en-US", "es-ES", "fr-FR", "de-DE", "pt-BR"],
                recommended_for=["multilingual", "clear", "versatile", "international"],
                settings=VoiceSettings(stability=0.6, similarity_boost=0.75, style=0.1)
            ),
        }
    
    def save_config(self):
        """Save current configuration to file"""
        config = {
            "voice_profiles": {
                name: profile.to_dict() 
                for name, profile in self.voice_profiles.items()
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Voice configuration saved to {self.config_file}")
    
    def load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                
                # Update profiles with saved settings
                for name, profile_data in config.get("voice_profiles", {}).items():
                    if name in self.voice_profiles:
                        settings_data = profile_data.get("settings", {})
                        self.voice_profiles[name].settings = VoiceSettings(**settings_data)
                
                print(f"✅ Voice configuration loaded from {self.config_file}")
            except Exception as e:
                print(f"⚠️  Error loading config: {e}")
    
    def get_voice_recommendations(self, 
                                criteria: Dict[str, str]) -> List[Tuple[str, VoiceProfile]]:
        """Get voice recommendations based on criteria"""
        matches = []
        
        for name, profile in self.voice_profiles.items():
            score = 0
            
            # Check gender match
            if criteria.get("gender") == profile.gender:
                score += 3
            
            # Check accent match
            if criteria.get("accent") == profile.accent:
                score += 2
            
            # Check language support
            if criteria.get("language") in profile.languages:
                score += 2
            
            # Check use case match
            use_case = criteria.get("use_case")
            if use_case and use_case in profile.recommended_for:
                score += 3
            
            # Check personality keywords
            personality = criteria.get("personality", "")
            if personality and personality in profile.personality:
                score += 2
            
            if score > 0:
                matches.append((name, profile, score))
        
        # Sort by score and return top matches
        matches.sort(key=lambda x: x[2], reverse=True)
        return [(name, profile) for name, profile, score in matches[:5]]
    
    def customize_voice_settings(self, voice_name: str, **settings):
        """Customize settings for a specific voice"""
        if voice_name in self.voice_profiles:
            profile = self.voice_profiles[voice_name]
            
            # Update settings
            for key, value in settings.items():
                if hasattr(profile.settings, key):
                    setattr(profile.settings, key, value)
                    print(f"✅ Updated {voice_name}.{key} = {value}")
                else:
                    print(f"⚠️  Unknown setting: {key}")
            
            return profile
        else:
            print(f"❌ Voice '{voice_name}' not found")
            return None
    
    def create_persona_mapping(self, persona_config: Dict[str, Dict]):
        """Create persona to voice mappings with custom settings"""
        mapping = {}
        
        for persona_name, config in persona_config.items():
            voice_name = config.get("voice")
            custom_settings = config.get("settings", {})
            language = config.get("language", "en-US")
            
            if voice_name in self.voice_profiles:
                profile = self.voice_profiles[voice_name]
                
                # Create custom settings if provided
                if custom_settings:
                    settings = VoiceSettings(**{
                        **asdict(profile.settings),
                        **custom_settings
                    })
                else:
                    settings = profile.settings
                
                mapping[persona_name] = {
                    "voice_id": profile.voice_id,
                    "language": language,
                    "settings": settings.to_dict()
                }
            else:
                print(f"⚠️  Voice '{voice_name}' not found for persona '{persona_name}'")
        
        return mapping
    
    def export_for_elevenlabs(self, personas: Dict[str, str]) -> Dict[str, str]:
        """Export simple voice mapping for ElevenLabs integration"""
        mapping = {}
        
        for persona, voice_name in personas.items():
            if voice_name in self.voice_profiles:
                mapping[persona] = self.voice_profiles[voice_name].voice_id
            else:
                print(f"⚠️  Voice '{voice_name}' not found")
        
        return mapping

def create_client_voice_showcase():
    """Create an interactive voice showcase for clients"""
    
    manager = VoiceConfigManager()
    
    print("🎭 Voice Showcase - Choose Your Perfect AI Voice")
    print("=" * 60)
    
    # Organize voices by category
    categories = {
        "Professional & Business": ["adam", "rachel", "daniel", "alice"],
        "Friendly & Conversational": ["antoni", "bella", "sam"],
        "Confident & Strong": ["domi", "josh"],
        "Energetic & Youthful": ["elli"],
        "Multilingual & International": ["giovanni", "matilda"]
    }
    
    for category, voice_names in categories.items():
        print(f"\n📂 {category}")
        print("-" * 40)
        
        for voice_name in voice_names:
            if voice_name in manager.voice_profiles:
                profile = manager.voice_profiles[voice_name]
                print(f"🎙️  {profile.name}")
                print(f"    {profile.gender.title()} | {profile.accent.title()} accent")
                print(f"    Personality: {profile.personality.replace('_', ' ').title()}")
                print(f"    Languages: {', '.join(profile.languages)}")
                print(f"    Best for: {', '.join(profile.recommended_for)}")
                print()
    
    # Save showcase configuration
    manager.save_config()
    
    return manager

if __name__ == "__main__":
    # Demo the voice configuration system
    print("🚀 Voice Configuration Management System")
    print("=" * 50)
    
    # Create showcase
    manager = create_client_voice_showcase()
    
    # Example: Get recommendations
    print("\n🔍 Example: Voice Recommendations")
    print("-" * 30)
    
    recommendations = manager.get_voice_recommendations({
        "gender": "female",
        "use_case": "business",
        "language": "en-US"
    })
    
    print("Top recommendations for: Female, Business, English")
    for name, profile in recommendations:
        print(f"  • {profile.name} - {profile.personality.replace('_', ' ')}")
    
    # Example: Customize voice settings
    print("\n⚙️  Example: Custom Voice Settings")
    print("-" * 30)
    
    manager.customize_voice_settings(
        "rachel",
        stability=0.8,
        similarity_boost=0.9,
        style=0.0
    )
    
    # Example: Create persona mapping
    print("\n🎭 Example: Persona Configuration")
    print("-" * 30)
    
    persona_config = {
        "stephen": {
            "voice": "adam",
            "language": "en-US",
            "settings": {"stability": 0.8, "style": 0.1}
        },
        "nova": {
            "voice": "bella", 
            "language": "en-US",
            "settings": {"stability": 0.6, "style": 0.2}
        },
        "sugar": {
            "voice": "elli",
            "language": "en-US", 
            "settings": {"stability": 0.4, "style": 0.3}
        }
    }
    
    mapping = manager.create_persona_mapping(persona_config)
    print("Created persona mapping:")
    for persona, config in mapping.items():
        print(f"  {persona}: {config['voice_id']} ({config['language']})")
    
    print("\n✨ Voice configuration system ready!")
    print("Clients can now easily customize voices and settings!")