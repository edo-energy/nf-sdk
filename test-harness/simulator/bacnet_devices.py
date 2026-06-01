"""
BACnet Device Simulator - bacpypes3 application entry point.

Creates a BACnet/IP device that exposes all simulated building equipment
points. Responds to Who-Is, ReadProperty, and ReadPropertyMultiple requests.
Values are sourced from the thermal simulation engine via HTTP polling.
"""
import argparse
import asyncio
import logging
import os
import socket

import yaml
import httpx

from bacpypes3.app import Application
from bacpypes3.primitivedata import ObjectIdentifier
from bacpypes3.local.analog import AnalogInputObject, AnalogOutputObject, AnalogValueObject
from bacpypes3.local.binary import BinaryInputObject, BinaryOutputObject, BinaryValueObject

_log = logging.getLogger(__name__)

THERMAL_ENGINE_URL = os.environ.get("THERMAL_ENGINE_URL", "http://localhost:8100")
BUILDING_CONFIG = os.environ.get("BUILDING_CONFIG", "/config/building.yml")
BACNET_PORT = int(os.environ.get("BACNET_PORT", "47808"))


# --- Writable object subclasses that forward writes to the thermal engine ---

class _WritableMixin:
    """Mixin that forwards presentValue writes to the thermal engine."""

    _write_callback = None  # set after construction: async fn(obj_id, value)

    async def write_property(self, attr, value, index=None, priority=None):
        await super().write_property(attr, value, index, priority)
        # attr may arrive as int (85) or string "presentValue"
        if attr == "presentValue" or attr == 85:
            if self._write_callback:
                resolved = self.presentValue
                try:
                    await self._write_callback(self.objectIdentifier, resolved)
                except Exception as e:
                    _log.warning(f"Write callback failed: {e}")


class WritableAnalogOutput(_WritableMixin, AnalogOutputObject):
    pass


class WritableAnalogValue(_WritableMixin, AnalogValueObject):
    pass


class WritableBinaryOutput(_WritableMixin, BinaryOutputObject):
    pass


class WritableBinaryValue(_WritableMixin, BinaryValueObject):
    pass

# BACnet object class map
OBJ_CLASS_MAP = {
    "ai": AnalogInputObject,
    "ao": WritableAnalogOutput,
    "av": WritableAnalogValue,
    "bi": BinaryInputObject,
    "bo": WritableBinaryOutput,
    "bv": WritableBinaryValue,
}

