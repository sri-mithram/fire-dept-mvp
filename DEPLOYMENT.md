# Deployment Instructions

## 📋 Pre-Deployment Checklist

- [ ] Code is pushed to GitHub
- [ ] You have an OpenAI API key
- [ ] You have accounts on deployment platforms (Vercel, Railway, or Render)

## 🔑 Environment Variables

### Required

**Backend** - Set in your deployment platform:
```
OPENAI_API_KEY=sk-your-key-here
```

Get your key from: https://platform.openai.com/api-keys

### Optional (Cloud Only)

**Frontend** - Set in your deployment platform:
```
VITE_API_BASE_URL=https://your-backend-url.com
VITE_GOOGLE_MAPS_API_KEY=your-google-maps-key (for Tracking tab)
VITE_ONEGEO_API_KEY=your-onegeo-key (for enhanced building data)
```

**Backend** - Set in your deployment platform:
```
CORS_ORIGINS=https://your-frontend-url.com
```

**Note**: Frontend API keys (VITE_*) are exposed in the browser. Use API key restrictions in Google Cloud Console for security.

---

## 🚀 Option 1: Vercel + Railway (Recommended - Free)

### Step 1: Deploy Frontend (Vercel)

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/sri-mithram/fire-dept-mvp.git
   git push -u origin master
   ```
   
   **Note:** If your default branch is `main` instead of `master`, use `main` instead.

2. **Deploy to Vercel (FRONTEND ONLY):**
   - Go to [vercel.com](https://vercel.com)
   - Sign up with GitHub
   - Click "New Project"
   - Import your repository
   - **⚠️ IMPORTANT: In project settings, set Root Directory to `frontend`**
   - **Framework Preset**: Vite (auto-detected)
   - **Build Command**: Leave as auto (or set to `npm run build`)
   - **Output Directory**: Leave as auto (or set to `dist`)
   - **⚠️ NOTE: Vercel is for FRONTEND ONLY. Backend runs separately on Railway/Render.**
   - Click "Deploy"
   
   **To set Root Directory after deployment:**
   1. Go to Project Settings → General
   2. Scroll to "Root Directory"
   3. Set to: `frontend`
   4. Save and redeploy

3. **Note your frontend URL** (e.g., `https://fire-dept-mvp.vercel.app`)

### Step 2: Deploy Backend (Railway)

1. **Go to [railway.app](https://railway.app)**
2. **Sign up with GitHub**
3. **New Project → Deploy from GitHub**
4. **Select your repository**
5. **Settings:**
   - **Root Directory**: `radio-transcription`
6. **Environment Variables:**
   - Click "Variables" tab
   - Add: `OPENAI_API_KEY` = `sk-your-key`
   - Add: `CORS_ORIGINS` = `https://your-frontend.vercel.app` (from Step 1)
7. **Deploy!**
8. **Note your backend URL** (e.g., `https://fire-dept-backend.railway.app`)

### Step 3: Connect Frontend to Backend

1. **Go back to Vercel**
2. **Settings → Environment Variables**
3. **Add:**
   - `VITE_API_BASE_URL` = `https://your-backend.railway.app` (from Step 2)
   - (Optional) `VITE_GOOGLE_MAPS_API_KEY` = `your-google-maps-key`
   - (Optional) `VITE_ONEGEO_API_KEY` = `your-onegeo-key`
4. **Redeploy** (automatic or click "Redeploy")

**⚠️ Important**: Vercel only hosts the frontend. The backend runs separately on Railway.

### Done! 🎉

Your app is live:
- Frontend: `https://your-frontend.vercel.app`
- Backend: `https://your-backend.railway.app`

---

## 🚀 Option 2: Render (One Platform)

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/fire-dept-mvp.git
git push -u origin master
```

**Note:** If your default branch is `main`, use `git push -u origin main` instead.

### Step 2: Deploy Backend

1. **Go to [render.com](https://render.com)**
2. **Sign up with GitHub**
3. **New → Web Service**
4. **Connect your repository**
5. **Settings:**
   - **Name**: `fire-dept-backend`
   - **Root Directory**: `radio-transcription`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python run.py`
6. **Environment Variables:**
   - `OPENAI_API_KEY` = `sk-your-key`
   - `API_HOST` = `0.0.0.0`
   - `API_PORT` = `$PORT` (Render provides this)
   - `CORS_ORIGINS` = `https://fire-dept-frontend.onrender.com` (update after frontend deploy)
7. **Deploy!**
8. **Note your backend URL** (e.g., `https://fire-dept-backend.onrender.com`)

### Step 3: Deploy Frontend

1. **New → Static Site**
2. **Connect your repository**
3. **Settings:**
   - **Name**: `fire-dept-frontend`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`
4. **Environment Variables:**
   - `VITE_API_BASE_URL` = `https://fire-dept-backend.onrender.com` (from Step 2)
5. **Deploy!**

### Step 4: Update Backend CORS

1. **Go back to backend service**
2. **Environment Variables**
3. **Update `CORS_ORIGINS`** with your actual frontend URL
4. **Redeploy**

### Done! 🎉

Your app is live on Render!

---

## 🔧 Troubleshooting

### Frontend can't connect to backend
- Check `VITE_API_BASE_URL` is set correctly
- Verify backend URL is accessible (visit it in browser)
- Check CORS settings in backend

### Backend won't start
- Verify `OPENAI_API_KEY` is set
- Check build logs for errors
- Ensure Python dependencies are installed

### WebSocket not working
- Some platforms don't support WebSockets
- Check if platform supports WebSocket upgrades
- Use `wss://` for HTTPS connections

---

## 📝 Quick Reference

**Environment Variables:**

| Variable | Where | Required | Value |
|----------|-------|----------|-------|
| `OPENAI_API_KEY` | Backend | ✅ Yes | `sk-...` |
| `VITE_API_BASE_URL` | Frontend | ⚠️ Cloud | `https://your-backend.com` |
| `CORS_ORIGINS` | Backend | ⚠️ Cloud | `https://your-frontend.com` |

**File Locations:**
- Backend `.env`: `radio-transcription/.env` (local only)
- Frontend config: `frontend/src/config.js` (uses env vars)

---

## ✅ Post-Deployment

1. Test frontend URL loads
2. Test backend health: `https://your-backend.com/api/v1/health`
3. Test live mic feature
4. Check browser console for errors
5. Monitor deployment logs

Your app is now live in the cloud! 🚀

