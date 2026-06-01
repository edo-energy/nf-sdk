import type { BuildingConfig } from '../types'

interface Props {
  config: BuildingConfig
  onChange: (c: BuildingConfig) => void
}

export function ConfigForm({ config, onChange }: Props) {
  const update = (path: string, value: unknown) => {
    const next = structuredClone(config)
    const keys = path.split('.')
    let obj: Record<string, unknown> = next as unknown as Record<string, unknown>
    for (let i = 0; i < keys.length - 1; i++) {
      obj = obj[keys[i]] as Record<string, unknown>
    }
    obj[keys[keys.length - 1]] = value
    onChange(next as BuildingConfig)
  }

  const addZone = () => {
    const next = structuredClone(config)
    const idx = next.zones.length + 1
    next.zones.push({
      name: `Zone ${idx}`,
      area_sqft: 2000,
      volume_cuft: 20000,
      r_value: 15,
      initial_temp: 72,
      setpoint_cooling: 74,
      setpoint_heating: 70,
      internal_load_btu: 5000,
      occupancy_schedule: 'business_hours',
    })
    onChange(next)
  }

  const removeZone = (idx: number) => {
    const next = structuredClone(config)
    next.zones.splice(idx, 1)
    onChange(next)
  }

  const addEquipment = (type: string) => {
    const next = structuredClone(config)
    const equip = next.equipment as unknown as Record<string, unknown[]>
    const list = equip[type] as unknown[]
    const maxId = list.reduce((m: number, e: unknown) => Math.max(m, (e as { device_id: number }).device_id || 0), 0)

    const templates: Record<string, unknown> = {
      ahus: { name: `AHU-${list.length + 1}`, device_id: maxId + 1 || 1001, supply_fan_hp: 15, max_airflow_cfm: 10000, cooling_capacity_tons: 25, heating_capacity_mbh: 200, serves_zones: [], economizer: true },
      vavs: { name: `VAV-${list.length + 1}`, device_id: maxId + 1 || 2001, zone: '', max_airflow_cfm: 1200, min_airflow_cfm: 250, has_reheat: true, reheat_capacity_mbh: 15, parent_ahu: '' },
      chillers: { name: `Chiller-${list.length + 1}`, device_id: maxId + 1 || 3001, capacity_tons: 50, min_plr: 0.2, design_lwt: 44, design_ewt: 54, condenser_type: 'air' },
      boilers: { name: `Boiler-${list.length + 1}`, device_id: maxId + 1 || 4001, capacity_mbh: 500, design_lwt: 180, efficiency: 0.92, fuel_type: 'gas' },
      fcus: { name: `FCU-${list.length + 1}`, device_id: maxId + 1 || 5001, zone: '', capacity_cooling_mbh: 24, capacity_heating_mbh: 18, fan_speeds: 3 },
      lighting: { name: `LTG-${list.length + 1}`, device_id: maxId + 1 || 6001, zone: '', max_watts: 5000, dimmable: true, occupancy_sensor: true },
      sensors: { name: `Sensor-${list.length + 1}`, device_id: maxId + 1 || 7001, type: 'oat', location: '' },
    }

    list.push(templates[type])
    onChange(next)
  }

  return (
    <div className="config-form">
      {/* Building Info */}
      <div className="section">
        <h2>Building</h2>
        <div className="form-row">
          <label>Name</label>
          <input value={config.building.name} onChange={e => update('building.name', e.target.value)} />
        </div>
        <div className="form-row">
          <label>Location</label>
          <input value={config.building.location} onChange={e => update('building.location', e.target.value)} />
        </div>
      </div>

      {/* Weather */}
      <div className="section">
        <h2>Weather</h2>
        <div className="form-row">
          <label>OAT (°F)</label>
          <input type="number" value={config.weather.fixed.outdoor_air_temp} onChange={e => update('weather.fixed.outdoor_air_temp', +e.target.value)} />
          <label>Humidity (%)</label>
          <input type="number" value={config.weather.fixed.humidity} onChange={e => update('weather.fixed.humidity', +e.target.value)} />
          <label>Wind (mph)</label>
          <input type="number" value={config.weather.fixed.wind_speed} onChange={e => update('weather.fixed.wind_speed', +e.target.value)} />
        </div>
      </div>

      {/* Time */}
      <div className="section">
        <h2>Time Acceleration</h2>
        <div className="form-row">
          <label>Factor (1-20x)</label>
          <input type="range" min="1" max="20" value={config.time.acceleration} onChange={e => update('time.acceleration', +e.target.value)} style={{ width: 200 }} />
          <span>{config.time.acceleration}x</span>
        </div>
      </div>

      {/* Zones */}
      <div className="section">
        <h2>Zones <button className="secondary" onClick={addZone}>+ Add Zone</button></h2>
        {config.zones.map((z, i) => (
          <div key={i} style={{ borderBottom: '1px solid #e5e7eb', paddingBottom: '0.5rem', marginBottom: '0.5rem' }}>
            <div className="form-row">
              <input value={z.name} onChange={e => { const next = structuredClone(config); next.zones[i].name = e.target.value; onChange(next) }} style={{ width: 200 }} />
              <label>Area</label>
              <input type="number" value={z.area_sqft} onChange={e => { const next = structuredClone(config); next.zones[i].area_sqft = +e.target.value; onChange(next) }} />
              <label>Clg SP</label>
              <input type="number" value={z.setpoint_cooling} onChange={e => { const next = structuredClone(config); next.zones[i].setpoint_cooling = +e.target.value; onChange(next) }} />
              <label>Htg SP</label>
              <input type="number" value={z.setpoint_heating} onChange={e => { const next = structuredClone(config); next.zones[i].setpoint_heating = +e.target.value; onChange(next) }} />
              <button className="danger" onClick={() => removeZone(i)}>×</button>
            </div>
          </div>
        ))}
      </div>

      {/* Equipment */}
      {(['ahus', 'vavs', 'chillers', 'boilers', 'fcus', 'lighting', 'sensors'] as const).map(type => (
        <div className="section" key={type}>
          <h2>{type.toUpperCase()} ({(config.equipment[type] as unknown[]).length}) <button className="secondary" onClick={() => addEquipment(type)}>+ Add</button></h2>
          {(config.equipment[type] as Array<{ name: string; device_id: number }>).map((item, i) => (
            <div key={i} className="form-row">
              <input value={item.name} onChange={e => { const next = structuredClone(config); (next.equipment[type] as Array<{ name: string }>)[i].name = e.target.value; onChange(next) }} style={{ width: 150 }} />
              <label>ID</label>
              <input type="number" value={item.device_id} onChange={e => { const next = structuredClone(config); (next.equipment[type] as Array<{ device_id: number }>)[i].device_id = +e.target.value; onChange(next) }} />
              <button className="danger" onClick={() => { const next = structuredClone(config); (next.equipment[type] as unknown[]).splice(i, 1); onChange(next) }}>×</button>
            </div>
          ))}
        </div>
      ))}
    </div>
  )
}
