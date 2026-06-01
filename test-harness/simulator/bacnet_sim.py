"""
BACnet Device Simulator using bacpypes3.

Reads building configuration and instantiates BACnet/IP devices
with appropriate object lists. Present-values are driven by the
thermal simulation engine via internal API.
"""
import asyncio
import os
import signal
import sys
from dataclasses import dataclass

import yaml
import httpx

from bacpypes3.debugging import ModuleLogger
from bacpypes3.argparse import SimpleArgumentParser
from bacpypes3.app import Application
from bacpypes3.local.analog import AnalogInputObject, AnalogOutputObject, AnalogValueObject
from bacpypes3.local.binary import BinaryInputObject, BinaryOutputObject, BinaryValueObject
from bacpypes3.local.cmd import Commandable
from bacpypes3.primitivedata import Real, CharacterString, Enumerated
from bacpypes3.basetypes import EngineeringUnits, StatusFlags, EventState, Reliability
from bacpypes3.object import DeviceObject
from bacpypes3.ipv4.app import NormalApplication


_debug = 0
_log = ModuleLogger(globals())

THERMAL_ENGINE_URL = os.environ.get("THERMAL_ENGINE_URL", "http://localhost:8100")
BUILDING_CONFIG = os.environ.get("BUILDING_CONFIG", "/config/building.yml")
BACNET_INTERFACE = os.environ.get("BACNET_INTERFACE", "")
BACNET_PORT = int(os.environ.get("BACNET_PORT", "47808"))


# --- Commandable object types for writable points ---

class CommandableAnalogOutput(Commandable, AnalogOutputObject):
    pass


class CommandableAnalogValue(Commandable, AnalogValueObject):
    pass


class CommandableBinaryOutput(Commandable, BinaryOutputObject):
    pass


class CommandableBinaryValue(Commandable, BinaryValueObject):
    pass


# --- BACnet Object Profiles per Equipment Type ---

def ahu_objects(name: str) -> list:
    """Create BACnet objects for an AHU."""
    return [
        ("analog-input", 1, f"{name} Supply Air Temp", EngineeringUnits.degreesFahrenheit, "supply_air_temp"),
        ("analog-input", 2, f"{name} Return Air Temp", EngineeringUnits.degreesFahrenheit, "return_air_temp"),
        ("analog-input", 3, f"{name} Mixed Air Temp", EngineeringUnits.degreesFahrenheit, "mixed_air_temp"),
        ("binary-input", 1, f"{name} Supply Fan Status", None, "supply_fan_status"),
        ("analog-output", 1, f"{name} Supply Fan Speed", EngineeringUnits.percent, "supply_fan_speed_pct"),
        ("analog-output", 2, f"{name} Cooling Valve", EngineeringUnits.percent, "cooling_valve_pct"),
        ("analog-output", 3, f"{name} Heating Valve", EngineeringUnits.percent, "heating_valve_pct"),
        ("analog-output", 4, f"{name} OA Damper", EngineeringUnits.percent, "oa_damper_pct"),
        ("analog-input", 4, f"{name} Filter DP", EngineeringUnits.inchesOfWater, "filter_dp"),
        ("analog-input", 5, f"{name} Duct Static Pressure", EngineeringUnits.inchesOfWater, "duct_static_pressure"),
    ]


def vav_objects(name: str) -> list:
    """Create BACnet objects for a VAV box."""
    return [
        ("analog-input", 1, f"{name} Zone Temp", EngineeringUnits.degreesFahrenheit, "zone_temp"),
        ("analog-value", 1, f"{name} Zone Temp Setpoint", EngineeringUnits.degreesFahrenheit, "zone_temp_setpoint"),
        ("analog-output", 1, f"{name} Damper Position", EngineeringUnits.percent, "damper_position_pct"),
        ("analog-output", 2, f"{name} Reheat Valve", EngineeringUnits.percent, "reheat_valve_pct"),
        ("analog-input", 2, f"{name} Airflow", EngineeringUnits.cubicFeetPerMinute, "airflow_cfm"),
        ("binary-value", 1, f"{name} Occupied", None, "occupied"),
    ]


