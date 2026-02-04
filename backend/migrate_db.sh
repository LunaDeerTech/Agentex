#!/bin/bash
# Database Migration Setup Script
# Run this after PostgreSQL is available

set -e

echo "================================================"
echo "Agentex Database Migration Setup"
echo "================================================"
echo ""

# Check if we're in the backend directory
if [ ! -f "alembic.ini" ]; then
    echo "❌ Error: alembic.ini not found. Please run from backend/ directory."
    exit 1
fi

# Check Python environment
echo "🔍 Checking Python environment..."
python --version
echo ""

# Check if Alembic is installed
echo "🔍 Checking Alembic installation..."
if ! python -c "import alembic" 2>/dev/null; then
    echo "❌ Alembic not found. Installing..."
    pip install alembic
else
    echo "✅ Alembic is installed"
fi
echo ""

# Check database connection
echo "🔍 Checking database connection..."
if python -c "
import asyncio
from app.core.database import engine

async def check():
    try:
        async with engine.connect() as conn:
            await conn.execute('SELECT 1')
        print('✅ Database connection successful')
        return 0
    except Exception as e:
        print(f'❌ Database connection failed: {e}')
        return 1
    finally:
        await engine.dispose()

exit(asyncio.run(check()))
" 2>&1; then
    echo ""
else
    echo ""
    echo "⚠️  Database not accessible. Please ensure PostgreSQL is running."
    echo "    Check your .env file for correct DATABASE_URL"
    exit 1
fi

# Show current migration status
echo "📊 Current migration status:"
alembic current || echo "No migrations applied yet"
echo ""

# Ask for confirmation
echo "This will apply the authentication tables migration which will:"
echo "  - Create 5 tables: users, roles, permissions, user_roles, role_permissions"
echo "  - Seed 4 default roles: admin, manager, developer, user"
echo "  - Seed 36 default permissions across 8 modules"
echo ""
read -p "Continue with migration? (y/N) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Migration cancelled."
    exit 0
fi

# Run migration
echo ""
echo "🚀 Running migration..."
alembic upgrade head

# Verify migration
echo ""
echo "✅ Migration complete!"
echo ""
echo "📊 Final migration status:"
alembic current
echo ""

# Show created tables
echo "📋 Verifying tables..."
python -c "
import asyncio
from sqlalchemy import text
from app.core.database import engine

async def verify():
    async with engine.connect() as conn:
        result = await conn.execute(text(
            \"\"\"
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN ('users', 'roles', 'permissions', 'user_roles', 'role_permissions')
            ORDER BY table_name
            \"\"\"
        ))
        tables = result.fetchall()
        if len(tables) == 5:
            print('✅ All 5 tables created successfully:')
            for table in tables:
                print(f'   - {table[0]}')
        else:
            print(f'⚠️  Expected 5 tables, found {len(tables)}')
    await engine.dispose()

asyncio.run(verify())
"
echo ""

# Show role count
echo "📋 Verifying seed data..."
python -c "
import asyncio
from sqlalchemy import text, select
from app.core.database import async_session_factory
from app.models import Role, Permission

async def verify_seed():
    async with async_session_factory() as session:
        # Count roles
        result = await session.execute(select(Role))
        roles = result.scalars().all()
        print(f'✅ Roles: {len(roles)}')
        for role in roles:
            print(f'   - {role.name}: {role.display_name}')

        # Count permissions
        result = await session.execute(select(Permission))
        perms = result.scalars().all()
        print(f'✅ Permissions: {len(perms)}')

        # Group by module
        modules = {}
        for perm in perms:
            modules[perm.module] = modules.get(perm.module, 0) + 1

        for module, count in sorted(modules.items()):
            print(f'   - {module}: {count} permissions')

asyncio.run(verify_seed())
"

echo ""
echo "================================================"
echo "✅ Database setup complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "  1. Implement auth service (Task 2.2)"
echo "  2. Create API endpoints"
echo "  3. Add JWT authentication"
echo ""
