"""
Streaming Optimization & Prosody Control System
Minimize latency with streaming STT/TTS and fine-tuned voice controls
"""

import asyncio
import time
import re
from typing import Dict, List, Optional, Generator, AsyncGenerator
from dataclasses import dataclass
from enum import Enum
import logging

class StreamingMode(Enum):
    """Streaming processing modes"""
    PARTIAL_HYPOTHESES = "partial"  # Stream STT hypotheses
    CLAUSE_STREAMING = "clause"     # Start TTS on clauses
    SENTENCE_STREAMING = "sentence" # Start TTS on sentences
    WORD_STREAMING = "word"         # Ultra-low latency word streaming

@dataclass
class ProsodySettings:
    """Advanced prosody control settings"""
    # ElevenLabs specific settings
    stability: float = 0.5          # 0.0-1.0: Voice consistency
    similarity_boost: float = 0.75  # 0.0-1.0: Voice similarity
    style: float = 0.0              # 0.0-1.0: Style exaggeration
    use_speaker_boost: bool = True   # Enhance speaker similarity
    
    # Prosody timing controls
    pause_after_comma: float = 0.3   # Seconds
    pause_after_period: float = 0.6  # Seconds
    pause_after_question: float = 0.5 # Seconds
    pause_after_exclamation: float = 0.4 # Seconds
    
    # Speech rate controls
    speaking_rate: float = 1.0       # 0.5-2.0: Speech speed multiplier
    pitch_adjustment: float = 0.0    # -20 to +20: Pitch shift in semitones
    
    # Quality vs latency tradeoffs
    latency_mode: str = "balanced"   # "ultra_low", "balanced", "quality"
    model_selection: str = "eleven_turbo_v2"  # ElevenLabs model

class StreamingTextProcessor:
    """Process text streams for optimal TTS timing"""
    
    def __init__(self, prosody_settings: ProsodySettings):
        self.prosody = prosody_settings
        self.logger = logging.getLogger(__name__)
        
        # Patterns for clause/sentence detection
        self.clause_patterns = [
            r'[,;:]',                    # Commas, semicolons, colons
            r'\b(and|but|or|however|also|furthermore)\b',  # Conjunctions
            r'\b(because|since|although|while|when|if)\b'  # Subordinating conjunctions
        ]
        
        self.sentence_patterns = [
            r'[.!?]+',                   # Sentence endings
            r'\b(so|therefore|thus|hence)\b[,.]',  # Conclusive transitions
        ]
        
        # SSML templates for prosody control
        self.ssml_templates = {
            "comma_pause": '<break time="{duration}s"/>',
            "period_pause": '<break time="{duration}s"/>',
            "question_pause": '<break time="{duration}s"/>',
            "emphasis": '<emphasis level="strong">{text}</emphasis>',
            "speed_change": '<prosody rate="{rate}">{text}</prosody>',
            "pitch_change": '<prosody pitch="{pitch}st">{text}</prosody>'
        }
    
    def optimize_for_streaming(self, text: str) -> str:
        """Optimize text for streaming TTS with prosody controls"""
        
        # Step 1: Add appropriate pauses
        optimized = self._add_prosody_pauses(text)
        
        # Step 2: Adjust speaking rate for latency mode
        if self.prosody.latency_mode == "ultra_low":
            optimized = self._apply_speed_optimization(optimized)
        
        # Step 3: Apply SSML for fine control
        if self.prosody.latency_mode == "quality":
            optimized = self._apply_ssml_enhancements(optimized)
        
        return optimized
    
    def _add_prosody_pauses(self, text: str) -> str:
        """Add SSML pause controls for natural speech rhythm"""
        
        # Replace punctuation with timed pauses
        text = re.sub(r',(?!\s*\d)', 
                     self.ssml_templates["comma_pause"].format(
                         duration=self.prosody.pause_after_comma), text)
        
        text = re.sub(r'\.(?!\s*\d)', 
                     self.ssml_templates["period_pause"].format(
                         duration=self.prosody.pause_after_period), text)
        
        text = re.sub(r'\?', 
                     self.ssml_templates["question_pause"].format(
                         duration=self.prosody.pause_after_question), text)
        
        text = re.sub(r'!', 
                     self.ssml_templates["question_pause"].format(
                         duration=self.prosody.pause_after_exclamation), text)
        
        return text
    
    def _apply_speed_optimization(self, text: str) -> str:
        """Apply speed optimizations for ultra-low latency"""
        
        # Increase speaking rate slightly for faster delivery
        faster_rate = min(1.3, self.prosody.speaking_rate * 1.2)
        
        return self.ssml_templates["speed_change"].format(
            rate=f"{faster_rate:.1f}",
            text=text
        )
    
    def _apply_ssml_enhancements(self, text: str) -> str:
        """Apply advanced SSML for quality mode"""
        
        # Add emphasis to important words
        emphasis_words = ["important", "urgent", "critical", "please", "sorry"]
        for word in emphasis_words:
            pattern = r'\b' + re.escape(word) + r'\b'
            replacement = self.ssml_templates["emphasis"].format(text=word)
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def split_for_streaming(self, text: str, mode: StreamingMode) -> List[str]:
        """Split text into chunks for streaming processing"""
        
        if mode == StreamingMode.WORD_STREAMING:
            return text.split()
        
        elif mode == StreamingMode.CLAUSE_STREAMING:
            # Split on clauses (commas, conjunctions)
            chunks = []
            current_chunk = ""
            
            for char in text:
                current_chunk += char
                if char in ",:;":
                    chunks.append(current_chunk.strip())
                    current_chunk = ""
            
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            
            return [chunk for chunk in chunks if chunk]
        
        elif mode == StreamingMode.SENTENCE_STREAMING:
            # Split on sentences
            return re.split(r'[.!?]+', text)
        
        else:  # PARTIAL_HYPOTHESES
            return [text]  # Process as single chunk