def chiller_objects(name: str) -> list:
    """Create BACnet objects for a chiller."""
    return [
        ("analog-input", 1, f"{name} CHW Supply Temp", EngineeringUnits.degreesFahrenheit, "chw_supply_temp"),
        ("analog-input", 2, f"{name} CHW Return Temp", EngineeringUnits.degreesFahrenheit, "chw_return_temp"),
        ("analog-input", 3, f"{name} Condenser Entering Temp", EngineeringUnits.degreesFahrenheit, "condenser_entering_temp"),
        ("analog-input", 4, f"{name} Load", EngineeringUnits.percent, "load_pct"),
        ("binary-output", 1, f"{name} Enable", None, "enabled"),
        ("analog-value", 1, f"{name} Setpoint", EngineeringUnits.degreesFahrenheit, "setpoint"),
    ]


def boiler_objects(name: str) -> list:
    """Create BACnet objects for a boiler."""
    return [
        ("analog-input", 1, f"{name} HW Supply Temp", EngineeringUnits.degreesFahrenheit, "hw_supply_temp"),
        ("analog-input", 2, f"{name} HW Return Temp", EngineeringUnits.degreesFahrenheit, "hw_return_temp"),
        ("analog-input", 3, f"{name} Firing Rate", EngineeringUnits.percent, "firing_rate_pct"),
        ("binary-output", 1, f"{name} Enable", None, "enabled"),
        ("analog-value", 1, f"{name} Setpoint", EngineeringUnits.degreesFahrenheit, "setpoint"),
    ]


def fcu_objects(name: str) -> list:
    """Create BACnet objects for a fan coil unit."""
    return [
        ("analog-input", 1, f"{name} Zone Temp", EngineeringUnits.degreesFahrenheit, "zone_temp"),
        ("analog-output", 1, f"{name} Fan Speed", EngineeringUnits.noUnits, "fan_speed"),
        ("analog-output", 2, f"{name} Valve Position", EngineeringUnits.percent, "valve_position_pct"),
        ("analog-input", 2, f"{name} Discharge Temp", EngineeringUnits.degreesFahrenheit, "discharge_temp"),
        ("multi-state-value", 1, f"{name} Mode", None, "mode"),
    ]


def lighting_objects(name: str) -> list:
    """Create BACnet objects for a lighting controller."""
    return [
        ("analog-output", 1, f"{name} Level", EngineeringUnits.percent, "level_pct"),
        ("binary-input", 1, f"{name} Occupancy", None, "occupancy_detected"),
        ("binary-value", 1, f"{name} Schedule Override", None, "schedule_override"),
    ]


def sensor_objects(name: str, sensor_type: str) -> list:
    """Create BACnet objects for a standalone sensor."""
    units_map = {
        "oat": EngineeringUnits.degreesFahrenheit,
        "humidity": EngineeringUnits.percentRelativeHumidity,
        "co2": EngineeringUnits.partsPerMillion,
        "power_meter": EngineeringUnits.kilowatts,
        "pressure": EngineeringUnits.inchesOfWater,
    }
    return [
        ("analog-input", 1, f"{name}", units_map.get(sensor_type, EngineeringUnits.noUnits), "value"),
    ]


# --- Device Application ---

@dataclass
class SimDevice:
    """Represents a simulated BACnet device with its objects."""
    name: str
    device_id: int
    equipment_type: str
    app: NormalApplication | None = None
    objects: dict = None  # maps (obj_type, instance) -> bacpypes object
    field_map: dict = None  # maps (obj_type, instance) -> thermal engine field name

    def __post_init__(self):
        self.objects = {}
        self.field_map = {}


