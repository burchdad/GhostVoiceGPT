"""
Language Auto-Detection & Dynamic Switching System
Detect language in first 2-3 seconds and switch STT/TTS accordingly
"""

import asyncio
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

class Language(Enum):
    """Supported languages"""
    EN_US = "en-US"
    EN_GB = "en-GB"
    ES_ES = "es-ES"
    FR_FR = "fr-FR"
    DE_DE = "de-DE"
    IT_IT = "it-IT"
    PT_BR = "pt-BR"
    JA_JP = "ja-JP"
    KO_KR = "ko-KR"
    ZH_CN = "zh-CN"

@dataclass
class LanguageResult:
    """Language detection result"""
    language: Language
    confidence: float
    detected_in_seconds: float

class LanguageDetector:
    """Real-time language detection from audio"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Language patterns for quick detection
        self.language_patterns = {
            Language.EN_US: ["hello", "hi", "yes", "no", "the", "and", "a", "to"],
            Language.ES_ES: ["hola", "sí", "no", "el", "la", "y", "de", "que"],
            Language.FR_FR: ["bonjour", "oui", "non", "le", "la", "et", "de", "que"],
            Language.DE_DE: ["hallo", "ja", "nein", "der", "die", "und", "von", "dass"],
            Language.IT_IT: ["ciao", "sì", "no", "il", "la", "e", "di", "che"],
            Language.PT_BR: ["olá", "sim", "não", "o", "a", "e", "de", "que"],
        }
        
        # Voice mappings per language
        self.voice_mappings = {
            Language.EN_US: {
                "professional": "pNInz6obpgDQGcFmaJgB",  # Adam
                "friendly": "EXAVITQu4vr4xnSDxMaL",     # Bella
                "energetic": "MF3mGyEYCl7XYWbV9V6O"     # Elli
            },
            Language.EN_GB: {
                "professional": "onwK4e9ZLuTAKqWW03F9",  # Daniel
                "friendly": "Xb7hH8MSUJpSbSDYk0k2",     # Alice
                "energetic": "Xb7hH8MSUJpSbSDYk0k2"     # Alice
            },
            Language.ES_ES: {
                "professional": "zcAOhNBS3c14rBihAFp1",  # Giovanni
                "friendly": "XrExE9yKIg1WjnnlVkGX",     # Matilda
                "energetic": "XrExE9yKIg1WjnnlVkGX"     # Matilda
            },
            Language.FR_FR: {
                "professional": "XrExE9yKIg1WjnnlVkGX",  # Matilda
                "friendly": "XrExE9yKIg1WjnnlVkGX",     # Matilda
                "energetic": "zcAOhNBS3c14rBihAFp1"     # Giovanni
            },
            Language.DE_DE: {
                "professional": "XrExE9yKIg1WjnnlVkGX",  # Matilda
                "friendly": "XrExE9yKIg1WjnnlVkGX",     # Matilda
                "energetic": "XrExE9yKIg1WjnnlVkGX"     # Matilda
            },
            Language.IT_IT: {
                "professional": "zcAOhNBS3c14rBihAFp1",  # Giovanni (native)
                "friendly": "zcAOhNBS3c14rBihAFp1",     # Giovanni
                "energetic": "zcAOhNBS3c14rBihAFp1"     # Giovanni
            }
        }
        
        # Prompt packs per language
        self.prompt_packs = {
            Language.EN_US: {
                "greeting": "Hello! I'm your AI assistant. How can I help you today?",
                "fallback": "I'm sorry, I didn't quite catch that. Could you repeat that please?",
                "transfer": "I'll connect you with a human agent who can better assist you.",
                "personality": "friendly and professional"
            },
            Language.ES_ES: {
                "greeting": "¡Hola! Soy tu asistente de IA. ¿Cómo puedo ayudarte hoy?",
                "fallback": "Lo siento, no entendí bien. ¿Podrías repetir eso por favor?",
                "transfer": "Te conectaré con un agente humano que podrá ayudarte mejor.",
                "personality": "amigable y profesional"
            },
            Language.FR_FR: {
                "greeting": "Bonjour! Je suis votre assistant IA. Comment puis-je vous aider aujourd'hui?",
                "fallback": "Désolé, je n'ai pas bien compris. Pourriez-vous répéter s'il vous plaît?",
                "transfer": "Je vais vous connecter avec un agent humain qui pourra mieux vous aider.",
                "personality": "amical et professionnel"
            },
            Language.DE_DE: {
                "greeting": "Hallo! Ich bin Ihr KI-Assistent. Wie kann ich Ihnen heute helfen?",
                "fallback": "Entschuldigung, das habe ich nicht ganz verstanden. Könnten Sie das bitte wiederholen?",
                "transfer": "Ich verbinde Sie mit einem menschlichen Mitarbeiter, der Ihnen besser helfen kann.",
                "personality": "freundlich und professionell"
            },
            Language.IT_IT: {
                "greeting": "Ciao! Sono il tuo assistente IA. Come posso aiutarti oggi?",
                "fallback": "Mi dispiace, non ho capito bene. Potresti ripetere per favore?",
                "transfer": "Ti collegherò con un agente umano che potrà aiutarti meglio.",
                "personality": "amichevole e professionale"
            }
        }
    
    async def detect_language_from_text(self, text: str, processing_time: float) -> Optional[LanguageResult]:
        """Detect language from transcribed text"""
        text_lower = text.lower()
        scores = {}
        
        # Score each language based on pattern matches
        for language, patterns in self.language_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern in text_lower:
                    score += 1
            
            # Normalize by pattern count
            if patterns:
                scores[language] = score / len(patterns)
        
        if not scores:
            return None
        
        # Get highest scoring language
        best_language = max(scores.keys(), key=lambda k: scores[k])
        confidence = scores[best_language]
        
        # Only return if confidence is above threshold
        if confidence >= 0.2:  # At least 20% of patterns matched
            return LanguageResult(
                language=best_language,
                confidence=confidence,
                detected_in_seconds=processing_time
            )
        
        return None
    
    def get_voice_for_language(self, language: Language, persona_style: str = "friendly") -> str:
        """Get appropriate voice ID for language and persona"""
        if language in self.voice_mappings:
            voices = self.voice_mappings[language]
            return voices.get(persona_style, list(voices.values())[0])
        
        # Fallback to English
        return self.voice_mappings[Language.EN_US][persona_style]
    
    def get_prompts_for_language(self, language: Language) -> Dict[str, str]:
        """Get prompt pack for language"""
        return self.prompt_packs.get(language, self.prompt_packs[Language.EN_US])

class FallbackSystem:
    """Fallback handling for various failure scenarios"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Canned responses for different failure scenarios
        self.fallback_responses = {
            "stt_low_confidence": [
                "I'm sorry, could you speak a bit louder?",
                "I didn't catch that clearly. Could you repeat that?",
                "Could you please say that again?"
            ],
            "stt_timeout": [
                "I'm having trouble hearing you. Let me connect you with someone who can help.",
                "There seems to be an audio issue. I'll transfer you to a human agent."
            ],
            "llm_rate_limit": [
                "I'm experiencing high demand right now. Please hold while I connect you with an agent.",
                "Let me transfer you to someone who can help you immediately."
            ],
            "llm_timeout": [
                "I'm taking longer than usual to process. Let me get you to a human agent.",
                "I'll connect you with someone right away."
            ],
            "tts_timeout": [
                "I'm having technical difficulties. Connecting you with a human agent now.",
                "Let me transfer you to someone who can assist you."
            ],
            "general_error": [
                "I'm experiencing technical difficulties. Let me connect you with a human agent.",
                "I'll transfer you to someone who can help you right away."
            ]
        }
        
        self.response_counters = {key: 0 for key in self.fallback_responses.keys()}
    
    def get_fallback_response(self, error_type: str) -> str:
        """Get appropriate fallback response for error type"""
        if error_type not in self.fallback_responses:
            error_type = "general_error"
        
        responses = self.fallback_responses[error_type]
        counter = self.response_counters[error_type]
        
        # Rotate through responses to avoid repetition
        response = responses[counter % len(responses)]
        self.response_counters[error_type] = (counter + 1) % len(responses)
        
        self.logger.info(f"Fallback response | type={error_type} | response={response}")
        return response
    
    def should_escalate(self, session_id: str, error_count: int, error_types: List[str]) -> bool:
        """Determine if call should be escalated to human"""
        
        # Escalate if too many errors
        if error_count >= 3:
            self.logger.warning(f"Escalating session {session_id} - too many errors: {error_count}")
            return True
        
        # Escalate on critical error types
        critical_errors = ["stt_timeout", "llm_timeout", "tts_timeout"]
        if any(error_type in critical_errors for error_type in error_types):
            self.logger.warning(f"Escalating session {session_id} - critical error: {error_types}")
            return True
        
        # Escalate on repeated low confidence
        if error_types.count("stt_low_confidence") >= 2:
            self.logger.warning(f"Escalating session {session_id} - repeated low confidence")
            return True
        
        return False

