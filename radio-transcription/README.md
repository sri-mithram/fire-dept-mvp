# Radio Transcription Backend

Multi-channel radio transcription system powered by OpenAI's GPT-4o (Whisper API).

## 🚀 Quick Start

### 1. Navigate to this directory

```bash
cd radio-transcription
```

### 2. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment

Create `.env` file:

```bash
OPENAI_API_KEY=your-api-key-here
```

### 4. Configure Channels

Edit `config.py` - Update `RADIO_CHANNELS` with your setup.

### 5. Run Server

```bash
python run.py
```

Server starts on `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

## 📡 Testing

### Test with audio files:

```bash
python test_with_audio_files.py audio1.mp3 audio2.mp3
```

### Check audio energy levels:

```bash
python check_audio_energy.py audio1.mp3
```

## 🔧 Configuration

Key settings in `config.py`:

- `OPENAI_API_KEY` - Set in .env file

- `RADIO_CHANNELS` - Configure your 2 channels

- `ENERGY_THRESHOLD` - Adjust speech detection sensitivity

- `ALERT_KEYWORDS` - Customize alert keywords

## 📊 API Endpoints

### REST API

- `GET /api/v1/health` - Health check

- `GET /api/v1/channels` - List channels

- `GET /api/v1/transcripts` - Get transcripts

- `GET /api/v1/alerts` - Get alerts

- `POST /api/v1/system/start` - Start transcription

- `POST /api/v1/system/stop` - Stop transcription

### WebSocket

- `ws://localhost:8000/ws` - Real-time transcript stream

## 📁 Project Structure

```
radio-transcription/
├── api/              # REST & WebSocket API
├── core/             # Business logic
├── utils/            # Utilities
├── data/             # Transcripts & alerts
├── config.py         # Configuration
└── run.py            # Entry point
```

## 📖 Documentation

See `README_BACKEND.md` for detailed documentation.

## 🔐 Security

- Never commit `.env` file

- Keep `OPENAI_API_KEY` secret

- Review `.gitignore` before pushing

## 🆘 Support

Check logs: `backend.log`

API docs: http://localhost:8000/docs

