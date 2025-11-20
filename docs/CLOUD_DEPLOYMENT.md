# Cloud Deployment Guide

Deploy the Fire Department MVP to the cloud - no local Node.js needed!

## 🚀 Quick Deploy Options

### Option 1: Vercel (Frontend) + Railway (Backend) - **Easiest & Free**

**Best for**: Quick deployment, free tier available

#### Frontend (Vercel)
1. **Push code to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/fire-dept-mvp.git
   git push -u origin main
   ```

2. **Deploy to Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Sign up with GitHub
   - Click "New Project"
   - Import your repository
   - **Root Directory**: Set to `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - Click "Deploy"

3. **Configure Environment Variables:**
   - In Vercel dashboard → Settings → Environment Variables
   - Add: `VITE_API_BASE_URL=https://your-backend.railway.app`

#### Backend (Railway)
1. **Go to [railway.app](https://railway.app)**
2. **Sign up with GitHub**
3. **New Project → Deploy from GitHub**
4. **Select your repository**
5. **Set Root Directory**: `radio-transcription`
6. **Add Environment Variables:**
   - `OPENAI_API_KEY=sk-your-key`
   - `API_HOST=0.0.0.0`
   - `API_PORT=8000`
7. **Deploy!**

**Cost**: Free tier available for both

---

### Option 2: Render (Full Stack) - **One Platform**

**Best for**: Simpler setup, everything in one place

#### Frontend
1. **Go to [render.com](https://render.com)**
2. **New → Static Site**
3. **Connect GitHub repository**
4. **Settings:**
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/dist`
5. **Add Environment Variable:**
   - `VITE_API_BASE_URL=https://your-backend.onrender.com`

#### Backend
1. **New → Web Service**
2. **Connect GitHub repository**
3. **Settings:**
   - **Root Directory**: `radio-transcription`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python run.py`
   - **Environment**: Python 3
4. **Add Environment Variables:**
   - `OPENAI_API_KEY=sk-your-key`
   - `API_HOST=0.0.0.0`
   - `API_PORT=$PORT` (Render provides this)
5. **Deploy!**

**Cost**: Free tier available (with limitations)

---

### Option 3: Docker + Any Cloud Provider

**Best for**: Full control, production-ready

#### Create Dockerfile for Frontend

Create `frontend/Dockerfile`:
```dockerfile
# Build stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Create `frontend/nginx.conf`:
```nginx
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /ws {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

#### Create Dockerfile for Backend

Create `radio-transcription/Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "run.py"]
```

#### Deploy with Docker

**Option A: Docker Compose (Single Server)**
Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  backend:
    build: ./radio-transcription
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - API_HOST=0.0.0.0
      - API_PORT=8000
    volumes:
      - ./radio-transcription/data:/app/data

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
```

Deploy to:
- **DigitalOcean App Platform**
- **AWS ECS/Fargate**
- **Google Cloud Run**
- **Azure Container Instances**

**Option B: Separate Services**
- Deploy frontend to **Vercel/Netlify** (static)
- Deploy backend to **Railway/Render** (Python service)

---

## 🔧 Configuration for Cloud

### Update Frontend API URL

Edit `frontend/src/components/TranscriptionTab.jsx`:
```javascript
// Change from localhost to your backend URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://your-backend.railway.app'
const WS_URL = API_BASE_URL.replace('http://', 'ws://').replace('https://', 'wss://') + '/ws'
```

### Update Backend CORS

Edit `radio-transcription/config.py`:
```python
CORS_ORIGINS = [
    "https://your-frontend.vercel.app",
    "https://your-frontend.netlify.app",
    # Add your frontend URL
]
```

### Environment Variables

**Frontend (.env or platform settings):**
```
VITE_API_BASE_URL=https://your-backend-url.com
```

**Backend (.env or platform settings):**
```
OPENAI_API_KEY=sk-your-key
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=https://your-frontend-url.com
```

---

## 📦 Platform-Specific Guides

### Vercel (Frontend)

1. **Install Vercel CLI** (optional):
   ```bash
   npm i -g vercel
   ```

2. **Deploy:**
   ```bash
   cd frontend
   vercel
   ```

3. **Configure:**
   - Set build command: `npm run build`
   - Set output directory: `dist`
   - Add environment variables in dashboard

### Railway (Backend)

1. **Install Railway CLI** (optional):
   ```bash
   npm i -g @railway/cli
   ```

2. **Deploy:**
   ```bash
   cd radio-transcription
   railway login
   railway init
   railway up
   ```

3. **Add Environment Variables:**
   ```bash
   railway variables set OPENAI_API_KEY=sk-your-key
   ```

### Render

1. **Create `render.yaml`** in project root:
   ```yaml
   services:
     - type: web
       name: fire-dept-backend
       env: python
       rootDir: radio-transcription
       buildCommand: pip install -r requirements.txt
       startCommand: python run.py
       envVars:
         - key: OPENAI_API_KEY
           sync: false
   
     - type: web
       name: fire-dept-frontend
       rootDir: frontend
       buildCommand: npm install && npm run build
       staticPublishPath: dist
       envVars:
         - key: VITE_API_BASE_URL
           value: https://fire-dept-backend.onrender.com
   ```

2. **Deploy:**
   - Connect GitHub repo
   - Render auto-detects `render.yaml`
   - Deploys both services

---

## 🎯 Recommended Setup (Easiest)

### For Quick Start:
1. **Frontend**: Vercel (free, automatic deployments)
2. **Backend**: Railway (free tier, easy Python deployment)

### For Production:
1. **Frontend**: Vercel or Netlify (CDN, fast)
2. **Backend**: Railway or Render (reliable, scalable)

---

## 🔐 Security Considerations

### Environment Variables
- ✅ Never commit `.env` files
- ✅ Use platform's environment variable settings
- ✅ Rotate API keys regularly

### CORS
- ✅ Only allow your frontend domain
- ✅ Don't use `*` in production

### API Keys
- ✅ Store in platform's secret management
- ✅ Use different keys for dev/prod

---

## 💰 Cost Comparison

| Platform | Frontend | Backend | Free Tier |
|----------|----------|---------|-----------|
| Vercel | ✅ | ❌ | 100GB bandwidth |
| Railway | ❌ | ✅ | $5 credit/month |
| Render | ✅ | ✅ | Limited hours |
| Netlify | ✅ | ❌ | 100GB bandwidth |
| Heroku | ✅ | ✅ | ❌ (paid only) |

**Recommended**: Vercel (frontend) + Railway (backend) = Free for small projects

---

## 🚀 Quick Deploy Script

Create `deploy.sh`:
```bash
#!/bin/bash

# Build frontend
cd frontend
npm install
npm run build
cd ..

# Deploy frontend to Vercel
cd frontend
vercel --prod
cd ..

# Deploy backend to Railway
cd radio-transcription
railway up
cd ..
```

---

## 📝 Deployment Checklist

- [ ] Push code to GitHub
- [ ] Set up frontend deployment (Vercel/Netlify)
- [ ] Set up backend deployment (Railway/Render)
- [ ] Configure environment variables
- [ ] Update CORS settings
- [ ] Update API URLs in frontend
- [ ] Test deployment
- [ ] Set up custom domain (optional)
- [ ] Configure SSL/HTTPS (automatic on most platforms)

---

## 🆘 Troubleshooting

### Frontend can't connect to backend
- Check CORS settings in backend
- Verify backend URL in frontend environment variables
- Check backend is running (visit backend URL directly)

### WebSocket not working
- Ensure WebSocket upgrade is configured
- Check if platform supports WebSockets (some don't)
- Use `wss://` for HTTPS connections

### Build fails
- Check Node.js version (need 18+)
- Check Python version (need 3.8+)
- Review build logs for errors

---

## 📚 Next Steps

1. Choose your platform(s)
2. Push code to GitHub
3. Follow platform-specific setup
4. Configure environment variables
5. Deploy!
6. Test and verify

Your app will be live on the cloud - no local Node.js needed! 🎉