class DynamicLanguageSystem:
    """Orchestrates dynamic language detection and switching"""
    
    def __init__(self):
        self.detector = LanguageDetector()
        self.fallback = FallbackSystem()
        self.logger = logging.getLogger(__name__)
        
        # Session state tracking
        self.session_states: Dict[str, Dict] = {}
    
    def initialize_session(self, session_id: str, default_language: Language = Language.EN_US):
        """Initialize session with default language"""
        self.session_states[session_id] = {
            "current_language": default_language,
            "detected_language": None,
            "language_locked": False,
            "switch_count": 0,
            "error_count": 0,
            "error_types": [],
            "start_time": time.time()
        }
        
        self.logger.info(f"Session initialized | session={session_id} | default_lang={default_language.value}")
    
    async def process_turn(self, session_id: str, audio_data: bytes, trace_id: str) -> Dict:
        """Process a conversation turn with language detection"""
        
        if session_id not in self.session_states:
            self.initialize_session(session_id)
        
        state = self.session_states[session_id]
        start_time = time.time()
        
        try:
            # Step 1: Transcribe with current language
            transcript_result = await self._transcribe_audio(
                audio_data, 
                state["current_language"],
                trace_id
            )
            
            # Step 2: Check if we need language detection (first few seconds)
            processing_time = time.time() - start_time
            if not state["language_locked"] and processing_time <= 3.0:
                detected = await self.detector.detect_language_from_text(
                    transcript_result["text"], 
                    processing_time
                )
                
                if detected and detected.language != state["current_language"]:
                    await self._switch_language(session_id, detected.language, trace_id)
                    
                    # Re-transcribe with detected language if confidence is high
                    if detected.confidence > 0.7:
                        transcript_result = await self._transcribe_audio(
                            audio_data,
                            detected.language,
                            trace_id
                        )
            
            # Step 3: Process with LLM
            llm_result = await self._process_with_llm(
                transcript_result["text"],
                state["current_language"],
                trace_id
            )
            
            # Step 4: Generate response with appropriate voice
            tts_result = await self._generate_response(
                llm_result["response"],
                state["current_language"],
                llm_result["persona_style"],
                trace_id
            )
            
            return {
                "success": True,
                "transcript": transcript_result["text"],
                "response": llm_result["response"],
                "audio": tts_result["audio"],
                "language": state["current_language"].value,
                "confidence": transcript_result["confidence"],
                "processing_time_ms": (time.time() - start_time) * 1000
            }
            
        except Exception as e:
            return await self._handle_error(session_id, str(e), trace_id)
    
    async def _transcribe_audio(self, audio_data: bytes, language: Language, trace_id: str) -> Dict:
        """Transcribe audio with language-specific STT"""
        # Placeholder for actual STT implementation
        # In production: use Deepgram with language parameter
        
        self.logger.info(f"STT processing | language={language.value} | trace={trace_id}")
        
        # Simulate processing
        await asyncio.sleep(0.1)
        
        return {
            "text": "Hello, I need help with my account",  # Placeholder
            "confidence": 0.95,
            "language": language.value
        }
    
    async def _process_with_llm(self, text: str, language: Language, trace_id: str) -> Dict:
        """Process text with language-appropriate prompts"""
        prompts = self.detector.get_prompts_for_language(language)
        
        self.logger.info(f"LLM processing | language={language.value} | trace={trace_id}")
        
        # Simulate LLM processing with language-specific prompts
        await asyncio.sleep(0.2)
        
        return {
            "response": prompts["greeting"],  # Use language-appropriate response
            "persona_style": "friendly",
            "intent": "greeting"
        }
    
    async def _generate_response(self, text: str, language: Language, persona_style: str, trace_id: str) -> Dict:
        """Generate TTS with language-appropriate voice"""
        voice_id = self.detector.get_voice_for_language(language, persona_style)
        
        self.logger.info(f"TTS processing | language={language.value} | voice={voice_id} | trace={trace_id}")
        
        # Simulate TTS processing
        await asyncio.sleep(0.15)
        
        return {
            "audio": b"placeholder_audio_data",  # Placeholder
            "voice_id": voice_id,
            "duration_ms": 2500
        }
    
    async def _switch_language(self, session_id: str, new_language: Language, trace_id: str):
        """Switch session language dynamically"""
        state = self.session_states[session_id]
        old_language = state["current_language"]
        
        state["current_language"] = new_language
        state["detected_language"] = new_language
        state["switch_count"] += 1
        
        # Lock language after first switch to prevent ping-ponging
        if state["switch_count"] >= 1:
            state["language_locked"] = True
        
        self.logger.info(
            f"Language switched | session={session_id} | from={old_language.value} | to={new_language.value} | trace={trace_id}"
        )
        
        # Import telemetry here to avoid circular imports
        from production_telemetry import telemetry
        telemetry.log_language_switch(trace_id, old_language.value, new_language.value)
    
    async def _handle_error(self, session_id: str, error: str, trace_id: str) -> Dict:
        """Handle processing errors with fallbacks"""
        state = self.session_states[session_id]
        state["error_count"] += 1
        
        # Determine error type
        error_type = "general_error"
        if "confidence" in error.lower():
            error_type = "stt_low_confidence"
        elif "timeout" in error.lower():
            error_type = "stt_timeout"
        elif "rate" in error.lower():
            error_type = "llm_rate_limit"
        
        state["error_types"].append(error_type)
        
        # Get fallback response
        fallback_response = self.fallback.get_fallback_response(error_type)
        
        # Check if we should escalate
        should_escalate = self.fallback.should_escalate(
            session_id,
            state["error_count"],
            state["error_types"]
        )
        
        self.logger.error(f"Turn error | session={session_id} | error={error} | escalate={should_escalate} | trace={trace_id}")
        
        return {
            "success": False,
            "error": error,
            "fallback_response": fallback_response,
            "should_escalate": should_escalate,
            "language": state["current_language"].value
        }

# Usage example
async def demo_dynamic_language_system():
    """Demo the dynamic language detection system"""
    print("🌍 Dynamic Language System Demo")
    print("=" * 40)
    
    system = DynamicLanguageSystem()
    
    # Initialize session
    session_id = "demo_session_123"
    system.initialize_session(session_id, Language.EN_US)
    
    # Simulate audio input (would be actual audio in production)
    fake_audio = b"fake_audio_data"
    
    # Process turn
    result = await system.process_turn(session_id, fake_audio, "trace_123")
    
    print("📊 Turn Result:")
    for key, value in result.items():
        if key != "audio":  # Skip binary data
            print(f"  {key}: {value}")
    
    print("\n✅ Dynamic language system ready!")
    print("   - Real-time language detection")
    print("   - Automatic voice switching")
    print("   - Language-specific prompts")
    print("   - Intelligent fallbacks")

if __name__ == "__main__":
    asyncio.run(demo_dynamic_language_system())