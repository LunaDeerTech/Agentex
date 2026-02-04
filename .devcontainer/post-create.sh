#!/bin/bash
# Post-create script for Agentex DevContainer
# This script runs once after the container is created

set -e

echo "=========================================="
echo "Agentex DevContainer Post-Create Setup"
echo "=========================================="

# Navigate to workspace
cd /workspace

# Install backend dependencies
echo ""
echo "📦 Installing Python dependencies..."
cd /workspace/backend
pip install --upgrade pip
pip install -r requirements.txt -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple

# Install development tools
echo ""
echo "🔧 Installing Python development tools..."
pip install pytest pytest-asyncio pytest-cov httpx black isort ruff mypy  -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple

# Install frontend dependencies
echo ""
echo "📦 Installing Node.js dependencies..."
cd /workspace/frontend
npm install

# Create .env file from example if it doesn't exist
echo ""
echo "⚙️ Setting up environment files..."
cd /workspace
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    cp .env.example .env
    echo "Created .env from .env.example"
fi

# Set up git configuration
echo ""
echo "🔐 Setting up Git..."
git config --global --add safe.directory /workspace

# Print success message
echo ""
echo "=========================================="
echo "✅ DevContainer setup complete!"
echo "=========================================="
echo ""
echo "Available services:"
echo "  - PostgreSQL: localhost:5432"
echo "  - Redis: localhost:6379"
echo "  - Milvus: localhost:19530"
echo "  - MinIO Console: localhost:9001"
echo ""
echo "To start development:"
echo "  Backend:  cd backend && uvicorn app.main:app --reload --host 0.0.0.0"
echo "  Frontend: cd frontend && npm run dev"
echo ""
