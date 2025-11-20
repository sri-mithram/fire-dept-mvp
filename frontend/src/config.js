// Configuration for API URLs
// Uses environment variables in production, defaults to localhost in development

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
export const WS_URL = API_BASE_URL
  .replace('http://', 'ws://')
  .replace('https://', 'wss://') + '/ws'

export const CONFIG = {
  API_BASE_URL,
  WS_URL,
  // Add other config here
}

