"""
Thermal Simulation Engine for NF Gateway Test Harness.

Provides RC-network thermal models for building zones and HVAC equipment.
Runs as a FastAPI service exposing state via REST + WebSocket.
"""
import asyncio
import time
import math
from dataclasses import dataclass, field
from typing import Optional

import yaml


# --- Thermal Zone Model ---

@dataclass
class Zone:
    name: str
    area_sqft: float
    volume_cuft: float
    r_value: float  # °F·hr·ft²/BTU
    capacitance: float  # BTU/°F (thermal mass)
    temp: float  # Current zone temperature °F
    setpoint_cooling: float
    setpoint_heating: float
    internal_load_btu: float  # BTU/hr internal gains
    hvac_load_btu: float = 0.0  # Current HVAC contribution BTU/hr (negative=cooling)
    occupancy: float = 1.0  # 0-1 occupancy fraction

    def step(self, outdoor_temp: float, dt_hours: float):
        """Advance zone temperature by dt_hours using RC model."""
        # Envelope heat transfer: Q_env = (T_out - T_zone) / R * A
        # Simplified: use R_value as overall thermal resistance per unit area
        envelope_area = self.area_sqft * 0.5  # rough exterior wall fraction
        q_envelope = (outdoor_temp - self.temp) / self.r_value * envelope_area

        # Total heat into zone
        q_total = q_envelope + self.internal_load_btu * self.occupancy + self.hvac_load_btu

        # dT = Q * dt / C
        dt_temp = (q_total * dt_hours) / self.capacitance
        self.temp += dt_temp


# --- Equipment Models ---

@dataclass
class AHU:
    name: str
    device_id: int
    max_airflow_cfm: float
    cooling_capacity_tons: float
    heating_capacity_mbh: float
    supply_fan_hp: float
    economizer: bool
    serves_zones: list

    # Runtime state
    supply_air_temp: float = 55.0
    return_air_temp: float = 72.0
    mixed_air_temp: float = 65.0
    supply_fan_status: bool = True
    supply_fan_speed_pct: float = 80.0
    cooling_valve_pct: float = 0.0
    heating_valve_pct: float = 0.0
    oa_damper_pct: float = 20.0
    filter_dp: float = 0.8  # in. w.c.
    duct_static_pressure: float = 1.2  # in. w.c.
    enabled: bool = True

    def update(self, zones: dict, outdoor_temp: float):
        """Update AHU state based on zone demands."""
        if not self.enabled or not self.supply_fan_status:
            self.supply_fan_speed_pct = 0.0
            self.cooling_valve_pct = 0.0
            self.heating_valve_pct = 0.0
            return

        # Calculate average zone temp for served zones
        served = [zones[z] for z in self.serves_zones if z in zones]
        if not served:
            return

        avg_zone_temp = sum(z.temp for z in served) / len(served)
        avg_clg_sp = sum(z.setpoint_cooling for z in served) / len(served)
        avg_htg_sp = sum(z.setpoint_heating for z in served) / len(served)

        self.return_air_temp = avg_zone_temp

        # Economizer logic
        if self.economizer and outdoor_temp < avg_zone_temp - 2:
            self.oa_damper_pct = min(100.0, max(20.0, (avg_zone_temp - outdoor_temp) * 10))
        else:
            self.oa_damper_pct = 20.0  # minimum OA

        # Mixed air temp
        oa_fraction = self.oa_damper_pct / 100.0
        self.mixed_air_temp = outdoor_temp * oa_fraction + self.return_air_temp * (1 - oa_fraction)

        # Cooling/heating control
        error = avg_zone_temp - avg_clg_sp
        if error > 0:
            # Needs cooling
            self.cooling_valve_pct = min(100.0, max(0.0, error * 30))
            self.heating_valve_pct = 0.0
            cooling_effect = self.cooling_valve_pct / 100.0
            self.supply_air_temp = self.mixed_air_temp - cooling_effect * (self.mixed_air_temp - 52.0)
        else:
            heat_error = avg_htg_sp - avg_zone_temp
            if heat_error > 0:
                # Needs heating
                self.heating_valve_pct = min(100.0, max(0.0, heat_error * 30))
                self.cooling_valve_pct = 0.0
                heating_effect = self.heating_valve_pct / 100.0
                self.supply_air_temp = self.mixed_air_temp + heating_effect * (95.0 - self.mixed_air_temp)
            else:
                self.cooling_valve_pct = 0.0
                self.heating_valve_pct = 0.0
                self.supply_air_temp = self.mixed_air_temp

        # Fan speed based on demand
        demand = sum(max(0, z.temp - z.setpoint_cooling) for z in served) + \
                 sum(max(0, z.setpoint_heating - z.temp) for z in served)
        self.supply_fan_speed_pct = min(100.0, max(30.0, 50.0 + demand * 5))
        self.duct_static_pressure = 0.5 + (self.supply_fan_speed_pct / 100.0) * 1.0


