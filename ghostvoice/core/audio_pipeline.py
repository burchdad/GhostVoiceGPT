"""Audio processing pipeline for real-time STT/TTS"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import json

logger = logging.getLogger(__name__)


class STTEngine(ABC):
    """Abstract base class for Speech-to-Text engines"""
    
    @abstractmethod
    async def transcribe(self, audio_data: bytes) -> str:
        """Convert audio to text"""
        pass


class TTSEngine(ABC):
    """Abstract base class for Text-to-Speech engines"""
    
    @abstractmethod
    async def synthesize(self, text: str, voice_id: str = "default") -> bytes:
        """Convert text to audio"""
        pass


class OpenAISTTEngine(STTEngine):
    """OpenAI Whisper STT implementation"""
    
    def __init__(self, client):
        self.client = client
        self.logger = logging.getLogger(f"{__name__}.OpenAISTT")
    
    async def transcribe(self, audio_data: bytes) -> str:
        """Transcribe audio using OpenAI Whisper"""
        try:
            # In real implementation, would use OpenAI Whisper API
            self.logger.debug(f"Transcribing {len(audio_data)} bytes with OpenAI")
            
            # Placeholder - real implementation would call:
            # response = await self.client.audio.transcriptions.create(
            #     model="whisper-1",
            #     file=audio_data,
            #     response_format="text"
            # )
            # return response
            
            return "This is a placeholder transcription"
            
        except Exception as e:
            self.logger.error(f"OpenAI STT failed: {e}")
            return ""


class OpenAITTSEngine(TTSEngine):
    """OpenAI TTS implementation"""
    
    def __init__(self, client):
        self.client = client
        self.voice_mapping = {
            "stephen_voice": "onyx",
            "nova_voice": "nova", 
            "sugar_voice": "shimmer",
            "default": "alloy"
        }
        self.logger = logging.getLogger(f"{__name__}.OpenAITTS")
    
    async def synthesize(self, text: str, voice_id: str = "default") -> bytes:
        """Synthesize speech using OpenAI TTS"""
        try:
            openai_voice = self.voice_mapping.get(voice_id, "alloy")
            self.logger.debug(f"Synthesizing text with OpenAI voice: {openai_voice}")
            
            # Placeholder - real implementation would call:
            # response = await self.client.audio.speech.create(
            #     model="tts-1",
            #     voice=openai_voice,
            #     input=text,
            #     response_format="mp3"
            # )
            # return response.content
            
            return b"placeholder_audio_data"
            
        except Exception as e:
            self.logger.error(f"OpenAI TTS failed: {e}")
            return b""


class ElevenLabsTTSEngine(TTSEngine):
    """ElevenLabs TTS implementation"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        # Map our persona voices to real ElevenLabs voice IDs
        # You can find these in your ElevenLabs dashboard or use popular voices
        self.voice_mapping = {
            "stephen_voice": "21m00Tcm4TlvDq8ikWAM",    # Rachel (confident female)
            "nova_voice": "EXAVITQu4vr4xnSDxMaL",       # Bella (warm, empathetic)
            "sugar_voice": "MF3mGyEYCl7XYWbV9V6O",      # Elli (bubbly, energetic) 
            "default": "21m00Tcm4TlvDq8ikWAM"           # Default to Rachel
        }
        self.logger = logging.getLogger(f"{__name__}.ElevenLabsTTS")
        
        # Import here to avoid dependency issues if not installed
        try:
            from elevenlabs import generate, set_api_key
            self.generate = generate
            set_api_key(api_key)
            self.logger.info("ElevenLabs SDK initialized successfully")
        except ImportError as e:
            self.logger.error(f"ElevenLabs SDK not installed: {e}")
            self.generate = None
    
    async def synthesize(self, text: str, voice_id: str = "default") -> bytes:
        """Synthesize speech using ElevenLabs"""
        try:
            if not self.generate:
                self.logger.error("ElevenLabs SDK not available")
                return b""
            
            elevenlabs_voice_id = self.voice_mapping.get(voice_id, self.voice_mapping["default"])
            self.logger.debug(f"Synthesizing text with ElevenLabs voice: {elevenlabs_voice_id}")
            
            # Generate audio using ElevenLabs
            audio = self.generate(
                text=text,
                voice=elevenlabs_voice_id,
                model="eleven_monolingual_v1"  # Use v1 for speed, v2 for quality
            )
            
            # Convert to bytes if it's a generator
            if hasattr(audio, '__iter__') and not isinstance(audio, (str, bytes)):
                audio_bytes = b''.join(audio)
            elif isinstance(audio, bytes):
                audio_bytes = audio
            elif isinstance(audio, str):
                # If it's a string, encode it (shouldn't happen with ElevenLabs but safe)
                audio_bytes = audio.encode('utf-8')
            else:
                # Try to convert to bytes
                try:
                    audio_bytes = bytes(audio)
                except (TypeError, ValueError):
                    self.logger.error(f"Cannot convert audio to bytes: {type(audio)}")
                    return b""
            
            self.logger.info(f"Generated {len(audio_bytes)} bytes with ElevenLabs")
            return audio_bytes
            
        except Exception as e:
            self.logger.error(f"ElevenLabs TTS failed: {e}")
            return b""


