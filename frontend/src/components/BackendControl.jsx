import { useState, useEffect } from 'react'
import './BackendControl.css'

import { API_BASE_URL } from '../config'

export default function BackendControl({ onBackendReady }) {
  const [status, setStatus] = useState('checking')
  const [message, setMessage] = useState('Checking backend status...')

  useEffect(() => {
    checkBackendStatus()
    const interval = setInterval(checkBackendStatus, 5000)
    return () => clearInterval(interval)
  }, [])

  async function checkBackendStatus() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/health`, {
        signal: AbortSignal.timeout(3000)
      })
      if (response.ok) {
        setStatus('ready')
        setMessage('Backend is ready!')
        onBackendReady?.(true)
      } else {
        setStatus('stopped')
        setMessage('Backend is not responding')
        onBackendReady?.(false)
      }
    } catch (error) {
      setStatus('stopped')
      if (error.name === 'AbortError') {
        setMessage('Backend connection timeout')
      } else if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
        setMessage('Cannot reach backend server')
      } else {
        setMessage('Backend is not running')
      }
      onBackendReady?.(false)
    }
  }

  if (status === 'ready') {
    return null // Hide when ready
  }

  const isLocalDev = API_BASE_URL.includes('localhost') || API_BASE_URL.includes('127.0.0.1')

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
        <div className="backend-help">
          {isLocalDev ? (
            <>
              <p>To start the backend locally:</p>
              <code>cd radio-transcription && python run.py</code>
            </>
          ) : (
            <>
              <p>Backend is not accessible at:</p>
              <code>{API_BASE_URL}</code>
              <p style={{ marginTop: '10px', fontSize: '12px', opacity: 0.8 }}>
                Make sure your backend is deployed and <code>VITE_API_BASE_URL</code> is set correctly.
              </p>
            </>
          )}
        </div>
      )}
    </div>
  )
}