@dataclass
class VAV:
    name: str
    device_id: int
    zone: str
    max_airflow_cfm: float
    min_airflow_cfm: float
    has_reheat: bool
    reheat_capacity_mbh: float
    parent_ahu: str

    # Runtime state
    damper_position_pct: float = 50.0
    reheat_valve_pct: float = 0.0
    airflow_cfm: float = 0.0
    zone_temp: float = 72.0
    zone_temp_setpoint: float = 74.0
    occupied: bool = True

    def update(self, zone: 'Zone', ahu_sat: float):
        """Update VAV state based on zone conditions."""
        self.zone_temp = zone.temp
        self.zone_temp_setpoint = zone.setpoint_cooling

        error = zone.temp - zone.setpoint_cooling
        if error > 0:
            # Zone too warm - open damper
            self.damper_position_pct = min(100.0, max(20.0, 50.0 + error * 20))
            self.reheat_valve_pct = 0.0
        else:
            heat_error = zone.setpoint_heating - zone.temp
            if heat_error > 0 and self.has_reheat:
                # Zone too cold - close damper to min, open reheat
                self.damper_position_pct = 20.0  # minimum
                self.reheat_valve_pct = min(100.0, max(0.0, heat_error * 30))
            else:
                self.damper_position_pct = max(20.0, 50.0 + error * 10)
                self.reheat_valve_pct = 0.0

        # Calculate airflow
        damper_frac = self.damper_position_pct / 100.0
        self.airflow_cfm = self.min_airflow_cfm + damper_frac * (self.max_airflow_cfm - self.min_airflow_cfm)

        # Calculate heat delivered to zone (BTU/hr)
        # Q = 1.08 * CFM * (SAT - zone_temp) for sensible heat
        supply_temp = ahu_sat
        if self.reheat_valve_pct > 0:
            reheat_rise = (self.reheat_valve_pct / 100.0) * 20.0  # max 20°F rise
            supply_temp = ahu_sat + reheat_rise

        zone.hvac_load_btu = 1.08 * self.airflow_cfm * (supply_temp - zone.temp)


@dataclass
class Chiller:
    name: str
    device_id: int
    capacity_tons: float
    min_plr: float
    design_lwt: float
    design_ewt: float
    condenser_type: str

    # Runtime state
    chw_supply_temp: float = 44.0
    chw_return_temp: float = 54.0
    condenser_entering_temp: float = 85.0
    load_pct: float = 0.0
    enabled: bool = True
    setpoint: float = 44.0
    kw: float = 0.0

    def update(self, total_cooling_load_tons: float, outdoor_temp: float):
        """Update chiller state based on load."""
        self.condenser_entering_temp = outdoor_temp
        if not self.enabled or total_cooling_load_tons <= 0:
            self.load_pct = 0.0
            self.kw = 0.0
            self.chw_supply_temp = self.chw_return_temp
            return

        self.load_pct = min(100.0, (total_cooling_load_tons / self.capacity_tons) * 100)
        plr = max(self.min_plr, self.load_pct / 100.0)

        # Simple power model: kW/ton varies with PLR and condenser temp
        base_kw_per_ton = 0.6
        condenser_penalty = max(0, (outdoor_temp - 85) * 0.01)
        plr_curve = 0.2 + 0.8 * plr  # part load efficiency
        kw_per_ton = (base_kw_per_ton + condenser_penalty) * plr_curve
        self.kw = kw_per_ton * total_cooling_load_tons

        # Leaving water temp - approaches setpoint as load decreases
        self.chw_supply_temp = self.setpoint + (1 - plr) * 2.0
        self.chw_return_temp = self.chw_supply_temp + plr * 10.0