# Object profile definitions: (type_key, instance_offset, name_suffix, units, sim_field)
PROFILES = {
    "ahu": lambda n: [
        ("ai", 1, f"{n} Supply Air Temp", "degreesFahrenheit", "supply_air_temp"),
        ("ai", 2, f"{n} Return Air Temp", "degreesFahrenheit", "return_air_temp"),
        ("ai", 3, f"{n} Mixed Air Temp", "degreesFahrenheit", "mixed_air_temp"),
        ("bi", 1, f"{n} Supply Fan Status", None, "supply_fan_status"),
        ("ao", 1, f"{n} Supply Fan Speed", "percent", "supply_fan_speed_pct"),
        ("ao", 2, f"{n} Cooling Valve", "percent", "cooling_valve_pct"),
        ("ao", 3, f"{n} Heating Valve", "percent", "heating_valve_pct"),
        ("ao", 4, f"{n} OA Damper", "percent", "oa_damper_pct"),
        ("ai", 4, f"{n} Filter DP", "inchesOfWater", "filter_dp"),
        ("ai", 5, f"{n} Duct Static", "inchesOfWater", "duct_static_pressure"),
    ],
    "vav": lambda n: [
        ("ai", 1, f"{n} Zone Temp", "degreesFahrenheit", "zone_temp"),
        ("av", 1, f"{n} Zone Temp SP", "degreesFahrenheit", "zone_temp_setpoint"),
        ("ao", 1, f"{n} Damper Pos", "percent", "damper_position_pct"),
        ("ao", 2, f"{n} Reheat Vlv", "percent", "reheat_valve_pct"),
        ("ai", 2, f"{n} Airflow", "cubicFeetPerMinute", "airflow_cfm"),
        ("bv", 1, f"{n} Occupied", None, "occupied"),
    ],
    "chiller": lambda n: [
        ("ai", 1, f"{n} CHW Supply", "degreesFahrenheit", "chw_supply_temp"),
        ("ai", 2, f"{n} CHW Return", "degreesFahrenheit", "chw_return_temp"),
        ("ai", 3, f"{n} Cond Enter", "degreesFahrenheit", "condenser_entering_temp"),
        ("ai", 4, f"{n} Load", "percent", "load_pct"),
        ("bo", 1, f"{n} Enable", None, "enabled"),
        ("av", 1, f"{n} Setpoint", "degreesFahrenheit", "setpoint"),
    ],
    "boiler": lambda n: [
        ("ai", 1, f"{n} HW Supply", "degreesFahrenheit", "hw_supply_temp"),
        ("ai", 2, f"{n} HW Return", "degreesFahrenheit", "hw_return_temp"),
        ("ai", 3, f"{n} Firing Rate", "percent", "firing_rate_pct"),
        ("bo", 1, f"{n} Enable", None, "enabled"),
        ("av", 1, f"{n} Setpoint", "degreesFahrenheit", "setpoint"),
    ],
    "fcu": lambda n: [
        ("ai", 1, f"{n} Zone Temp", "degreesFahrenheit", "zone_temp"),
        ("ao", 1, f"{n} Fan Speed", "noUnits", "fan_speed"),
        ("ao", 2, f"{n} Valve Pos", "percent", "valve_position_pct"),
        ("ai", 2, f"{n} Disch Temp", "degreesFahrenheit", "discharge_temp"),
    ],
    "lighting": lambda n: [
        ("ao", 1, f"{n} Level", "percent", "level_pct"),
        ("bi", 1, f"{n} Occupancy", None, "occupancy_detected"),
        ("bv", 1, f"{n} Sched Override", None, "schedule_override"),
    ],
    "sensor": lambda n: [
        ("ai", 1, f"{n}", "noUnits", "value"),
    ],
}

SENSOR_UNITS = {
    "oat": "degreesFahrenheit",
    "humidity": "percentRelativeHumidity",
    "co2": "partsPerMillion",
    "power_meter": "kilowatts",
    "pressure": "inchesOfWater",
}


