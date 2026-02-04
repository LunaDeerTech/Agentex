# Agentex Development Guide

## Architecture
Web AI Agent platform: Vue 3 + TypeScript frontend ↔ FastAPI async backend ↔ PostgreSQL/Redis/Milvus.

```
frontend/src/       → Vue 3 SFCs, Pinia stores, Axios API layer
backend/app/api/    → FastAPI routers (thin, delegate to services)
backend/app/services/ → Business logic (class-based, injected AsyncSession)
backend/app/models/ → SQLAlchemy 2.0 ORM (UUID PKs, soft delete via BaseModel)
```

## Key Commands
```bash
make dev-backend          # uvicorn app.main:app --reload (port 8000)
make dev-frontend         # npm run dev (port 5173)
make test-backend         # pytest tests/ -v
make lint-backend         # ruff check + mypy
cd backend && alembic upgrade head   # run migrations
```

## Backend Patterns

### Layered Architecture
Routers → Services → Models. **Never call DB directly in routers.**
```python
# In api/v1/auth.py - router instantiates service
auth_service = AuthService(db)
result = await auth_service.register(user_data)
```

### Model Conventions (see backend/app/models/base.py)
- Inherit from `BaseModel` for UUID pk + timestamps + soft delete
- Tables: plural, snake_case (`users`, `api_keys`, `user_roles`)
- All datetime fields use `DateTime(timezone=True)`

### Response/Error Format (see backend/app/core/exceptions.py)
```python
{"code": 0, "message": "success", "data": {...}}  # success
{"code": 40100, "message": "...", "data": null}   # 401 error
```
Use `AppError(code, message, status_code)` for business errors.

### Auth Dependencies (see backend/app/api/deps.py)
```python
user: User = Depends(get_current_user)         # JWT or API key
user: User = Depends(get_current_active_user)  # + is_active check
require_permissions("module", "action")         # decorator for RBAC
```

### Testing (see backend/tests/conftest.py)
Use `pytest-asyncio`. Key fixtures: `client` (AsyncClient), `db` (AsyncSession), `test_user`.

## Frontend Patterns

### API Layer (see frontend/src/api/request.ts)
- All calls go through Axios instance with auth interceptor
- Responses unwrap `data` field; code ≠ 0 → Promise.reject
- Token stored in localStorage, injected via `useAuthStore`

### Stores (see frontend/src/stores/auth.ts)
- Pinia with Composition API: `defineStore('name', () => { ... })`
- One store per domain: `auth`, `session`, `user`

### Components
- Use `<script setup lang="ts">` exclusively
- UI primitives in `src/components/ui/` (shadcn-vue style)

## Database Migrations
```bash
cd backend
alembic revision --autogenerate -m "description"  # create migration
alembic upgrade head                              # apply
alembic downgrade -1                              # rollback one
```

## Design Docs Reference
Read before implementing new features:
- [docs/APIDesign.md](docs/APIDesign.md) - endpoint specs, error codes
- [docs/DatabaseDesign.md](docs/DatabaseDesign.md) - full schema reference
- [docs/BackendDesign.md](docs/BackendDesign.md) - service interfaces
- [docs/FrontendDesign.md](docs/FrontendDesign.md) - UI/UX specs, color palette