class DeepgramSTTEngine(STTEngine):
    """Deepgram STT implementation"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.logger = logging.getLogger(f"{__name__}.DeepgramSTT")
    
    async def transcribe(self, audio_data: bytes) -> str:
        """Transcribe audio using Deepgram"""
        try:
            self.logger.debug(f"Transcribing {len(audio_data)} bytes with Deepgram")
            
            # Placeholder - real implementation would use Deepgram SDK
            return "This is a placeholder Deepgram transcription"
            
        except Exception as e:
            self.logger.error(f"Deepgram STT failed: {e}")
            return ""


class AudioPipeline:
    """Main audio processing pipeline"""
    
    def __init__(self, stt_engine: STTEngine, tts_engine: TTSEngine):
        self.stt_engine = stt_engine
        self.tts_engine = tts_engine
        self.logger = logging.getLogger(__name__)
    
    async def speech_to_text(self, audio_data: bytes) -> str:
        """Convert speech to text"""
        try:
            transcript = await self.stt_engine.transcribe(audio_data)
            self.logger.info(f"STT result: {transcript[:100]}...")
            return transcript
        except Exception as e:
            self.logger.error(f"STT pipeline failed: {e}")
            return ""
    
    async def text_to_speech(self, text: str, persona: str = "stephen") -> bytes:
        """Convert text to speech"""
        try:
            # Map persona to voice ID
            voice_mapping = {
                "stephen": "stephen_voice",
                "nova": "nova_voice", 
                "sugar": "sugar_voice"
            }
            voice_id = voice_mapping.get(persona, "default")
            
            audio_data = await self.tts_engine.synthesize(text, voice_id)
            self.logger.info(f"TTS generated {len(audio_data)} bytes for: {text[:50]}...")
            return audio_data
        except Exception as e:
            self.logger.error(f"TTS pipeline failed: {e}")
            return b""


class AudioPipelineFactory:
    """Factory for creating audio pipelines"""
    
    @staticmethod
    def create_pipeline(config: Dict[str, Any]) -> AudioPipeline:
        """Create audio pipeline based on configuration"""
        
        # Create STT engine
        stt_provider = config.get("stt_provider", "openai")
        if stt_provider == "openai":
            stt_engine = OpenAISTTEngine(config["openai_client"])
        elif stt_provider == "deepgram":
            stt_engine = DeepgramSTTEngine(config["deepgram_api_key"])
        else:
            raise ValueError(f"Unsupported STT provider: {stt_provider}")
        
        # Create TTS engine
        tts_provider = config.get("tts_provider", "openai")
        if tts_provider == "openai":
            tts_engine = OpenAITTSEngine(config["openai_client"])
        elif tts_provider == "elevenlabs":
            tts_engine = ElevenLabsTTSEngine(config["elevenlabs_api_key"])
        else:
            raise ValueError(f"Unsupported TTS provider: {tts_provider}")
        
        return AudioPipeline(stt_engine, tts_engine)