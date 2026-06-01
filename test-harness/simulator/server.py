"""
FastAPI server for the thermal simulation engine.

Provides REST API + WebSocket for:
- Simulation state queries
- Configuration management
- Fault injection
- Time control
"""
import asyncio
import json
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from simulator.thermal_engine import ThermalSimulation, Fault


class FaultRequest(BaseModel):
    target_type: str  # "sensor", "equipment", "communication"
    target_name: str
    fault_type: str  # "freeze", "offset", "nan", "offline", "stuck"
    parameters: dict = {}
    scheduled_time: float | None = None


class WriteRequest(BaseModel):
    device_id: int
    object_type: str
    object_instance: int
    value: float


class TimeControlRequest(BaseModel):
    acceleration: int | None = None
    paused: bool | None = None


class WeatherOverride(BaseModel):
    outdoor_air_temp: float | None = None
    humidity: float | None = None
    wind_speed: float | None = None


# Globals
sim: ThermalSimulation | None = None
sim_task: asyncio.Task | None = None
paused: bool = False
ws_clients: set[WebSocket] = set()

CONFIG_PATH = "/config/building.yml"


async def sim_loop():
    """Main simulation loop - runs at accelerated time."""
    global sim, paused
    while True:
        if sim and not paused:
            sim.step()
            # Broadcast state to WebSocket clients
            state = sim.get_state()
            dead_clients = set()
            for ws in ws_clients:
                try:
                    await ws.send_json(state)
                except Exception:
                    dead_clients.add(ws)
            ws_clients.difference_update(dead_clients)

        # Sleep based on acceleration: real_sleep = timestep / acceleration
        accel = sim.acceleration if sim else 1
        sleep_time = (sim.timestep_seconds if sim else 60.0) / max(1, accel)
        await asyncio.sleep(sleep_time)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global sim, sim_task
    import os
    config_path = os.environ.get("BUILDING_CONFIG", CONFIG_PATH)
    sim = ThermalSimulation(config_path)
    sim_task = asyncio.create_task(sim_loop())
    yield
    sim_task.cancel()


app = FastAPI(title="Building Simulation Engine", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- REST Endpoints ---

@app.get("/api/state")
async def get_state():
    """Get full simulation state."""
    if not sim:
        raise HTTPException(503, "Simulation not initialized")
    return sim.get_state()


@app.get("/api/zones")
async def get_zones():
    """Get all zone states."""
    if not sim:
        raise HTTPException(503, "Simulation not initialized")
    return {name: {"temp": z.temp, "setpoint_cooling": z.setpoint_cooling,
                   "setpoint_heating": z.setpoint_heating, "hvac_load_btu": z.hvac_load_btu,
                   "occupancy": z.occupancy}
            for name, z in sim.zones.items()}


@app.get("/api/equipment")
async def get_equipment():
    """Get all equipment states."""
    if not sim:
        raise HTTPException(503, "Simulation not initialized")
    state = sim.get_state()
    return {k: state[k] for k in ["ahus", "vavs", "chillers", "boilers", "fcus", "lighting", "sensors"]}


@app.get("/api/time")
async def get_time():
    """Get virtual time info."""
    if not sim:
        raise HTTPException(503, "Simulation not initialized")
    return {
        "sim_time": sim.sim_time,
        "acceleration": sim.acceleration,
        "paused": paused,
        "timestep_seconds": sim.timestep_seconds,
    }


@app.post("/api/time")
async def set_time(req: TimeControlRequest):
    """Set time acceleration or pause."""
    global paused
    if not sim:
        raise HTTPException(503, "Simulation not initialized")
    if req.acceleration is not None:
        sim.acceleration = max(1, min(20, req.acceleration))
    if req.paused is not None:
        paused = req.paused
    return {"acceleration": sim.acceleration, "paused": paused}


@app.post("/api/weather")
async def set_weather(req: WeatherOverride):
    """Override weather conditions."""
    if not sim:
        raise HTTPException(503, "Simulation not initialized")
    if req.outdoor_air_temp is not None:
        sim.outdoor_temp = req.outdoor_air_temp
    if req.humidity is not None:
        sim.outdoor_humidity = req.humidity
    if req.wind_speed is not None:
        sim.wind_speed = req.wind_speed
    return {"outdoor_air_temp": sim.outdoor_temp, "humidity": sim.outdoor_humidity,
            "wind_speed": sim.wind_speed}


@app.get("/api/faults")
async def get_faults():
    """List active faults."""
    if not sim:
        raise HTTPException(503, "Simulation not initialized")
    return {fid: {"target_type": f.target_type, "target_name": f.target_name,
                  "fault_type": f.fault_type, "active": f.active, "parameters": f.parameters}
            for fid, f in sim.faults.items()}


@app.post("/api/faults")
async def add_fault(req: FaultRequest):
    """Inject a fault."""
    if not sim:
        raise HTTPException(503, "Simulation not initialized")
    fault_id = str(uuid.uuid4())[:8]
    fault = Fault(
        id=fault_id,
        target_type=req.target_type,
        target_name=req.target_name,
        fault_type=req.fault_type,
        parameters=req.parameters,
        scheduled_time=req.scheduled_time,
    )
    sim.add_fault(fault)
    return {"id": fault_id, "status": "active"}


@app.delete("/api/faults/{fault_id}")
async def remove_fault(fault_id: str):
    """Remove a fault."""
    if not sim:
        raise HTTPException(503, "Simulation not initialized")
    if fault_id not in sim.faults:
        raise HTTPException(404, f"Fault {fault_id} not found")
    sim.remove_fault(fault_id)
    return {"id": fault_id, "status": "removed"}


@app.post("/api/write")
async def handle_bacnet_write(req: WriteRequest):
    """Handle a BACnet write forwarded from the BACnet simulator."""
    if not sim:
        raise HTTPException(503, "Simulation not initialized")
    sim.handle_write(req.device_id, req.object_type, req.object_instance, req.value)
    return {"status": "ok"}


@app.get("/api/config")
async def get_config():
    """Get the current building configuration."""
    if not sim:
        raise HTTPException(503, "Simulation not initialized")
    return sim.config


@app.post("/api/config")
async def update_config(request: Request):
    """Hot-reload the simulation with a new building configuration."""
    global sim
    if not sim:
        raise HTTPException(503, "Simulation not initialized")
    config = await request.json()
    try:
        sim.reload(config)
    except Exception as e:
        raise HTTPException(400, f"Invalid configuration: {e}")
    return {"status": "ok", "zones": len(sim.zones)}


# --- WebSocket ---

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """Stream simulation state in real-time."""
    await ws.accept()
    ws_clients.add(ws)
    try:
        while True:
            # Keep connection alive, handle incoming messages
            data = await ws.receive_text()
            # Could handle commands via WS in the future
    except WebSocketDisconnect:
        ws_clients.discard(ws)