class StreamingTTSEngine:
    """High-performance streaming TTS with prosody optimization"""
    
    def __init__(self, api_key: str, prosody_settings: ProsodySettings):
        self.api_key = api_key
        self.prosody = prosody_settings
        self.text_processor = StreamingTextProcessor(prosody_settings)
        self.logger = logging.getLogger(__name__)
        
        # Performance tracking
        self.chunk_timings = []
        self.total_processing_time = 0
        
        try:
            from elevenlabs import generate, set_api_key, Voice, VoiceSettings
            self.generate = generate
            set_api_key(api_key)
            self.Voice = Voice
            self.VoiceSettings = VoiceSettings
            self.logger.info("ElevenLabs SDK initialized for streaming")
        except ImportError:
            self.logger.error("ElevenLabs SDK not available")
            self.generate = None
    
    async def stream_generate(self, 
                            text_chunks: List[str], 
                            voice_id: str,
                            trace_id: str) -> AsyncGenerator[bytes, None]:
        """Stream TTS generation for multiple text chunks"""
        
        if not self.generate:
            self.logger.error("ElevenLabs SDK not available")
            return
        
        # Configure voice settings for latency mode
        voice_settings = self._get_optimized_voice_settings()
        model = self._get_optimized_model()
        
        self.logger.info(f"Streaming TTS | chunks={len(text_chunks)} | voice={voice_id} | model={model} | trace={trace_id}")
        
        for i, chunk in enumerate(text_chunks):
            if not chunk.strip():
                continue
            
            chunk_start = time.time()
            
            try:
                # Optimize text for this chunk
                optimized_chunk = self.text_processor.optimize_for_streaming(chunk)
                
                # Generate audio for chunk (using simplified voice settings)
                audio_generator = self.generate(
                    text=optimized_chunk,
                    voice=self.Voice(voice_id=voice_id, settings=None),  # Simplified for compatibility
                    model=model,
                    stream=True  # Enable streaming
                )
                
                # Stream audio chunks
                chunk_audio = b""
                async for audio_chunk in self._async_audio_generator(audio_generator):
                    chunk_audio += audio_chunk
                    yield audio_chunk
                
                # Track timing
                chunk_time = (time.time() - chunk_start) * 1000
                self.chunk_timings.append(chunk_time)
                
                self.logger.debug(f"Chunk {i+1}/{len(text_chunks)} | duration={chunk_time:.1f}ms | size={len(chunk_audio)} bytes")
                
            except Exception as e:
                self.logger.error(f"TTS chunk failed | chunk={i} | error={e} | trace={trace_id}")
                continue
    
    def _get_optimized_voice_settings(self) -> Dict[str, float]:
        """Get voice settings optimized for latency mode"""
        
        if self.prosody.latency_mode == "ultra_low":
            # Optimize for speed
            return {
                "stability": 0.3,          # Lower stability for faster generation
                "similarity_boost": 0.6,   # Lower similarity for speed
                "style": 0.0,              # No style for fastest processing
                "use_speaker_boost": False # Disable for speed
            }
        
        elif self.prosody.latency_mode == "balanced":
            # Balance quality and speed
            return {
                "stability": self.prosody.stability,
                "similarity_boost": self.prosody.similarity_boost,
                "style": self.prosody.style * 0.5,  # Reduce style slightly
                "use_speaker_boost": self.prosody.use_speaker_boost
            }
        
        else:  # quality mode
            # Full quality settings
            return {
                "stability": self.prosody.stability,
                "similarity_boost": self.prosody.similarity_boost,
                "style": self.prosody.style,
                "use_speaker_boost": self.prosody.use_speaker_boost
            }
    
    def _get_optimized_model(self) -> str:
        """Get model optimized for latency requirements"""
        
        if self.prosody.latency_mode == "ultra_low":
            return "eleven_turbo_v2"      # Fastest model
        elif self.prosody.latency_mode == "balanced":
            return "eleven_multilingual_v2"  # Good balance
        else:
            return "eleven_multilingual_v2"  # Best quality
    
    async def _async_audio_generator(self, sync_generator) -> AsyncGenerator[bytes, None]:
        """Convert sync generator to async for streaming"""
        try:
            for chunk in sync_generator:
                yield chunk
                # Small yield to allow other tasks to run
                await asyncio.sleep(0)
        except Exception as e:
            self.logger.error(f"Audio streaming error: {e}")

