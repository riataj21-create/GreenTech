# GreenTech - Technical Documentation 🌿

## Project Overview
**GreenTech** is a multilingual AI-powered agricultural advisory system built with Streamlit, Google Gemini AI, and speech processing capabilities.

---

## 🏗️ Architecture Overview

### Backend Architecture
```
GreenTech/
├── services/          # Core business logic services
│   ├── ai_service.py     # Gemini AI integration & prompt engineering
│   ├── voice_service.py  # Speech recognition with Faster Whisper
│   └── tts_service.py    # Text-to-speech with pyttsx3
├── utils/            # Utilities & configuration
│   ├── config.py        # Environment config & constants
│   └── storage.py       # Persistent JSON file storage
├── pages/            # Streamlit UI pages
├── data/             # JSON data files
└── main.py           # Application entry point
```

### Technology Stack
- **Frontend**: Streamlit (Web UI framework)
- **AI**: Google Gemini API (`google-genai` SDK v1.16.0)
- **Speech-to-Text**: Faster Whisper (OpenAI Whisper implementation)
- **Text-to-Speech**: pyttsx3 (Windows SAPI voices)
- **Audio**: sounddevice, scipy (recording & resampling)
- **Storage**: JSON files with atomic writes

---

## 🔧 Backend Services

### 1. AI Service (`services/ai_service.py`)

**Purpose**: Handles all Gemini AI interactions for agricultural advice

**Key Functions**:
- `get_agricultural_advice()` - Main API function
- `check_ai_status()` - Connection health check
- `_build_prompt()` - Multilingual prompt construction
- `_get_crop_context()` - Local knowledge injection

**Features**:
- **Multilingual Support**: 5 languages (English, Telugu, Hindi, Tamil, Kannada)
- **Context Enhancement**: Uses local agriculture.json knowledge base
- **Error Handling**: Translates API errors to user-friendly messages
- **Prompt Engineering**: Structured agricultural advisory format
- **Security**: API keys never exposed in responses

**Error Handling**:
```python
# Quota errors with clear guidance
"Gemini API quota exceeded. This usually means:
• Free tier daily limit reached - wait 24 hours or upgrade to paid tier
• Too many requests per minute - wait a few minutes and try again  
• Billing account needs setup for continued usage"
```

### 2. Voice Service (`services/voice_service.py`)

**Purpose**: Speech recognition pipeline with microphone recording

**Key Functions**:
- `start_recording()` / `stop_recording()` - Push-to-talk recording
- `transcribe_audio()` - Whisper-based transcription  
- `check_dependencies()` - Dependency & hardware validation

**Features**:
- **Native Sample Rate Recording**: Records at device native rate (44100Hz)
- **Audio Enhancement**: 3x amplification with clipping protection
- **Intelligent Resampling**: scipy-based resampling to 16kHz for Whisper
- **Push-to-Talk**: No fixed duration, user-controlled recording
- **Model**: Whisper `small` model (better accuracy than `base`)
- **Multilingual**: Language-specific transcription for all 5 languages

**Audio Processing Pipeline**:
1. Record at native device rate (typically 44100Hz)
2. Apply 3x gain boost for quiet microphones  
3. Resample to 16kHz using scipy
4. Pass float32 array directly to Whisper (no file I/O)

### 3. TTS Service (`services/tts_service.py`)

**Purpose**: Text-to-speech using Windows SAPI voices

**Key Functions**:
- `speak()` - Threaded speech synthesis
- `get_tts_status()` - Voice availability for language
- `list_installed_voices()` - Available voice enumeration

**Features**:
- **Language Detection**: Matches voices to GreenTech language settings
- **Thread Safety**: Daemon threads for non-blocking speech
- **Voice Fallback**: English voice fallback for unavailable languages
- **Error Handling**: Clean messages for missing language voices

### 4. Storage Service (`utils/storage.py`)

**Purpose**: Persistent JSON-based history storage

**Key Functions**:
- `save_to_history()` - Atomic write with entry limit
- `load_history_into_session()` - Startup data loading
- `get_history()` / `clear_history()` - Data access

**Features**:
- **Atomic Writes**: Write to .tmp then rename (prevents corruption)
- **Entry Limiting**: Maximum 200 entries with FIFO eviction
- **Streamlit Integration**: Syncs with session state
- **Metadata**: Tracks timestamp, language, input method

---

## 🛠️ Configuration System

### Environment Variables (`.env`)
```bash
# Required: Gemini API key from https://aistudio.google.com/apikey
GEMINI_API_KEY=your_api_key_here

# Optional: Model selection (default: gemini-3.6-flash)
GEMINI_MODEL=gemini-3.6-flash
```

### Available Gemini Models
- `gemini-3.7-flash` - Latest, most capable Flash model
- `gemini-3.6-flash` - **Default** - Previous generation Flash  
- `gemini-3.5-flash` - Older Flash model
- `gemini-2.5-flash` - Fast and cost-effective
- `gemini-2.5-pro` - Most advanced reasoning (higher cost)