def get_local_ip():
    """Get the container's IP on the Docker network."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "0.0.0.0"
    finally:
        s.close()


class DeviceSimulator:
    """
    Creates a single BACnet/IP device with all simulated equipment objects.
    Objects are namespaced by device_id to avoid instance collisions.
    """

    def __init__(self, config_path: str):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        self.app: Application | None = None
        # Maps (object_type_str, global_instance) -> (equip_type, equip_name, field_name)
        self.obj_field_map: dict[tuple[str, int], tuple[str, str, str]] = {}
        self.http_client: httpx.AsyncClient | None = None

    async def start(self):
        """Create the BACnet application and all objects."""
        self.http_client = httpx.AsyncClient(base_url=THERMAL_ENGINE_URL, timeout=5.0)

        local_ip = get_local_ip()
        print(f"  BACnet binding to 0.0.0.0:{BACNET_PORT} (local IP: {local_ip})")

        # Bind to 0.0.0.0 so we receive both unicast AND broadcast traffic.
        # In Docker, a socket bound to a specific IP won't receive subnet broadcasts.
        args = argparse.Namespace(
            name="Building Simulator",
            instance=1000,
            network=0,
            address=f"0.0.0.0:{BACNET_PORT}",
            vendoridentifier=999,
            foreign=None,
            bbmd=None,
        )
        self.app = Application.from_args(args)

        # Add objects from all equipment
        equip = self.config.get("equipment", {})
        type_keys = {
            "ahus": "ahu", "vavs": "vav", "chillers": "chiller",
            "boilers": "boiler", "fcus": "fcu", "lighting": "lighting",
            "sensors": "sensor",
        }

        total_objects = 0
        for config_key, equip_type in type_keys.items():
            for item in equip.get(config_key, []):
                device_id = item["device_id"]
                name = item["name"]

                profile_fn = PROFILES[equip_type]
                objects = profile_fn(name)

                if equip_type == "sensor":
                    stype = item.get("type", "oat")
                    unit = SENSOR_UNITS.get(stype, "noUnits")
                    objects = [("ai", 1, name, unit, "value")]

                for obj_type_key, local_inst, obj_name, units, field in objects:
                    # Global instance = device_id * 100 + local_instance
                    global_inst = device_id * 100 + local_inst
                    obj_class = OBJ_CLASS_MAP[obj_type_key]

                    # Map type keys to BACnet object type tuples
                    type_map = {
                        "ai": "analog-input", "ao": "analog-output", "av": "analog-value",
                        "bi": "binary-input", "bo": "binary-output", "bv": "binary-value",
                    }
                    bacnet_type = type_map[obj_type_key]

                    kwargs = {
                        "objectIdentifier": (bacnet_type, global_inst),
                        "objectName": obj_name,
                    }
                    if obj_type_key in ("ai", "ao", "av"):
                        kwargs["presentValue"] = 0.0
                    else:
                        kwargs["presentValue"] = "inactive"

                    obj = obj_class(**kwargs)
                    # Wire write callback for writable objects
                    if hasattr(obj, '_write_callback'):
                        obj._write_callback = self._handle_bacnet_write
                    self.app.add_object(obj)
                    self.obj_field_map[(bacnet_type, global_inst)] = (equip_type, name, field)
                    total_objects += 1

        print(f"BACnet Simulator: device 1000 with {total_objects} objects")

        # Start polling thermal engine for value updates
        asyncio.create_task(self._poll_thermal_engine())

    async def _handle_bacnet_write(self, object_identifier, value):
        """Forward a BACnet write to the thermal engine."""
        obj_type = str(object_identifier[0])
        global_inst = int(object_identifier[1])
        device_id = global_inst // 100
        local_inst = global_inst % 100

        # Convert binary active/inactive to numeric
        if isinstance(value, str):
            value = 1.0 if value == "active" else 0.0
        else:
            value = float(value)

        _log.info(f"BACnet write: {obj_type}:{global_inst} = {value} -> device {device_id} inst {local_inst}")
        await self.http_client.post("/api/write", json={
            "device_id": device_id,
            "object_type": obj_type,
            "object_instance": local_inst,
            "value": value,
        })

    async def _poll_thermal_engine(self):
        """Poll thermal engine and update BACnet object presentValues."""
        state_key_map = {
            "ahu": "ahus", "vav": "vavs", "chiller": "chillers",
            "boiler": "boilers", "fcu": "fcus", "lighting": "lighting",
            "sensor": "sensors",
        }

        while True:
            try:
                resp = await self.http_client.get("/api/state")
                if resp.status_code == 200:
                    state = resp.json()
                    for (bacnet_type, inst), (equip_type, equip_name, field_name) in self.obj_field_map.items():
                        state_key = state_key_map[equip_type]
                        equip_state = state.get(state_key, {}).get(equip_name, {})
                        if not equip_state or field_name not in equip_state:
                            continue

                        value = equip_state[field_name]
                        obj = self.app.get_object_id(ObjectIdentifier((bacnet_type, inst)))
                        if obj is None:
                            continue

                        if bacnet_type in ("binary-input", "binary-output", "binary-value"):
                            obj.presentValue = "active" if value else "inactive"
                        else:
                            obj.presentValue = float(value) if value is not None else 0.0
            except Exception as e:
                _log.warning(f"Thermal engine poll error: {e}")

            await asyncio.sleep(1.0)

    async def stop(self):
        if self.http_client:
            await self.http_client.aclose()


async def main():
    config_path = os.environ.get("BUILDING_CONFIG", BUILDING_CONFIG)
    print(f"BACnet Device Simulator starting...")
    print(f"  Config: {config_path}")
    print(f"  Thermal Engine: {THERMAL_ENGINE_URL}")

    sim = DeviceSimulator(config_path)
    await sim.start()

    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        await sim.stop()


if __name__ == "__main__":
    asyncio.run(main())