class StreamingOrchestrator:
    """Orchestrate end-to-end streaming pipeline"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)
        
        # Default prosody settings
        self.prosody_configs = {
            "ultra_low_latency": ProsodySettings(
                latency_mode="ultra_low",
                stability=0.3,
                similarity_boost=0.6,
                style=0.0,
                pause_after_comma=0.1,
                pause_after_period=0.3,
                speaking_rate=1.2
            ),
            "balanced": ProsodySettings(
                latency_mode="balanced",
                stability=0.5,
                similarity_boost=0.75,
                style=0.1,
                pause_after_comma=0.2,
                pause_after_period=0.4,
                speaking_rate=1.1
            ),
            "high_quality": ProsodySettings(
                latency_mode="quality",
                stability=0.7,
                similarity_boost=0.85,
                style=0.2,
                pause_after_comma=0.3,
                pause_after_period=0.6,
                speaking_rate=1.0
            )
        }
    
    async def stream_process_turn(self, 
                                text: str, 
                                voice_id: str,
                                latency_profile: str = "balanced",
                                streaming_mode: StreamingMode = StreamingMode.CLAUSE_STREAMING,
                                trace_id: Optional[str] = None) -> AsyncGenerator[Dict, None]:
        """Process turn with streaming optimizations"""
        
        start_time = time.time()
        
        # Get prosody settings for latency profile
        prosody = self.prosody_configs.get(latency_profile, self.prosody_configs["balanced"])
        
        # Initialize streaming TTS
        tts_engine = StreamingTTSEngine(self.api_key, prosody)
        
        # Split text for streaming
        text_chunks = tts_engine.text_processor.split_for_streaming(text, streaming_mode)
        
        self.logger.info(f"Streaming process | chunks={len(text_chunks)} | mode={streaming_mode.value} | profile={latency_profile} | trace={trace_id}")
        
        # Stream audio generation
        chunk_index = 0
        trace_id_str = trace_id or f"trace_{int(time.time())}"
        async for audio_chunk in tts_engine.stream_generate(text_chunks, voice_id, trace_id_str):
            yield {
                "type": "audio_chunk",
                "chunk_index": chunk_index,
                "audio_data": audio_chunk,
                "timestamp": time.time(),
                "processing_time_ms": (time.time() - start_time) * 1000
            }
            chunk_index += 1
        
        # Final summary
        total_time = (time.time() - start_time) * 1000
        yield {
            "type": "completion",
            "total_chunks": len(text_chunks),
            "total_processing_time_ms": total_time,
            "average_chunk_time_ms": total_time / len(text_chunks) if text_chunks else 0,
            "streaming_mode": streaming_mode.value,
            "latency_profile": latency_profile
        }

# Performance testing utilities
class StreamingPerformanceAnalyzer:
    """Analyze streaming performance metrics"""
    
    def __init__(self):
        self.test_results = []
    
    async def benchmark_streaming_modes(self, api_key: str, test_text: str, voice_id: str):
        """Benchmark different streaming modes"""
        
        orchestrator = StreamingOrchestrator(api_key)
        
        test_configs = [
            ("ultra_low_latency", StreamingMode.WORD_STREAMING),
            ("ultra_low_latency", StreamingMode.CLAUSE_STREAMING),
            ("balanced", StreamingMode.CLAUSE_STREAMING),
            ("balanced", StreamingMode.SENTENCE_STREAMING),
            ("high_quality", StreamingMode.SENTENCE_STREAMING)
        ]
        
        print("🚀 Streaming Performance Benchmark")
        print("=" * 50)
        
        for latency_profile, streaming_mode in test_configs:
            print(f"\n📊 Testing: {latency_profile} + {streaming_mode.value}")
            
            start_time = time.time()
            chunk_count = 0
            first_chunk_time = None
            
            async for result in orchestrator.stream_process_turn(
                text=test_text,
                voice_id=voice_id,
                latency_profile=latency_profile,
                streaming_mode=streaming_mode,
                trace_id=f"bench_{latency_profile}_{streaming_mode.value}"
            ):
                if result["type"] == "audio_chunk":
                    chunk_count += 1
                    if first_chunk_time is None:
                        first_chunk_time = time.time() - start_time
                
                elif result["type"] == "completion":
                    total_time = time.time() - start_time
                    
                    results = {
                        "latency_profile": latency_profile,
                        "streaming_mode": streaming_mode.value,
                        "total_time_ms": total_time * 1000,
                        "first_chunk_time_ms": first_chunk_time * 1000 if first_chunk_time else 0,
                        "chunk_count": chunk_count,
                        "avg_chunk_time_ms": result["average_chunk_time_ms"]
                    }
                    
                    self.test_results.append(results)
                    
                    print(f"  ⏱️  Total time: {results['total_time_ms']:.1f}ms")
                    print(f"  🎯 First chunk: {results['first_chunk_time_ms']:.1f}ms")
                    print(f"  📦 Chunks: {results['chunk_count']}")
                    print(f"  📊 Avg/chunk: {results['avg_chunk_time_ms']:.1f}ms")
        
        # Show summary
        self._print_benchmark_summary()
    
    def _print_benchmark_summary(self):
        """Print benchmark summary"""
        print("\n🎯 Performance Summary")
        print("=" * 30)
        
        for result in sorted(self.test_results, key=lambda x: x["first_chunk_time_ms"]):
            print(f"🏆 {result['latency_profile']:15} | {result['streaming_mode']:12} | First: {result['first_chunk_time_ms']:6.1f}ms | Total: {result['total_time_ms']:6.1f}ms")

# Usage example
async def demo_streaming_system():
    """Demo the streaming optimization system"""
    print("⚡ Streaming Optimization Demo")
    print("=" * 40)
    
    # Test text
    test_text = "Hello! I'm your AI assistant, and I'm here to help you today. Whether you need information, support, or just want to chat, I'm ready to assist you with whatever you need."
    
    # Demo different configurations
    api_key = "sk_14163aaea3cbf2f09141089320b9af8b03fb108eaa971f33"
    voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel
    
    orchestrator = StreamingOrchestrator(api_key)
    
    print(f"📝 Test text: {test_text[:50]}...")
    print(f"🎤 Voice: Rachel")
    
    # Demo clause streaming with balanced profile
    print(f"\n🔄 Streaming with clause-based chunking...")
    
    async for result in orchestrator.stream_process_turn(
        text=test_text,
        voice_id=voice_id,
        latency_profile="balanced",
        streaming_mode=StreamingMode.CLAUSE_STREAMING,
        trace_id="demo_123"
    ):
        if result["type"] == "audio_chunk":
            print(f"  📦 Chunk {result['chunk_index']} | {len(result['audio_data'])} bytes | {result['processing_time_ms']:.1f}ms")
        elif result["type"] == "completion":
            print(f"  ✅ Complete | {result['total_chunks']} chunks | {result['total_processing_time_ms']:.1f}ms total")
    
    print("\n⚡ Streaming system ready!")
    print("   - Ultra-low latency mode available")
    print("   - Clause and sentence streaming")
    print("   - Optimized prosody controls")
    print("   - Real-time audio chunking")

if __name__ == "__main__":
    asyncio.run(demo_streaming_system())