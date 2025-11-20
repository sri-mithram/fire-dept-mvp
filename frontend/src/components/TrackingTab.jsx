import { useEffect, useRef, useState } from 'react'
import * as THREE from 'three'
import { loadGoogleMaps } from '../utils/loadGoogleMaps'
import './TrackingTab.css'

// Note: Google Maps API should be loaded in index.html
// API keys should be set via environment variables

const ONEGEO_API_KEY = import.meta.env.VITE_ONEGEO_API_KEY
const GOOGLE_MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY

export default function TrackingTab() {
  const canvasRef = useRef(null)
  const containerRef = useRef(null)
  const [address, setAddress] = useState('')
  const [dataSource, setDataSource] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showStreetView, setShowStreetView] = useState(false)
  const [currentLocation, setCurrentLocation] = useState(null)
  const [currentAddress, setCurrentAddress] = useState(null)
  
  const sceneRef = useRef(null)
  const cameraRef = useRef(null)
  const rendererRef = useRef(null)
  const buildingGroupRef = useRef(null)
  const personnelObjectsRef = useRef([])
  const personnelPerFloorRef = useRef([])
  const floorBoundsRef = useRef([])
  const animationIdRef = useRef(null)
  
  const isDraggingRef = useRef(false)
  const previousMousePositionRef = useRef({ x: 0, y: 0 })
  const rotationYRef = useRef(0)
  const rotationXRef = useRef(0.3)
  const buildingCenterHeightRef = useRef(8)
  const cameraRadiusRef = useRef(25)
  const minCameraRadiusRef = useRef(8)
  const maxCameraRadiusRef = useRef(100)

  useEffect(() => {
    initThreeJS()
    return () => {
      if (animationIdRef.current) {
        cancelAnimationFrame(animationIdRef.current)
      }
      if (rendererRef.current) {
        rendererRef.current.dispose()
      }
    }
  }, [])

  function initThreeJS() {
    if (!canvasRef.current) return
    
    const canvas = canvasRef.current
    const width = canvas.clientWidth || 800
    const height = canvas.clientHeight || 600

    const scene = new THREE.Scene()
    scene.background = new THREE.Color(0x001122)
    scene.fog = new THREE.Fog(0x001122, 100, 1000)

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000)
    camera.position.set(15, 12, 20)
    camera.lookAt(0, 5, 0)

    const renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true })
    renderer.setSize(width, height)
    renderer.setPixelRatio(window.devicePixelRatio)
    renderer.shadowMap.enabled = true

    // Lighting
    const ambientLight = new THREE.AmbientLight(0x0099FF, 0.4)
    scene.add(ambientLight)

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8)
    directionalLight.position.set(20, 30, 10)
    directionalLight.castShadow = true
    scene.add(directionalLight)

    const pointLight = new THREE.PointLight(0x0099FF, 0.6, 100)
    pointLight.position.set(0, 15, 0)
    scene.add(pointLight)

    // Ground
    const groundGeometry = new THREE.PlaneGeometry(50, 50)
    const groundMaterial = new THREE.MeshStandardMaterial({
      color: 0x112233,
      emissive: 0x000011
    })
    const ground = new THREE.Mesh(groundGeometry, groundMaterial)
    ground.rotation.x = -Math.PI / 2
    ground.position.y = -0.5
    ground.receiveShadow = true
    scene.add(ground)

    const buildingGroup = new THREE.Group()
    scene.add(buildingGroup)

    // Mouse controls
    canvas.addEventListener('mousedown', (e) => {
      isDraggingRef.current = true
      previousMousePositionRef.current = { x: e.clientX, y: e.clientY }
    })

    canvas.addEventListener('mousemove', (e) => {
      if (isDraggingRef.current) {
        const deltaX = e.clientX - previousMousePositionRef.current.x
        const deltaY = e.clientY - previousMousePositionRef.current.y
        
        rotationYRef.current += deltaX * 0.01
        rotationXRef.current = Math.max(0, Math.min(Math.PI / 2, rotationXRef.current - deltaY * 0.01))
        
        previousMousePositionRef.current = { x: e.clientX, y: e.clientY }
      }
    })

    canvas.addEventListener('mouseup', () => {
      isDraggingRef.current = false
    })

    canvas.addEventListener('mouseleave', () => {
      isDraggingRef.current = false
    })

    // Zoom controls
    canvas.addEventListener('wheel', (e) => {
      e.preventDefault()
      const zoomSpeed = 0.1
      const zoomDelta = e.deltaY * zoomSpeed
      cameraRadiusRef.current += zoomDelta
      cameraRadiusRef.current = Math.max(minCameraRadiusRef.current, Math.min(maxCameraRadiusRef.current, cameraRadiusRef.current))
    }, { passive: false })

    // Handle resize
    window.addEventListener('resize', () => {
      const width = canvas.clientWidth
      const height = canvas.clientHeight
      camera.aspect = width / height
      camera.updateProjectionMatrix()
      renderer.setSize(width, height)
    })

    sceneRef.current = scene
    cameraRef.current = camera
    rendererRef.current = renderer
    buildingGroupRef.current = buildingGroup

    // Start animation loop
    animate()
  }

  function animate() {
    if (!rendererRef.current || !sceneRef.current || !cameraRef.current) return
    
    animationIdRef.current = requestAnimationFrame(animate)
    
    animatePersonnel()
    
    // Apply camera rotation
    const camera = cameraRef.current
    const radius = cameraRadiusRef.current
    const rotY = rotationYRef.current
    const rotX = rotationXRef.current
    const centerHeight = buildingCenterHeightRef.current
    
    camera.position.x = Math.sin(rotY) * Math.cos(rotX) * radius
    camera.position.y = Math.sin(rotX) * radius + centerHeight
    camera.position.z = Math.cos(rotY) * Math.cos(rotX) * radius
    camera.lookAt(0, centerHeight, 0)
    
    rendererRef.current.render(sceneRef.current, cameraRef.current)
  }

  function animatePersonnel() {
    const time = Date.now() * 0.001
    const personnelObjects = personnelObjectsRef.current
    const floorBounds = floorBoundsRef.current
    
    personnelObjects.forEach((personnel, index) => {
      const floor = floorBounds[personnel.floorIndex] || { minX: -5, maxX: 5, minZ: -4, maxZ: 4, y: 0.1 }

      const now = Date.now()
      if (now - personnel.waypointReachedTime > personnel.changeWaypointInterval) {
        personnel.currentWaypoint = (personnel.currentWaypoint + 1) % personnel.waypoints.length
        const wp = personnel.waypoints[personnel.currentWaypoint]
        personnel.targetX = wp.x
        personnel.targetZ = wp.z
        personnel.waypointReachedTime = now
        personnel.changeWaypointInterval = 3000 + Math.random() * 4000
      }

      const dx = personnel.targetX - personnel.mesh.position.x
      const dz = personnel.targetZ - personnel.mesh.position.z
      const distance = Math.sqrt(dx * dx + dz * dz)

      if (distance > 0.1) {
        const speed = personnel.speed * (0.8 + Math.random() * 0.4)
        personnel.mesh.position.x += dx * speed
        personnel.mesh.position.z += dz * speed
        personnel.mesh.rotation.y = Math.atan2(dx, dz) + (Math.random() - 0.5) * 0.1
      } else {
        personnel.currentWaypoint = Math.floor(Math.random() * personnel.waypoints.length)
        const wp = personnel.waypoints[personnel.currentWaypoint]
        personnel.targetX = wp.x
        personnel.targetZ = wp.z
      }

      personnel.mesh.position.x = Math.max(floor.minX - 0.2, Math.min(floor.maxX + 0.2, personnel.mesh.position.x))
      personnel.mesh.position.z = Math.max(floor.minZ - 0.2, Math.min(floor.maxZ + 0.2, personnel.mesh.position.z))

      personnel.mesh.position.y = floor.y + Math.sin(time * 3 + index) * 0.04
      personnel.walkCycle = (personnel.walkCycle || 0) + 0.2 + Math.random() * 0.1
    })
  }

  function createPersonnelFigurine() {
    const personnel = new THREE.Group()
    const material = new THREE.MeshStandardMaterial({
      color: 0xFFD700,
      emissive: 0xFFA500,
      emissiveIntensity: 0.3,
      metalness: 0.5,
      roughness: 0.5
    })

    // Head
    const head = new THREE.Mesh(new THREE.SphereGeometry(0.15, 12, 12), material)
    head.position.set(0, 0.65, 0)
    personnel.add(head)

    // Body
    const body = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 0.4, 12), material)
    body.position.set(0, 0.25, 0)
    personnel.add(body)

    // Arms
    const armGeo = new THREE.CylinderGeometry(0.05, 0.05, 0.3, 8)
    const leftArm = new THREE.Mesh(armGeo, material)
    leftArm.position.set(-0.2, 0.3, 0)
    leftArm.rotation.z = 0.3
    personnel.add(leftArm)

    const rightArm = new THREE.Mesh(armGeo, material)
    rightArm.position.set(0.2, 0.3, 0)
    rightArm.rotation.z = -0.3
    personnel.add(rightArm)

    // Legs
    const legGeo = new THREE.CylinderGeometry(0.06, 0.06, 0.35, 8)
    const leftLeg = new THREE.Mesh(legGeo, material)
    leftLeg.position.set(-0.08, -0.15, 0)
    personnel.add(leftLeg)

    const rightLeg = new THREE.Mesh(legGeo, material)
    rightLeg.position.set(0.08, -0.15, 0)
    personnel.add(rightLeg)

    // Helmet
    const helmet = new THREE.Mesh(
      new THREE.SphereGeometry(0.18, 12, 12),
      new THREE.MeshStandardMaterial({
        color: 0xFF6600,
        emissive: 0xFF3300,
        emissiveIntensity: 0.8,
        transparent: true,
        opacity: 0.6
      })
    )
    helmet.position.set(0, 0.65, 0)
    personnel.add(helmet)

    personnel.scale.set(0.8, 0.8, 0.8)
    personnel.traverse((child) => {
      if (child.isMesh) child.castShadow = true
    })

    return personnel
  }

  async function loadBuilding() {
    if (!address.trim()) return
    
    setIsLoading(true)
    try {
      // Load Google Maps API if not already loaded
      await loadGoogleMaps()
      
      if (!window.google || !window.google.maps) {
        throw new Error('Google Maps API not loaded. Please set VITE_GOOGLE_MAPS_API_KEY environment variable.')
      }

      const { Geocoder } = await window.google.maps.importLibrary("geocoding")
      const geocoder = new Geocoder()

      geocoder.geocode({ address: address }, async (results, status) => {
        if (status !== 'OK' || !results[0]) {
          alert('Address not found')
          setIsLoading(false)
          return
        }

        const location = results[0].geometry.location
        const lat = location.lat()
        const lng = location.lng()
        
        setCurrentAddress(address)
        setCurrentLocation({ lat, lng })

        // Try ONEGEO first
        try {
          const onegeoData = await getONEGEOBuildingData(lat, lng, address)
          if (onegeoData) {
            setDataSource('ONEGEO')
            createBuildingFromData(onegeoData)
            setIsLoading(false)
            return
          }
        } catch (error) {
          console.log('ONEGEO failed:', error)
        }

        // Fallback to default building
        setDataSource('Default')
        createBuildingFromData({
          floors: 3,
          height: 9.6,
          width: 12,
          depth: 8
        })
        setIsLoading(false)
      })
    } catch (error) {
      console.error('Error loading building:', error)
      alert('Error loading building: ' + error.message)
      setIsLoading(false)
    }
  }

  async function getONEGEOBuildingData(lat, lng, address) {
    if (!ONEGEO_API_KEY) {
      console.warn('ONEGEO API key not configured. Set VITE_ONEGEO_API_KEY environment variable.')
      return null
    }
    
    try {
      const bboxSize = 0.002
      const west = lng - bboxSize
      const south = lat - bboxSize
      const east = lng + bboxSize
      const north = lat + bboxSize
      const bbox = `${west},${south},${east},${north}`
      
      let apiUrl = `https://data.onegeo.co/api/?token=${ONEGEO_API_KEY}&bbox=${bbox}`
      let response = await fetch(apiUrl)
      
      if (!response.ok) {
        if (response.status === 401) {
          console.warn('ONEGEO API key invalid or expired')
          return null
        }
        return null
      }
      
      const data = await response.json()
      
      if (!data || !data.features || data.features.length === 0) {
        return null
      }
      
      // Find closest building
      let closestBuilding = null
      let minDist = Infinity
      
      data.features.forEach(feature => {
        if (feature.geometry && feature.geometry.type === 'Polygon') {
          const coords = feature.geometry.coordinates[0]
          let sumLon = 0, sumLat = 0
          coords.forEach(coord => {
            sumLon += coord[0]
            sumLat += coord[1]
          })
          const centerLon = sumLon / coords.length
          const centerLat = sumLat / coords.length
          
          const dLat = (centerLat - lat) * 111000
          const dLon = (centerLon - lng) * 111000 * Math.cos(lat * Math.PI / 180)
          const dist = Math.sqrt(dLat * dLat + dLon * dLon)
          
          if (dist < minDist && dist < 200) {
            minDist = dist
            closestBuilding = feature
          }
        }
      })
      
      if (!closestBuilding) {
        return null
      }
      
      const properties = closestBuilding.properties || {}
      const geometry = closestBuilding.geometry
      
      let floors = null
      if (properties['building:levels'] !== undefined) {
        floors = parseInt(properties['building:levels'])
      } else if (properties.levels !== undefined) {
        floors = parseInt(properties.levels)
      }
      
      let height = null
      if (properties.height !== undefined && properties.height > 0) {
        height = parseFloat(properties.height)
      }
      
      if (floors && !height) {
        height = floors * 3.2
      } else if (height && !floors) {
        floors = Math.max(1, Math.floor(height / 3.2))
      }
      
      if (geometry.type === 'Polygon' && geometry.coordinates[0]) {
        const coords = geometry.coordinates[0]
        const lons = coords.map(c => c[0])
        const lats = coords.map(c => c[1])
        const lonDiff = Math.max(...lons) - Math.min(...lons)
        const latDiff = Math.max(...lats) - Math.min(...lats)
        
        const width = lonDiff * 111000 * Math.cos(lat * Math.PI / 180)
        const depth = latDiff * 111000
        
        const finalFloors = Math.max(1, floors || 3)
        const finalHeight = height || (finalFloors * 3.2)
        
        return {
          floors: finalFloors,
          height: finalHeight,
          width: Math.max(5, Math.min(30, width)),
          depth: Math.max(5, Math.min(30, depth))
        }
      }
      
      return null
    } catch (error) {
      console.error('ONEGEO error:', error)
      return null
    }
  }

  function createBuildingFromData(buildingData) {
    if (!buildingGroupRef.current || !sceneRef.current) return
    
    // Clear existing building
    while (buildingGroupRef.current.children.length > 0) {
      buildingGroupRef.current.remove(buildingGroupRef.current.children[0])
    }
    personnelObjectsRef.current = []
    personnelPerFloorRef.current = []
    floorBoundsRef.current = []

    const floorHeight = 3
    const numFloors = buildingData.floors || Math.max(1, Math.floor((buildingData.height || 15) / floorHeight))
    const floorWidth = buildingData.width || 12
    const floorDepth = buildingData.depth || 8

    const floors = []

    for (let i = 0; i < numFloors; i++) {
      const yPos = i * floorHeight

      // Floor
      const floorGeometry = new THREE.BoxGeometry(floorWidth, 0.2, floorDepth)
      const floorMaterial = new THREE.MeshStandardMaterial({
        color: 0x336699,
        emissive: 0x001133,
        metalness: 0.3,
        roughness: 0.7
      })
      const floor = new THREE.Mesh(floorGeometry, floorMaterial)
      floor.position.set(0, yPos, 0)
      floor.receiveShadow = true
      buildingGroupRef.current.add(floor)

      // Walls
      const wallMaterial = new THREE.MeshStandardMaterial({
        color: 0x4477AA,
        emissive: 0x001122,
        metalness: 0.2,
        roughness: 0.8,
        transparent: true,
        opacity: 0.7
      })

      const frontWall = new THREE.Mesh(
        new THREE.BoxGeometry(floorWidth, floorHeight * 0.8, 0.1),
        wallMaterial
      )
      frontWall.position.set(0, yPos + floorHeight * 0.4, floorDepth / 2)
      frontWall.castShadow = true
      buildingGroupRef.current.add(frontWall)

      const leftWall = new THREE.Mesh(
        new THREE.BoxGeometry(0.1, floorHeight * 0.8, floorDepth),
        wallMaterial
      )
      leftWall.position.set(-floorWidth / 2, yPos + floorHeight * 0.4, 0)
      leftWall.castShadow = true
      buildingGroupRef.current.add(leftWall)

      const rightWall = new THREE.Mesh(
        new THREE.BoxGeometry(0.1, floorHeight * 0.8, floorDepth),
        wallMaterial
      )
      rightWall.position.set(floorWidth / 2, yPos + floorHeight * 0.4, 0)
      rightWall.castShadow = true
      buildingGroupRef.current.add(rightWall)

      const floorBoundsData = {
        y: yPos + 0.1,
        minX: -floorWidth / 2 + 0.5,
        maxX: floorWidth / 2 - 0.5,
        minZ: -floorDepth / 2 + 0.5,
        maxZ: floorDepth / 2 - 0.5
      }
      floors.push(floorBoundsData)
      floorBoundsRef.current.push(floorBoundsData)

      // Create personnel
      const numPersonnel = Math.max(1, Math.min(3, Math.floor(floorWidth * floorDepth / 20)))
      personnelPerFloorRef.current.push(numPersonnel)

      for (let j = 0; j < numPersonnel; j++) {
        const personnel = createPersonnelFigurine()
        const startX = floors[i].minX + Math.random() * (floors[i].maxX - floors[i].minX)
        const startZ = floors[i].minZ + Math.random() * (floors[i].maxZ - floors[i].minZ)
        personnel.position.set(startX, floors[i].y, startZ)

        const waypoints = []
        for (let w = 0; w < 5; w++) {
          waypoints.push({
            x: floors[i].minX + Math.random() * (floors[i].maxX - floors[i].minX),
            z: floors[i].minZ + Math.random() * (floors[i].maxZ - floors[i].minZ)
          })
        }

        personnelObjectsRef.current.push({
          mesh: personnel,
          floorIndex: i,
          targetX: startX,
          targetZ: startZ,
          currentWaypoint: 0,
          waypoints: waypoints,
          speed: 0.015 + Math.random() * 0.02,
          walkCycle: 0,
          waypointReachedTime: Date.now(),
          changeWaypointInterval: 3000 + Math.random() * 4000
        })

        buildingGroupRef.current.add(personnel)
      }
    }

    // Roof
    const roofGeometry = new THREE.BoxGeometry(floorWidth + 0.5, 0.3, floorDepth + 0.5)
    const roofMaterial = new THREE.MeshStandardMaterial({
      color: 0x225588,
      emissive: 0x001122,
      metalness: 0.5,
      roughness: 0.5
    })
    const roof = new THREE.Mesh(roofGeometry, roofMaterial)
    roof.position.set(0, numFloors * floorHeight + 0.15, 0)
    roof.castShadow = true
    buildingGroupRef.current.add(roof)

    // Adjust camera
    buildingCenterHeightRef.current = (numFloors * floorHeight) * 0.4
    const diagonal = Math.sqrt(floorWidth * floorWidth + floorDepth * floorDepth)
    const maxDimension = Math.max(numFloors * floorHeight, diagonal)
    const boundingRadius = maxDimension * 0.8
    const fov = cameraRef.current.fov * (Math.PI / 180)
    const distance = boundingRadius / Math.sin(fov / 2)
    cameraRadiusRef.current = Math.max(distance * 0.9, 8)
    minCameraRadiusRef.current = Math.max(5, cameraRadiusRef.current * 0.3)
    maxCameraRadiusRef.current = Math.max(50, cameraRadiusRef.current * 3)
  }

  function zoomIn() {
    const zoomStep = 5
    cameraRadiusRef.current = Math.max(minCameraRadiusRef.current, cameraRadiusRef.current - zoomStep)
  }

  function zoomOut() {
    const zoomStep = 5
    cameraRadiusRef.current = Math.min(maxCameraRadiusRef.current, cameraRadiusRef.current + zoomStep)
  }

  const streetViewPanoramaRef = useRef(null)

  async function loadStreetView() {
    if (!currentLocation || !currentAddress) return
    
    try {
      // Load Google Maps API if not already loaded
      await loadGoogleMaps()
      
      if (!window.google || !window.google.maps) {
        console.error('Google Maps API not loaded. Please set VITE_GOOGLE_MAPS_API_KEY environment variable.')
        alert('Google Maps API not loaded. Please set VITE_GOOGLE_MAPS_API_KEY in your .env file.')
        return
      }
      
      setShowStreetView(true)
      
      // Wait for DOM to update, then initialize Street View
      setTimeout(async () => {
        const streetViewContainer = document.getElementById('street-view')
        if (!streetViewContainer) {
          console.error('Street View container not found')
          return
        }
        
        try {
          // Import Street View library
          const { StreetViewPanorama } = await window.google.maps.importLibrary("streetView")
          
          const location = new window.google.maps.LatLng(currentLocation.lat, currentLocation.lng)
          
          // Check if Street View is available
          const streetViewService = new window.google.maps.StreetViewService()
          streetViewService.getPanorama({ location: location, radius: 50 }, (data, status) => {
            if (status === 'OK') {
              // Initialize panorama
              if (!streetViewPanoramaRef.current) {
                streetViewPanoramaRef.current = new StreetViewPanorama(streetViewContainer, {
                  position: location,
                  pov: { heading: 0, pitch: 0 },
                  zoom: 1
                })
              } else {
                streetViewPanoramaRef.current.setPosition(location)
              }
            } else {
              // Street View not available for this location
              streetViewContainer.innerHTML = `
                <div style="display: flex; align-items: center; justify-content: center; height: 100%; color: rgba(255, 255, 255, 0.7); text-align: center; padding: 20px;">
                  <div>
                    <p style="margin: 0; font-size: 16px;">Street View not available for this location</p>
                    <p style="margin: 10px 0 0 0; font-size: 12px; opacity: 0.6;">Address: ${currentAddress}</p>
                  </div>
                </div>
              `
            }
          })
        } catch (error) {
          console.error('Error initializing Street View:', error)
          const streetViewContainer = document.getElementById('street-view')
          if (streetViewContainer) {
            streetViewContainer.innerHTML = `
              <div style="display: flex; align-items: center; justify-content: center; height: 100%; color: rgba(255, 255, 255, 0.7); text-align: center; padding: 20px;">
                <div>
                  <p style="margin: 0; font-size: 16px;">Error loading Street View</p>
                  <p style="margin: 10px 0 0 0; font-size: 12px; opacity: 0.6;">${error.message}</p>
                </div>
              </div>
            `
          }
        }
      }, 100)
    } catch (error) {
      console.error('Error loading Street View:', error)
      alert(`Failed to load Street View: ${error.message}\n\nPlease check:\n1. VITE_GOOGLE_MAPS_API_KEY is set in your .env file\n2. The API key has Street View Static API enabled\n3. Your network connection`)
    }
  }

  return (
    <div className="tracking-tab" ref={containerRef}>
      <div className="building-panel">
        <div className="address-input-container">
          <input
            type="text"
            className="address-input"
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && loadBuilding()}
            placeholder="Enter building address"
          />
          <button
            className="address-button"
            onClick={loadBuilding}
            disabled={isLoading}
          >
            {isLoading ? 'Loading...' : 'Load Building'}
          </button>
        </div>
        
        {dataSource && (
          <div className="data-source-indicator">
            Data Source: <span>{dataSource}</span>
          </div>
        )}
        
        {currentLocation && (
          <button
            className="street-view-toggle"
            onClick={loadStreetView}
            title="View Street View"
          >
            📍
          </button>
        )}
        
        <div className="building-container">
          <div className="building-title">Tracking</div>
          <canvas ref={canvasRef} id="buildingCanvas"></canvas>
          
          <div className="zoom-controls">
            <button className="zoom-button" onClick={zoomIn} title="Zoom In">+</button>
            <button className="zoom-button" onClick={zoomOut} title="Zoom Out">−</button>
          </div>
        </div>
      </div>
      
      {showStreetView && currentLocation && (
        <div className="street-view-expanded active">
          <div className="street-view-header">
            <h3>Street View</h3>
            <button className="street-view-close" onClick={() => setShowStreetView(false)}>×</button>
          </div>
          <div className="street-view-iframe-container">
            <div id="street-view" style={{ width: '100%', height: '100%' }}></div>
          </div>
        </div>
      )}
    </div>
  )
}
