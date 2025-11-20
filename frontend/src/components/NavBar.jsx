import './NavBar.css'

export default function NavBar({ activeTab, setActiveTab }) {
  return (
    <nav className="nav-bar">
      <div 
        className={`nav-tab ${activeTab === 'transcription' ? 'active' : ''}`}
        onClick={() => setActiveTab('transcription')}
      >
        Transcription
      </div>
      <div 
        className={`nav-tab ${activeTab === 'tracking' ? 'active' : ''}`}
        onClick={() => setActiveTab('tracking')}
      >
        Tracking
      </div>
      <div 
        className={`nav-tab ${activeTab === 'health' ? 'active' : ''}`}
        onClick={() => setActiveTab('health')}
      >
        Health
      </div>
    </nav>
  )
}

