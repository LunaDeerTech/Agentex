# Agentex Backend

AI Agent Platform with MCP Integration, RAG Knowledge Bases, and Rule Engine.

## Tech Stack

- **Framework**: FastAPI 0.110+
- **Python**: 3.11+
- **Database**: PostgreSQL 15+ with SQLAlchemy 2.0 (async)
- **Cache**: Redis 7.0+
- **Migrations**: Alembic
- **Validation**: Pydantic 2.0

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7.0+

### Installation

1. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate  # Windows
```

2. Install dependencies:

```bash
pip install -e ".[dev]"
# or
pip install -r requirements.txt
```

3. Configure environment:

```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Create the database:

```bash
createdb agentex
```

5. Run the application:

```bash
uvicorn app.main:app --reload
```

### Available Endpoints

- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **Readiness Check**: http://localhost:8000/health/ready
- **Liveness Check**: http://localhost:8000/health/live

## Project Structure

```
backend/
├── app/
│   ├── api/              # FastAPI routers
│   │   └── health.py     # Health check endpoints
│   ├── core/             # Core configuration
│   │   ├── config.py     # Settings management
│   │   ├── database.py   # Database connection
│   │   ├── redis.py      # Redis connection
│   │   └── logging.py    # Structured logging
│   ├── models/           # SQLAlchemy ORM models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   └── main.py           # Application entry point
├── tests/                # Test files
├── alembic/              # Database migrations
├── pyproject.toml        # Project configuration
├── requirements.txt      # Dependencies
└── .env.example          # Environment template
```

## Development

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Linting
ruff check .

# Formatting
ruff format .

# Type checking
mypy app
```
