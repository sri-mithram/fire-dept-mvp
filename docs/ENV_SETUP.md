# Environment Variables Setup

## Quick Setup

1. **Create `.env` file** in `radio-transcription/` directory:
   ```bash
   cd radio-transcription
   cp .env.example .env
   ```

2. **Edit `.env`** and add your OpenAI API key:
   ```
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

## Required Variables

### OPENAI_API_KEY (Required)
```
OPENAI_API_KEY=sk-...
```
- **Required for**: Transcription service
- **Get it from**: https://platform.openai.com/api-keys
- **Format**: Starts with `sk-`

## Optional Variables

### API_HOST
```
API_HOST=0.0.0.0
```
- Default: `0.0.0.0` (allows external connections)
- For cloud: Keep as `0.0.0.0`

### API_PORT
```
API_PORT=8000
```
- Default: `8000`
- For cloud: Some platforms use `$PORT` (auto-set)

### CORS_ORIGINS (For Cloud Deployment)
```
CORS_ORIGINS=https://your-frontend.vercel.app,https://your-frontend.netlify.app
```
- Add your frontend URL when deploying to cloud
- Separate multiple URLs with commas

## File Location

- **Local**: `radio-transcription/.env`
- **Cloud**: Set in platform's environment variables (Railway, Render, etc.)

## Security

- ✅ `.env` is in `.gitignore` (never committed)
- ✅ Never share your API keys
- ✅ Use different keys for dev/prod
- ✅ Rotate keys regularly
