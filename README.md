# GhostVoiceGPT - Multi-Carrier AI Voice System with Advanced TTS

A carrier-agnostic AI voice system that handles inbound and outbound calls with human-like conversation capabilities across multiple telephony providers. Now featuring **13+ professional ElevenLabs voices** and **multilingual support**!

## 🚀 Features

- **Multi-Carrier Support**: Twilio, Telnyx, Vonage, SignalWire, Bandwidth
- **Real-time Audio**: WebSocket streaming with <300ms latency
- **Natural AI Conversations**: STT → LLM → TTS pipeline with emotion detection
- **🎤 Advanced Voice System**: 13+ professional voices with multilingual support
- **🌍 Multilingual TTS**: Support for 10+ languages including Spanish, French, German, Italian
- **🎭 Voice Personas**: Configurable voice personalities with custom settings
- **Smart Call Handling**: Barge-in support, interruption handling, transfers
- **CRM Integration**: Automatic lead qualification and call logging
- **TCPA Compliance**: DNC checking, consent management, call throttling
- **Analytics Dashboard**: Live call monitoring, transcripts, performance metrics

## 🎵 Voice System Highlights

### 13+ Professional Voices Available:
- **Professional**: Adam, Rachel, Daniel, Alice
- **Conversational**: Antoni, Bella, Sam  
- **Confident**: Domi, Josh
- **Energetic**: Elli
- **Multilingual**: Giovanni (Italian), Matilda (Multi-European)

### Language Support:
- 🇺🇸 English (US/UK) - All voices
- 🇪🇸 Spanish - Giovanni, Matilda
- 🇫🇷 French - Giovanni, Matilda  
- 🇩🇪 German - Matilda
- 🇮🇹 Italian - Giovanni (native)
- 🇧🇷 Portuguese - Matilda
- 🇯🇵 Japanese - Matilda
- 🇰🇷 Korean - Matilda
- 🇨🇳 Chinese - Matilda

### Voice Configuration:
- **Stability**: Control voice consistency vs. variation
- **Similarity**: How close to stay to original voice  
- **Style**: Amount of stylistic exaggeration
- **Speaker Boost**: Enhanced voice similarity

## 🏗️ Architecture

```
PSTN/SIP ↔ Carrier APIs ↔ Telephony Adapter Layer
                               ↓
                        Real-time Media Bus (WebSocket)
                               ↓
                    STT → LLM Brain → TTS → Audio Output
                               ↓
                    GhostCRM + Analytics + Compliance
```

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **API Server** | FastAPI + WebSocket | Real-time call orchestration |
| **Speech-to-Text** | Deepgram / OpenAI Realtime API | Audio transcription |
| **AI Brain** | GPT-4o / Custom LLM | Conversation logic & context |
| **Text-to-Speech** | ElevenLabs / OpenAI Audio | Natural voice synthesis |
| **Telephony** | Multi-carrier adapters | Call routing & management |
| **Database** | PostgreSQL + Redis | Call logs & session state |
| **CRM** | Airtable / Custom API | Lead management |

## 📁 Project Structure

```
ghostvoice/
├── adapters/              # Carrier-specific implementations
│   ├── base.py           # Abstract telephony adapter
│   ├── twilio.py         # Twilio Media Streams
│   ├── telnyx.py         # Telnyx Call Control + Streaming
│   ├── vonage.py         # Vonage WebSocket bridge
│   ├── signalwire.py     # SignalWire Relay API
│   └── bandwidth.py     # Bandwidth StartStream
├── core/                 # Core voice processing
│   ├── orchestrator.py   # Main call coordinator
│   ├── audio_pipeline.py # 🎤 ElevenLabs TTS integration
│   ├── ai/              # LLM integration & prompts
│   └── personas/        # Voice personality configs
├── voice_system/        # 🎵 Advanced Voice Management
│   ├── multilingual_voice_test.py    # Test voices & languages
│   ├── voice_config_manager.py       # Voice configuration system
│   ├── advanced_voice_manager.py     # Advanced voice management
│   └── voice_config.json            # Saved voice configurations
├── api/                 # FastAPI endpoints
│   ├── webhooks/        # Carrier webhook handlers
│   ├── websockets/      # Real-time audio streaming
│   └── rest/           # Management APIs
├── config/             # Configuration management
└── tests/              # Test suite
```

## 🚦 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your carrier credentials and API keys
```

### 3. Run the Server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Test Voice Generation & Multilingual Support
```bash
# Test all 13+ voices in multiple languages
python multilingual_voice_test.py

# Configure voice settings and preferences  
python voice_config_manager.py

# Generate individual persona samples
python demo_personas.py  

