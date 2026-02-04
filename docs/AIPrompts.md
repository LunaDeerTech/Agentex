# Agentex AI 开发 Prompt 指南

> **版本**：1.0  
> **更新日期**：2024-01  
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
- 前端：Vue 3.4+, TypeScript 5.3+, Vite 5.0+, Pinia, Element Plus
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
2. 使用 Element Plus 组件
3. 响应式设计
4. 加载状态和错误处理
5. 使用 Pinia 管理状态（如需要）

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
3. 支持 v-model（如需要）
4. 编写组件测试

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
- Element Plus
- Axios

**要求：**
1. 使用 Vite 创建项目
2. 配置 TypeScript（严格模式）
3. 配置 ESLint + Prettier
4. 配置 Element Plus（按需引入）
5. 配置 Pinia 状态管理
6. 配置 Vue Router
7. 配置 Axios 请求封装
8. 创建基础布局

**输出：**
请生成以下文件结构：
- vite.config.ts
- tsconfig.json
- src/main.ts
- src/router/index.ts
- src/stores/index.ts
- src/api/request.ts
- src/App.vue

**验收标准：**
- 项目可以通过 `npm run dev` 启动
- 访问首页显示欢迎信息
- Element Plus 组件可以正常使用
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
1. 使用 Element Plus 表单组件
2. 使用 Composition API
3. 完善的类型定义
4. 友好的错误提示

**输出：**
- src/views/auth/LoginView.vue
- src/views/auth/RegisterView.vue
- src/stores/auth.ts
- src/router/index.ts（更新守卫）
- src/api/auth.ts
- src/api/request.ts（更新拦截器）
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

---

## 5. 阶段三：扩展功能 Prompts

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
