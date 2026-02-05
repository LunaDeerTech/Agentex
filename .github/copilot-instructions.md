# Agentex Development Guide

## Architecture
AI Agent platform: Vue 3 + TypeScript frontend ↔ FastAPI async backend ↔ PostgreSQL/Redis/Milvus.

```
frontend/src/       → Vue 3 SFCs, Pinia stores, Axios API layer
backend/app/api/    → FastAPI routers (thin, delegate to services)
backend/app/services/ → Business logic (class-based, injected AsyncSession)
backend/app/models/ → SQLAlchemy 2.0 ORM (UUID PKs, soft delete via BaseModel)
backend/app/integrations/llm/ → LLM provider clients (OpenAI, Anthropic)
```

## Key Commands
```bash
make dev-backend          # uvicorn --reload (port 8000)
make dev-frontend         # npm run dev (port 5173)
make test-backend         # pytest tests/ -v
make lint-backend         # ruff check + mypy
cd backend && alembic upgrade head   # run migrations
```

## Backend Patterns

### Layered Architecture
Routers → Services → Models. **Never query DB directly in routers.**
```python
# api/v1/auth.py - router instantiates service with session
auth_service = AuthService(db)
result = await auth_service.register(user_data)
```

### Models (see backend/app/models/base.py)
- Inherit from `BaseModel` → gets UUID `id`, `created_at`, `updated_at`, soft delete (`is_deleted`, `deleted_at`)
- Tables: plural snake_case (`users`, `api_keys`, `user_roles`)
- Always use `DateTime(timezone=True)` for datetime columns

### Schemas (see backend/app/schemas/)
- Pydantic v2 models for request/response validation
- Use `Field(...)` for constraints, `@field_validator` for custom validation
- Return `model_validate(orm_instance)` from services

### Standardized API Response Format
```python
{"code": 0, "message": "success", "data": {...}}  # success
{"code": 40100, "message": "...", "data": null}   # error
```
Error codes: 401xx auth, 403xx permission, 404xx not found, 500xx server.
Raise `AppError(code, message, status_code)` for business errors.

### Auth Dependencies (see backend/app/api/deps.py)
```python
user: User = Depends(get_current_user)           # JWT or X-API-Key header
user: User = Depends(get_current_active_user)    # + is_active check
@router.post("/", dependencies=[Depends(require_permissions("items:create"))])
```

### Testing (see backend/tests/conftest.py)
Use `pytest-asyncio`. Key fixtures: `client` (AsyncClient), `db` (AsyncSession), `test_user`, `default_role`.

### LLM Integration (see backend/app/integrations/llm/)
Providers extend `BaseLLMClient`. Use `LLMMessage`, `LLMResponse`, `LLMStreamChunk` dataclasses. Factory pattern via `factory.py`.

## Frontend Patterns

### API Layer (see frontend/src/api/request.ts)
- All calls via Axios instance with auth interceptor
- Responses auto-unwrap `data` field; `code ≠ 0` → `Promise.reject`
- Token in localStorage, injected via `useAuthStore`

### Stores (see frontend/src/stores/)
- Pinia Composition API: `defineStore('name', () => { ... })`
- Domain stores: `auth`, `session`, `user`, `models`

### Components
- Always `<script setup lang="ts">`
- UI primitives in `src/components/ui/` (shadcn-vue/radix-vue style with `class-variance-authority`)

## Database Migrations
```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head      # apply
alembic downgrade -1      # rollback
```

## Design Docs (read before new features)
- [docs/APIDesign.md](docs/APIDesign.md) - endpoints, error codes, pagination
- [docs/DatabaseDesign.md](docs/DatabaseDesign.md) - full schema, naming conventions
- [docs/BackendDesign.md](docs/BackendDesign.md) - service interfaces
- [docs/FrontendDesign.md](docs/FrontendDesign.md) - UI specs, color palette
