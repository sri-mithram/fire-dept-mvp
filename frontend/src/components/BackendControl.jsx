import { useState, useEffect } from 'react'
import './BackendControl.css'

import { API_BASE_URL } from '../config'

const CONTROL_SERVER_URL = 'http://localhost:8001' // Only for local dev
const BACKEND_URL = API_BASE_URL

export default function BackendControl({ onBackendReady }) {
  const [status, setStatus] = useState('checking')
  const [message, setMessage] = useState('Checking backend status...')
  const [controlServerAvailable, setControlServerAvailable] = useState(false)

  useEffect(() => {
    checkBackendStatus()
    const interval = setInterval(checkBackendStatus, 5000)
    return () => clearInterval(interval)
  }, [])

  async function checkBackendStatus() {
    // First check if control server is available
    try {
      const controlResponse = await fetch(`${CONTROL_SERVER_URL}/backend-status`)
      if (controlResponse.ok) {
        setControlServerAvailable(true)
        const data = await controlResponse.json()
        
        if (data.backend_ready) {
          setStatus('ready')
          setMessage('Backend is ready!')
          onBackendReady(true)
        } else if (data.backend_running) {
          setStatus('starting')
          setMessage('Backend is starting, please wait...')
          onBackendReady(false)
        } else {
          setStatus('stopped')
          setMessage('Backend is stopped')
          onBackendReady(false)
        }
        return
      }
    } catch (error) {
      // Control server not available - try direct backend check
      setControlServerAvailable(false)
    }

    // Fallback: Check backend directly
    try {
      const response = await fetch(`${BACKEND_URL}/api/v1/health`, {
        signal: AbortSignal.timeout(2000)
      })
      if (response.ok) {
        setStatus('ready')
        setMessage('Backend is ready!')
        onBackendReady(true)
      } else {
        setStatus('stopped')
        setMessage('Backend is not responding')
        onBackendReady(false)
      }
    } catch (error) {
      setStatus('stopped')
      setMessage('Backend is not running')
      onBackendReady(false)
    }
  }

  async function startBackend() {
    try {
      setStatus('starting')
      setMessage('Starting backend...')
      
      const response = await fetch(`${CONTROL_SERVER_URL}/start-backend`)
      const data = await response.json()
      
      if (data.status === 'starting' || data.status === 'already_running') {
        // Poll for status
        const pollInterval = setInterval(async () => {
          const statusResponse = await fetch(`${CONTROL_SERVER_URL}/backend-status`)
          const statusData = await statusResponse.json()
          
          if (statusData.backend_ready) {
            clearInterval(pollInterval)
            setStatus('ready')
            setMessage('Backend is ready!')
            onBackendReady(true)
          }
        }, 2000)
      } else {
        setStatus('error')
        setMessage(`Failed: ${data.message || 'Unknown error'}`)
      }
    } catch (error) {
      setStatus('error')
      setMessage(`Error: ${error.message}. Make sure control_server.py is running!`)
    }
  }

  if (status === 'ready') {
    return null // Hide when ready
  }

  return (
    <div className="backend-control-panel">
      <div className="backend-status">
        <span className={`status-indicator status-${status}`}>
          {status === 'ready' && '✅'}
          {status === 'starting' && '⏳'}
          {status === 'stopped' && '❌'}
          {status === 'error' && '⚠️'}
        </span>
        <span className="status-text">{message}</span>
      </div>
      
      {status === 'stopped' && (
        <button 
          className="start-backend-btn"
          onClick={startBackend}
          disabled={!controlServerAvailable}
        >
          {controlServerAvailable ? '🚀 Start Backend Server' : '⚠️ Control Server Not Running'}
        </button>
      )}
      
      {!controlServerAvailable && status === 'stopped' && (
        <div className="control-server-hint">
          Run: <code>python control_server.py</code> to enable backend control
        </div>
      )}
    </div>
  )
}

