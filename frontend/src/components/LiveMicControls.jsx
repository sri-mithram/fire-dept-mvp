import { useState } from 'react'
import './LiveMicControls.css'

import { API_BASE_URL } from '../config'

export default function LiveMicControls({ apiUrl = API_BASE_URL }) {
  const [isRecording, setIsRecording] = useState(false)
  const [status, setStatus] = useState('Ready to record')

  async function startRecording() {
    try {
      setStatus('Starting...')
      const response = await fetch(`${apiUrl}/api/v1/live-transcription/start`, {
        method: 'POST'
      })
      const data = await response.json()
      
      if (data.status === 'success' || data.status === 'already_recording') {
        setIsRecording(true)
        setStatus('🎤 Recording... Speak into your microphone')
      } else {
        setStatus(`Failed: ${data.message || 'Unknown error'}`)
      }
    } catch (error) {
      setStatus(`Error: ${error.message}`)
    }
  }

  async function stopRecording() {
    try {
      setStatus('Stopping...')
      const response = await fetch(`${apiUrl}/api/v1/live-transcription/stop`, {
        method: 'POST'
      })
      const data = await response.json()
      
      if (data.status === 'success' || data.status === 'not_recording') {
        setIsRecording(false)
        setStatus('Recording stopped')
      } else {
        setStatus(`Failed: ${data.message || 'Unknown error'}`)
      }
    } catch (error) {
      setStatus(`Error: ${error.message}`)
    }
  }

  return (
    <div className="live-mic-controls">
      <div className="live-mic-header">
        <h3>Live Microphone Transcription</h3>
        <div className={`status-indicator ${isRecording ? 'recording' : ''}`}>
          {isRecording ? '●' : '○'}
        </div>
      </div>
      
      <div className="live-mic-status">{status}</div>
      
      <div className="live-mic-buttons">
        {!isRecording ? (
          <button 
            className="start-btn"
            onClick={startRecording}
          >
            🎤 Start Live Mic
          </button>
        ) : (
          <button 
            className="stop-btn"
            onClick={stopRecording}
          >
            🛑 Stop Live Mic
          </button>
        )}
      </div>
    </div>
  )
}

