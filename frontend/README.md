# Fire Department MVP - Frontend

React frontend for the Fire Department MVP application.

## Quick Start

### Option 1: Auto-Start Everything (Recommended)

```bash
npm start
```

This will:
- ✅ Auto-start the Python backend
- ✅ Start the Vite dev server
- ✅ Open the frontend in your browser

**Just one command!**

### Option 2: Manual Start

```bash
# Install dependencies
npm install

# Start dev server (assumes backend is already running)
npm run dev
```

## Development

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **WebSocket**: ws://localhost:8000/ws

## Build for Production

```bash
npm run build
```

Output will be in `dist/` folder - ready to deploy!

## Project Structure

```
frontend/
├── src/
│   ├── components/      # React components
│   │   ├── BackendControl.jsx
│   │   ├── TranscriptionTab.jsx
│   │   ├── LiveMicControls.jsx
│   │   └── ...
│   ├── App.jsx          # Main app component
│   ├── main.jsx         # Entry point
│   └── index.css        # Global styles
├── dev-server.js        # Auto-start dev server
├── vite.config.js       # Vite configuration
└── package.json         # Dependencies
```

