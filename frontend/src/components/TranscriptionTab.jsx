import { useState, useEffect, useRef } from 'react'
import LiveMicControls from './LiveMicControls'
import RadioSystemControls from './RadioSystemControls'
import TranscriptDisplay from './TranscriptDisplay'
import './TranscriptionTab.css'

import { API_BASE_URL, WS_URL } from '../config'

export default function TranscriptionTab() {
  const [websocket, setWebsocket] = useState(null)
  const [isConnected, setIsConnected] = useState(false)
  const [transcripts, setTranscripts] = useState([])
  const wsRef = useRef(null)

  useEffect(() => {
    connectWebSocket()
    
    // Auto-start transcription system when component mounts
    autoStartSystem()
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [])

  async function autoStartSystem() {
    try {
      // Check if system is already running
      const statusResponse = await fetch(`${API_BASE_URL}/api/v1/system/status`)
      if (statusResponse.ok) {
        const status = await statusResponse.json()
        if (status.is_running) {
          console.log('Transcription system is already running')
          return
        }
      }
      
      // Start the system
      const startResponse = await fetch(`${API_BASE_URL}/api/v1/system/start`, {
        method: 'POST'
      })
      
      if (startResponse.ok) {
        console.log('Transcription system started automatically')
      } else {
        console.warn('Failed to auto-start transcription system. You may need to click "Start System" manually.')
      }
    } catch (error) {
      console.warn('Could not auto-start transcription system:', error)
      // Don't show error to user - they can start manually if needed
    }
  }

  function connectWebSocket() {
    try {
      const clientId = `frontend-${Date.now()}`
      const ws = new WebSocket(`${WS_URL}?client_id=${clientId}`)
      wsRef.current = ws

      ws.onopen = () => {
        setIsConnected(true)
        console.log('WebSocket connected')
      }

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          handleWebSocketMessage(message)
        } catch (e) {
          console.error('Error parsing WebSocket message:', e)
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        setIsConnected(false)
      }

      ws.onclose = () => {
        setIsConnected(false)
        console.log('WebSocket disconnected')
        // Attempt reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000)
      }

      setWebsocket(ws)
    } catch (error) {
      console.error('Error connecting to WebSocket:', error)
    }
  }

  function handleWebSocketMessage(message) {
    switch (message.type) {
      case 'transcript':
        setTranscripts(prev => [...prev, message.data])
        break
      case 'alert':
        // Handle alerts
        console.warn('ALERT:', message.data)
        break
      case 'status':
        // Handle status updates
        break
      default:
        console.log('Unknown message type:', message.type)
    }
  }

  return (
    <div className="transcription-tab">
      <div className="container">
        <div className="transcription-panel">
          <div className="section-title">Radio Transcription</div>
          
          <div className="controls-section">
            <RadioSystemControls apiUrl={API_BASE_URL} />
            <LiveMicControls apiUrl={API_BASE_URL} />
          </div>

          <div className="transcript-section">
            <TranscriptDisplay 
              transcripts={transcripts}
              isConnected={isConnected}
            />
          </div>
        </div>
      </div>
    </div>
  )
}