@dataclass
class Boiler:
    name: str
    device_id: int
    capacity_mbh: float
    design_lwt: float
    efficiency: float
    fuel_type: str

    # Runtime state
    hw_supply_temp: float = 180.0
    hw_return_temp: float = 160.0
    firing_rate_pct: float = 0.0
    enabled: bool = True
    setpoint: float = 180.0
    kw: float = 0.0  # for electric, gas_rate_therms for gas

    def update(self, total_heating_load_mbh: float):
        """Update boiler state based on load."""
        if not self.enabled or total_heating_load_mbh <= 0:
            self.firing_rate_pct = 0.0
            self.kw = 0.0
            self.hw_supply_temp = self.hw_return_temp
            return

        self.firing_rate_pct = min(100.0, (total_heating_load_mbh / self.capacity_mbh) * 100)
        plr = self.firing_rate_pct / 100.0

        # Leaving water temp
        self.hw_supply_temp = self.hw_return_temp + plr * (self.design_lwt - self.hw_return_temp)
        self.hw_return_temp = self.hw_supply_temp - plr * 20.0

        # Fuel consumption
        input_mbh = total_heating_load_mbh / self.efficiency
        if self.fuel_type == "electric":
            self.kw = input_mbh * 293.07  # MBH to W, /1000 to kW... simplified
        else:
            self.kw = input_mbh * 0.01  # parasitic (pumps, controls)


@dataclass
class FCU:
    name: str
    device_id: int
    zone: str
    capacity_cooling_mbh: float
    capacity_heating_mbh: float
    fan_speeds: int

    # Runtime state
    zone_temp: float = 72.0
    fan_speed: int = 0  # 0=off, 1-3
    valve_position_pct: float = 0.0
    discharge_temp: float = 72.0
    mode: int = 1  # 1=off, 2=cool, 3=heat, 4=auto

    def update(self, zone: 'Zone'):
        """Update FCU based on zone needs."""
        self.zone_temp = zone.temp
        error_cool = zone.temp - zone.setpoint_cooling
        error_heat = zone.setpoint_heating - zone.temp

        if error_cool > 1.0:
            self.mode = 2
            self.fan_speed = min(self.fan_speeds, max(1, int(error_cool)))
            self.valve_position_pct = min(100.0, error_cool * 30)
            capacity_frac = self.valve_position_pct / 100.0
            self.discharge_temp = zone.temp - capacity_frac * 15.0
            zone.hvac_load_btu += -self.capacity_cooling_mbh * 1000 * capacity_frac * (self.fan_speed / self.fan_speeds)
        elif error_heat > 1.0:
            self.mode = 3
            self.fan_speed = min(self.fan_speeds, max(1, int(error_heat)))
            self.valve_position_pct = min(100.0, error_heat * 30)
            capacity_frac = self.valve_position_pct / 100.0
            self.discharge_temp = zone.temp + capacity_frac * 20.0
            zone.hvac_load_btu += self.capacity_heating_mbh * 1000 * capacity_frac * (self.fan_speed / self.fan_speeds)
        else:
            self.mode = 1
            self.fan_speed = 0
            self.valve_position_pct = 0.0
            self.discharge_temp = zone.temp


@dataclass
class Lighting:
    name: str
    device_id: int
    zone: str
    max_watts: float
    dimmable: bool
    occupancy_sensor: bool

    # Runtime state
    level_pct: float = 100.0
    occupancy_detected: bool = True
    schedule_override: bool = False
    actual_watts: float = 0.0

    def update(self, zone: 'Zone'):
        """Update lighting state."""
        if self.occupancy_sensor and not self.occupancy_detected and not self.schedule_override:
            self.actual_watts = 0.0
            self.level_pct = 0.0
        else:
            self.actual_watts = self.max_watts * (self.level_pct / 100.0)

        # Lighting adds heat to zone (3.412 BTU/hr per watt)
        zone.internal_load_btu += self.actual_watts * 3.412


