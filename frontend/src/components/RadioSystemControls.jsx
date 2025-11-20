import { useState, useEffect } from 'react'
import './RadioSystemControls.css'

import { API_BASE_URL } from '../config'

export default function RadioSystemControls({ apiUrl = API_BASE_URL }) {
  const [isRunning, setIsRunning] = useState(false)

  // Check system status on mount and periodically
  useEffect(() => {
    checkStatus()
    const interval = setInterval(checkStatus, 5000) // Check every 5 seconds
    return () => clearInterval(interval)
  }, [])

  async function checkStatus() {
    try {
      const response = await fetch(`${apiUrl}/api/v1/system/status`)
      if (response.ok) {
        const data = await response.json()
        setIsRunning(data.is_running || false)
      }
    } catch (error) {
      // Silently fail - backend might not be running
    }
  }

  async function startSystem() {
    try {
      const response = await fetch(`${apiUrl}/api/v1/system/start`, {
        method: 'POST'
      })
      const data = await response.json()
      
      if (data.status === 'success' || data.status === 'already_running') {
        setIsRunning(true)
      } else {
        alert(`Failed: ${data.message || 'Unknown error'}`)
      }
    } catch (error) {
      alert(`Error: ${error.message}`)
    }
  }

  async function stopSystem() {
    try {
      const response = await fetch(`${apiUrl}/api/v1/system/stop`, {
        method: 'POST'
      })
      const data = await response.json()
      
      if (data.status === 'success' || data.status === 'not_running') {
        setIsRunning(false)
      } else {
        alert(`Failed: ${data.message || 'Unknown error'}`)
      }
    } catch (error) {
      alert(`Error: ${error.message}`)
    }
  }

  return (
    <div className="radio-system-controls">
      <h3>Radio System</h3>
      <div className="radio-buttons">
        {!isRunning ? (
          <button className="start-btn" onClick={startSystem}>
            Start System
          </button>
        ) : (
          <button className="stop-btn" onClick={stopSystem}>
            Stop System
          </button>
        )}
      </div>
    </div>
  )
}

