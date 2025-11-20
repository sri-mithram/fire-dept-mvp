import { useState, useEffect } from 'react'
import NavBar from './components/NavBar'
import TranscriptionTab from './components/TranscriptionTab'
import TrackingTab from './components/TrackingTab'
import HealthTab from './components/HealthTab'
import BackendControl from './components/BackendControl'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('transcription')
  const [backendReady, setBackendReady] = useState(false)

  return (
    <div className="app">
      <NavBar activeTab={activeTab} setActiveTab={setActiveTab} />
      <div className="main-content">
        {activeTab === 'transcription' && (
          <div className="content-view active">
            <BackendControl onBackendReady={setBackendReady} />
            {backendReady && <TranscriptionTab />}
          </div>
        )}
        {activeTab === 'tracking' && (
          <div className="content-view active">
            <TrackingTab />
          </div>
        )}
        {activeTab === 'health' && (
          <div className="content-view active">
            <HealthTab />
          </div>
        )}
      </div>
    </div>
  )
}

export default App

