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

### OPENAI_API_KEY (Required - Backend)
```
OPENAI_API_KEY=sk-...
```
- **Required for**: Transcription service
- **Get it from**: https://platform.openai.com/api-keys
- **Format**: Starts with `sk-`
- **Location**: Set in `radio-transcription/.env` or deployment platform

## Frontend Environment Variables

### VITE_GOOGLE_MAPS_API_KEY (Optional - Frontend)
```
VITE_GOOGLE_MAPS_API_KEY=your-google-maps-api-key
```
- **Purpose**: Used for geocoding addresses and Street View in the Tracking tab
- **Get it from**: https://console.cloud.google.com/google/maps-apis
- **Required**: No (Tracking tab will show a message if not set)
- **Location**: Set in `frontend/.env` or deployment platform environment variables

### VITE_ONEGEO_API_KEY (Optional - Frontend)
```
VITE_ONEGEO_API_KEY=your-onegeo-api-key
```
- **Purpose**: Used for enhanced building data (height, floors, etc.) in the Tracking tab
- **Get it from**: https://onegeo.co/api/#plans
- **Required**: No (will fallback to default building data if not set)
- **Location**: Set in `frontend/.env` or deployment platform environment variables

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

## File Locations

- **Backend (Local)**: `radio-transcription/.env`
- **Frontend (Local)**: `frontend/.env` (create from `frontend/.env.example`)
- **Cloud**: Set in platform's environment variables (Railway, Render, Vercel, etc.)

## Security

- ✅ `.env` files are in `.gitignore` (never committed)
- ✅ Never share your API keys
- ✅ Use different keys for dev/prod
- ✅ Rotate keys regularly
- ✅ Frontend keys (VITE_*) are exposed in the browser - use API key restrictions in Google Cloud Console
- ✅ Backend keys go in `radio-transcription/.env`
- ✅ Frontend keys go in `frontend/.env` or deployment platform
