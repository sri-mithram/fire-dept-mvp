import { useState } from 'react'
import './RadioSystemControls.css'

import { API_BASE_URL } from '../config'

export default function RadioSystemControls({ apiUrl = API_BASE_URL }) {
  const [isRunning, setIsRunning] = useState(false)

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

