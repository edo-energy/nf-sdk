import { useState, useCallback } from 'react'

interface Props {
  faults: Record<string, { target_type: string; target_name: string; fault_type: string; active: boolean }>
  simApi: string
}

export function FaultInjection({ faults, simApi }: Props) {
  const [targetType, setTargetType] = useState('sensor')
  const [targetName, setTargetName] = useState('')
  const [faultType, setFaultType] = useState('freeze')
  const [offset, setOffset] = useState(5)

  const injectFault = useCallback(async () => {
    if (!targetName) return
    const params: Record<string, number> = {}
    if (faultType === 'offset') params.offset = offset

    await fetch(`${simApi}/api/faults`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        target_type: targetType,
        target_name: targetName,
        fault_type: faultType,
        parameters: params,
      }),
    })
  }, [simApi, targetType, targetName, faultType, offset])

  const clearFault = useCallback(async (id: string) => {
    await fetch(`${simApi}/api/faults/${id}`, { method: 'DELETE' })
  }, [simApi])

  return (
    <div className="fault-panel">
      <h2>Fault Injection</h2>

      <div className="fault-row">
        <select value={targetType} onChange={e => setTargetType(e.target.value)}>
          <option value="sensor">Sensor</option>
          <option value="equipment">Equipment</option>
          <option value="communication">Communication</option>
        </select>

        <input
          placeholder="Target name (e.g., OAT-Sensor)"
          value={targetName}
          onChange={e => setTargetName(e.target.value)}
          style={{ width: 200 }}
        />

        <select value={faultType} onChange={e => setFaultType(e.target.value)}>
          <option value="freeze">Freeze Value</option>
          <option value="offset">Add Offset</option>
          <option value="nan">Set to NaN</option>
          <option value="offline">Take Offline</option>
          <option value="stuck">Stuck Actuator</option>
        </select>

        {faultType === 'offset' && (
          <input
            type="number"
            value={offset}
            onChange={e => setOffset(+e.target.value)}
            style={{ width: 80 }}
            placeholder="Offset"
          />
        )}

        <button className="inject" onClick={injectFault}>Inject</button>
      </div>

      {/* Active Faults */}
      <div className="active-faults">
        {Object.entries(faults).map(([id, f]) => (
          <div className="active-fault" key={id}>
            <span>{f.target_type}: {f.target_name} — {f.fault_type}</span>
            <button className="clear" onClick={() => clearFault(id)}>Clear</button>
          </div>
        ))}
        {Object.keys(faults).length === 0 && (
          <div style={{ fontSize: '0.75rem', color: '#666', padding: '0.25rem 0' }}>
            No active faults
          </div>
        )}
      </div>
    </div>
  )
}
