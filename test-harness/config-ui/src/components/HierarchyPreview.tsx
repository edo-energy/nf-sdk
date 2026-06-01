import type { BuildingConfig } from '../types'

interface Props {
  config: BuildingConfig
}

export function HierarchyPreview({ config }: Props) {
  const totalDevices =
    config.equipment.ahus.length +
    config.equipment.vavs.length +
    config.equipment.chillers.length +
    config.equipment.boilers.length +
    config.equipment.fcus.length +
    config.equipment.lighting.length +
    config.equipment.sensors.length

  // Rough object count: AHU=10, VAV=6, Chiller=6, Boiler=5, FCU=5, Lighting=3, Sensor=1
  const totalObjects =
    config.equipment.ahus.length * 10 +
    config.equipment.vavs.length * 6 +
    config.equipment.chillers.length * 6 +
    config.equipment.boilers.length * 5 +
    config.equipment.fcus.length * 5 +
    config.equipment.lighting.length * 3 +
    config.equipment.sensors.length * 1

  // Build hierarchy: Plant → AHU → VAV → Zone
  const ahuTree = config.equipment.ahus.map(ahu => ({
    ...ahu,
    vavs: config.equipment.vavs.filter(v => v.parent_ahu === ahu.name),
  }))

  // Device IDs for conflict detection
  const allIds = [
    ...config.equipment.ahus,
    ...config.equipment.vavs,
    ...config.equipment.chillers,
    ...config.equipment.boilers,
    ...config.equipment.fcus,
    ...config.equipment.lighting,
    ...config.equipment.sensors,
  ].map(e => e.device_id)
  const duplicates = allIds.filter((id, i) => allIds.indexOf(id) !== i)

  // Orphan zones (zones not served by any VAV/FCU)
  const servedZones = new Set([
    ...config.equipment.vavs.map(v => v.zone),
    ...config.equipment.fcus.map(f => f.zone),
  ])
  const orphanZones = config.zones.filter(z => !servedZones.has(z.name))

  return (
    <div className="hierarchy-panel">
      <h2>Building Hierarchy</h2>

      {duplicates.length > 0 && (
        <div className="status-bar error">
          ⚠ Duplicate device IDs: {[...new Set(duplicates)].join(', ')}
        </div>
      )}

      {orphanZones.length > 0 && (
        <div className="status-bar error">
          ⚠ Unserved zones: {orphanZones.map(z => z.name).join(', ')}
        </div>
      )}

      <div style={{ fontSize: '0.8rem' }}>
        <div className="tree-label equip">🏢 {config.building.name}</div>

        {/* Plant level */}
        <div className="tree-node">
          {config.equipment.chillers.length > 0 && (
            <div className="tree-label equip">❄️ Chillers ({config.equipment.chillers.length})</div>
          )}
          {config.equipment.boilers.length > 0 && (
            <div className="tree-label equip">🔥 Boilers ({config.equipment.boilers.length})</div>
          )}
        </div>

        {/* AHU → VAV → Zone tree */}
        <div className="tree-node">
          {ahuTree.map(ahu => (
            <div key={ahu.name}>
              <div className="tree-label equip">🌀 {ahu.name}</div>
              <div className="tree-node">
                {ahu.vavs.map(vav => (
                  <div key={vav.name}>
                    <div className="tree-label">📦 {vav.name} → <span className="tree-label zone">{vav.zone || '(no zone)'}</span></div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* FCUs */}
        {config.equipment.fcus.length > 0 && (
          <div className="tree-node">
            <div className="tree-label equip">🌡️ FCUs ({config.equipment.fcus.length})</div>
          </div>
        )}

        {/* Lighting + Sensors */}
        {config.equipment.lighting.length > 0 && (
          <div className="tree-node">
            <div className="tree-label equip">💡 Lighting ({config.equipment.lighting.length})</div>
          </div>
        )}
        {config.equipment.sensors.length > 0 && (
          <div className="tree-node">
            <div className="tree-label equip">📡 Sensors ({config.equipment.sensors.length})</div>
          </div>
        )}
      </div>

      <div className="stats">
        <div><strong>{totalDevices}</strong> BACnet devices</div>
        <div><strong>~{totalObjects}</strong> BACnet objects</div>
        <div><strong>{config.zones.length}</strong> thermal zones</div>
      </div>
    </div>
  )
}
