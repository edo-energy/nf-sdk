import { useState, useCallback } from 'react'
import { ConfigForm } from './components/ConfigForm'
import { HierarchyPreview } from './components/HierarchyPreview'
import type { BuildingConfig } from './types'

const DEFAULT_CONFIG: BuildingConfig = {
  building: { name: 'New Test Building', location: 'Chicago, IL' },
  weather: { mode: 'fixed', fixed: { outdoor_air_temp: 85, humidity: 55, wind_speed: 8 } },
  time: { acceleration: 1 },
  zones: [],
  equipment: { ahus: [], vavs: [], chillers: [], boilers: [], fcus: [], lighting: [], sensors: [] },
}

function App() {
  const [config, setConfig] = useState<BuildingConfig>(DEFAULT_CONFIG)
  const [status, setStatus] = useState<{ msg: string; error?: boolean } | null>(null)

  const handleDeploy = useCallback(async () => {
    const simApi = import.meta.env.VITE_SIM_API || 'http://localhost:8100'
    try {
      setStatus({ msg: 'Deploying configuration...' })
      const resp = await fetch(`${simApi}/api/config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      })
      if (resp.ok) {
        setStatus({ msg: 'Configuration deployed successfully.' })
      } else {
        setStatus({ msg: `Deploy failed: ${resp.statusText}`, error: true })
      }
    } catch (e) {
      setStatus({ msg: `Deploy failed: ${e}`, error: true })
    }
  }, [config])

  return (
    <div className="app">
      <h1>NF Test Harness — Building Configuration</h1>
      {status && (
        <div className={`status-bar ${status.error ? 'error' : ''}`}>
          {status.msg}
        </div>
      )}
      <div className="panels">
        <ConfigForm config={config} onChange={setConfig} />
        <div>
          <HierarchyPreview config={config} />
          <div className="actions">
            <button className="primary" onClick={handleDeploy}>Deploy Configuration</button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