@dataclass
class Sensor:
    name: str
    device_id: int
    sensor_type: str
    location: str

    # Runtime state
    value: float = 0.0

    def update(self, outdoor_temp: float, outdoor_humidity: float, zones: dict, total_kw: float):
        """Update sensor reading based on type."""
        if self.sensor_type == "oat":
            self.value = outdoor_temp
        elif self.sensor_type == "humidity":
            self.value = outdoor_humidity
        elif self.sensor_type == "co2":
            # CO2 correlates with occupancy - base 400ppm + occupancy contribution
            zone_names = list(zones.keys())
            if zone_names:
                avg_occupancy = sum(z.occupancy for z in zones.values()) / len(zones)
                self.value = 400 + avg_occupancy * 500 + (len(zones) * 20)
            else:
                self.value = 400.0
        elif self.sensor_type == "power_meter":
            self.value = total_kw
        elif self.sensor_type == "pressure":
            self.value = 0.05  # building static pressure


# --- Fault Injection ---

@dataclass
class Fault:
    id: str
    target_type: str  # "sensor", "equipment", "communication"
    target_name: str
    fault_type: str  # "freeze", "offset", "nan", "offline", "stuck"
    parameters: dict = field(default_factory=dict)
    active: bool = True
    scheduled_time: Optional[float] = None  # sim time to activate


# --- Simulation Engine ---

