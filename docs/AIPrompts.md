# Agentex AI 开发 Prompt 指南

> **版本**：1.2
> **更新日期**：2026-02-05
> **用途**：为 AI 辅助开发提供标准化 Prompt 模板

---

## 目录

1. [使用说明](#1-使用说明)
2. [通用 Prompt 模板](#2-通用-prompt-模板)
3. [阶段一：基础框架 Prompts](#3-阶段一基础框架-prompts)
4. [阶段二：核心功能 Prompts](#4-阶段二核心功能-prompts)
5. [阶段三：扩展功能 Prompts](#5-阶段三扩展功能-prompts)
6. [阶段四：测试与优化 Prompts](#6-阶段四测试与优化-prompts)
7. [阶段五：部署上线 Prompts](#7-阶段五部署上线-prompts)
8. [调试与修复 Prompts](#8-调试与修复-prompts)

---

## 1. 使用说明

### 1.1 Prompt 使用流程

```
1. 在任务分解表中找到当前任务 ID
2. 在本文档中找到对应的 Prompt
3. 复制 Prompt 并根据实际情况填充 [占位符]
4. 与 AI 对话，逐步完成任务
5. 审查生成的代码
6. 运行测试验证
```

### 1.2 Prompt 结构说明

每个 Prompt 包含以下部分：

| 部分 | 说明 |
|------|------|
| **上下文** | 项目背景和当前状态 |
| **任务** | 具体要完成的工作 |
| **要求** | 技术规范和约束 |
| **输出** | 期望的代码/文件结构 |
| **验收标准** | 如何判断任务完成 |

### 1.3 通用上下文（每次对话开始时提供）

```markdown
## 项目上下文

我正在开发 Agentex，一个 WebAI Agent 应用平台。

**技术栈：**
- 后端：FastAPI 0.110+, Python 3.11+, SQLAlchemy 2.0, PostgreSQL 15+, Redis 7.0+
- 前端：Vue 3.4+, TypeScript 5.3+, Vite 5.0+, Pinia, shadcn-vue, Inspira UI
- UI 风格：Linear 极简风（深色主题、1px 边框、Inter/JetBrains Mono 字体）
- 图标：Lucide Vue Next (stroke-width: 1.5px)
- Agent 通信：AG-UI 协议（基于 HTTP SSE）
- 向量数据库：Milvus 2.3+
- 异步任务：Celery + Redis

**项目结构：**
```
agentex/
├── backend/
│   ├── app/
│   │   ├── api/          # API 路由
│   │   ├── core/         # 核心配置
│   │   ├── models/       # 数据库模型
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # 业务逻辑
│   │   ├── agents/       # Agent 实现
│   │   └── utils/        # 工具函数
│   ├── tests/
│   └── main.py
├── frontend/
│   ├── src/
│   │   ├── api/          # API 调用
│   │   ├── components/   # Vue 组件
│   │   ├── composables/  # 组合式函数
│   │   ├── stores/       # Pinia stores
│   │   ├── views/        # 页面
│   │   └── router/       # 路由
│   └── ...
└── docker-compose.yml
```

**相关文档：**
- 设计文档在 docs/ 目录
- 数据库设计见 DatabaseDesign.md
- API 设计见 APIDesign.md
- 系统架构见 SystemArchitecture.md
```

---

## 2. 通用 Prompt 模板

### 2.1 数据库表设计 Prompt

```markdown
## 任务：设计 [表名] 数据库表

请根据以下要求设计数据库表：

**业务需求：**
[描述表的业务用途]

**需要的字段：**
[列出主要字段]

**关联关系：**
[描述与其他表的关系]

**要求：**
1. 使用 SQLAlchemy 2.0 声明式模型
2. 包含 created_at, updated_at 时间戳
3. 包含软删除支持（is_deleted）
4. 使用 UUID 作为主键
5. 添加必要的索引
6. 生成 Alembic 迁移脚本

**输出：**
1. SQLAlchemy 模型文件
2. Alembic 迁移脚本
```

### 2.2 API 接口 Prompt

```markdown
## 任务：实现 [功能名] API

请实现以下 API 接口：

**接口列表：**
- [HTTP方法] [路径] - [描述]

**业务逻辑：**
[描述核心业务逻辑]

**要求：**
1. 使用 FastAPI 路由
2. 使用 Pydantic 定义 request/response schemas
3. 实现完整的错误处理
4. 添加 OpenAPI 文档注释
5. 添加认证依赖（如需要）
6. 编写单元测试

**输出：**
1. router 文件
2. schemas 文件
3. service 文件
4. 测试文件
```

### 2.3 Vue 页面 Prompt

```markdown
## 任务：实现 [页面名] 页面

请实现以下 Vue 页面：

**页面功能：**
[描述页面核心功能]

**UI 布局：**
[描述页面布局结构]

**数据交互：**
[描述需要的 API 调用]

**要求：**
1. 使用 Vue 3 Composition API + TypeScript
2. 使用 shadcn-vue 作为基础组件库
3. 遵循 Linear 极简风格（深色主题、1px 边框、无阴影）
4. 使用 Inspira UI 添加科技感效果（如需要）
5. 使用 Lucide 图标（stroke-width: 1.5px）
6. 响应式设计
7. 加载状态和错误处理
8. 使用 Pinia 管理状态（如需要）

**输出：**
1. Vue 页面组件
2. 相关子组件
3. API 调用函数
4. Pinia store（如需要）
```

### 2.4 Vue 组件 Prompt

```markdown
## 任务：实现 [组件名] 组件

请实现以下 Vue 组件：

**组件功能：**
[描述组件功能]

**Props：**
[列出组件 props]

**Events：**
[列出组件 emit 的事件]

**要求：**
1. 使用 Vue 3 Composition API + TypeScript
2. 使用 defineProps 和 defineEmits
3. 遵循 Linear 极简风格（深色主题、1px 边框）
4. 使用 shadcn-vue 基础组件
5. 支持 v-model（如需要）
6. 编写组件测试

**输出：**
1. Vue 组件文件
2. 组件测试文件
```

---

## 3. 阶段一：基础框架 Prompts

### 任务 1.2：后端项目初始化

```markdown
## 任务：初始化 FastAPI 后端项目

请帮我创建 Agentex 后端项目的基础结构。

**技术栈：**
- FastAPI 0.110+
- Python 3.11+
- SQLAlchemy 2.0（异步）
- PostgreSQL
- Redis
- Alembic（数据库迁移）
- Pydantic 2.0

**要求：**
1. 创建标准的项目目录结构
2. 配置 pyproject.toml（使用 poetry 或 pip）
3. 配置环境变量管理（pydantic-settings）
4. 配置日志系统（structlog）
5. 配置数据库连接（异步）
6. 配置 Redis 连接
7. 创建健康检查端点
8. 配置 CORS

**输出：**
请生成以下文件：
- pyproject.toml 或 requirements.txt
- app/core/config.py
- app/core/database.py
- app/core/redis.py
- app/core/logging.py
- app/main.py
- app/api/health.py

**验收标准：**
- 项目可以通过 `uvicorn app.main:app --reload` 启动
- 访问 /docs 可以看到 Swagger 文档
- 访问 /health 返回健康状态
```

### 任务 1.3：前端项目初始化

```markdown
## 任务：初始化 Vue 3 前端项目

请帮我创建 Agentex 前端项目的基础结构。

**技术栈：**
- Vue 3.4+
- TypeScript 5.3+
- Vite 5.0+
- Pinia
- Vue Router 4
- shadcn-vue（基础 UI 组件库）
- Inspira UI（科技感增强组件）
- Lucide Vue Next（图标库）
- Axios

**设计风格：Linear 极简风**
- 深色主题（#030303 底色）
- 1px 细边框，不使用阴影区分层级
- Inter 字体（UI）+ JetBrains Mono（代码）
- Lucide 图标（stroke-width: 1.5px）

**要求：**
1. 使用 Vite 创建项目
2. 配置 TypeScript（严格模式）
3. 配置 ESLint + Prettier
4. 配置 shadcn-vue（按需引入组件）
5. 配置 Pinia 状态管理
6. 配置 Vue Router
7. 配置 Axios 请求封装
8. 创建 Linear 风格的 CSS 变量定义
9. 配置 Google Fonts（Inter, JetBrains Mono）
10. 创建深色主题基础布局

**输出：**
请生成以下文件结构：
- vite.config.ts
- tsconfig.json
- src/main.ts
- src/router/index.ts
- src/stores/index.ts
- src/api/request.ts
- src/styles/variables.css（CSS 变量定义）
- src/App.vue

**验收标准：**
- 项目可以通过 `npm run dev` 启动
- 访问首页显示欢迎信息
- Linear 深色主题正确应用
- shadcn-vue 组件可以正常使用
```

### 任务 1.4：DevContainer 开发环境

```markdown
## 任务：配置 DevContainer 开发环境

请帮我配置 Agentex 的 DevContainer 开发环境，提供统一的容器化开发体验。

**需要的服务：**
1. 开发容器（Python 3.11 + Node.js 20）
2. PostgreSQL 15
3. Redis 7
4. Milvus 2.3（可选，后续添加）

**要求：**
1. 创建 .devcontainer/devcontainer.json 配置
2. 创建 .devcontainer/docker-compose.yml（定义依赖服务）
3. 配置 VS Code 扩展（Python, Vue, ESLint, Prettier 等）
4. 配置开发容器的启动命令
5. 配置端口转发
6. 配置数据持久化（volumes）
7. 创建 .env.example

**devcontainer.json 要点：**
- 使用 docker-compose 方式
- 安装必要的 VS Code 扩展
- 配置 Python 和 Node.js 环境
- 设置环境变量
- 配置 postCreateCommand（安装依赖）

**输出：**
- .devcontainer/devcontainer.json
- .devcontainer/docker-compose.yml
- .devcontainer/Dockerfile（开发容器镜像）
- .env.example
- README.md（DevContainer 使用说明）

**验收标准：**
- 使用 VS Code "Reopen in Container" 可以启动开发环境
- 容器内 Python 和 Node.js 环境可用
- PostgreSQL 和 Redis 可以连接
- 代码变更可以热重载
- VS Code 扩展功能正常
```

### 任务 1.5：PostgreSQL 数据库初始化

```markdown
## 任务：初始化 PostgreSQL 数据库配置

请帮我配置 PostgreSQL 数据库连接和 Alembic 迁移工具。

**要求：**
1. 配置 SQLAlchemy 2.0 异步引擎
2. 创建数据库会话管理
3. 配置 Alembic 用于数据库迁移
4. 创建基础模型基类（含 UUID 主键、时间戳、软删除）
5. 配置连接池参数

**数据库配置项：**
- DATABASE_URL（从环境变量读取）
- 连接池大小
- 连接超时时间

**输出：**
- app/core/database.py（数据库配置）
- app/models/base.py（模型基类）
- alembic.ini
- alembic/env.py
- alembic/script.py.mako

**验收标准：**
- 数据库可连接
- `alembic revision --autogenerate` 可执行
- `alembic upgrade head` 可执行
```

### 任务 1.6：Redis 配置

```markdown
## 任务：配置 Redis 连接

请帮我配置 Redis 连接，用于缓存和会话管理。

**功能：**
1. Redis 连接配置
2. 连接池管理
3. 基础缓存操作封装
4. 健康检查

**要求：**
1. 使用 redis-py 异步客户端
2. 支持连接池
3. 支持 Redis Sentinel（可选）
4. 提供 get/set/delete 等基础操作

**配置项：**
- REDIS_URL（从环境变量读取）
- 连接池大小
- 过期时间默认值

**输出：**
- app/core/redis.py

**验收标准：**
- Redis 可连接
- 基础缓存操作可用
```

### 任务 1.7：CI/CD 基础配置

```markdown
## 任务：配置 GitHub Actions CI/CD

请帮我配置 GitHub Actions 用于自动化测试和构建。

**CI 流程：**
1. 代码检查（lint）
2. 单元测试
3. 构建检查

**需要的 Workflow：**
1. ci.yml - 每次 PR 和 push 触发
2. 后端测试 job
3. 前端测试 job

**要求：**
1. 使用 GitHub Actions
2. 缓存依赖加速构建
3. 并行运行前后端测试
4. 测试覆盖率报告

**输出：**
- .github/workflows/ci.yml

**验收标准：**
- PR 触发自动测试
- 测试通过显示绿色标记
```

### 任务 2.1：用户/角色/权限表设计

```markdown
## 任务：设计用户认证相关数据库表

请帮我设计用户认证系统的数据库表。

**需要的表：**
1. users - 用户表
2. roles - 角色表
3. permissions - 权限表
4. user_roles - 用户角色关联表
5. role_permissions - 角色权限关联表

**users 表字段：**
- id (UUID, PK)
- username (unique)
- email (unique)
- hashed_password
- is_active
- is_superuser
- created_at, updated_at, is_deleted

**参考：**
请参考 docs/DatabaseDesign.md 中的设计

**要求：**
1. 使用 SQLAlchemy 2.0 声明式模型
2. 包含适当的索引
3. 生成 Alembic 迁移脚本

**输出：**
- app/models/user.py
- app/models/role.py
- app/models/permission.py
- alembic/versions/xxx_create_auth_tables.py
```

### 任务 2.2：用户注册/登录 API

```markdown
## 任务：实现用户注册和登录 API

请帮我实现用户注册和登录功能。

**API 接口：**
1. POST /api/v1/auth/register - 用户注册
2. POST /api/v1/auth/login - 用户登录
3. POST /api/v1/auth/refresh - 刷新 Token

**业务逻辑：**
- 注册：验证用户名/邮箱唯一性，密码加密存储
- 登录：验证凭据，返回 JWT Token（access + refresh）
- 刷新：使用 refresh token 获取新的 access token

**要求：**
1. 使用 python-jose 生成 JWT
2. 使用 passlib + bcrypt 加密密码
3. Token 过期时间可配置
4. 完整的错误处理
5. 单元测试

**输出：**
- app/api/v1/auth.py
- app/schemas/auth.py
- app/services/auth.py
- app/core/security.py
- tests/test_auth.py
```

### 任务 2.3：JWT Token 认证中间件

```markdown
## 任务：实现 JWT Token 认证中间件

请帮我实现 FastAPI 的 JWT 认证依赖。

**功能：**
1. 从 Authorization header 提取 Bearer token
2. 验证 token 有效性和过期时间
3. 获取当前用户信息
4. 可选：验证用户权限

**要求：**
1. 创建 get_current_user 依赖
2. 创建 get_current_active_user 依赖
3. 创建 require_permissions 依赖工厂
4. 处理 token 过期、无效等异常

**输出：**
- app/api/deps.py
- 更新 app/core/security.py
```

### 任务 2.4-2.7：前端认证系统

```markdown
## 任务：实现前端认证系统

请帮我实现 Vue 前端的完整认证系统。

**功能模块：**
1. 登录页面 (/login)
2. 注册页面 (/register)
3. 认证状态管理（Pinia store）
4. 路由守卫
5. Axios 请求拦截器

**登录页面：**
- 用户名/密码输入
- 表单验证
- 登录按钮（带 loading）
- 注册链接

**认证 Store：**
- user 信息
- token 存储（localStorage）
- login/logout actions
- isAuthenticated getter

**路由守卫：**
- 保护需要认证的路由
- 未登录重定向到 /login
- 已登录访问 /login 重定向到首页

**Axios 拦截器：**
- 请求拦截：自动添加 Authorization header
- 响应拦截：401 自动跳转登录页

**要求：**
1. 使用 shadcn-vue 表单组件（Input, Button, Card）
2. 遵循 Linear 极简风格（深色主题、1px 边框）
3. 使用 Composition API + TypeScript
4. 使用 Lucide 图标（stroke-width: 1.5px）
5. 完善的类型定义
6. 友好的错误提示（Toast 组件）

**输出：**
- src/views/auth/LoginView.vue
- src/views/auth/RegisterView.vue
- src/stores/auth.ts
- src/router/index.ts（更新守卫）
- src/api/auth.ts
- src/api/request.ts（更新拦截器）
```

### 任务 3.1-3.4：基础框架完善（后端）

```markdown
## 任务：完善后端基础框架

请帮我完善后端基础框架，包括用户信息 API、API 密钥管理、全局异常处理和日志系统。

**3.1 用户信息 API：**
- GET /api/v1/users/me - 获取当前用户信息
- PUT /api/v1/users/me - 更新当前用户信息
- PUT /api/v1/users/me/password - 修改密码

**3.2 API 密钥管理：**
- POST /api/v1/users/me/api-keys - 创建 API Key
- GET /api/v1/users/me/api-keys - 获取 API Key 列表
- DELETE /api/v1/users/me/api-keys/{key_id} - 删除 API Key
- API Key 认证支持

**3.3 全局异常处理：**
- 自定义业务异常类
- 全局异常处理器
- 统一错误响应格式：`{ "code": 错误码, "message": "错误信息", "data": null }`

**3.4 日志系统：**
- 使用 structlog 结构化日志
- 请求日志中间件
- 日志级别可配置

**要求：**
1. 遵循 RESTful 设计
2. 完整的输入验证
3. 合理的错误码设计

**输出：**
- app/api/v1/users.py
- app/schemas/user.py
- app/services/user.py
- app/core/exceptions.py
- app/core/logging.py
- app/api/middleware.py
```

### 任务 3.5-3.7：基础框架完善（前端）

```markdown
## 任务：实现前端基础布局

请帮我实现前端主布局组件和设置页面。

**3.5 主布局组件：**
- 左侧边栏（可收起）
  - Logo
  - 导航菜单（对话、设置等）
  - 用户信息（底部）
- 右侧内容区
  - 顶部工具栏（可选）
  - 主内容区

**3.6 设置页布局：**
- 左侧设置菜单
  - 个人信息
  - API 密钥
  - 模型管理
  - MCP 管理
  - 知识库
  - SKILL
  - 规则（后续）
- 右侧设置内容区

**3.7 个人信息页面：**
- 用户头像
- 用户名、邮箱展示
- 编辑个人信息表单
- 修改密码功能

**UI 要求：**
1. Linear 极简风格（深色主题）
2. 1px 边框，无阴影
3. 使用 Lucide 图标（stroke-width: 1.5px）
4. 响应式设计
5. 动画过渡效果（subtle）

**输出：**
- src/layouts/MainLayout.vue
- src/layouts/SettingsLayout.vue
- src/components/layout/Sidebar.vue
- src/components/layout/SettingsMenu.vue
- src/views/settings/ProfileView.vue
- src/views/settings/ApiKeysView.vue
```

### 任务 4.1-4.3：会话系统（后端）

```markdown
## 任务：实现会话系统后端

请帮我实现对话会话的后端功能。

**4.1 会话/消息表设计：**

chat_sessions 表：
- id (UUID, PK)
- user_id (FK -> users)
- title
- agent_type (react, agentic_rag, plan_execute)
- model_config_id (FK -> model_configs)
- settings (JSONB) - 温度、系统提示等
- created_at, updated_at, is_deleted

chat_messages 表：
- id (UUID, PK)
- session_id (FK -> chat_sessions)
- role (user, assistant, system, tool)
- content
- metadata (JSONB) - 工具调用、思考过程等
- created_at

**4.2 会话 CRUD API：**
- POST /api/v1/sessions - 创建会话
- GET /api/v1/sessions - 获取会话列表
- GET /api/v1/sessions/{id} - 获取会话详情
- PUT /api/v1/sessions/{id} - 更新会话
- DELETE /api/v1/sessions/{id} - 删除会话

**4.3 消息 API：**
- POST /api/v1/sessions/{id}/messages - 添加消息
- GET /api/v1/sessions/{id}/messages - 获取消息历史

**要求：**
1. 分页支持
2. 按用户隔离数据
3. 软删除

**输出：**
- app/models/session.py
- app/models/message.py
- app/schemas/session.py
- app/schemas/message.py
- app/api/v1/sessions.py
- app/services/session.py
- alembic/versions/xxx_create_session_tables.py
```

### 任务 4.4-4.6：会话系统（前端）

```markdown
## 任务：实现对话页面前端

请帮我实现对话页面的基础结构。

**4.4 对话页面基础结构：**
- 左侧：会话列表面板
- 中间：消息展示区域
- 底部：输入区域

**4.5 会话列表组件：**
- 新建会话按钮
- 会话列表（按时间倒序）
  - 会话标题
  - 最后消息时间
  - 会话类型标签
- 会话右键菜单（重命名、删除）
- 当前会话高亮
- 搜索过滤（可选）

**4.6 消息列表组件：**
- 消息气泡样式
  - 用户消息（右侧）
  - AI 消息（左侧）
  - 系统消息（居中）
- Markdown 渲染支持
- 代码高亮
- 复制消息按钮
- 消息时间戳

**UI 要求：**
1. Linear 极简风格
2. 流畅的滚动体验
3. 自动滚动到最新消息
4. 空状态提示

**输出：**
- src/views/ChatView.vue
- src/components/chat/SessionList.vue
- src/components/chat/SessionItem.vue
- src/components/chat/MessageList.vue
- src/components/chat/MessageItem.vue
- src/components/chat/ChatInput.vue
- src/stores/session.ts
- src/api/session.ts
```

---

## 4. 阶段二：核心功能 Prompts

### 任务 5.1-5.6：模型管理模块

```markdown
## 任务：实现 LLM 模型管理模块

请帮我实现 LLM 模型配置和管理功能。

**后端功能：**
1. 模型配置表设计（provider, model_name, api_key, base_url, params）
2. 模型配置 CRUD API
3. LLM 客户端抽象基类
4. OpenAI 客户端实现
5. Anthropic 客户端实现
6. 模型测试接口

**前端功能：**
1. 模型管理页面（列表、添加、编辑、删除）
2. 模型配置表单
3. 模型测试功能
4. 模型选择器组件

**LLM 客户端接口：**
```python
class BaseLLMClient(ABC):
    @abstractmethod
    async def chat(self, messages: list, **kwargs) -> AsyncIterator[str]:
        """流式对话"""
        pass

    @abstractmethod
    async def complete(self, prompt: str, **kwargs) -> str:
        """单次完成"""
        pass
```

**参考：**
- docs/BackendDesign.md 第 6 节

**要求：**
1. API Key 加密存储
2. 支持自定义 base_url（兼容 Azure、本地部署）
3. 流式输出支持
4. 完善的错误处理

**输出：**
- 后端：models, schemas, api, services
- 前端：views, components, api, stores
```

### 任务 6.1-6.6：Agent 服务基础

```markdown
## 任务：实现 Agent 服务基础架构

请帮我实现 Agent 服务的基础架构，包括 Agent 基类和 ReAct Agent。

**Agent 基类设计：**
```python
class BaseAgent(ABC):
    def __init__(self, llm_client, tools: list = None, config: dict = None):
        pass

    @abstractmethod
    async def run(self, input: str, context: dict = None) -> AsyncIterator[AgentEvent]:
        """运行 Agent，产生 AG-UI 事件流"""
        pass
```

**AG-UI 事件类型：**
参考 docs/APIDesign.md 第 12 节，需要支持：
- RUN_STARTED / RUN_FINISHED / RUN_ERROR
- TEXT_MESSAGE_START / TEXT_MESSAGE_CONTENT / TEXT_MESSAGE_END
- TOOL_CALL_START / TOOL_CALL_ARGS / TOOL_CALL_END
- STEP_STARTED / STEP_FINISHED

**ReAct Agent：**
实现思考-行动-观察循环：
1. 思考：分析问题，决定下一步
2. 行动：调用工具
3. 观察：获取工具结果
4. 重复直到得出最终答案

**后端 API：**
- POST /api/v1/agent/chat - 启动 Agent 对话（SSE 响应）

**前端：**
- useAgentChat composable
- 消息流式展示组件

**要求：**
1. 使用 ag-ui-protocol SDK
2. 正确实现 SSE 响应
3. 支持中断/取消

**参考：**
- docs/BackendDesign.md 第 3.2 节
- docs/APIDesign.md 第 12 节

**输出：**
- app/agents/base.py
- app/agents/react.py
- app/agents/factory.py
- app/api/v1/agent.py
- src/composables/useAgentChat.ts
- src/components/chat/MessageStream.vue
```

### 任务 7.1-7.6：Agent 服务完善

```markdown
## 任务：完善 Agent 服务

请帮我实现更多 Agent 类型和前端展示组件。

**7.1 AgenticRAG Agent：**
- 继承 BaseAgent
- 整合知识库检索
- 流程：接收问题 → 检索相关文档 → 基于检索结果回答
- 支持多知识库

**7.2 PlanAndExecute Agent：**
- 任务规划阶段：将复杂任务拆解为子任务
- 执行阶段：按顺序执行子任务
- 重规划：根据执行结果调整计划
- 支持任务依赖

**7.3 思考过程展示组件：**
- 可折叠的思考过程区域
- 步骤列表展示
- 每个步骤：
  - 步骤编号
  - 思考内容
  - 执行时间
- 实时更新动画

**7.4 工具调用展示组件：**
- 工具名称和图标
- 输入参数（可折叠 JSON）
- 执行状态（loading/success/error）
- 输出结果
- 执行耗时

**7.5 Agent 选择器组件：**
- 下拉选择 Agent 类型
- Agent 类型说明（tooltip）
- 当前会话 Agent 类型显示

**7.6 对话输入组件完善：**
- 多行输入框（自动增高）
- 发送按钮
- 停止生成按钮（流式输出时显示）
- 重新生成按钮
- 快捷键支持（Enter 发送，Shift+Enter 换行）

**要求：**
1. 组件解耦，可复用
2. 平滑的动画效果
3. 良好的加载状态反馈

**输出：**
- app/agents/agentic_rag.py
- app/agents/plan_execute.py
- src/components/chat/ThinkingProcess.vue
- src/components/chat/ToolCallDisplay.vue
- src/components/chat/AgentSelector.vue
- src/components/chat/ChatInput.vue（更新）
```

### 任务 8.1：MCP 连接表设计

```markdown
## 任务：设计 MCP 连接数据库表

请帮我设计 MCP 连接的数据库表。

**mcp_connections 表：**
- id (UUID, PK)
- user_id (FK -> users)
- name - 连接名称
- description - 描述
- transport_type - 传输类型（stdio, sse, websocket）
- config (JSONB) - 连接配置
  - stdio: { command, args, env }
  - sse: { url, headers }
  - websocket: { url, auth_token }
- status - 连接状态（connected, disconnected, error）
- last_connected_at
- created_at, updated_at, is_deleted

**mcp_tools_cache 表：**
- id (UUID, PK)
- connection_id (FK -> mcp_connections)
- tool_name
- tool_description
- input_schema (JSONB)
- cached_at

**要求：**
1. 支持多种传输类型
2. 配置信息加密存储（敏感信息）
3. 工具缓存减少重复请求

**输出：**
- app/models/mcp.py
- alembic/versions/xxx_create_mcp_tables.py
```

### 任务 8.4-8.6：MCP 管理功能

```markdown
## 任务：实现 MCP 连接管理功能

请帮我实现 MCP 连接的管理 API 和前端页面。

**8.4 MCP 连接管理 API：**
- POST /api/v1/mcp/connections - 创建连接
- GET /api/v1/mcp/connections - 获取连接列表
- GET /api/v1/mcp/connections/{id} - 获取连接详情
- PUT /api/v1/mcp/connections/{id} - 更新连接
- DELETE /api/v1/mcp/connections/{id} - 删除连接
- POST /api/v1/mcp/connections/{id}/test - 测试连接
- GET /api/v1/mcp/connections/{id}/tools - 获取工具列表

**8.5 MCP 管理页面：**
- 连接列表
  - 连接名称、类型、状态
  - 快捷操作（测试、编辑、删除）
- 添加/编辑连接对话框
  - 连接类型选择
  - 根据类型显示不同配置项
  - 测试连接按钮
- 连接详情
  - 基本信息
  - 可用工具列表

**8.6 工具选择器组件：**
- 树形结构展示（按连接分组）
- 工具搜索
- 勾选启用/禁用
- 工具详情弹窗

**输出：**
- app/api/v1/mcp.py
- app/schemas/mcp.py
- app/services/mcp.py
- src/views/settings/McpView.vue
- src/components/mcp/ConnectionList.vue
- src/components/mcp/ConnectionForm.vue
- src/components/mcp/ToolSelector.vue
- src/api/mcp.ts
- src/stores/mcp.ts
```

### 任务 9.1-9.2：SKILL 表设计和 API

```markdown
## 任务：实现 SKILL 数据管理

请帮我实现 SKILL 的数据库表设计和 CRUD API。

**9.1 SKILL 表设计：**

skills 表：
- id (UUID, PK)
- user_id (FK -> users)
- name - SKILL 名称
- description - 描述
- version - 版本号
- definition (TEXT) - YAML 定义内容
- input_schema (JSONB) - 输入参数 schema
- output_schema (JSONB) - 输出参数 schema
- is_public - 是否公开
- status - 状态（draft, active, deprecated）
- created_at, updated_at, is_deleted

skill_executions 表：
- id (UUID, PK)
- skill_id (FK -> skills)
- user_id (FK -> users)
- session_id (FK -> chat_sessions, nullable)
- inputs (JSONB)
- outputs (JSONB)
- status - 执行状态
- started_at, finished_at
- error_message

**9.2 SKILL CRUD API：**
- POST /api/v1/skills - 创建 SKILL
- GET /api/v1/skills - 获取 SKILL 列表
- GET /api/v1/skills/{id} - 获取 SKILL 详情
- PUT /api/v1/skills/{id} - 更新 SKILL
- DELETE /api/v1/skills/{id} - 删除 SKILL
- POST /api/v1/skills/{id}/validate - 验证 SKILL 定义
- POST /api/v1/skills/{id}/execute - 执行 SKILL

**输出：**
- app/models/skill.py
- app/schemas/skill.py
- app/api/v1/skills.py
- app/services/skill.py
- alembic/versions/xxx_create_skill_tables.py
```

### 任务 9.5-9.7：SKILL 前端

```markdown
## 任务：实现 SKILL 管理前端

请帮我实现 SKILL 管理的前端页面和组件。

**9.5 SKILL 管理页面：**
- SKILL 列表
  - 名称、版本、状态、描述
  - 快捷操作（编辑、执行、删除）
- 新建 SKILL 按钮
- 状态过滤（全部、草稿、激活、废弃）
- 搜索

**9.6 SKILL 编辑器组件：**
- 左侧：YAML 编辑器
  - 语法高亮（使用 Monaco Editor 或 CodeMirror）
  - 自动补全
  - 错误提示
- 右侧：实时预览
  - 可视化步骤流程图
  - 输入输出 schema 展示
- 底部工具栏
  - 验证按钮
  - 保存按钮
  - 测试运行按钮

**9.7 SKILL 选择器组件：**
- 下拉列表选择
- 显示 SKILL 名称和描述
- 支持搜索
- 可多选（可选）

**输出：**
- src/views/settings/SkillView.vue
- src/views/settings/SkillEditorView.vue
- src/components/skill/SkillList.vue
- src/components/skill/SkillEditor.vue
- src/components/skill/SkillPreview.vue
- src/components/skill/SkillSelector.vue
- src/api/skill.ts
- src/stores/skill.ts
```

### 任务 10.1：知识库表设计

```markdown
## 任务：设计知识库数据库表

请帮我设计 RAG 知识库的数据库表。

**knowledge_bases 表：**
- id (UUID, PK)
- user_id (FK -> users)
- name - 知识库名称
- description - 描述
- embedding_model - 使用的 embedding 模型
- chunk_size - 分块大小
- chunk_overlap - 分块重叠
- collection_name - Milvus collection 名称
- document_count - 文档数量
- status - 状态（creating, ready, error）
- created_at, updated_at, is_deleted

**knowledge_documents 表：**
- id (UUID, PK)
- knowledge_base_id (FK -> knowledge_bases)
- filename - 文件名
- file_type - 文件类型（pdf, md, txt, html）
- file_size - 文件大小
- file_path - 存储路径
- chunk_count - 分块数量
- status - 处理状态（pending, processing, completed, failed）
- error_message
- processed_at
- created_at, updated_at, is_deleted

**要求：**
1. 支持多种文档类型
2. 记录处理状态
3. 支持增量更新

**输出：**
- app/models/knowledge.py
- alembic/versions/xxx_create_knowledge_tables.py
```

### 任务 10.7-10.9：知识库前端

```markdown
## 任务：实现知识库管理前端

请帮我实现知识库管理的前端页面和组件。

**10.7 知识库管理页面：**
- 知识库列表
  - 名称、文档数、状态
  - 快捷操作（查看、编辑、删除）
- 新建知识库按钮
- 知识库详情页
  - 基本信息
  - 文档列表
  - 上传文档
  - 测试检索

**文档管理：**
- 文档列表
  - 文件名、类型、大小、状态
  - 处理进度条
  - 删除按钮
- 文件上传区域
  - 拖拽上传
  - 多文件支持
  - 上传进度

**10.8 知识库选择器组件：**
- 下拉多选
- 显示知识库名称和文档数
- 搜索支持

**10.9 检索结果展示组件：**
- 检索来源标签
- 来源文档链接
- 相关度分数
- 原文片段预览（可展开）

**输出：**
- src/views/settings/KnowledgeView.vue
- src/views/settings/KnowledgeDetailView.vue
- src/components/knowledge/KnowledgeList.vue
- src/components/knowledge/DocumentList.vue
- src/components/knowledge/FileUploader.vue
- src/components/knowledge/KnowledgeSelector.vue
- src/components/knowledge/RetrievalResult.vue
- src/api/knowledge.ts
- src/stores/knowledge.ts
```

### 任务 8.2-8.3：MCP 客户端实现

```markdown
## 任务：实现 MCP 客户端

请帮我实现 MCP（Model Context Protocol）客户端，支持标准 MCP 和 WS-MCP 扩展。

**标准 MCP 客户端：**
- 支持 stdio 传输
- 支持 SSE 传输
- 实现 tools/list、tools/call 方法
- 实现 resources/list、resources/read 方法

**WS-MCP 客户端：**
- 基于 WebSocket 传输
- 支持事件订阅（参考 docs/CustomizeWsMessageProtocol.md）
- 支持双向通信

**MCP 客户端接口：**
```python
class MCPClient(ABC):
    @abstractmethod
    async def connect(self) -> None:
        pass

    @abstractmethod
    async def list_tools(self) -> list[Tool]:
        pass

    @abstractmethod
    async def call_tool(self, name: str, arguments: dict) -> Any:
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        pass
```

**要求：**
1. 使用官方 mcp SDK
2. 连接池管理
3. 自动重连机制
4. 超时处理

**参考：**
- docs/BackendDesign.md 第 4 节

**输出：**
- app/mcp/base.py
- app/mcp/stdio_client.py
- app/mcp/sse_client.py
- app/mcp/ws_client.py
- app/mcp/manager.py
```

### 任务 9.3-9.4：SKILL 解析器和执行器

```markdown
## 任务：实现 SKILL 解析器和执行器

请帮我实现 SKILL（结构化工作流）的解析和执行功能。

**SKILL 定义格式（YAML）：**
```yaml
name: example_skill
version: "1.0"
description: 示例 SKILL

inputs:
  - name: query
    type: string
    required: true

steps:
  - id: step1
    type: llm_call
    config:
      prompt: "处理: {{query}}"
    outputs:
      - name: result

  - id: step2
    type: tool_call
    config:
      tool: web_search
      args:
        query: "{{steps.step1.result}}"

outputs:
  - name: final_result
    value: "{{steps.step2.result}}"
```

**解析器功能：**
1. 解析 YAML 定义
2. 验证语法正确性
3. 验证变量引用
4. 生成执行计划

**执行器功能：**
1. 按步骤执行
2. 变量替换（模板语法）
3. 条件执行
4. 错误处理和重试
5. 产生 AG-UI 事件

**要求：**
1. 支持 LLM 调用步骤
2. 支持工具调用步骤
3. 支持条件分支
4. 支持循环
5. 状态持久化

**参考：**
- docs/BackendDesign.md 第 7 节

**输出：**
- app/skill/parser.py
- app/skill/executor.py
- app/skill/validators.py
- tests/test_skill.py
```

### 任务 10.2-10.6：RAG 知识库

```markdown
## 任务：实现 RAG 知识库功能

请帮我实现 RAG（检索增强生成）知识库功能。

**功能模块：**
1. Milvus 向量存储封装
2. 文档处理服务（Celery 异步任务）
3. 知识库 CRUD API
4. 文档上传 API
5. 语义检索 API

**文档处理流程：**
```
上传文件 → 解析内容 → 分块 → 向量化 → 存储到 Milvus
```

**支持的文档类型：**
- PDF
- Markdown
- TXT
- HTML

**向量存储接口：**
```python
class VectorStore(ABC):
    @abstractmethod
    async def add_documents(self, docs: list[Document]) -> list[str]:
        pass

    @abstractmethod
    async def search(self, query: str, top_k: int = 5) -> list[Document]:
        pass

    @abstractmethod
    async def delete(self, ids: list[str]) -> None:
        pass
```

**要求：**
1. 使用 langchain 文档加载器
2. 支持自定义分块策略
3. 支持多种 embedding 模型
4. 检索结果包含来源信息

**参考：**
- docs/BackendDesign.md 第 8 节

**输出：**
- app/rag/vector_store.py
- app/rag/document_processor.py
- app/rag/embeddings.py
- app/tasks/document_tasks.py
- app/api/v1/knowledge.py
```

### 任务 10.10-10.11：自定义 Agent 表设计和 API

```markdown
## 任务：实现自定义 Agent 数据管理

请帮我实现自定义 Agent 的数据库表设计和 CRUD API。

**10.10 自定义 Agent 表设计：**

custom_agents 表：
- id (UUID, PK)
- name - Agent 名称
- description - Agent 描述
- agent_type - Agent 架构类型（react, agentic_rag, plan_execute）
- system_prompt (TEXT) - 系统提示词
- icon - Agent 图标（emoji 或图标名）
- is_default (BOOLEAN) - 是否为系统默认 Agent
- enabled (BOOLEAN) - 是否启用
- owner_id (FK -> users, nullable) - 所有者（系统默认时为 NULL）
- created_at, updated_at

agent_knowledge_bases 表（关联知识库）：
- id (UUID, PK)
- agent_id (FK -> custom_agents, ON DELETE CASCADE)
- knowledge_base_id (FK -> knowledge_bases, ON DELETE CASCADE)
- created_at
- UNIQUE (agent_id, knowledge_base_id)

agent_mcp_connections 表（关联 MCP 连接）：
- id (UUID, PK)
- agent_id (FK -> custom_agents, ON DELETE CASCADE)
- mcp_connection_id (FK -> mcp_connections, ON DELETE CASCADE)
- created_at
- UNIQUE (agent_id, mcp_connection_id)

agent_skills 表（关联 SKILL）：
- id (UUID, PK)
- agent_id (FK -> custom_agents, ON DELETE CASCADE)
- skill_id (FK -> skills, ON DELETE CASCADE)
- created_at
- UNIQUE (agent_id, skill_id)

**系统默认 Agent 初始化数据：**
| name | agent_type | is_default | description |
|------|------------|------------|-------------|
| ReAct Agent | react | true | 支持多轮思考和工具调用的通用 Agent |
| RAG Agent | agentic_rag | true | 专注于知识库检索的 Agent |
| Plan & Execute Agent | plan_execute | true | 先规划后执行的任务分解 Agent |

**10.11 自定义 Agent CRUD API：**
- GET /api/v1/agents - 获取 Agent 列表（含系统默认和用户自定义）
- GET /api/v1/agents/{id} - 获取 Agent 详情（包含关联资源）
- POST /api/v1/agents - 创建自定义 Agent
- PUT /api/v1/agents/{id} - 更新自定义 Agent（不能修改系统默认）
- DELETE /api/v1/agents/{id} - 删除自定义 Agent（不能删除系统默认）
- GET /api/v1/agents/types - 获取所有 Agent 架构类型及默认提示词
- POST /api/v1/agents/{id}/duplicate - 复制 Agent（可基于默认创建自定义版本）

**要求：**
1. 系统默认 Agent（is_default=true）不可编辑和删除
2. 关联资源需验证用户访问权限
3. 同一用户下 Agent 名称不能重复
4. 每用户最多 50 个自定义 Agent
5. 复制时继承原 Agent 的所有配置

**参考：**
- docs/DatabaseDesign.md 第 7 节
- docs/APIDesign.md 第 11 节
- docs/BackendDesign.md 第 2.8 节

**输出：**
- app/models/custom_agent.py
- app/schemas/custom_agent.py
- app/api/v1/agents.py
- app/services/custom_agent.py
- alembic/versions/xxx_create_custom_agent_tables.py
```

### 任务 10.12-10.13：Agent 资源关联和初始化

```markdown
## 任务：实现 Agent 资源关联和系统默认 Agent 初始化

**10.12 Agent 资源关联 API：**

在 Agent CRUD 中实现资源关联管理：

创建/更新 Agent 请求体：
```json
{
  "name": "运维助手",
  "description": "专注于服务器运维的 Agent",
  "agent_type": "react",
  "icon": "🔧",
  "system_prompt": "You are an expert DevOps engineer...",
  "knowledge_base_ids": ["kb-uuid-1", "kb-uuid-2"],
  "mcp_connection_ids": ["mcp-uuid-1"],
  "skill_ids": ["skill-uuid-1"],
  "enabled": true
}
```

获取 Agent 详情响应：
```json
{
  "id": "uuid",
  "name": "运维助手",
  "agent_type": "react",
  "knowledge_bases": [
    { "id": "kb-uuid-1", "name": "技术文档知识库" }
  ],
  "mcp_connections": [
    { "id": "mcp-uuid-1", "name": "GitHub MCP" }
  ],
  "skills": [
    { "id": "skill-uuid-1", "name": "代码审查" }
  ],
  ...
}
```

**10.13 系统默认 Agent 初始化：**

创建数据库迁移或初始化脚本，插入三个系统默认 Agent：

1. **ReAct Agent**
   - agent_type: react
   - system_prompt: 包含思考-行动-观察循环的提示词
   - 不关联任何资源

2. **RAG Agent**
   - agent_type: agentic_rag
   - system_prompt: 包含知识检索和引用的提示词
   - 不关联任何资源

3. **Plan & Execute Agent**
   - agent_type: plan_execute
   - system_prompt: 包含任务分解和执行的提示词
   - 不关联任何资源

**要求：**
1. 迁移脚本需幂等（可重复执行）
2. 系统默认 Agent 的 owner_id 为 NULL
3. 默认提示词参考 docs/BackendDesign.md 第 3 节

**输出：**
- alembic/versions/xxx_init_default_agents.py
- app/services/custom_agent.py（更新）
```

### 任务 10.14-10.15：Agent 管理页面和选择器

```markdown
## 任务：实现 Agent 管理前端页面和选择器组件

**10.14 Agent 管理页面 (AgentsView)：**

页面布局：
- 标题栏：「Agent 管理」+ 「创建 Agent」按钮
- 系统默认 Agent 分组
  - 卡片展示：图标、名称、描述、架构类型
  - 只显示「复制」按钮
- 我的 Agent 分组
  - 卡片展示：图标、名称、描述、架构类型、关联资源数量
  - 操作按钮：编辑、复制、删除

创建/编辑 Agent 弹窗：
- 基本信息区域
  - Agent 名称（必填）
  - 图标选择器（emoji picker）
  - 描述（可选）
  - Agent 架构选择（下拉）
- 系统提示词区域
  - 多行文本编辑器
  - 「使用默认提示词」按钮
- 预配置资源区域
  - 知识库多选下拉
  - MCP 连接多选下拉
  - SKILL 多选下拉
- 启用开关
- 保存/取消按钮

**10.15 Agent 选择器组件 (CustomAgentSelector)：**

位置：对话输入框左侧，attach 图标之前

组件结构：
- 触发按钮
  - 当前 Agent 图标
  - 当前 Agent 名称
  - 下拉箭头
- 下拉菜单
  - 搜索框
  - 「默认 Agent」分组标题
    - ReAct Agent
    - RAG Agent
    - Plan & Execute Agent
  - 「我的 Agent」分组标题
    - 用户自定义 Agent 列表
  - 分隔线
  - 「管理 Agent」链接（跳转设置页）

**要求：**
1. 使用 shadcn-vue 组件（Select, Dialog, Popover）
2. Linear 风格（深色主题、1px 边框）
3. 支持键盘导航
4. 搜索支持模糊匹配

**输出：**
- src/views/settings/AgentsView.vue
- src/components/agent/AgentList.vue
- src/components/agent/AgentCard.vue
- src/components/agent/AgentFormDialog.vue
- src/components/agent/EmojiPicker.vue
- src/components/chat/CustomAgentSelector.vue
- src/api/agents.ts
- src/stores/agents.ts
```

### 任务 10.16-10.17：Agent 资源自动应用和复制

```markdown
## 任务：实现 Agent 选择后资源自动应用和复制功能

**10.16 Agent 资源自动应用：**

当用户在对话界面选择一个 Agent 时：

1. 更新会话配置的 agent_type 和 system_prompt
2. 获取该 Agent 预配置的资源列表
3. 自动勾选对应的知识库
4. 自动勾选对应的 MCP 连接
5. 自动勾选对应的 SKILL
6. 用户可以在预配置基础上额外添加或取消资源

实现方式：
```typescript
// src/composables/useAgentConfig.ts
export function useAgentConfig() {
  const sessionStore = useSessionStore()
  const agentStore = useAgentStore()

  async function selectAgent(agentId: string) {
    const agent = await agentStore.getAgentDetail(agentId)

    // 更新会话配置
    sessionStore.updateConfig({
      agent_type: agent.agent_type,
      system_prompt: agent.system_prompt,
      knowledge_base_ids: agent.knowledge_bases.map(kb => kb.id),
      mcp_connection_ids: agent.mcp_connections.map(mcp => mcp.id),
      skill_ids: agent.skills.map(skill => skill.id)
    })

    // 触发 UI 更新
    emit('agent-changed', agent)
  }

  return { selectAgent }
}
```

**10.17 Agent 复制功能：**

复制 Agent API 调用：
- POST /api/v1/agents/{agent_id}/duplicate
- 请求体：{ "name": "我的 ReAct Agent" }

复制逻辑：
1. 复制原 Agent 的所有配置（agent_type, system_prompt, icon）
2. 复制关联的知识库、MCP 连接、SKILL
3. 设置 is_default = false
4. 设置 owner_id = 当前用户
5. 使用新名称

前端交互：
1. 点击「复制」按钮
2. 弹出输入框，输入新 Agent 名称
3. 确认后调用 API
4. 成功后跳转到编辑页面

**要求：**
1. 复制时验证资源访问权限（复制系统默认 Agent 时无需验证）
2. 复制失败时给出明确错误提示
3. 提供良好的加载状态反馈

**输出：**
- src/composables/useAgentConfig.ts
- src/components/chat/ChatInput.vue（更新）
- src/components/agent/DuplicateAgentDialog.vue
- src/stores/agents.ts（更新）
```

---

## 5. 阶段三：扩展功能 Prompts

### 任务 11.1：规则表设计

```markdown
## 任务：设计规则引擎数据库表

请帮我设计规则引擎的数据库表。

**rules 表：**
- id (UUID, PK)
- user_id (FK -> users)
- name - 规则名称
- description - 描述
- trigger_type - 触发类型（event, schedule, manual）
- trigger_config (JSONB) - 触发配置
  - event: { source, event_type, filter }
  - schedule: { cron_expression }
  - manual: {}
- conditions (JSONB) - 条件表达式树
- actions (JSONB) - 动作列表
- priority - 优先级
- is_active - 是否启用
- created_at, updated_at, is_deleted

**rule_executions 表：**
- id (UUID, PK)
- rule_id (FK -> rules)
- trigger_event (JSONB) - 触发事件
- matched_conditions - 匹配结果
- executed_actions - 执行的动作
- status - 执行状态
- started_at, finished_at
- error_message

**要求：**
1. 支持复杂条件表达式
2. 记录完整执行日志
3. 支持规则优先级

**输出：**
- app/models/rule.py
- alembic/versions/xxx_create_rule_tables.py
```

### 任务 11.2-11.4：规则引擎核心

```markdown
## 任务：实现规则引擎核心

请帮我实现规则引擎的核心功能。

**规则定义结构：**
```python
class Rule:
    id: UUID
    name: str
    description: str
    trigger: Trigger           # 触发条件
    conditions: list[Condition] # 前置条件
    actions: list[Action]      # 执行动作
    priority: int
    is_active: bool
```

**触发器类型：**
- 事件触发（WS-MCP 事件）
- 定时触发（Cron 表达式）
- 手动触发

**条件类型：**
- 比较条件（==, !=, >, <, >=, <=）
- 字符串条件（contains, startswith, regex）
- 逻辑组合（AND, OR, NOT）

**动作类型：**
- 发送消息
- 调用工具
- 执行 SKILL
- 触发 Agent
- Webhook

**要求：**
1. 条件评估支持嵌套
2. 动作支持并行/串行执行
3. 支持变量上下文
4. 规则执行日志

**参考：**
- docs/BackendDesign.md 第 9 节

**输出：**
- app/rule_engine/engine.py
- app/rule_engine/condition.py
- app/rule_engine/action.py
- app/rule_engine/trigger.py
```

### 任务 11.5-11.6：规则 API 和事件订阅

```markdown
## 任务：实现规则管理 API 和事件订阅

请帮我实现规则的管理 API 和 WS-MCP 事件订阅功能。

**11.5 规则 CRUD API：**
- POST /api/v1/rules - 创建规则
- GET /api/v1/rules - 获取规则列表
- GET /api/v1/rules/{id} - 获取规则详情
- PUT /api/v1/rules/{id} - 更新规则
- DELETE /api/v1/rules/{id} - 删除规则
- POST /api/v1/rules/{id}/toggle - 启用/禁用规则
- POST /api/v1/rules/{id}/test - 测试规则
- GET /api/v1/rules/{id}/executions - 获取执行历史

**11.6 WS-MCP 事件订阅：**
- 订阅 WS-MCP 服务器事件
- 事件匹配规则触发器
- 事件过滤
- 批量事件处理

**要求：**
1. 规则变更实时生效
2. 事件去重处理
3. 错误重试机制

**输出：**
- app/api/v1/rules.py
- app/schemas/rule.py
- app/services/rule.py
- app/rule_engine/event_handler.py
```

### 任务 12.1-12.6：规则引擎前端

```markdown
## 任务：实现规则引擎前端

请帮我实现规则引擎的完整前端界面。

**12.1 规则管理页面：**
- 规则列表
  - 名称、触发类型、状态、优先级
  - 快捷操作（启用/禁用、编辑、删除）
- 新建规则按钮
- 状态过滤、搜索

**12.2 规则编辑器组件：**
- 基本信息表单
  - 规则名称、描述
  - 优先级
- 触发器配置
- 条件配置
- 动作配置
- 保存/取消按钮

**12.3 条件构建器组件：**
- 可视化条件构建
- 支持嵌套条件组（AND/OR）
- 条件类型选择
  - 比较条件
  - 字符串条件
  - 存在性检查
- 变量选择器
- 值输入

**12.4 动作配置器组件：**
- 动作类型选择
  - 发送消息
  - 调用工具
  - 执行 SKILL
  - 触发 Agent
  - Webhook
- 动作参数配置
- 动作排序（拖拽）
- 并行/串行选择

**12.5 规则测试功能：**
- 模拟触发事件
- 条件匹配预览
- 动作模拟执行
- 执行结果展示

**12.6 规则日志展示：**
- 执行历史列表
- 执行详情
  - 触发事件
  - 条件匹配结果
  - 动作执行结果
  - 错误信息
- 时间范围过滤

**输出：**
- src/views/settings/RulesView.vue
- src/views/settings/RuleEditorView.vue
- src/components/rule/RuleList.vue
- src/components/rule/RuleEditor.vue
- src/components/rule/TriggerConfig.vue
- src/components/rule/ConditionBuilder.vue
- src/components/rule/ActionConfig.vue
- src/components/rule/RuleTestPanel.vue
- src/components/rule/RuleLogList.vue
- src/api/rule.ts
- src/stores/rule.ts
```

### 任务 13.1-13.2：细粒度权限系统

```markdown
## 任务：实现细粒度权限系统

请帮我完善权限系统，支持资源级别的访问控制。

**权限模型：**
- 基于 RBAC（角色-权限）
- 支持资源所有权检查
- 支持资源分享

**资源类型：**
- 会话（Session）
- 知识库（Knowledge）
- SKILL
- MCP 连接
- 规则

**权限检查流程：**
```
1. 检查用户是否为超级管理员 → 允许
2. 检查用户角色权限 → 有权限继续
3. 检查资源所有权 → 是所有者允许
4. 检查资源分享 → 已分享允许
5. 拒绝
```

**要求：**
1. 创建权限检查装饰器/依赖
2. 支持权限缓存（Redis）
3. 支持批量权限检查
4. 权限变更日志

**输出：**
- app/core/permissions.py
- app/api/deps.py（更新）
- app/services/permission.py
```

### 任务 13.3-13.7：权限管理功能

```markdown
## 任务：实现用户和角色管理功能

请帮我实现管理员的用户和角色管理功能。

**13.3 用户管理 API：**
- GET /api/v1/admin/users - 获取用户列表（分页）
- GET /api/v1/admin/users/{id} - 获取用户详情
- PUT /api/v1/admin/users/{id} - 更新用户信息
- PUT /api/v1/admin/users/{id}/roles - 更新用户角色
- POST /api/v1/admin/users/{id}/toggle - 启用/禁用用户
- DELETE /api/v1/admin/users/{id} - 删除用户

**13.4 角色管理 API：**
- POST /api/v1/admin/roles - 创建角色
- GET /api/v1/admin/roles - 获取角色列表
- GET /api/v1/admin/roles/{id} - 获取角色详情
- PUT /api/v1/admin/roles/{id} - 更新角色
- PUT /api/v1/admin/roles/{id}/permissions - 更新角色权限
- DELETE /api/v1/admin/roles/{id} - 删除角色

**13.5 用户管理页面：**
- 用户列表
  - 用户名、邮箱、角色、状态
  - 快捷操作
- 用户详情/编辑对话框
- 角色分配

**13.6 权限配置组件：**
- 权限树形结构展示
- 勾选授权
- 按模块分组
- 全选/取消全选

**13.7 侧边栏权限过滤：**
- 根据用户权限动态显示菜单项
- 无权限的菜单项隐藏
- 权限变更实时生效

**输出：**
- app/api/v1/admin.py
- app/schemas/admin.py
- app/services/admin.py
- src/views/settings/UsersView.vue
- src/views/settings/RolesView.vue
- src/components/admin/UserList.vue
- src/components/admin/UserForm.vue
- src/components/admin/RoleList.vue
- src/components/admin/PermissionTree.vue
- src/components/layout/Sidebar.vue（更新）
- src/api/admin.ts
```

### 任务 14.1-14.7：优化与完善

```markdown
## 任务：系统优化与完善

请帮我完成系统的优化和完善工作。

**14.1 Reflexion Agent 实现：**
- 继承 BaseAgent
- 实现自我反思循环
  - 执行 → 评估结果 → 反思 → 改进 → 重试
- 最大重试次数限制
- 反思历史记录

**14.2 系统设置 API：**
- GET /api/v1/settings - 获取系统设置
- PUT /api/v1/settings - 更新系统设置
- 设置项：
  - 默认模型
  - 默认 Agent 类型
  - 会话保留天数
  - 其他全局配置

**14.3 操作日志实现：**
- 记录关键操作（创建、更新、删除）
- 操作人、操作时间、操作类型
- 操作详情（变更内容）
- 查询 API

**14.4 系统设置页面：**
- 通用设置
- 默认配置
- 系统信息展示

**14.5 全局加载状态优化：**
- 顶部加载进度条
- 骨架屏（Skeleton）
- 加载状态管理

**14.6 错误处理优化：**
- 统一 Toast 提示组件
- 错误边界组件
- 网络错误重试
- 友好的错误信息

**14.7 响应式布局完善：**
- 移动端适配
- 侧边栏响应式收起
- 表格响应式
- 触摸手势支持

**输出：**
- app/agents/reflexion.py
- app/api/v1/settings.py
- app/api/v1/audit.py
- app/models/audit.py
- app/services/audit.py
- src/views/settings/SystemView.vue
- src/components/common/LoadingBar.vue
- src/components/common/Skeleton.vue
- src/components/common/Toast.vue
- src/components/common/ErrorBoundary.vue
- 布局组件响应式更新
```

---

## 6. 阶段四：测试与优化 Prompts

### 任务 15.1：后端单元测试

```markdown
## 任务：补充后端单元测试

请帮我为以下模块补充单元测试，目标覆盖率 > 80%。

**需要测试的模块：**
1. 认证服务（auth service）
2. Agent 服务
3. MCP 客户端
4. SKILL 解析器/执行器
5. 规则引擎

**测试要求：**
1. 使用 pytest
2. 使用 pytest-asyncio 处理异步
3. 使用 pytest-mock 进行模拟
4. 使用 factory_boy 创建测试数据
5. 测试正常流程和边界情况

**测试用例模板：**
```python
class TestAuthService:
    async def test_register_success(self):
        """测试正常注册"""
        pass

    async def test_register_duplicate_email(self):
        """测试重复邮箱注册"""
        pass

    async def test_login_success(self):
        """测试正常登录"""
        pass

    async def test_login_wrong_password(self):
        """测试密码错误"""
        pass
```

**输出：**
- tests/services/test_auth.py
- tests/agents/test_react.py
- tests/mcp/test_client.py
- tests/skill/test_executor.py
- tests/rule_engine/test_engine.py
- tests/conftest.py（fixtures）
```

### 任务 15.2-15.3：集成测试

```markdown
## 任务：编写集成测试

请帮我编写后端 API 集成测试和前端组件测试。

**15.2 后端集成测试：**
测试完整的 API 流程，包括数据库交互。

测试场景：
1. 用户注册 → 登录 → 获取信息 → 更新信息
2. 创建会话 → 发送消息 → 获取历史
3. 创建模型配置 → 测试调用
4. 创建知识库 → 上传文档 → 检索
5. 创建 SKILL → 验证 → 执行

要求：
- 使用 pytest + httpx
- 使用测试数据库
- 事务回滚保证测试隔离
- 测试数据 fixtures

**15.3 前端组件测试：**
测试核心 Vue 组件。

测试范围：
1. 表单组件（输入验证、提交）
2. 列表组件（渲染、分页、筛选）
3. 对话组件（消息展示、发送）
4. 状态管理（Pinia stores）

要求：
- 使用 Vitest + Vue Test Utils
- 组件快照测试
- 用户交互测试

**输出：**
- tests/integration/test_auth_flow.py
- tests/integration/test_session_flow.py
- tests/integration/test_knowledge_flow.py
- tests/integration/conftest.py
- frontend/src/components/__tests__/
- frontend/vitest.config.ts
```

### 任务 15.4：E2E 测试

```markdown
## 任务：编写 E2E 测试

请帮我编写核心用户流程的 E2E 测试。

**测试场景：**
1. 用户注册登录流程
2. 创建会话并对话
3. 配置模型并测试
4. 创建知识库并上传文档
5. 创建并执行 SKILL

**使用工具：**
- Playwright

**测试结构：**
```typescript
test.describe('用户认证', () => {
  test('用户可以注册新账号', async ({ page }) => {
    // ...
  });

  test('用户可以登录', async ({ page }) => {
    // ...
  });
});

test.describe('对话功能', () => {
  test('用户可以创建新会话', async ({ page }) => {
    // ...
  });

  test('用户可以发送消息并收到回复', async ({ page }) => {
    // ...
  });
});
```

**要求：**
1. 测试前自动准备测试数据
2. 测试后清理数据
3. 截图失败用例
4. 生成测试报告

**输出：**
- frontend/e2e/auth.spec.ts
- frontend/e2e/chat.spec.ts
- frontend/e2e/model.spec.ts
- frontend/e2e/knowledge.spec.ts
- frontend/playwright.config.ts
```

### 任务 15.5-15.6：压力测试

```markdown
## 任务：编写压力测试

请帮我编写 API 和 SSE 连接的压力测试。

**15.5 API 压力测试：**
使用 Locust 或 k6 进行 API 压力测试。

测试场景：
1. 登录接口
2. 会话列表接口
3. 消息历史接口
4. 知识库检索接口

测试指标：
- 并发用户数
- 请求吞吐量 (RPS)
- 响应时间 (P50, P95, P99)
- 错误率

目标：
- 100 并发用户
- P95 < 200ms
- 错误率 < 0.1%

**15.6 AG-UI SSE 压力测试：**
测试 SSE 长连接的并发能力。

测试场景：
1. 并发建立 SSE 连接
2. 同时进行流式输出
3. 连接保持稳定性

测试指标：
- 最大并发连接数
- 消息延迟
- 连接断开率

目标：
- 支持 1000 并发连接
- 消息延迟 < 100ms

**输出：**
- tests/load/locustfile.py 或 tests/load/k6_script.js
- tests/load/sse_stress_test.py
- tests/load/README.md（运行说明）
```

### 任务 16.1：安全审计

```markdown
## 任务：安全审计和修复

请帮我进行安全审计并修复发现的问题。

**审计清单：**

1. 认证安全
   - JWT 配置（密钥强度、过期时间）
   - 密码策略（最小长度、复杂度）
   - 暴力破解防护（登录限流）
   - Token 刷新机制

2. 授权安全
   - 权限检查覆盖
   - 越权访问测试
   - 资源隔离验证

3. 输入验证
   - SQL 注入防护
   - XSS 防护
   - 参数校验完整性
   - 文件上传安全

4. 敏感数据
   - API Key 加密存储
   - 日志脱敏
   - 错误信息泄露

5. API 安全
   - CORS 配置
   - 请求限流
   - 安全响应头

**要求：**
1. 输出安全检查报告
2. 提供修复代码
3. 添加安全测试用例

**输出：**
- docs/SECURITY_AUDIT.md
- 修复补丁
- tests/security/
```

### 任务 16.2-16.3：性能优化

```markdown
## 任务：性能优化

请帮我分析并优化系统性能。

**后端优化方向：**
1. 数据库查询优化（N+1 问题、索引）
2. 缓存策略（Redis）
3. 异步处理优化
4. 连接池配置

**前端优化方向：**
1. 路由懒加载
2. 组件按需加载
3. 虚拟滚动（长列表）
4. 图片懒加载
5. Bundle 分析和优化

**性能指标目标：**
- API P95 响应时间 < 200ms
- 首页 LCP < 2s
- TTI < 3s

**请提供：**
1. 当前代码中可能的性能问题分析
2. 优化建议和具体实现
3. 优化前后对比方案

**输出：**
- 性能分析报告
- 优化后的代码
```

### 任务 16.4-16.6：Bug 修复与文档完善

```markdown
## 任务：Bug 修复、代码重构与文档完善

请帮我完成测试阶段发现的 Bug 修复、代码质量改进和文档完善。

**16.4 Bug 修复：**
根据测试报告修复所有 P0/P1 级别 Bug。

流程：
1. 分析 Bug 报告
2. 定位问题根因
3. 编写修复代码
4. 添加回归测试
5. 验证修复

**16.5 代码重构：**
基于代码质量分析进行重构。

重构方向：
1. 消除代码重复
2. 简化复杂函数
3. 改善命名
4. 优化模块结构
5. 提升类型覆盖

工具：
- pylint / ruff（Python）
- ESLint（TypeScript）
- SonarQube（可选）

**16.6 文档完善：**

API 文档：
- OpenAPI 文档补充描述
- 请求/响应示例
- 错误码说明

开发文档：
- README.md 更新
- 架构说明文档
- 本地开发指南
- 部署指南

用户文档：
- 功能使用说明
- 常见问题 FAQ

**输出：**
- Bug 修复 PR
- 重构 PR
- docs/API.md
- docs/DEVELOPMENT.md
- docs/DEPLOYMENT.md
- docs/USER_GUIDE.md
```

---

## 7. 阶段五：部署上线 Prompts

### 任务 17.1-17.5：生产环境部署

```markdown
## 任务：配置生产环境部署

请帮我配置生产环境的部署方案。

**部署架构：**
- Docker Compose（单机）或 Kubernetes
- Nginx 反向代理
- PostgreSQL（生产配置）
- Redis（持久化配置）
- Milvus

**需要的文件：**
1. docker-compose.prod.yml
2. Nginx 配置
3. 生产环境变量模板
4. 数据库初始化脚本
5. 启动/停止脚本

**Nginx 配置要点：**
- SSL/TLS 配置
- 静态文件服务
- API 反向代理
- SSE 长连接支持
- Gzip 压缩
- 安全头

**要求：**
1. 支持零停机部署
2. 健康检查配置
3. 日志配置
4. 备份配置

**输出：**
- docker-compose.prod.yml
- nginx/nginx.conf
- nginx/sites-enabled/agentex.conf
- scripts/deploy.sh
- scripts/backup.sh
- .env.prod.example
```

### 任务 17.6-17.7：监控和日志

```markdown
## 任务：配置监控和日志系统

请帮我配置生产环境的监控和日志收集。

**监控方案：**
- Prometheus（指标收集）
- Grafana（可视化）
- 应用指标暴露

**需要监控的指标：**
- 请求量和延迟
- 错误率
- 活跃用户数
- Agent 执行统计
- 资源使用率

**日志方案：**
- 结构化日志（JSON）
- 日志收集（Loki 或 ELK）
- 日志轮转

**要求：**
1. Prometheus metrics 端点
2. Grafana 仪表板配置
3. 告警规则配置
4. 日志查询示例

**输出：**
- prometheus/prometheus.yml
- grafana/dashboards/agentex.json
- grafana/alerting/rules.yml
- 后端 metrics 端点代码
```

### 任务 17.8-17.10：备份与上线验证

```markdown
## 任务：备份策略配置与上线验证

请帮我配置数据备份策略并准备上线验证清单。

**17.8 备份策略配置：**

数据库备份：
- PostgreSQL 定时备份脚本
- 备份频率：每日全量 + 每小时增量
- 备份保留策略：7 天全量，24 小时增量
- 备份存储位置配置
- 备份加密

Milvus 备份：
- Collection 备份
- 定时备份任务

文件备份：
- 上传文件备份
- 配置文件备份

恢复验证：
- 恢复流程文档
- 定期恢复测试

**17.9 上线验证清单：**

功能验证：
- [ ] 用户注册/登录
- [ ] 会话创建和对话
- [ ] 模型调用
- [ ] MCP 连接
- [ ] 知识库检索
- [ ] SKILL 执行
- [ ] 规则触发

性能验证：
- [ ] API 响应时间
- [ ] SSE 流式输出延迟
- [ ] 并发用户测试

安全验证：
- [ ] SSL 证书有效
- [ ] 安全头配置
- [ ] 权限控制生效

监控验证：
- [ ] 指标采集正常
- [ ] 告警规则有效
- [ ] 日志收集正常

**17.10 用户文档发布：**

文档站点：
- 使用 VitePress 或 Docusaurus
- 部署到 GitHub Pages 或 Vercel

文档内容：
- 快速开始
- 功能介绍
- API 参考
- 常见问题
- 更新日志

**输出：**
- scripts/backup.sh
- scripts/restore.sh
- docs/BACKUP.md
- docs/RELEASE_CHECKLIST.md
- docs-site/（文档站点源码）
```

---

## 8. 调试与修复 Prompts

### 8.1 Bug 修复 Prompt

```markdown
## 任务：修复 Bug

**Bug 描述：**
[详细描述 Bug 现象]

**复现步骤：**
1. [步骤1]
2. [步骤2]
3. [步骤3]

**期望行为：**
[描述期望的正确行为]

**实际行为：**
[描述实际的错误行为]

**错误日志：**
```
[粘贴相关错误日志]
```

**相关代码：**
文件：[文件路径]
```
[粘贴相关代码片段]
```

**请帮我：**
1. 分析 Bug 原因
2. 提供修复方案
3. 生成修复后的代码
4. 添加防止回归的测试
```

### 8.2 代码审查 Prompt

```markdown
## 任务：代码审查

请帮我审查以下代码：

**代码类型：**[前端/后端]

**代码：**
```[语言]
[粘贴代码]
```

**请检查：**
1. 功能正确性
2. 类型安全性
3. 错误处理
4. 安全性问题（SQL注入、XSS等）
5. 性能问题
6. 代码规范
7. 可维护性

**输出格式：**
- 问题列表（按严重程度排序）
- 改进建议
- 优化后的代码
```

### 8.3 重构建议 Prompt

```markdown
## 任务：代码重构建议

我想重构以下代码，请给出建议：

**当前代码：**
```[语言]
[粘贴代码]
```

**重构原因：**
[描述为什么需要重构]

**请提供：**
1. 代码坏味道分析
2. 重构策略建议
3. 重构后的代码
4. 重构前后的对比说明
5. 需要更新的测试
```

---

## 附录：常用代码片段

### A.1 FastAPI 路由模板

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.example import ExampleCreate, ExampleResponse
from app.services.example import ExampleService

router = APIRouter(prefix="/examples", tags=["examples"])

@router.post("", response_model=ExampleResponse, status_code=status.HTTP_201_CREATED)
async def create_example(
    data: ExampleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建示例"""
    service = ExampleService(db)
    return await service.create(data, current_user.id)
```

### A.2 Vue Composable 模板

```typescript
import { ref, computed } from 'vue'
import { useRequest } from '@/composables/useRequest'

export function useExample() {
  const loading = ref(false)
  const error = ref<Error | null>(null)
  const data = ref<ExampleData | null>(null)

  const fetchData = async (id: string) => {
    loading.value = true
    error.value = null
    try {
      data.value = await exampleApi.get(id)
    } catch (e) {
      error.value = e as Error
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    error,
    data,
    fetchData,
  }
}
```

### A.3 Pydantic Schema 模板

```python
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

class ExampleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None

class ExampleCreate(ExampleBase):
    pass

class ExampleUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None

class ExampleResponse(ExampleBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
```

---

> 💡 **提示**：使用这些 Prompt 时，请根据实际情况调整细节。如果 AI 生成的代码需要修改，可以追加说明进行迭代。
