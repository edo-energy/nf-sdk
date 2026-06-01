"""
Simulator package entry point.
Runs both the thermal engine API server and the BACnet device simulator.
"""
import asyncio
import multiprocessing
import os
import sys
import uvicorn


def run_thermal_server():
    """Run the thermal simulation FastAPI server."""
    uvicorn.run(
        "simulator.server:app",
        host="0.0.0.0",
        port=8100,
        log_level="info",
    )


def run_bacnet_sim():
    """Run the BACnet device simulator."""
    from simulator.bacnet_devices import main
    asyncio.run(main())


if __name__ == "__main__":
    # Run both processes
    thermal_proc = multiprocessing.Process(target=run_thermal_server, daemon=True)
    thermal_proc.start()

    # Give thermal server time to start
    import time
    time.sleep(3)

    # Run BACnet sim in main process
    run_bacnet_sim()