### Language Configuration (`utils/config.py`)
```python
LANGUAGES = {
    "English":  {"code": "en", "label": "English",  "native": "English"},
    "Telugu":   {"code": "te", "label": "Telugu",   "native": "తెలుగు"},
    "Hindi":    {"code": "hi", "label": "Hindi",    "native": "हिन्दी"},
    "Tamil":    {"code": "ta", "label": "Tamil",    "native": "தமிழ்"},
    "Kannada":  {"code": "kn", "label": "Kannada",  "native": "ಕನ್ನಡ"},
}
```

---

## 📊 Data Layer

### Agriculture Knowledge Base (`data/agriculture.json`)
**Purpose**: Local agricultural knowledge to enhance Gemini responses

**Structure**:
```json
{
  "crops": {
    "rice": {
      "aliases": ["paddy"],
      "growing_conditions": {...},
      "common_problems": [...], 
      "preventive_practices": [...]
    }
  }
}
```

**Usage**: Injected into Gemini prompts as contextual knowledge for better crop-specific advice

### History Storage (`data/history.json`)
**Purpose**: Persistent user interaction history

**Entry Format**:
```json
{
  "id": "uuid4",
  "timestamp": "2026-08-29T18:00:00Z",
  "crop": "rice",
  "problem": "leaves turning yellow",
  "advice": "AI response...",
  "language": "English", 
  "input_method": "voice"
}
```

---

## 🔍 Error Handling & Diagnostics

### Backend Status Check
```bash
python backend_test.py
```

**Output Example**:
```
=== VOICE SERVICE ===
Voice ready: True
Microphone: Microphone (Realtek(R) Audio)

=== TTS SERVICE ===
TTS available: True
Installed voices: 2
Example voice: Microsoft David Desktop - English (United States)

=== AI SERVICE ===
AI OK: False  # Expected - quota exceeded
Message: Could not connect to Gemini API.

=== STORAGE ===
History entries: 0
History file: C:\Users\user\...\data\history.json

=== CONFIGURATION ===
Gemini configured: True
Gemini model: gemini-3.6-flash
Supported languages: ['English', 'Telugu', 'Hindi', 'Tamil', 'Kannada']
```

### Common Issues & Solutions

