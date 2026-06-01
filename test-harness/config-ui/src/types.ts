export interface WeatherConfig {
  mode: 'fixed' | 'tmy3'
  fixed: { outdoor_air_temp: number; humidity: number; wind_speed: number }
  tmy3_file?: string
}

export interface ZoneConfig {
  name: string
  area_sqft: number
  volume_cuft: number
  r_value: number
  initial_temp: number
  setpoint_cooling: number
  setpoint_heating: number
  internal_load_btu: number
  occupancy_schedule: string
}

export interface AHUConfig {
  name: string
  device_id: number
  supply_fan_hp: number
  max_airflow_cfm: number
  cooling_capacity_tons: number
  heating_capacity_mbh: number
  serves_zones: string[]
  economizer: boolean
}

export interface VAVConfig {
  name: string
  device_id: number
  zone: string
  max_airflow_cfm: number
  min_airflow_cfm: number
  has_reheat: boolean
  reheat_capacity_mbh: number
  parent_ahu: string
}

export interface ChillerConfig {
  name: string
  device_id: number
  capacity_tons: number
  min_plr: number
  design_lwt: number
  design_ewt: number
  condenser_type: string
}

export interface BoilerConfig {
  name: string
  device_id: number
  capacity_mbh: number
  design_lwt: number
  efficiency: number
  fuel_type: string
}

export interface FCUConfig {
  name: string
  device_id: number
  zone: string
  capacity_cooling_mbh: number
  capacity_heating_mbh: number
  fan_speeds: number
}

export interface LightingConfig {
  name: string
  device_id: number
  zone: string
  max_watts: number
  dimmable: boolean
  occupancy_sensor: boolean
}

export interface SensorConfig {
  name: string
  device_id: number
  type: string
  location: string
}

export interface EquipmentConfig {
  ahus: AHUConfig[]
  vavs: VAVConfig[]
  chillers: ChillerConfig[]
  boilers: BoilerConfig[]
  fcus: FCUConfig[]
  lighting: LightingConfig[]
  sensors: SensorConfig[]
}

export interface BuildingConfig {
  building: { name: string; location: string }
  weather: WeatherConfig
  time: { acceleration: number }
  zones: ZoneConfig[]
  equipment: EquipmentConfig
}