class ThermalSimulation:
    def __init__(self, config_path: str):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        self.zones: dict[str, Zone] = {}
        self.ahus: dict[str, AHU] = {}
        self.vavs: dict[str, VAV] = {}
        self.chillers: dict[str, Chiller] = {}
        self.boilers: dict[str, Boiler] = {}
        self.fcus: dict[str, FCU] = {}
        self.lighting: dict[str, Lighting] = {}
        self.sensors: dict[str, Sensor] = {}
        self.faults: dict[str, Fault] = {}

        self.outdoor_temp: float = 85.0
        self.outdoor_humidity: float = 55.0
        self.wind_speed: float = 8.0
        self.sim_time: float = time.time()
        self.acceleration: int = 1
        self.running: bool = False
        self.timestep_seconds: float = 60.0  # 1 minute simulation timestep

        self._build_from_config()

    def _build_from_config(self):
        """Instantiate all objects from YAML config."""
        # Weather
        weather = self.config.get("weather", {})
        if weather.get("mode") == "fixed":
            fixed = weather.get("fixed", {})
            self.outdoor_temp = fixed.get("outdoor_air_temp", 85.0)
            self.outdoor_humidity = fixed.get("humidity", 55.0)
            self.wind_speed = fixed.get("wind_speed", 8.0)

        # Time
        time_cfg = self.config.get("time", {})
        self.acceleration = time_cfg.get("acceleration", 1)

        # Zones
        for z in self.config.get("zones", []):
            volume = z.get("volume_cuft", z.get("area_sqft", 1000) * 10)
            # Default capacitance: air density ~0.075 lb/ft³, Cp ~0.24 BTU/(lb·°F)
            # Plus building mass contribution (~5x air alone)
            capacitance = z.get("capacitance", volume * 0.075 * 0.24 * 5)
            self.zones[z["name"]] = Zone(
                name=z["name"],
                area_sqft=z.get("area_sqft", 1000),
                volume_cuft=volume,
                r_value=z.get("r_value", 15.0),
                capacitance=capacitance,
                temp=z.get("initial_temp", 72.0),
                setpoint_cooling=z.get("setpoint_cooling", 74.0),
                setpoint_heating=z.get("setpoint_heating", 70.0),
                internal_load_btu=z.get("internal_load_btu", 0.0),
            )

        # Equipment
        equip = self.config.get("equipment", {})

        for a in equip.get("ahus", []):
            self.ahus[a["name"]] = AHU(
                name=a["name"],
                device_id=a["device_id"],
                max_airflow_cfm=a.get("max_airflow_cfm", 10000),
                cooling_capacity_tons=a.get("cooling_capacity_tons", 25),
                heating_capacity_mbh=a.get("heating_capacity_mbh", 200),
                supply_fan_hp=a.get("supply_fan_hp", 15),
                economizer=a.get("economizer", True),
                serves_zones=a.get("serves_zones", []),
            )

        for v in equip.get("vavs", []):
            self.vavs[v["name"]] = VAV(
                name=v["name"],
                device_id=v["device_id"],
                zone=v["zone"],
                max_airflow_cfm=v.get("max_airflow_cfm", 1200),
                min_airflow_cfm=v.get("min_airflow_cfm", 250),
                has_reheat=v.get("has_reheat", True),
                reheat_capacity_mbh=v.get("reheat_capacity_mbh", 15),
                parent_ahu=v.get("parent_ahu", ""),
            )

        for c in equip.get("chillers", []):
            self.chillers[c["name"]] = Chiller(
                name=c["name"],
                device_id=c["device_id"],
                capacity_tons=c.get("capacity_tons", 50),
                min_plr=c.get("min_plr", 0.2),
                design_lwt=c.get("design_lwt", 44),
                design_ewt=c.get("design_ewt", 54),
                condenser_type=c.get("condenser_type", "air"),
            )

        for b in equip.get("boilers", []):
            self.boilers[b["name"]] = Boiler(
                name=b["name"],
                device_id=b["device_id"],
                capacity_mbh=b.get("capacity_mbh", 500),
                design_lwt=b.get("design_lwt", 180),
                efficiency=b.get("efficiency", 0.92),
                fuel_type=b.get("fuel_type", "gas"),
            )

        for f in equip.get("fcus", []):
            self.fcus[f["name"]] = FCU(
                name=f["name"],
                device_id=f["device_id"],
                zone=f["zone"],
                capacity_cooling_mbh=f.get("capacity_cooling_mbh", 24),
                capacity_heating_mbh=f.get("capacity_heating_mbh", 18),
                fan_speeds=f.get("fan_speeds", 3),
            )

        for lt in equip.get("lighting", []):
            self.lighting[lt["name"]] = Lighting(
                name=lt["name"],
                device_id=lt["device_id"],
                zone=lt["zone"],
                max_watts=lt.get("max_watts", 5000),
                dimmable=lt.get("dimmable", True),
                occupancy_sensor=lt.get("occupancy_sensor", True),
            )

        for s in equip.get("sensors", []):
            self.sensors[s["name"]] = Sensor(
                name=s["name"],
                device_id=s["device_id"],
                sensor_type=s.get("type", "oat"),
                location=s.get("location", ""),
            )

    def step(self):
        """Advance simulation by one timestep."""
        dt_hours = self.timestep_seconds / 3600.0

        # Reset zone HVAC loads before equipment updates
        for zone in self.zones.values():
            zone.hvac_load_btu = 0.0

        # Update AHUs
        for ahu in self.ahus.values():
            ahu.update(self.zones, self.outdoor_temp)

        # Update VAVs (depends on AHU supply air temp)
        for vav in self.vavs.values():
            if vav.zone in self.zones:
                parent = self.ahus.get(vav.parent_ahu)
                sat = parent.supply_air_temp if parent else 55.0
                vav.update(self.zones[vav.zone], sat)

        # Update FCUs
        for fcu in self.fcus.values():
            if fcu.zone in self.zones:
                fcu.update(self.zones[fcu.zone])

        # Update lighting (adds internal gains)
        for lt in self.lighting.values():
            if lt.zone in self.zones:
                lt.update(self.zones[lt.zone])

        # Step zone temperatures
        for zone in self.zones.values():
            zone.step(self.outdoor_temp, dt_hours)

        # Calculate total loads for plant equipment
        total_cooling_tons = sum(
            max(0, -z.hvac_load_btu) / 12000.0 for z in self.zones.values()
        )
        total_heating_mbh = sum(
            max(0, z.hvac_load_btu) / 1000.0 for z in self.zones.values()
        )

        # Update plant
        for chiller in self.chillers.values():
            chiller.update(total_cooling_tons / max(1, len(self.chillers)), self.outdoor_temp)

        for boiler in self.boilers.values():
            boiler.update(total_heating_mbh / max(1, len(self.boilers)))

        # Calculate total power
        total_kw = sum(c.kw for c in self.chillers.values()) + \
                   sum(b.kw for b in self.boilers.values()) + \
                   sum(lt.actual_watts / 1000.0 for lt in self.lighting.values())

        # Update sensors
        for sensor in self.sensors.values():
            sensor.update(self.outdoor_temp, self.outdoor_humidity, self.zones, total_kw)

        # Apply faults
        self._apply_faults()

        # Advance sim time
        self.sim_time += self.timestep_seconds

    def _apply_faults(self):
        """Apply active faults to equipment/sensors."""
        for fault in self.faults.values():
            if not fault.active:
                continue
            if fault.scheduled_time and self.sim_time < fault.scheduled_time:
                continue

            if fault.target_type == "sensor":
                sensor = self.sensors.get(fault.target_name)
                if not sensor:
                    continue
                if fault.fault_type == "freeze":
                    pass  # value already frozen (not updated)
                elif fault.fault_type == "offset":
                    sensor.value += fault.parameters.get("offset", 5.0)
                elif fault.fault_type == "nan":
                    sensor.value = float('nan')

            elif fault.target_type == "equipment":
                # Find equipment by name across all types
                equip = (self.ahus.get(fault.target_name) or
                         self.chillers.get(fault.target_name) or
                         self.boilers.get(fault.target_name))
                if equip and fault.fault_type == "offline":
                    equip.enabled = False
                elif fault.fault_type == "stuck":
                    pass  # outputs frozen at current values

    def get_state(self) -> dict:
        """Return full simulation state as a dictionary."""
        return {
            "sim_time": self.sim_time,
            "acceleration": self.acceleration,
            "weather": {
                "outdoor_air_temp": self.outdoor_temp,
                "humidity": self.outdoor_humidity,
                "wind_speed": self.wind_speed,
            },
            "zones": {
                name: {
                    "temp": z.temp,
                    "setpoint_cooling": z.setpoint_cooling,
                    "setpoint_heating": z.setpoint_heating,
                    "hvac_load_btu": z.hvac_load_btu,
                    "occupancy": z.occupancy,
                }
                for name, z in self.zones.items()
            },
            "ahus": {
                name: {
                    "device_id": a.device_id,
                    "supply_air_temp": a.supply_air_temp,
                    "return_air_temp": a.return_air_temp,
                    "mixed_air_temp": a.mixed_air_temp,
                    "supply_fan_status": a.supply_fan_status,
                    "supply_fan_speed_pct": a.supply_fan_speed_pct,
                    "cooling_valve_pct": a.cooling_valve_pct,
                    "heating_valve_pct": a.heating_valve_pct,
                    "oa_damper_pct": a.oa_damper_pct,
                    "filter_dp": a.filter_dp,
                    "duct_static_pressure": a.duct_static_pressure,
                    "enabled": a.enabled,
                }
                for name, a in self.ahus.items()
            },
            "vavs": {
                name: {
                    "device_id": v.device_id,
                    "zone_temp": v.zone_temp,
                    "zone_temp_setpoint": v.zone_temp_setpoint,
                    "damper_position_pct": v.damper_position_pct,
                    "reheat_valve_pct": v.reheat_valve_pct,
                    "airflow_cfm": v.airflow_cfm,
                    "occupied": v.occupied,
                }
                for name, v in self.vavs.items()
            },
            "chillers": {
                name: {
                    "device_id": c.device_id,
                    "chw_supply_temp": c.chw_supply_temp,
                    "chw_return_temp": c.chw_return_temp,
                    "condenser_entering_temp": c.condenser_entering_temp,
                    "load_pct": c.load_pct,
                    "enabled": c.enabled,
                    "setpoint": c.setpoint,
                    "kw": c.kw,
                }
                for name, c in self.chillers.items()
            },
            "boilers": {
                name: {
                    "device_id": b.device_id,
                    "hw_supply_temp": b.hw_supply_temp,
                    "hw_return_temp": b.hw_return_temp,
                    "firing_rate_pct": b.firing_rate_pct,
                    "enabled": b.enabled,
                    "setpoint": b.setpoint,
                }
                for name, b in self.boilers.items()
            },
            "fcus": {
                name: {
                    "device_id": f.device_id,
                    "zone_temp": f.zone_temp,
                    "fan_speed": f.fan_speed,
                    "valve_position_pct": f.valve_position_pct,
                    "discharge_temp": f.discharge_temp,
                    "mode": f.mode,
                }
                for name, f in self.fcus.items()
            },
            "lighting": {
                name: {
                    "device_id": lt.device_id,
                    "level_pct": lt.level_pct,
                    "occupancy_detected": lt.occupancy_detected,
                    "actual_watts": lt.actual_watts,
                }
                for name, lt in self.lighting.items()
            },
            "sensors": {
                name: {
                    "device_id": s.device_id,
                    "type": s.sensor_type,
                    "value": s.value,
                }
                for name, s in self.sensors.items()
            },
            "faults": {
                fid: {
                    "target_type": f.target_type,
                    "target_name": f.target_name,
                    "fault_type": f.fault_type,
                    "active": f.active,
                    "parameters": f.parameters,
                }
                for fid, f in self.faults.items()
            },
        }

    def add_fault(self, fault: Fault):
        self.faults[fault.id] = fault

    def remove_fault(self, fault_id: str):
        if fault_id in self.faults:
            # Restore equipment if it was disabled
            fault = self.faults[fault_id]
            if fault.target_type == "equipment" and fault.fault_type == "offline":
                equip = (self.ahus.get(fault.target_name) or
                         self.chillers.get(fault.target_name) or
                         self.boilers.get(fault.target_name))
                if equip:
                    equip.enabled = True
            del self.faults[fault_id]

    def handle_write(self, device_id: int, object_type: str, object_instance: int, value: float):
        """Handle a BACnet write from NF - feeds back into simulation."""
        # Find the equipment with this device_id
        for vav in self.vavs.values():
            if vav.device_id == device_id:
                if object_type == "analog-value" and object_instance == 1:
                    # Zone temp setpoint write
                    if vav.zone in self.zones:
                        self.zones[vav.zone].setpoint_cooling = value
                        vav.zone_temp_setpoint = value
                return

        for ahu in self.ahus.values():
            if ahu.device_id == device_id:
                if object_type == "analog-output":
                    if object_instance == 1:  # fan speed
                        ahu.supply_fan_speed_pct = value
                    elif object_instance == 2:  # cooling valve
                        ahu.cooling_valve_pct = value
                    elif object_instance == 3:  # heating valve
                        ahu.heating_valve_pct = value
                    elif object_instance == 4:  # OA damper
                        ahu.oa_damper_pct = value
                return

        for chiller in self.chillers.values():
            if chiller.device_id == device_id:
                if object_type == "analog-value" and object_instance == 1:
                    chiller.setpoint = value
                elif object_type == "binary-output" and object_instance == 1:
                    chiller.enabled = bool(value)
                return

        for boiler in self.boilers.values():
            if boiler.device_id == device_id:
                if object_type == "analog-value" and object_instance == 1:
                    boiler.setpoint = value
                elif object_type == "binary-output" and object_instance == 1:
                    boiler.enabled = bool(value)
                return

    def reload(self, config: dict):
        """Hot-reload simulation from a new config dict."""
        self.config = config
        self.zones.clear()
        self.ahus.clear()
        self.vavs.clear()
        self.chillers.clear()
        self.boilers.clear()
        self.fcus.clear()
        self.lighting.clear()
        self.sensors.clear()
        self.faults.clear()
        self._build_from_config()
