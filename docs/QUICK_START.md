# Quick Start

## Setup (One Time)

### 1. Install Dependencies

**Frontend:**
```bash
cd frontend
npm install
```

**Backend:**
```bash
cd radio-transcription
pip install -r requirements.txt
```

### 2. Configure Environment

Create `radio-transcription/.env`:
```bash
cd radio-transcription
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-key-here
```

Get your key from: https://platform.openai.com/api-keys

### 3. Start Everything

```bash
cd frontend
npm start
```

This will:
- ✅ Auto-start Python backend
- ✅ Start React frontend
- ✅ Open browser automatically

## Using the App

1. Wait for backend to start (5-10 seconds)
2. Click "🎤 Start Live Mic" button
3. Speak into your microphone
4. See real-time transcripts!

## Requirements

- Node.js 18+ ([Download](https://nodejs.org/))
- Python 3.8+ ([Download](https://www.python.org/))
- OpenAI API Key ([Get one](https://platform.openai.com/api-keys))
