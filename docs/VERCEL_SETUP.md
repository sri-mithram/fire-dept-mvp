# Vercel Setup (Frontend Only)

## ⚠️ Important

**Vercel is for the FRONTEND ONLY.** The backend (Python FastAPI) runs separately on Railway, Render, or another Python hosting service.

## Vercel Build Configuration

Vercel will automatically detect your Vite/React app. The `vercel.json` file is already configured, but here's what you need:

### Required Settings

1. **Root Directory**: `frontend`
2. **Framework**: Vite (auto-detected)
3. **Build Command**: `npm run build` (auto-detected)
4. **Output Directory**: `dist` (auto-detected)

### Environment Variables

Set these in **Vercel Project Settings → Environment Variables**:

#### Required (After Backend is Deployed)

```
VITE_API_BASE_URL=https://your-backend.railway.app
```

Replace `your-backend.railway.app` with your actual backend URL from Railway/Render.

#### Optional

```
VITE_GOOGLE_MAPS_API_KEY=your-google-maps-key
VITE_ONEGEO_API_KEY=your-onegeo-key
```

### Build Process

Vercel will:
1. Install dependencies: `npm install`
2. Build the app: `npm run build`
3. Serve the `dist` folder

**No backend code runs on Vercel!**

## Troubleshooting

### Build Fails

- Check that Root Directory is set to `frontend`
- Verify `package.json` exists in `frontend/` directory
- Check build logs for specific errors

### Frontend Can't Connect to Backend

- Verify `VITE_API_BASE_URL` is set correctly in Vercel
- Check that backend is running and accessible
- Verify CORS is configured on backend (should include your Vercel URL)

### API Keys Not Working

- Frontend keys (VITE_*) are exposed in the browser
- Use API key restrictions in Google Cloud Console
- Never put backend keys (like OPENAI_API_KEY) in Vercel - those go in Railway/Render

## Next Steps

After Vercel deployment:
1. Deploy backend to Railway (see [DEPLOYMENT.md](../DEPLOYMENT.md))
2. Set `VITE_API_BASE_URL` in Vercel to point to your backend
3. Redeploy Vercel to apply changes

