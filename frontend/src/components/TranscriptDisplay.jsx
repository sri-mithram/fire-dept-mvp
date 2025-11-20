import './TranscriptDisplay.css'

export default function TranscriptDisplay({ transcripts, isConnected }) {
  return (
    <div className="transcript-display">
      <div className="transcript-header">
        <h3>Transcripts</h3>
        <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
          {isConnected ? '● Connected' : '○ Disconnected'}
        </div>
      </div>
      
      <div className="transcript-content">
        {transcripts.length === 0 ? (
          <div className="empty-state">
            {isConnected 
              ? 'Waiting for transcripts...' 
              : 'Not connected. Waiting for backend...'}
          </div>
        ) : (
          transcripts.map((transcript, index) => (
            <div 
              key={index} 
              className={`transcript-item ${transcript.is_alert ? 'alert' : ''}`}
            >
              <div className="transcript-meta">
                <span className="channel">{transcript.channel || 'Unknown'}</span>
                <span className="timestamp">
                  {transcript.timestamp 
                    ? new Date(transcript.timestamp).toLocaleTimeString()
                    : ''}
                </span>
              </div>
              <div className="transcript-text">{transcript.text}</div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

