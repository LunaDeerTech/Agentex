# User Authentication Models

This directory contains SQLAlchemy ORM models for user authentication and authorization using RBAC (Role-Based Access Control).

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER AUTHENTICATION SCHEMA                     │
└─────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │    users     │
    ├──────────────┤
    │ id (PK)      │───┐
    │ username     │   │
    │ email        │   │
    │ password_hash│   │
    │ is_active    │   │
    │ is_superuser │   │
    │ is_deleted   │   │
    │ created_at   │   │
    │ updated_at   │   │
    └──────────────┘   │
                       │
                       │ N:M through user_roles
                       │
    ┌──────────────────┼────────────────┐
    │                  │                │
    │          ┌───────▼────────┐       │
    │          │  user_roles    │       │
    │          ├────────────────┤       │
    │          │ id (PK)        │       │
    │      ┌───│ user_id (FK)   │       │
    │      │   │ role_id (FK)   │───┐   │
    │      │   │ created_at     │   │   │
    │      │   └────────────────┘   │   │
    │      │                        │   │
    │      │                        │   │
    │ ┌────▼─────────┐         ┌───▼───────────┐
    │ │    roles     │         │  permissions  │
    │ ├──────────────┤         ├───────────────┤
    │ │ id (PK)      │         │ id (PK)       │
    │ │ name         │         │ module        │
    │ │ display_name │         │ action        │
    │ │ description  │         │ name          │
    │ │ is_system    │         │ description   │
    │ │ is_deleted   │         │ created_at    │
    │ │ created_at   │         └───────────────┘
    │ │ updated_at   │                 │
    │ └──────────────┘                 │
    │         │                        │
    │         │ N:M through role_permissions
    │         │                        │
    │         └────────┬───────────────┘
    │                  │
    │          ┌───────▼────────────┐
    │          │ role_permissions   │
    │          ├────────────────────┤
    │          │ id (PK)            │
    │          │ role_id (FK)       │
    │          │ permission_id (FK) │
    │          │ created_at         │
    └──────────└────────────────────┘
```

## Models

### User
- **File**: `user.py`
- **Table**: `users`
- **Description**: Stores user account information and credentials

**Fields**:
- `id`: UUID primary key
- `username`: Unique username (max 50 chars)
- `email`: Unique email address (max 255 chars)
- `hashed_password`: Bcrypt hashed password
- `avatar_url`: Optional profile picture URL
- `is_active`: Account active status
- `is_superuser`: Superuser flag
- `is_deleted`: Soft delete flag
- `last_login_at`: Last login timestamp
- `created_at`, `updated_at`: Auto-managed timestamps

**Relationships**:
- Many-to-many with `Role` through `user_roles` table

### Role
- **File**: `role.py`
- **Table**: `roles`
- **Description**: Defines user roles for access control

**Fields**:
- `id`: UUID primary key
- `name`: Unique role identifier (e.g., "admin", "user")
- `display_name`: Human-readable role name
- `description`: Role description
- `is_system`: System role flag (cannot be deleted)
- `is_deleted`: Soft delete flag
- `created_at`, `updated_at`: Auto-managed timestamps

**Relationships**:
- Many-to-many with `User` through `user_roles` table
- Many-to-many with `Permission` through `role_permissions` table

**Default Roles**:
- `admin`: 超级管理员 - All permissions
- `manager`: 管理员 - User and configuration management
- `developer`: 开发者 - Resource and rule management
- `user`: 普通用户 - Basic chat/agent usage only

### Permission
- **File**: `permission.py`
- **Table**: `permissions`
- **Description**: Defines granular permissions for resources and actions

**Fields**:
- `id`: UUID primary key
- `module`: Module/resource name (e.g., "models", "mcp")
- `action`: Action type (e.g., "view", "create", "edit", "delete")
- `name`: Unique permission identifier (format: `module:action`)
- `description`: Permission description
- `created_at`: Creation timestamp

**Relationships**:
- Many-to-many with `Role` through `role_permissions` table

**Permission Modules**:
- `users`: User management
- `roles`: Role management
- `models`: LLM model configuration
- `mcp`: MCP connection management
- `knowledge`: Knowledge base management
- `skills`: SKILL workflow management
- `rules`: Rule engine management
- `chat`: Chat session management

### UserRole
- **File**: `role.py`
- **Table**: `user_roles`
- **Description**: Association table linking users to roles

### RolePermission
- **File**: `permission.py`
- **Table**: `role_permissions`
- **Description**: Association table linking roles to permissions

## Database Migration

### Run Migration
```bash
cd backend
alembic upgrade head
```

### Create New Migration
```bash
alembic revision --autogenerate -m "description"
```

### Rollback Migration
```bash
alembic downgrade -1
```

## Usage Examples

### Creating a User
```python
from app.models import User

user = User(
    username="john",
    email="john@example.com",
    hashed_password="$2b$12$...",  # Use passlib to hash
    is_active=True,
)
db.add(user)
await db.commit()
```

### Assigning a Role
```python
from app.models import Role, UserRole

# Get role
role = await db.get(Role, role_id)

# Assign to user
user_role = UserRole(user_id=user.id, role_id=role.id)
db.add(user_role)
await db.commit()

# Access user's roles
await db.refresh(user)
for role in user.roles:
    print(role.name)
```

### Checking Permissions
```python
# Get user with roles and permissions
user = await db.get(User, user_id)
await db.refresh(user, ["roles"])

# Check if user has permission
permissions = set()
for role in user.roles:
    for perm in role.permissions:
        permissions.add(perm.name)

has_permission = "models:create" in permissions
```

## Testing

Run model tests:
```bash
pytest tests/models/test_auth.py -v
```

## Design Principles

1. **UUID Primary Keys**: All tables use UUIDs for better distribution and security
2. **Soft Delete**: `is_deleted` flag for data retention
3. **Timestamps**: Automatic `created_at` and `updated_at` tracking
4. **Indexes**: Strategic indexes on foreign keys and frequently queried fields
5. **Constraints**: Unique constraints on username and email
6. **Cascading Deletes**: Association tables cascade on parent deletion
7. **Eager Loading**: `selectin` loading for commonly accessed relationships

## References

- [DatabaseDesign.md](../../../docs/DatabaseDesign.md) - Complete database schema
- [BackendDesign.md](../../../docs/BackendDesign.md) - Service layer design
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
