# Agentex - AI Agent Platform Development Guide

## Project Overview
Agentex is a Web AI Agent platform with MCP (Model Context Protocol) integration, RAG knowledge bases, SKILL management, and a rule engine. The project is currently in the **design/documentation phase** - implementation has not yet started.

## Architecture Summary
```
Frontend (Vue 3 + TS + shadcn-vue + Inspira UI)
    ↓ HTTP REST / AG-UI (SSE)
Backend (FastAPI + SQLAlchemy 2.0 async)
    ↓                    ↓
PostgreSQL + Redis   External Services (LLM APIs, MCP Servers)
    ↓
Milvus (Vector DB for RAG)
```

## Tech Stack & Versions
| Layer | Stack |
|-------|-------|
| Backend | Python 3.11+, FastAPI 0.110+, SQLAlchemy 2.0 (async), Pydantic 2.0 |
| Frontend | Vue 3.4+, TypeScript 5.3+, Vite 5.0+, Pinia, shadcn-vue, Inspira UI |
| Database | PostgreSQL 15+, Redis 7.0+, Milvus 2.3+ |
| Communication | AG-UI protocol (SSE), WebSocket for WS-MCP |
| UI Design | Linear 极简风 (Dark theme, 1px borders, Inter/JetBrains Mono fonts) |

## Project Structure (Target)
```
agentex/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routers (RESTful endpoints)
│   │   ├── core/         # Config, security, dependencies
│   │   ├── models/       # SQLAlchemy ORM models (UUID PKs, soft delete)
│   │   ├── schemas/      # Pydantic request/response schemas
│   │   ├── services/     # Business logic layer
│   │   ├── agents/       # Agent implementations (ReAct, AgenticRAG, etc.)
│   │   └── utils/        # Helpers and utilities
│   ├── tests/
│   └── main.py
├── frontend/
│   ├── src/
│   │   ├── api/          # Axios API client functions
│   │   ├── components/   # Reusable Vue components
│   │   ├── composables/  # Vue composition functions
│   │   ├── stores/       # Pinia state stores
│   │   ├── views/        # Page-level components
│   │   └── router/       # Vue Router config
└── docs/                 # Design documentation (reference these!)
```

## Key Design Patterns

### Backend Conventions
- **Layered architecture**: API → Service → Data Access (no direct DB calls in routers)
- **All async**: Use `async/await` throughout, `AsyncSession` for DB
- **UUIDs for PKs**: All tables use UUID primary keys, not auto-increment
- **Soft delete**: Include `is_deleted` field on entities
- **Standard timestamps**: Always include `created_at`, `updated_at`
- **Response format**: `{ "code": 0, "message": "success", "data": {...} }`
- **Error codes**: 40xxx (client), 50xxx (server) - see [APIDesign.md](docs/APIDesign.md#14-错误码定义)

### Frontend Conventions
- **Composition API + TypeScript**: All components use `<script setup lang="ts">`
- **Linear 极简风格**: Dark theme with 1px borders, no shadows for elevation
- **shadcn-vue + Inspira UI**: Base components from shadcn-vue, sci-fi effects from Inspira UI
- **Color palette**: Follow Obsidian palette in [FrontendDesign.md](docs/FrontendDesign.md#13-色彩规范)
- **Typography**: Inter for UI text, JetBrains Mono for code/agent output
- **Icons**: Lucide with `stroke-width: 1.5px`
- **Pinia stores**: One store per domain (user, session, model, mcp, etc.)
- **API layer**: Wrap all Axios calls in `src/api/` modules

### Database Naming
- Tables: lowercase, plural, underscore-separated (`chat_sessions`, `mcp_connections`)
- Columns: lowercase, underscore-separated (`user_id`, `created_at`)
- Foreign keys: `<singular_table>_id` pattern
- See full conventions in [DatabaseDesign.md](docs/DatabaseDesign.md#12-命名规范)

## Core Modules & Services

| Module | Purpose | Key Files |
|--------|---------|-----------|
| UserService | Auth, JWT, API keys | `services/user_service.py` |
| SessionService | Chat sessions & messages | `services/session_service.py` |
| ModelService | LLM provider configs | `services/model_service.py` |
| MCPService | Standard + WS-MCP clients | `services/mcp_service.py` |
| SkillService | SKILL.md parsing & execution | `services/skill_service.py` |
| RAGService | Knowledge base + vector search | `services/rag_service.py` |
| RuleService | Event-triggered automation | `services/rule_service.py` |
| AgentService | Agent orchestration (ReAct, etc.) | `services/agent_service.py` |

## Protocol-Specific Notes

### AG-UI Protocol (Frontend ↔ Backend)
- Uses **Server-Sent Events (SSE)** for streaming agent responses
- Events: `TEXT_MESSAGE_START`, `TEXT_MESSAGE_CONTENT`, `TOOL_CALL_START`, `TOOL_CALL_END`, etc.
- See [SystemArchitecture.md](docs/SystemArchitecture.md) section 3 for event types

### WS-MCP Protocol (Backend ↔ MCP Servers)
- WebSocket-based JSON-RPC 2.0 with auth wrapper
- Message types: `auth`, `message`, `ping`, `pong`, `error`, `close`
- See full protocol spec in [CustomizeWsMessageProcotol.md](docs/CustomizeWsMessageProcotol.md)

## Development Commands
```bash
# Backend
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Documentation Reference
All design docs are in `docs/` - **read these before implementing**:
- [APIDesign.md](docs/APIDesign.md) - REST API specifications with examples
- [DatabaseDesign.md](docs/DatabaseDesign.md) - All table schemas
- [BackendDesign.md](docs/BackendDesign.md) - Service interfaces and business rules
- [FrontendDesign.md](docs/FrontendDesign.md) - UI specs and component breakdown
- [AIPrompts.md](docs/AIPrompts.md) - Prompt templates for common dev tasks
