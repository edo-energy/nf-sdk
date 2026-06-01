#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Defaults
CONFIG_FILE="${1:-default.yml}"
ACCELERATION="${2:-1}"

echo "============================================"
echo "  NF Gateway Test Harness"
echo "============================================"
echo ""
echo "  Config:       $CONFIG_FILE"
echo "  Acceleration: ${ACCELERATION}x"
echo ""

# Validate config exists
if [ ! -f "configs/$CONFIG_FILE" ]; then
    echo "ERROR: Config file configs/$CONFIG_FILE not found."
    echo "Available configs:"
    ls configs/*.yml 2>/dev/null || echo "  (none)"
    exit 1
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed or not in PATH."
    exit 1
fi

if ! docker compose version &> /dev/null; then
    echo "ERROR: Docker Compose V2 is required."
    exit 1
fi

# Export env vars for compose
export BUILDING_CONFIG_FILE="$CONFIG_FILE"
export TIME_ACCELERATION="$ACCELERATION"

echo "Building containers..."
docker compose build

echo ""
echo "Starting services..."
docker compose up -d

echo ""
echo "Waiting for services to become healthy..."

# Wait for simulator
echo -n "  Simulator: "
for i in $(seq 1 30); do
    if curl -sf http://localhost:8100/api/state > /dev/null 2>&1; then
        echo "ready"
        break
    fi
    if [ "$i" -eq 30 ]; then
        echo "TIMEOUT"
        echo "  Check logs: docker compose logs simulator"
    fi
    sleep 2
done

# Wait for NF
echo -n "  NF Gateway: "
for i in $(seq 1 60); do
    if curl -sf http://localhost:8080/api/v1/platform > /dev/null 2>&1; then
        echo "ready"
        break
    fi
    if [ "$i" -eq 60 ]; then
        echo "TIMEOUT"
        echo "  Check logs: docker compose logs nf"
    fi
    sleep 2
done

# Wait for time controller
echo -n "  Time Controller: "
for i in $(seq 1 15); do
    if curl -sf http://localhost:8200/api/time > /dev/null 2>&1; then
        echo "ready"
        break
    fi
    if [ "$i" -eq 15 ]; then
        echo "TIMEOUT"
    fi
    sleep 2
done

echo ""
echo "============================================"
echo "  Services Available:"
echo "============================================"
echo ""
echo "  NF Console:        http://localhost:8080"
echo "  Config UI:         http://localhost:3001"
echo "  Sim Dashboard:     http://localhost:3002"
echo "  Simulation API:    http://localhost:8100"
echo "  Time Controller:   http://localhost:8200"
echo "  edo-service:       http://localhost:3000"
echo ""
echo "  Acceleration: ${ACCELERATION}x"
echo ""
echo "To stop:  docker compose down"
echo "To logs:  docker compose logs -f [service]"
echo "============================================"
