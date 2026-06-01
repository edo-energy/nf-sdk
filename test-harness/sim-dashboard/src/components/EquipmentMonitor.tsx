interface Props {
  ahus: Record<string, Record<string, number | boolean>>
  chillers: Record<string, Record<string, number | boolean>>
  boilers: Record<string, Record<string, number | boolean>>
  sensors: Record<string, { device_id: number; type: string; value: number }>
}

export function EquipmentMonitor({ ahus, chillers, boilers, sensors }: Props) {
  return (
    <>
      {/* AHUs */}
      {Object.entries(ahus).map(([name, a]) => (
        <div className="card" key={name}>
          <h3>🌀 {name}</h3>
          <div className="metric"><span className="name">Supply Air Temp</span><span className="val cool">{Number(a.supply_air_temp).toFixed(1)}°F</span></div>
          <div className="metric"><span className="name">Return Air Temp</span><span className="val">{Number(a.return_air_temp).toFixed(1)}°F</span></div>
          <div className="metric"><span className="name">Mixed Air Temp</span><span className="val">{Number(a.mixed_air_temp).toFixed(1)}°F</span></div>
          <div className="metric"><span className="name">Fan Speed</span><span className="val">{Number(a.supply_fan_speed_pct).toFixed(0)}%</span></div>
          <div className="metric"><span className="name">Cooling Valve</span><span className="val cool">{Number(a.cooling_valve_pct).toFixed(0)}%</span></div>
          <div className="metric"><span className="name">Heating Valve</span><span className="val warm">{Number(a.heating_valve_pct).toFixed(0)}%</span></div>
          <div className="metric"><span className="name">OA Damper</span><span className="val">{Number(a.oa_damper_pct).toFixed(0)}%</span></div>
          <div className="metric"><span className="name">Duct Static</span><span className="val">{Number(a.duct_static_pressure).toFixed(2)} in.wc</span></div>
        </div>
      ))}

      {/* Chillers */}
      {Object.entries(chillers).map(([name, c]) => (
        <div className="card" key={name}>
          <h3>❄️ {name}</h3>
          <div className="metric"><span className="name">CHW Supply</span><span className="val cool">{Number(c.chw_supply_temp).toFixed(1)}°F</span></div>
          <div className="metric"><span className="name">CHW Return</span><span className="val">{Number(c.chw_return_temp).toFixed(1)}°F</span></div>
          <div className="metric"><span className="name">Load</span><span className="val">{Number(c.load_pct).toFixed(0)}%</span></div>
          <div className="metric"><span className="name">Power</span><span className="val">{Number(c.kw).toFixed(1)} kW</span></div>
          <div className="metric"><span className="name">Enabled</span><span className={`val ${c.enabled ? 'ok' : 'warm'}`}>{c.enabled ? 'Yes' : 'No'}</span></div>
        </div>
      ))}

      {/* Boilers */}
      {Object.entries(boilers).map(([name, b]) => (
        <div className="card" key={name}>
          <h3>🔥 {name}</h3>
          <div className="metric"><span className="name">HW Supply</span><span className="val warm">{Number(b.hw_supply_temp).toFixed(1)}°F</span></div>
          <div className="metric"><span className="name">HW Return</span><span className="val">{Number(b.hw_return_temp).toFixed(1)}°F</span></div>
          <div className="metric"><span className="name">Firing Rate</span><span className="val">{Number(b.firing_rate_pct).toFixed(0)}%</span></div>
          <div className="metric"><span className="name">Enabled</span><span className={`val ${b.enabled ? 'ok' : 'warm'}`}>{b.enabled ? 'Yes' : 'No'}</span></div>
        </div>
      ))}

      {/* Sensors */}
      {Object.entries(sensors).map(([name, s]) => (
        <div className="card" key={name}>
          <h3>📡 {name}</h3>
          <div className="metric"><span className="name">Type</span><span className="val">{s.type}</span></div>
          <div className="metric"><span className="name">Value</span><span className="val ok">{Number(s.value).toFixed(1)}</span></div>
        </div>
      ))}
    </>
  )
}
