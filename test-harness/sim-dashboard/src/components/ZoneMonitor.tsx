interface Props {
  zones: Record<string, {
    temp: number
    setpoint_cooling: number
    setpoint_heating: number
    hvac_load_btu: number
    occupancy: number
  }>
}

export function ZoneMonitor({ zones }: Props) {
  return (
    <>
      {Object.entries(zones).map(([name, z]) => {
        const tempClass = z.temp > z.setpoint_cooling ? 'warm' :
                          z.temp < z.setpoint_heating ? 'cool' : 'ok'
        return (
          <div className="card" key={name}>
            <h3>{name}</h3>
            <div className="metric">
              <span className="name">Temperature</span>
              <span className={`val ${tempClass}`}>{z.temp.toFixed(1)}°F</span>
            </div>
            <div className="metric">
              <span className="name">Cooling Setpoint</span>
              <span className="val">{z.setpoint_cooling.toFixed(1)}°F</span>
            </div>
            <div className="metric">
              <span className="name">Heating Setpoint</span>
              <span className="val">{z.setpoint_heating.toFixed(1)}°F</span>
            </div>
            <div className="metric">
              <span className="name">HVAC Load</span>
              <span className={`val ${z.hvac_load_btu < 0 ? 'cool' : z.hvac_load_btu > 0 ? 'warm' : ''}`}>
                {(z.hvac_load_btu / 1000).toFixed(1)} kBTU/hr
              </span>
            </div>
            <div className="metric">
              <span className="name">Occupancy</span>
              <span className="val">{(z.occupancy * 100).toFixed(0)}%</span>
            </div>
          </div>
        )
      })}
    </>
  )
}