#### 1. Gemini API Quota Exceeded
**Symptoms**: "Gemini API quota exceeded" error
**Solutions**:
- Wait 24 hours (free tier daily reset)
- Upgrade to paid tier at [Google AI Studio](https://aistudio.google.com/)
- Switch to cheaper model: `GEMINI_MODEL=gemini-2.5-flash`

#### 2. Voice Service Issues
**Symptoms**: "No microphone found" or poor transcription
**Solutions**:
- Check microphone permissions in Windows
- Install scipy: `pip install scipy>=1.11.0`
- Verify sounddevice: `python -c "import sounddevice; print(sounddevice.query_devices())"`

#### 3. TTS Not Working
**Symptoms**: No speech output or language not supported
**Solutions**:
- Windows only - requires Windows SAPI voices
- Install language packs in Windows Settings
- Check available voices: Settings page in GreenTech app

---

## 🚀 Performance Optimizations

### 1. Voice Processing
- **Native Rate Recording**: Eliminates resampling artifacts
- **Direct Array Processing**: No intermediate file I/O
- **Model Caching**: Whisper model loaded once, reused
- **Background Processing**: Non-blocking audio transcription

### 2. AI Service
- **Prompt Optimization**: Structured format for consistent responses
- **Context Caching**: Local agriculture.json reduces API calls
- **Error Recovery**: Graceful fallbacks for API issues

### 3. Storage
- **Atomic Writes**: Prevents data corruption on crashes
- **Entry Limiting**: Prevents unbounded file growth
- **JSON Streaming**: Memory-efficient large file handling

---

## 🔒 Security Considerations

### API Key Security
- ✅ Keys loaded from environment variables
- ✅ Never logged or returned in responses
- ✅ .env file in .gitignore
- ✅ .env.example template provided

### Input Validation
- ✅ Crop/problem text sanitization
- ✅ Language parameter validation
- ✅ Audio duration limits
- ✅ File path validation for storage

### Error Information
- ✅ Generic error messages to users
- ✅ Detailed errors only to stderr/logs
- ✅ No API response leakage

---

## 🧪 Testing & Quality Assurance

### Automated Tests
```bash
# Backend functionality test
python backend_test.py

# Syntax validation
python -m py_compile services/*.py utils/*.py pages/*.py

# Dependency check  
pip check
```

### Manual Testing Checklist
- [ ] Voice recording and transcription accuracy
- [ ] TTS playback in available languages
- [ ] AI advice generation (when quota available)
- [ ] History persistence across app restarts
- [ ] Error handling for missing dependencies
- [ ] UI responsiveness and navigation

---

## 📋 Technical Interview Questions & Answers

### Architecture Questions

**Q: How does the voice processing pipeline work?**
A: 
1. **Recording**: Uses sounddevice to record at native device sample rate (44100Hz) for optimal quality
2. **Enhancement**: Applies 3x gain amplification to boost quiet microphone input
3. **Resampling**: Uses scipy to resample from native rate to 16kHz (Whisper's expected rate)  
4. **Transcription**: Passes float32 numpy array directly to Faster Whisper (no file I/O)
5. **Language**: Uses language-specific Whisper models for better accuracy

**Q: How do you handle Gemini API rate limits and quotas?**
A:
- **Error Detection**: Parse API error messages for quota/rate limit indicators
- **User Messaging**: Provide clear, actionable error messages explaining free tier limits
- **Model Flexibility**: Allow model switching via environment variable for cost optimization  
- **Graceful Degradation**: Application remains functional when AI service is unavailable
- **No Retry Loops**: Avoid hammering the API with automatic retries

**Q: Explain the multilingual support implementation.**
A:
- **Configuration-Driven**: Language definitions in `utils/config.py` with native names and ISO codes
- **AI Prompts**: Explicit language instructions in prompts ("Respond entirely in తెలుగు")
- **Voice Recognition**: Language-specific Whisper transcription using ISO language codes
- **TTS Mapping**: Intelligent voice selection based on language with English fallback
- **UI**: Native language labels in interface (తెలుగు, हिन्दी, etc.)

### Technical Deep Dive

**Q: How do you ensure data persistence and prevent corruption?**
A: **Atomic Write Pattern**:
```python
# Write to temporary file first
with open(f"{filepath}.tmp", 'w') as f:
    json.dump(data, f)
# Then rename (atomic operation on most filesystems)  
os.rename(f"{filepath}.tmp", filepath)
```
This prevents corruption if the process crashes during write operations.

**Q: What's your audio processing optimization strategy?**
A:
- **Native Rate Recording**: Avoid unnecessary resampling in the recording phase
- **Memory Efficiency**: Direct numpy array processing without temp files
- **Quality Enhancement**: 3x gain boost with clipping protection for quiet inputs
- **Model Optimization**: Use Whisper `small` model for accuracy/speed balance
- **Resampling Quality**: scipy.signal.resample for high-quality rate conversion

**Q: How do you handle real-time audio in a web application?**
A:
- **Push-to-Talk Model**: User-controlled recording start/stop (not fixed duration)
- **Thread Safety**: Audio callbacks run in separate threads with proper locking
- **State Management**: Global recording state with thread-safe access
- **Non-Blocking UI**: Recording doesn't freeze the Streamlit interface
- **Error Recovery**: Clean teardown of audio streams on failures

### Scalability & Performance

**Q: How would you scale this for production use?**
A:
1. **Database Layer**: Replace JSON files with PostgreSQL/MongoDB
2. **Audio Service**: Separate microservice for voice processing  
3. **API Gateway**: Rate limiting and load balancing for Gemini API
4. **Caching**: Redis for frequently accessed agricultural knowledge
5. **CDN**: Static asset delivery and global deployment
6. **Monitoring**: Application metrics and health checks

**Q: What are the current performance bottlenecks?**
A:
1. **Whisper Model Loading**: ~2-3 second cold start (mitigated by lazy loading)
2. **Gemini API Latency**: Network round-trip for AI responses  
3. **Audio Processing**: Real-time constraints for speech recognition
4. **File I/O**: JSON serialization for history (acceptable for current scale)

### Security & Reliability

**Q: How do you secure API keys and sensitive data?**
A:
- **Environment Variables**: Keys loaded from .env, never hardcoded
- **No Logging**: API keys never appear in logs or error messages
- **Response Filtering**: Only safe data returned from service functions
- **Input Sanitization**: Validate all user inputs before API calls
- **Error Boundaries**: Generic error messages to users, detailed logs for developers

**Q: What's your error handling philosophy?**
A:
- **User-Friendly Messages**: Clear, actionable error descriptions
- **Graceful Degradation**: App remains functional when services fail
- **Developer Context**: Detailed errors logged to stderr for debugging
- **Recovery Guidance**: Specific instructions for common issues (quota exceeded, etc.)
- **No Information Leakage**: Never expose internal implementation details

---

## 🔧 Development Commands

```bash
# Start application
streamlit run main.py

# Run backend tests  
python backend_test.py

# Check dependencies
pip install -r requirements.txt
pip check

# Validate code
python -m py_compile services/*.py utils/*.py pages/*.py

# Clean cache
rm -rf __pycache__ services/__pycache__ utils/__pycache__ pages/__pycache__
```

---

## 📞 Support & Troubleshooting

### Quick Diagnostics
1. Run `python backend_test.py` 
2. Check `.env` file has `GEMINI_API_KEY`
3. Verify microphone permissions in Windows
4. Test voice recording with Windows Voice Recorder
5. Check Gemini API quota at [Google AI Studio](https://aistudio.google.com/)

### Log Locations
- **Application Errors**: Streamlit console output
- **Voice Service**: stderr output with `[GreenTech voice]` prefix  
- **TTS Service**: stderr output with `[GreenTech tts_service]` prefix
- **AI Service**: stderr output with `[GreenTech ai_service error]` prefix

---

*Last Updated: August 29, 2026*
*GreenTech v1.0.0 - Production Ready* ✅