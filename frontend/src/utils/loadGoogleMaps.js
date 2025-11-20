// Utility to load Google Maps API dynamically with API key from environment
export function loadGoogleMaps() {
  return new Promise((resolve, reject) => {
    // Check if already loaded
    if (window.google && window.google.maps) {
      resolve(window.google.maps)
      return
    }

    const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY
    
    if (!apiKey) {
      reject(new Error('VITE_GOOGLE_MAPS_API_KEY environment variable is not set. Please set it in your .env file or deployment platform.'))
      return
    }

    // Check if script is already being loaded
    const existingScript = document.querySelector('script[src*="maps.googleapis.com"]')
    if (existingScript) {
      // Wait for it to load
      const checkInterval = setInterval(() => {
        if (window.google && window.google.maps) {
          clearInterval(checkInterval)
          resolve(window.google.maps)
        }
      }, 100)
      
      // Timeout after 10 seconds
      setTimeout(() => {
        clearInterval(checkInterval)
        if (!window.google || !window.google.maps) {
          reject(new Error('Google Maps API failed to load'))
        }
      }, 10000)
      return
    }

    // Create and load script with callback
    const callbackName = `initGoogleMaps_${Date.now()}`
    
    // Set up global callback
    window[callbackName] = () => {
      if (window.google && window.google.maps) {
        resolve(window.google.maps)
      } else {
        reject(new Error('Google Maps API failed to initialize'))
      }
      delete window[callbackName]
    }
    
    // Create script
    const script = document.createElement('script')
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&v=beta&libraries=places,geometry,streetView&callback=${callbackName}`
    script.async = true
    script.defer = true
    
    script.onerror = () => {
      reject(new Error('Failed to load Google Maps API script. Check your API key and network connection.'))
      delete window[callbackName]
    }
    
    document.head.appendChild(script)
  })
}

