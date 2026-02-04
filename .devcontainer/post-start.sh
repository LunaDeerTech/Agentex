#!/bin/bash
# Post-start script for Agentex DevContainer
# This script runs every time the container starts

set -e

echo "=========================================="
echo "Agentex DevContainer Starting..."
echo "=========================================="

# Fix permissions for vscode user directories (in case volume was created with wrong permissions)
echo "🔧 Fixing vscode user directory permissions..."
if [ -d "/home/vscode/.vscode-server" ]; then
    sudo chown -R vscode:vscode /home/vscode/.vscode-server 2>/dev/null || true
    chmod -R 755 /home/vscode/.vscode-server 2>/dev/null || true
fi

# Wait for services to be ready
echo "⏳ Waiting for services..."

# Wait for PostgreSQL
echo -n "  PostgreSQL: "
until pg_isready -h postgres -p 5432 -U agentex -q 2>/dev/null; do
    echo -n "."
    sleep 1
done
echo " ✓"

# Wait for Redis
echo -n "  Redis: "
until redis-cli -h redis ping >/dev/null 2>&1; do
    echo -n "."
    sleep 1
done
echo " ✓"

# Wait for Milvus (with timeout)
echo -n "  Milvus: "
MILVUS_READY=false
for i in {1..30}; do
    if curl -s http://milvus-standalone:9091/healthz >/dev/null 2>&1; then
        MILVUS_READY=true
        break
    fi
    echo -n "."
    sleep 2
done
if [ "$MILVUS_READY" = true ]; then
    echo " ✓"
else
    echo " ⚠ (may still be starting)"
fi

echo ""
echo "=========================================="
echo "✅ All services ready!"
echo "=========================================="
echo ""
echo "Quick commands:"
echo "  make dev-backend   - Start backend server"
echo "  make dev-frontend  - Start frontend server"
echo "  make dev           - Start both servers"
echo "  make test          - Run all tests"
echo ""
