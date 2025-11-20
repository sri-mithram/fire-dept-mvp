import { useState, useEffect } from 'react'
import { API_BASE_URL } from '../config'
import './HealthTab.css'

export default function HealthTab() {
  const [mode, setMode] = useState('realtime') // 'realtime' or 'upload'
  const [stats, setStats] = useState(null)
  const [manualHeartRate, setManualHeartRate] = useState('')
  const [manualOxygen, setManualOxygen] = useState('')
  const [exportStatus, setExportStatus] = useState('')

  useEffect(() => {
    if (mode === 'realtime') {
      fetchHealthStats()
      const interval = setInterval(fetchHealthStats, 5000)
      return () => clearInterval(interval)
    }
  }, [mode])

  async function fetchHealthStats() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/health/stats`)
      if (response.ok) {
        const data = await response.json()
        setStats(data)
      }
    } catch (error) {
      console.error('Error fetching health stats:', error)
    }
  }

  async function submitManualData() {
    try {
      if (manualHeartRate) {
        await fetch(`${API_BASE_URL}/api/v1/health/data?data_type=heart_rate&value=${manualHeartRate}&source=manual_entry`, {
          method: 'POST'
        })
      }
      if (manualOxygen) {
        await fetch(`${API_BASE_URL}/api/v1/health/data?data_type=oxygen&value=${manualOxygen}&source=manual_entry`, {
          method: 'POST'
        })
      }
      setManualHeartRate('')
      setManualOxygen('')
      fetchHealthStats()
    } catch (error) {
      console.error('Error submitting health data:', error)
    }
  }

  async function exportData(type) {
    try {
      setExportStatus('Exporting...')
      const endpoint = type === 'transcripts' 
        ? '/api/v1/export/transcripts'
        : type === 'alerts'
        ? '/api/v1/export/alerts'
        : '/api/v1/export/all'
      
      const response = await fetch(`${API_BASE_URL}${endpoint}`)
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `fire_dept_${type}_${new Date().toISOString().split('T')[0]}.${type === 'all' ? 'xml' : 'json'}`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)
        setExportStatus('Export successful!')
      } else {
        setExportStatus('Export failed')
      }
    } catch (error) {
      console.error('Export error:', error)
      setExportStatus('Export failed')
    }
  }

  return (
    <div className="health-tab">
      <div className="container">
        <div className="health-dashboard-container">
          <div className="section-title">Health Dashboard</div>

          {/* Export Section */}
          <div className="export-section">
            <h3>📥 Export Data</h3>
            <div className="export-buttons">
              <button onClick={() => exportData('transcripts')}>
                Export Transcripts (JSON)
              </button>
              <button onClick={() => exportData('alerts')}>
                Export Alerts (JSON)
              </button>
              <button onClick={() => exportData('all')}>
                Export All (XML)
              </button>
            </div>
            {exportStatus && <div className="export-status">{exportStatus}</div>}
          </div>

          {/* Mode Toggle */}
          <div className="mode-toggle">
            <button 
              className={mode === 'realtime' ? 'active' : ''}
              onClick={() => setMode('realtime')}
            >
              📊 Real-Time Stats
            </button>
            <button 
              className={mode === 'upload' ? 'active' : ''}
              onClick={() => setMode('upload')}
            >
              📤 Upload File
            </button>
          </div>

          {/* Real-Time Stats Section */}
          {mode === 'realtime' && (
            <div className="realtime-section">
              <h2>📊 Real-Time Health Monitoring</h2>
              <p>Live health data from connected devices</p>

              {/* Current Stats Display */}
              {stats && (
                <div className="stats-grid">
                  {stats.heart_rate && (
                    <div className="stat-card">
                      <div className="stat-label">Heart Rate</div>
                      <div className="stat-value">{stats.heart_rate.current || 'N/A'}</div>
                      <div className="stat-unit">BPM</div>
                      {stats.heart_rate.average && (
                        <div className="stat-details">
                          Avg: {stats.heart_rate.average.toFixed(1)} | 
                          Min: {stats.heart_rate.min} | 
                          Max: {stats.heart_rate.max}
                        </div>
                      )}
                    </div>
                  )}
                  
                  {stats.oxygen && (
                    <div className="stat-card">
                      <div className="stat-label">Oxygen Saturation</div>
                      <div className="stat-value">{stats.oxygen.current || 'N/A'}</div>
                      <div className="stat-unit">%</div>
                      {stats.oxygen.average && (
                        <div className="stat-details">
                          Avg: {stats.oxygen.average.toFixed(1)}% | 
                          Min: {stats.oxygen.min}% | 
                          Max: {stats.oxygen.max}%
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* Manual Data Entry */}
              <div className="manual-entry">
                <h3>Manual Entry (Testing)</h3>
                <div className="entry-form">
                  <input
                    type="number"
                    placeholder="Heart Rate (BPM)"
                    value={manualHeartRate}
                    onChange={(e) => setManualHeartRate(e.target.value)}
                  />
                  <input
                    type="number"
                    placeholder="Oxygen (%)"
                    step="0.1"
                    value={manualOxygen}
                    onChange={(e) => setManualOxygen(e.target.value)}
                  />
                  <button onClick={submitManualData}>Submit</button>
                </div>
              </div>
            </div>
          )}

          {/* Upload File Section */}
          {mode === 'upload' && (
            <div className="upload-section">
              <h2>📤 Upload Health Data</h2>
              <p>Upload your Apple Health export.xml file to visualize heart rate and oxygen levels</p>
              <div className="upload-area">
                <input type="file" accept=".xml" id="healthFileInput" />
                <p>Select your export.xml file</p>
              </div>
              <div className="upload-info">
                <h3>How to Export from Apple Health:</h3>
                <ol>
                  <li>Open the Health app on your iPhone</li>
                  <li>Tap your profile picture (top right)</li>
                  <li>Scroll down and tap "Export All Health Data"</li>
                  <li>Wait for the export to complete</li>
                  <li>Upload the export.xml file above</li>
                </ol>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