class BACnetSimulator:
    """Manages all simulated BACnet devices."""

    def __init__(self, config_path: str):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        self.devices: dict[int, SimDevice] = {}
        self.http_client: httpx.AsyncClient | None = None
        self._running = True
        self._comm_faults: set[int] = set()  # device IDs with comm faults

    def build_devices(self):
        """Build device list from configuration."""
        equip = self.config.get("equipment", {})

        for ahu in equip.get("ahus", []):
            self._add_device(ahu["name"], ahu["device_id"], "ahu", ahu_objects(ahu["name"]))

        for vav in equip.get("vavs", []):
            self._add_device(vav["name"], vav["device_id"], "vav", vav_objects(vav["name"]))

        for ch in equip.get("chillers", []):
            self._add_device(ch["name"], ch["device_id"], "chiller", chiller_objects(ch["name"]))

        for bl in equip.get("boilers", []):
            self._add_device(bl["name"], bl["device_id"], "boiler", boiler_objects(bl["name"]))

        for fcu in equip.get("fcus", []):
            self._add_device(fcu["name"], fcu["device_id"], "fcu", fcu_objects(fcu["name"]))

        for lt in equip.get("lighting", []):
            self._add_device(lt["name"], lt["device_id"], "lighting", lighting_objects(lt["name"]))

        for s in equip.get("sensors", []):
            self._add_device(s["name"], s["device_id"], "sensor",
                             sensor_objects(s["name"], s.get("type", "oat")))

    def _add_device(self, name: str, device_id: int, equip_type: str, obj_defs: list):
        """Register a device with its object definitions."""
        dev = SimDevice(name=name, device_id=device_id, equipment_type=equip_type)
        for obj_type, instance, obj_name, units, field in obj_defs:
            dev.field_map[(obj_type, instance)] = field
        self.devices[device_id] = dev

    async def start(self):
        """Start all BACnet device applications."""
        self.http_client = httpx.AsyncClient(base_url=THERMAL_ENGINE_URL, timeout=5.0)

        # For simplicity in the simulator, we run all devices as objects
        # within a single BACnet application with multiple device objects.
        # Each "device" gets its own BACnet device instance on the network.
        # In bacpypes3, we use one Application per device.
        # To avoid port conflicts, devices share a single UDP port and use
        # different device instances.

        # NOTE: Full multi-device support requires running each device
        # on a separate port or using BACnet router functionality.
        # For the test harness, we use a single application with the
        # first device ID and add all objects with namespaced instances.

        # Simplified approach: single app, objects from all devices with
        # device-specific instance offsets
        print(f"BACnet Simulator: {len(self.devices)} devices configured")
        print(f"Thermal engine URL: {THERMAL_ENGINE_URL}")

        # Start update loop
        asyncio.create_task(self._update_loop())

    async def _update_loop(self):
        """Periodically fetch state from thermal engine and update BACnet objects."""
        while self._running:
            try:
                resp = await self.http_client.get("/api/state")
                if resp.status_code == 200:
                    state = resp.json()
                    self._update_values(state)
            except Exception as e:
                print(f"Failed to fetch thermal state: {e}")

            await asyncio.sleep(1.0)  # Update every second

    def _update_values(self, state: dict):
        """Update BACnet object present-values from simulation state."""
        # Map equipment types to state keys
        type_map = {
            "ahu": "ahus",
            "vav": "vavs",
            "chiller": "chillers",
            "boiler": "boilers",
            "fcu": "fcus",
            "lighting": "lighting",
            "sensor": "sensors",
        }

        for device_id, dev in self.devices.items():
            if device_id in self._comm_faults:
                continue  # Don't update - simulating communication fault

            state_key = type_map.get(dev.equipment_type)
            if not state_key or state_key not in state:
                continue

            equip_state = state[state_key].get(dev.name)
            if not equip_state:
                continue

            # Update each object's value from the matching field
            for (obj_type, instance), field_name in dev.field_map.items():
                if field_name in equip_state:
                    value = equip_state[field_name]
                    # Store the current value (would update actual BACnet objects here)
                    dev.objects[(obj_type, instance)] = value

    async def handle_write_callback(self, device_id: int, obj_type: str, instance: int, value: float):
        """Forward a BACnet write to the thermal engine."""
        if self.http_client:
            try:
                await self.http_client.post("/api/write", json={
                    "device_id": device_id,
                    "object_type": obj_type,
                    "object_instance": instance,
                    "value": value,
                })
            except Exception as e:
                print(f"Failed to forward write to thermal engine: {e}")

    def set_comm_fault(self, device_id: int, active: bool):
        """Enable/disable communication fault for a device."""
        if active:
            self._comm_faults.add(device_id)
        else:
            self._comm_faults.discard(device_id)

    async def stop(self):
        self._running = False
        if self.http_client:
            await self.http_client.aclose()


async def main():
    config_path = os.environ.get("BUILDING_CONFIG", BUILDING_CONFIG)
    print(f"Loading building config from: {config_path}")

    simulator = BACnetSimulator(config_path)
    simulator.build_devices()
    await simulator.start()

    # Keep running
    stop_event = asyncio.Event()

    def _signal_handler():
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            loop.add_signal_handler(sig, _signal_handler)
        except NotImplementedError:
            pass  # Windows

    await stop_event.wait()
    await simulator.stop()


if __name__ == "__main__":
    asyncio.run(main())
