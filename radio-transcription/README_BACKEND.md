# Radio Transcription Backend

Multi-channel radio transcription system powered by OpenAI's GPT-4o (Whisper API).

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file:

```bash
OPENAI_API_KEY=your-api-key-here
ENVIRONMENT=development
```

### 3. Configure Channels

Edit `config.py` and update `RADIO_CHANNELS` with your setup:

```python
RADIO_CHANNELS = {
    "channel_1": {
        "name": "Fire Dispatch",
        "device_index": 0,  # Update when dongle arrives
        "frequency": "154.280 MHz",
        "color": "🔴",
        "priority": "HIGH",
        "enabled": True
    },
    # Add more channels...
}
```

### 4. Run Server

```bash
python run.py
```

Server starts on `http://localhost:8000`

---

## 📡 API Endpoints

### REST API

All endpoints are prefixed with `/api/v1`

#### System Control

- **POST** `/system/start` - Start transcription
- **POST** `/system/stop` - Stop transcription
- **GET** `/system/status` - Get system status
- **GET** `/devices` - List audio devices

#### Transcripts

- **GET** `/transcripts` - Get transcripts with filters
  - Query params: `date`, `channel`, `limit`, `offset`
- **GET** `/transcripts/recent` - Get recent transcripts
  - Query params: `minutes`, `channel`
- **GET** `/search` - Search transcripts by text
  - Query params: `query`, `date`, `channel`, `limit`

#### Alerts

- **GET** `/alerts` - Get alerts with filters
  - Query params: `date`, `priority`, `limit`, `offset`
- **GET** `/alerts/critical` - Get critical alerts
  - Query params: `hours`

#### Statistics

- **GET** `/stats/summary` - Get summary stats
- **GET** `/stats/timeline` - Get timeline data
  - Query params: `date`, `interval_minutes`

#### Utility

- **GET** `/health` - Health check
- **GET** `/channels` - Get channel configurations

### WebSocket

Connect to `/ws` for real-time streaming:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws?client_id=frontend-1');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  switch(message.type) {
    case 'transcript':
      // New transcript received
      console.log(message.data);
      break;
    case 'alert':
      // Alert detected
      console.log('ALERT:', message.data);
      break;
    case 'status':
      // System status update
      console.log('Status:', message.data);
      break;
  }
};
```

---

## 🔧 Configuration

### Key Settings in `config.py`

```python
# OpenAI API
OPENAI_API_KEY  # Set in .env file

# Audio
SAMPLE_RATE = 16000
AUDIO_CHANNELS = 1
CHUNK_DURATION = 0.1

# VAD (Voice Activity Detection)
VAD_MODE = 3  # 0-3, higher = more aggressive
VAD_SILENCE_DURATION = 0.8  # Seconds
VAD_MIN_SPEECH_DURATION = 0.5

# API Server
API_HOST = "0.0.0.0"
API_PORT = 8000

# CORS (for frontend)
CORS_ORIGINS = [
    "http://localhost:3000",  # React
    "http://localhost:5173",  # Vite
]
```

---

## 📊 Data Storage

### File Structure

```
data/
├── transcripts/
│   ├── transcript_2025-11-18.jsonl
│   └── transcript_2025-11-19.jsonl
└── alerts/
    ├── alerts_2025-11-18.jsonl
    └── alerts_2025-11-19.jsonl
```

### Format

JSONL format (one JSON object per line):

```json
{"timestamp": "2025-11-18T14:30:05Z", "channel": "Fire Dispatch", "text": "Engine 5 to dispatch", "confidence": 0.98, "alert": false, "alert_keywords": []}
{"timestamp": "2025-11-18T14:31:02Z", "channel": "Fire Dispatch", "text": "Mayday, firefighter down", "confidence": 0.97, "alert": true, "alert_keywords": ["mayday", "firefighter down"]}
```

---

## 🧪 Testing

### Test Audio Devices

```bash
python -c "from core.audio_manager import AudioManager; print(AudioManager().list_devices())"
```

### Test Transcription

```python
import asyncio
from core.transcription_service import TranscriptionService
import numpy as np

