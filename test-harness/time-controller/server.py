"""
Time Controller Service for NF Gateway Test Harness.

Manages libfaketime offset files for all containers that need
accelerated time. Provides REST API for time control.
"""
import asyncio
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


class TimeState(BaseModel):
    acceleration: int = 1
    paused: bool = False
    start_wall_time: float = 0.0
    start_sim_time: float = 0.0
    current_sim_time: float = 0.0
    offset_seconds: float = 0.0


class TimeControlRequest(BaseModel):
    acceleration: int | None = None
    paused: bool | None = None
    jump_seconds: float | None = None  # Jump forward by N seconds of sim time


# Globals
state = TimeState()
FAKETIME_DIR = os.environ.get("FAKETIME_DIR", "/faketime")
UPDATE_INTERVAL = 0.5  # seconds between offset file updates

controller_task: asyncio.Task | None = None


def write_faketime_offset(offset_seconds: float):
    """Write the faketime offset to the shared file."""
    faketime_path = Path(FAKETIME_DIR) / "offset"
    try:
        # libfaketime format: +Xs or -Xs for offset in seconds
        sign = "+" if offset_seconds >= 0 else ""
        faketime_path.write_text(f"{sign}{int(offset_seconds)}\n")
    except OSError as e:
        print(f"Warning: Could not write faketime offset: {e}")


async def time_controller_loop():
    """Continuously advance the faketime offset based on acceleration."""
    global state
    last_update = time.time()

    while True:
        now = time.time()
        dt_real = now - last_update
        last_update = now

        if not state.paused and state.acceleration > 1:
            # Accumulate extra time offset
            # If acceleration=10, for every 1 real second, we add 9 extra seconds
            extra_seconds = dt_real * (state.acceleration - 1)
            state.offset_seconds += extra_seconds
            write_faketime_offset(state.offset_seconds)

        # Calculate current sim time
        elapsed_real = now - state.start_wall_time
        state.current_sim_time = state.start_sim_time + elapsed_real + state.offset_seconds

        await asyncio.sleep(UPDATE_INTERVAL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global state, controller_task

    state.start_wall_time = time.time()
    state.start_sim_time = time.time()
    state.acceleration = int(os.environ.get("TIME_ACCELERATION", "1"))

    # Ensure faketime directory exists
    Path(FAKETIME_DIR).mkdir(parents=True, exist_ok=True)
    write_faketime_offset(0)

    controller_task = asyncio.create_task(time_controller_loop())
    yield
    controller_task.cancel()


app = FastAPI(title="Time Controller", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/time")
async def get_time():
    """Get current virtual time state."""
    return {
        "acceleration": state.acceleration,
        "paused": state.paused,
        "sim_time": state.current_sim_time,
        "wall_time": time.time(),
        "offset_seconds": state.offset_seconds,
        "start_time": state.start_sim_time,
    }


@app.post("/api/time")
async def set_time(req: TimeControlRequest):
    """Control time acceleration."""
    global state

    if req.acceleration is not None:
        state.acceleration = max(1, min(20, req.acceleration))

    if req.paused is not None:
        state.paused = req.paused

    if req.jump_seconds is not None:
        state.offset_seconds += req.jump_seconds
        write_faketime_offset(state.offset_seconds)

    return {
        "acceleration": state.acceleration,
        "paused": state.paused,
        "offset_seconds": state.offset_seconds,
    }


@app.post("/api/time/reset")
async def reset_time():
    """Reset time offset to zero."""
    global state
    state.offset_seconds = 0.0
    state.start_wall_time = time.time()
    state.start_sim_time = time.time()
    write_faketime_offset(0)
    return {"status": "reset", "offset_seconds": 0.0}
