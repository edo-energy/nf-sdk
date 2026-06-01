import { useState, useEffect, useRef, useCallback } from 'react'
import { ZoneMonitor } from './components/ZoneMonitor'
import { EquipmentMonitor } from './components/EquipmentMonitor'
import { FaultInjection } from './components/FaultInjection'

interface SimState {
  sim_time: number
  acceleration: number
  weather: { outdoor_air_temp: number; humidity: number; wind_speed: number }
  zones: Record<string, { temp: number; setpoint_cooling: number; setpoint_heating: number; hvac_load_btu: number; occupancy: number }>
  ahus: Record<string, Record<string, number | boolean>>
  vavs: Record<string, Record<string, number | boolean>>
  chillers: Record<string, Record<string, number | boolean>>
  boilers: Record<string, Record<string, number | boolean>>
  fcus: Record<string, Record<string, number | boolean>>
  lighting: Record<string, Record<string, number | boolean>>
  sensors: Record<string, { device_id: number; type: string; value: number }>
  faults: Record<string, { target_type: string; target_name: string; fault_type: string; active: boolean }>
}

interface TimeInfo {
  acceleration: number
  paused: boolean
  sim_time: number
  wall_time: number
  offset_seconds: number
}

const SIM_API = import.meta.env.VITE_SIM_API || 'http://localhost:8100'
const TIME_API = import.meta.env.VITE_TIME_API || 'http://localhost:8200'

function App() {
  const [state, setState] = useState<SimState | null>(null)
  const [timeInfo, setTimeInfo] = useState<TimeInfo | null>(null)
  const wsRef = useRef<WebSocket | null>(null)

  // Connect to WebSocket for real-time updates
  useEffect(() => {
    const ws = new WebSocket(`${SIM_API.replace('http', 'ws')}/ws`)
    ws.onmessage = (ev) => {
      try {
        setState(JSON.parse(ev.data))
      } catch { /* ignore parse errors */ }
    }
    ws.onclose = () => {
      // Reconnect after delay
      setTimeout(() => {
        wsRef.current = null
      }, 2000)
    }
    wsRef.current = ws
    return () => ws.close()
  }, [])

  // Poll time controller
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const resp = await fetch(`${TIME_API}/api/time`)
        if (resp.ok) setTimeInfo(await resp.json())
      } catch { /* ignore */ }
    }, 1000)
    return () => clearInterval(interval)
  }, [])

  // Fallback: poll state if WebSocket not connected
  useEffect(() => {
    const interval = setInterval(async () => {
      if (wsRef.current?.readyState === WebSocket.OPEN) return
      try {
        const resp = await fetch(`${SIM_API}/api/state`)
        if (resp.ok) setState(await resp.json())
      } catch { /* ignore */ }
    }, 2000)
    return () => clearInterval(interval)
  }, [])

  const setAcceleration = useCallback(async (accel: number) => {
    await fetch(`${TIME_API}/api/time`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ acceleration: accel }),
    })
  }, [])

  const togglePause = useCallback(async () => {
    await fetch(`${TIME_API}/api/time`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ paused: !timeInfo?.paused }),
    })
  }, [timeInfo])

  const formatTime = (ts: number) => new Date(ts * 1000).toLocaleString()

  return (
    <div className="app">
      <div className="header">
        <h1>NF Test Harness — Simulation Dashboard</h1>
        <div className="clock">
          <div className="clock-item">
            <div className="label">Sim Time</div>
            <div className={`value ${timeInfo?.paused ? 'paused' : ''}`}>
              {state ? formatTime(state.sim_time) : '--'}
            </div>
          </div>
          <div className="clock-item">
            <div className="label">Acceleration</div>
            <div className="value">{timeInfo?.acceleration || 1}x</div>
          </div>
          <div className="clock-item">
            <div className="label">OAT</div>
            <div className="value">{state?.weather.outdoor_air_temp.toFixed(1) || '--'}°F</div>
          </div>
          <div className="clock-item">
            <button className="inject" onClick={togglePause} style={{ padding: '0.4rem 0.8rem' }}>
              {timeInfo?.paused ? '▶ Resume' : '⏸ Pause'}
            </button>
          </div>
        </div>
      </div>

      {state && (
        <>
          <h2>Thermal Zones</h2>
          <div className="grid">
            <ZoneMonitor zones={state.zones} />
          </div>

          <h2 style={{ marginTop: '1rem' }}>Equipment</h2>
          <div className="grid">
            <EquipmentMonitor
              ahus={state.ahus}
              chillers={state.chillers}
              boilers={state.boilers}
              sensors={state.sensors}
            />
          </div>

          <FaultInjection
            faults={state.faults}
            simApi={SIM_API}
          />
        </>
      )}

      {!state && (
        <div style={{ color: '#888', textAlign: 'center', marginTop: '4rem' }}>
          Connecting to simulation engine...
        </div>
      )}
    </div>
  )
}

export default App
