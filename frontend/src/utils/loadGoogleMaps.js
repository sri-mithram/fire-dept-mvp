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
      existingScript.addEventListener('load', () => {
        if (window.google && window.google.maps) {
          resolve(window.google.maps)
        } else {
          reject(new Error('Google Maps API failed to load'))
        }
      })
      return
    }

    // Create and load script
    const script = document.createElement('script')
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&v=beta&libraries=places,geometry,streetView&loading=async&callback=initGoogleMaps`
    script.async = true
    script.defer = true
    
    // Set up callback
    window.initGoogleMaps = () => {
      if (window.google && window.google.maps) {
        resolve(window.google.maps)
      } else {
        reject(new Error('Google Maps API failed to initialize'))
      }
      delete window.initGoogleMaps
    }
    
    script.onerror = () => {
      reject(new Error('Failed to load Google Maps API script'))
      delete window.initGoogleMaps
    }
    
    document.head.appendChild(script)
  })
}

