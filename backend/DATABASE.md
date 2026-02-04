# 数据库配置说明

## 概述

本项目使用 SQLAlchemy 2.0 异步 ORM + Alembic 进行数据库管理。

## 配置文件

### 1. 环境变量 (`.env`)

```bash
# PostgreSQL 配置
DATABASE_URL=postgresql+asyncpg://agentex:agentex123@postgres:5432/agentex
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
DATABASE_POOL_TIMEOUT=30
DATABASE_ECHO=false  # 开发时可设为 true 查看 SQL
```

### 2. 数据库配置 (`app/core/database.py`)

提供以下功能：
- 异步数据库引擎（带连接池）
- 异步会话工厂
- FastAPI 依赖注入
- 数据库生命周期管理

### 3. 基础模型 (`app/models/base.py`)

#### Base
SQLAlchemy 声明式基类。

#### BaseModel
所有业务模型的基类，包含：
- `id`: UUID 主键
- `created_at`: 创建时间（自动设置）
- `updated_at`: 更新时间（自动更新）
- `is_deleted`: 软删除标志
- `deleted_at`: 删除时间

#### Mixins
- `TimestampMixin`: 时间戳字段
- `SoftDeleteMixin`: 软删除字段

## 使用方法

### 1. 创建模型

```python
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class User(BaseModel):
    """用户模型。"""

    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)
```

### 2. 在 API 中使用数据库会话

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.user import User

router = APIRouter()


@router.get("/users/{user_id}")
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取用户信息。"""
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()
    return user
```

### 3. 在服务中使用数据库

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserService:
    """用户服务。"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_email(self, email: str) -> User | None:
        """根据邮箱获取用户。"""
        result = await self.db.execute(
            select(User).where(
                User.email == email,
                User.is_deleted == False
            )
        )
        return result.scalar_one_or_none()

    async def create_user(self, username: str, email: str, password: str) -> User:
        """创建新用户。"""
        user = User(
            username=username,
            email=email,
            hashed_password=password  # 实际应用中需要哈希处理
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def soft_delete_user(self, user_id: str) -> None:
        """软删除用户。"""
        from datetime import datetime

        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if user:
            user.is_deleted = True
            user.deleted_at = datetime.now(datetime.timezone.utc)
            await self.db.commit()
```

## Alembic 数据库迁移

### 初始化（已完成）

```bash
alembic init alembic
```

### 创建迁移

```bash
# 自动生成迁移（推荐）
alembic revision --autogenerate -m "描述信息"

# 手动创建空迁移
alembic revision -m "描述信息"
```

### 应用迁移

```bash
# 升级到最新版本
alembic upgrade head

# 升级指定步数
alembic upgrade +1

# 升级到指定版本
alembic upgrade <revision_id>
```

### 回滚迁移

```bash
# 回滚到上一个版本
alembic downgrade -1

# 回滚到指定版本
alembic downgrade <revision_id>

# 回滚所有迁移
alembic downgrade base
```

### 查看迁移历史

```bash
# 查看当前版本
alembic current

# 查看迁移历史
alembic history

# 查看详细历史
alembic history --verbose
```

### 检查数据库状态

```bash
# 检查数据库是否与代码同步
alembic check
```

## 测试数据库连接

```bash
python test_db_connection.py
```

该脚本会测试：
1. ✓ 模块导入
2. ✓ 配置加载
3. ✓ Base 模型
4. ✓ 数据库连接
5. ✓ 会话工厂
6. ✓ Alembic 配置

## 常见问题

### 1. 连接池耗尽

如果遇到 "QueuePool limit of size X overflow Y reached" 错误：

```python
# 增加连接池大小
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
```

### 2. 长时间运行的连接

使用 `pool_pre_ping=True`（已配置）确保连接有效性。

### 3. 软删除查询

记得在查询时过滤软删除的记录：

```python
# ✓ 正确
result = await db.execute(
    select(User).where(User.is_deleted == False)
)

# ✗ 错误（会包含已删除的记录）
result = await db.execute(select(User))
```

### 4. 迁移冲突

如果多人同时创建迁移导致冲突：

```bash
# 合并迁移分支
alembic merge -m "merge branches" <revision1> <revision2>
```

## 最佳实践

1. **始终使用 BaseModel**：确保所有模型继承自 `BaseModel` 以获得标准字段
2. **软删除**：使用 `is_deleted` 标志而非真删除
3. **索引**：为常用查询字段添加索引
4. **外键**：使用 `ForeignKey` 定义关系
5. **迁移**：代码和数据库同步前运行 `alembic check`
6. **测试**：使用独立的测试数据库
7. **连接管理**：使用 `Depends(get_db)` 自动管理连接生命周期

## 参考资料

- [SQLAlchemy 2.0 文档](https://docs.sqlalchemy.org/en/20/)
- [Alembic 文档](https://alembic.sqlalchemy.org/)
- [asyncpg 文档](https://magicstack.github.io/asyncpg/)