# Open audio_test.html in browser to test playback
```

### 5. Configure Webhooks
Point your carrier webhooks to:
- Twilio: `https://your-domain.com/webhooks/twilio`
- Telnyx: `https://your-domain.com/webhooks/telnyx`
- etc.

## 🎤 Voice System & Testing

### Professional Voice Library
The system now includes 13+ professional ElevenLabs voices:

**Generated Voice Samples:**
- `demo_stephen.mp3` - Stephen persona (Adam voice - confident, authoritative)
- `demo_nova.mp3` - Nova persona (Bella voice - warm, empathetic)  
- `demo_sugar.mp3` - Sugar persona (Elli voice - bubbly, energetic)
- `client_demo_*.mp3` - All available voice samples for client review

**Voice Categories:**
- **Professional & Business**: Adam, Rachel, Daniel, Alice
- **Friendly & Conversational**: Antoni, Bella, Sam
- **Confident & Strong**: Domi, Josh  
- **Energetic & Youthful**: Elli
- **Multilingual**: Giovanni (Italian+), Matilda (Multi-European)

### Multilingual Testing
```bash
# Test voices across multiple languages
python multilingual_voice_test.py

# Generated multilingual samples:
# test_giovanni_it_IT.mp3 (Italian)
# test_giovanni_es_ES.mp3 (Spanish)  
# test_matilda_fr_FR.mp3 (French)
# test_matilda_de_DE.mp3 (German)
```

### Voice Configuration Management
```bash
# Interactive voice configuration
python voice_config_manager.py

# Features:
# - Smart voice recommendations based on criteria
# - Custom voice parameter tuning (stability, similarity, style)
# - Easy persona-to-voice mapping
# - Client-friendly voice showcase
```

### Audio Playback Issues?
If you can't hear the generated audio:

1. **Mobile Testing**: Use the web server for phone testing
   ```bash
   python -m http.server 8091 --bind 0.0.0.0
   # Access: http://your-ip:8091/mobile_test.html
   ```
2. **HTML Audio Player**: Open `audio_test.html` or `mobile_test.html`
3. **Direct File Testing**: Right-click MP3 files → "Open with" → Choose media player
4. **System Check**: Verify speakers/headphones and Windows sound settings

## 🔧 Configuration

### Carrier Selection
```python
# Set primary carrier via environment
CARRIER=telnyx  # or twilio, vonage, signalwire, bandwidth

# Or use config-driven routing
CARRIER_ROUTING={
    "primary": "telnyx",
    "fallback": ["bandwidth", "twilio"],
    "geographic": {
        "US": "bandwidth",
        "CA": "telnyx",
        "EU": "vonage"
    }
}
```

### Voice Personas
```python
VOICE_PERSONAS = {
    "stephen": {"voice_id": "...", "tone": "professional", "speed": 1.0},
    "nova": {"voice_id": "...", "tone": "friendly", "speed": 1.1},
    "sugar": {"voice_id": "...", "tone": "warm", "speed": 0.9}
}
```

## 📊 Usage Examples

### Inbound Call Handling
```python
# Automatic call answering with AI qualification
@app.websocket("/voice/inbound/{session_id}")
async def handle_inbound_call(websocket, session_id):
    adapter = get_carrier_adapter()
    orchestrator = VoiceOrchestrator(session_id)
    
    await orchestrator.greet_caller()
    await orchestrator.qualify_intent()
    await orchestrator.route_or_transfer()
```

### Outbound Campaign
```python
# Launch AI-driven outbound campaigns
campaign = OutboundCampaign(
    leads=airtable.get_inactive_leads(200),
    persona="stephen",
    script_template="reactivation",
    compliance_check=True
)
await campaign.execute()
```

## 🔐 Compliance & Security

- **TCPA Compliance**: Automated consent checking and opt-out handling
- **DNC Registry**: Real-time Do Not Call list validation
- **Call Recording**: Encrypted storage with retention policies
- **Data Privacy**: GDPR/CCPA compliant data handling
- **Rate Limiting**: Configurable call throttling per jurisdiction

## 📈 Monitoring & Analytics

- **Real-time Dashboard**: Live call monitoring and agent performance
- **Conversation Analytics**: Sentiment analysis and keyword tracking
- **Performance Metrics**: Latency, conversion rates, call quality scores
- **A/B Testing**: Voice persona and script optimization

## 🚀 Deployment

### Docker
```bash
docker build -t ghostvoice .
docker run -p 8000:8000 ghostvoice
```

### Kubernetes
```bash
kubectl apply -f k8s/
```

### Cloud Providers
- AWS: ECS/EKS with ALB
- GCP: Cloud Run with Load Balancer
- Azure: Container Instances with App Gateway

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs/](docs/)
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: support@ghostvoice.ai

---

**Built with ❤️ by the GhostVoice Team**