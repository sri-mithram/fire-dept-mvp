/**
 * Development Server with Auto-Backend Start
 * 
 * This server:
 * 1. Auto-starts the Python backend
 * 2. Serves the React frontend via Vite
 * 3. Proxies API requests to backend
 * 
 * Just run: npm start
 */

import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { existsSync } from 'fs';
import http from 'http';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const PROJECT_ROOT = join(__dirname, '..');
const BACKEND_DIR = join(PROJECT_ROOT, 'radio-transcription');
const BACKEND_SCRIPT = join(BACKEND_DIR, 'run.py');

let backendProcess = null;
let viteProcess = null;

// Check if backend is already running
function checkBackend() {
  return new Promise((resolve) => {
    const req = http.request('http://localhost:8000/api/v1/health', { timeout: 2000 }, (res) => {
      resolve(res.statusCode === 200);
    });
    req.on('error', () => resolve(false));
    req.on('timeout', () => {
      req.destroy();
      resolve(false);
    });
    req.end();
  });
}

// Start Python backend
function startBackend() {
  if (backendProcess) {
    console.log('Backend already running');
    return;
  }

  if (!existsSync(BACKEND_SCRIPT)) {
    console.error(`Backend script not found: ${BACKEND_SCRIPT}`);
    return;
  }

  console.log('🚀 Starting Python backend...');
  
  backendProcess = spawn('python', ['run.py'], {
    cwd: BACKEND_DIR,
    stdio: 'inherit',
    shell: true
  });

  backendProcess.on('error', (error) => {
    console.error('Failed to start backend:', error);
    backendProcess = null;
  });

  backendProcess.on('exit', (code) => {
    console.log(`Backend exited with code ${code}`);
    backendProcess = null;
  });
}

// Start Vite dev server
function startVite() {
  console.log('🎨 Starting Vite dev server...');
  
  viteProcess = spawn('npm', ['run', 'dev'], {
    cwd: __dirname,
    stdio: 'inherit',
    shell: true
  });

  viteProcess.on('error', (error) => {
    console.error('Failed to start Vite:', error);
  });
}

// Cleanup on exit
process.on('SIGINT', () => {
  console.log('\n🛑 Shutting down...');
  
  if (backendProcess) {
    console.log('Stopping backend...');
    backendProcess.kill();
  }
  
  if (viteProcess) {
    console.log('Stopping Vite...');
    viteProcess.kill();
  }
  
  process.exit(0);
});

// Main
async function main() {
  console.log('='.repeat(60));
  console.log('Fire Department MVP - Development Server');
  console.log('='.repeat(60));
  console.log();
  
  // Check if backend is already running
  const backendRunning = await checkBackend();
  
  if (!backendRunning) {
    startBackend();
    // Wait a bit for backend to start
    await new Promise(resolve => setTimeout(resolve, 3000));
  } else {
    console.log('✅ Backend already running on port 8000');
  }
  
  // Start Vite
  startVite();
  
  console.log();
  console.log('✅ Development server starting...');
  console.log('📱 Frontend: http://localhost:5173');
  console.log('🔧 Backend:  http://localhost:8000');
  console.log();
  console.log('Press Ctrl+C to stop');
}

main().catch(console.error);
