# Fire Department MVP

Real-time radio transcription and health monitoring system.

## 🚀 Quick Start

### Local Development

1. **Install dependencies:**
```bash
   # Frontend
   cd frontend && npm install

   # Backend
   cd ../radio-transcription && pip install -r requirements.txt
```

2. **Configure environment:**
```bash
   # Create .env file
   cd radio-transcription
   cp .env.example .env
   
   # Edit .env and add your OpenAI API key
   # OPENAI_API_KEY=sk-your-key-here
   ```

3. **Start everything:**
   ```bash
   cd ../frontend
   npm start
   ```

The dev server will auto-start the backend and open your browser!

## ☁️ Cloud Deployment

**Don't want to install Node.js locally?** Deploy to the cloud!

See [DEPLOYMENT.md](DEPLOYMENT.md) for step-by-step instructions.

**Quick options:**
- **Vercel + Railway** (Recommended - Free tier)
- **Render** (One platform - Free tier)

Both options are fully documented in [DEPLOYMENT.md](DEPLOYMENT.md).

## 📋 Requirements

- **Node.js** 18+ (for frontend)
- **Python** 3.8+ (for backend)
- **OpenAI API Key** ([Get one](https://platform.openai.com/api-keys))

## 🔑 Environment Variables

### Required

**Backend** (`radio-transcription/.env`):
```
OPENAI_API_KEY=sk-your-key-here
```

### Optional (Cloud Deployment)

**Frontend** (set in platform):
```
VITE_API_BASE_URL=https://your-backend-url.com
```

**Backend** (set in platform):
```
CORS_ORIGINS=https://your-frontend-url.com
```

See [Environment Setup](docs/ENV_SETUP.md) for details.

## ✨ Features

- 🎤 **Live Microphone Transcription** - Real-time speech-to-text
- 📡 **Radio Channel Transcription** - Multi-channel monitoring
- ❤️ **Health Monitoring** - Real-time health stats
- 🏢 **Building Tracking** - 3D visualization (coming soon)

## 📁 Project Structure

```
fire-dept-mvp-main/
├── frontend/              # React app
│   ├── src/
│   └── package.json
├── radio-transcription/   # Python backend
│   ├── api/
│   ├── core/
│   └── .env              # Create this file (see .env.example)
└── docs/                  # Documentation
```

## 📖 Documentation

- [Quick Start](docs/QUICK_START.md) - Get started quickly
- [Environment Setup](docs/ENV_SETUP.md) - Configure API keys
- [Cloud Deployment](docs/CLOUD_DEPLOYMENT.md) - Deploy to cloud

## 🆘 Troubleshooting

### Backend won't start
- Check `.env` file exists in `radio-transcription/`
- Verify `OPENAI_API_KEY` is set correctly
- Check port 8000 is not in use

### Frontend won't start
- Install Node.js 18+ from [nodejs.org](https://nodejs.org/)
- Run `npm install` in `frontend/` directory

### Live mic not working
- Check microphone permissions
- Verify backend is running
- Check browser console for errors

## 📝 License

See LICENSE file for details.