async def test():
    service = TranscriptionService()
    # Create dummy audio (silence)
    audio = np.zeros(16000, dtype=np.float32)
    result = await service.transcribe(audio, "Test")
    print(result)

asyncio.run(test())
```

### Test API

```bash
# Start server
python run.py

# In another terminal
curl http://localhost:8000/api/v1/health
```

---

## 🚨 Alert System

### Default Keywords

```python
ALERT_KEYWORDS = [
    "mayday", "emergency", "officer down",
    "firefighter down", "code red", "evacuate",
    "urgent", "help", "injury", "collapse"
]
```

### Priority Levels

- **CRITICAL**: mayday, firefighter down, officer down
- **HIGH**: emergency, urgent, evacuate
- **MEDIUM**: injury, help
- **LOW**: default

---

## 🔌 Hardware Setup (When Dongle Arrives)

### 1. List Audio Devices

```bash
curl http://localhost:8000/api/v1/devices
```

### 2. Update config.py

Update `device_index` for each channel:

```python
RADIO_CHANNELS = {
    "channel_1": {
        "device_index": 2,  # ← Update this
        # ...
    }
}
```

### 3. Restart Server

```bash
python run.py
```

### 4. Start Transcription

```bash
curl -X POST http://localhost:8000/api/v1/system/start
```

---

## 📝 Development

### Project Structure

```
radio-transcription-backend/
├── core/           # Business logic
├── api/            # REST & WebSocket
├── utils/          # Utilities
├── data/           # Storage
├── config.py       # Configuration
└── run.py          # Entry point
```

### Adding New Features

1. **New endpoint**: Add to `api/routes.py`
2. **New core logic**: Add to `core/`
3. **New storage**: Update `utils/storage.py`

---

## 🐛 Troubleshooting

### "No OpenAI API Key"

Set in `.env` file:

```bash
OPENAI_API_KEY=sk-...
```

### "No audio devices found"

Check audio devices:

```bash
python -c "import sounddevice as sd; print(sd.query_devices())"
```

### "Permission denied" on audio

**Linux**: Add user to audio group

```bash
sudo usermod -a -G audio $USER
```

### WebSocket not connecting

Check CORS settings in `config.py`:

```python
CORS_ORIGINS = ["http://localhost:3000"]  # Add your frontend URL
```

---

## 📊 Cost Estimation

### OpenAI Whisper API Pricing

- ~$0.006 per minute

### Example Costs

- **12 hours/day** monitoring: ~$4.32/day = ~$130/month
- **24/7** monitoring: ~$8.64/day = ~$260/month
- **2 channels 12hr/day**: ~$8.64/day = ~$260/month

---

## 🔐 Security Notes

- **Never commit** `.env` file
- **Protect** system control endpoints in production
- **Use HTTPS** in production
- **Implement auth** for public deployment

---

## 📞 Support

For issues or questions, check:

1. Logs: `backend.log`
2. API docs: http://localhost:8000/docs
3. Health check: http://localhost:8000/api/v1/health

---

## ✅ Production Checklist

- [ ] Set strong OpenAI API key
- [ ] Configure proper audio device indices
- [ ] Update CORS origins for production frontend
- [ ] Set up HTTPS
- [ ] Implement authentication
- [ ] Set up monitoring/alerting
- [ ] Configure log rotation
- [ ] Set up automated backups
- [ ] Test failover scenarios

---

## 🎉 **COMPLETE! All Files Created**

### **Final File List:**

```
✅ config.py
✅ requirements.txt
✅ .env
✅ .gitignore

Core (7 files):
✅ utils/logger.py
✅ utils/storage.py
✅ core/vad_detector.py
✅ core/transcription_service.py
✅ core/alert_system.py
✅ core/channel_manager.py
✅ core/audio_manager.py

API (4 files):
✅ api/models.py
✅ api/websocket.py
✅ api/routes.py
✅ api/server.py

Main:
✅ run.py
✅ README_BACKEND.md
```

