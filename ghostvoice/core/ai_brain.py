"""AI Brain module for conversation logic"""

import logging
from typing import List, Dict, Any
import json

logger = logging.getLogger(__name__)


class VoicePersona:
    """Defines personality and voice characteristics"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.personality = config.get("personality", "friendly")
        self.voice_id = config.get("voice_id", "default")
        self.system_prompt = config.get("system_prompt", "You are a helpful AI assistant.")
        self.greeting = config.get("greeting", "Hello! How can I help you today?")
        self.conversation_style = config.get("conversation_style", "conversational")


class AIBrain:
    """Main AI conversation engine"""
    
    def __init__(self, openai_client, personas_config: Dict[str, Any]):
        self.openai_client = openai_client
        self.personas = self._load_personas(personas_config)
        self.logger = logging.getLogger(__name__)
    
    def _load_personas(self, config: Dict[str, Any]) -> Dict[str, VoicePersona]:
        """Load voice personas from configuration"""
        personas = {}
        
        # Default personas
        default_personas = {
            "stephen": {
                "personality": "confident, knowledgeable, slightly witty",
                "voice_id": "stephen_voice",
                "elevenlabs_voice_id": "21m00Tcm4TlvDq8ikWAM",  # Rachel - confident female
                "system_prompt": "You are Stephen, a confident and knowledgeable AI assistant with a slight wit. Keep responses conversational and under 50 words.",
                "greeting": "Hey there! Stephen here. What's on your mind?",
                "conversation_style": "confident"
            },
            "nova": {
                "personality": "warm, empathetic, supportive",
                "voice_id": "nova_voice",
                "elevenlabs_voice_id": "EXAVITQu4vr4xnSDxMaL",  # Bella - warm, empathetic
                "system_prompt": "You are Nova, a warm and empathetic AI assistant. You're supportive and caring in your responses. Keep responses under 50 words.",
                "greeting": "Hi! I'm Nova. I'm here to help and support you however I can.",
                "conversation_style": "supportive"
            },
            "sugar": {
                "personality": "bubbly, energetic, enthusiastic",
                "voice_id": "sugar_voice",
                "elevenlabs_voice_id": "MF3mGyEYCl7XYWbV9V6O",  # Elli - bubbly, energetic
                "system_prompt": "You are Sugar, a bubbly and energetic AI assistant. You're enthusiastic and positive. Keep responses upbeat and under 50 words.",
                "greeting": "Hey there, sweetie! Sugar here and I'm super excited to chat with you!",
                "conversation_style": "energetic"
            }
        }
        
        # Merge with provided config
        all_personas = {**default_personas, **config}
        
        for name, persona_config in all_personas.items():
            personas[name] = VoicePersona(name, persona_config)
        
        return personas
    
    async def generate_greeting(self, persona_name: str = "stephen") -> str:
        """Generate greeting for specified persona"""
        persona = self.personas.get(persona_name, self.personas["stephen"])
        return persona.greeting
    
    async def generate_response(self, user_input: str, conversation_history: List[Dict[str, Any]], persona_name: str = "stephen") -> str:
        """Generate AI response using OpenAI"""
        try:
            persona = self.personas.get(persona_name, self.personas["stephen"])
            
            # Build conversation context
            messages = [{"role": "system", "content": persona.system_prompt}]
            
            # Add recent conversation history (last 10 exchanges)
            for exchange in conversation_history[-10:]:
                messages.append({
                    "role": exchange["role"],
                    "content": exchange["content"]
                })
            
            # Add current user input
            messages.append({"role": "user", "content": user_input})
            
            # Generate response
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=150,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            self.logger.info(f"Generated response ({persona_name}): {ai_response[:100]}...")
            return ai_response
            
        except Exception as e:
            self.logger.error(f"AI response generation failed: {e}")
            # Fallback response
            return "I'm sorry, I'm having trouble understanding right now. Could you please repeat that?"
    
    def get_persona_voice_id(self, persona_name: str) -> str:
        """Get voice ID for persona"""
        persona = self.personas.get(persona_name, self.personas["stephen"])
        return persona.voice_id
    
    def get_available_personas(self) -> List[str]:
        """Get list of available personas"""
        return list(self.personas.keys())