# Agentex

> Web AI Agent Platform with MCP Integration, RAG Knowledge Bases, and Rule Engine

Agentex 是一个现代化的 AI Agent 平台，支持 MCP (Model Context Protocol) 集成、RAG 知识库、SKILL 管理和规则引擎。

## 🚀 快速开始

### 方式一：使用 DevContainer（推荐）

DevContainer 提供了一个完整的、预配置的开发环境，包含所有必需的服务。

#### 前提条件

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [VS Code](https://code.visualstudio.com/)
- [Dev Containers 扩展](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

#### 启动步骤

1. 克隆项目

   ```bash
   git clone https://github.com/your-org/agentex.git
   cd agentex
   ```

2. 在 VS Code 中打开项目

   ```bash
   code .
   ```

3. 当 VS Code 提示 "Reopen in Container" 时点击确认，或者：
   - 按 `F1` 打开命令面板
   - 输入 "Dev Containers: Reopen in Container"
   - 按 Enter

4. 等待容器构建完成（首次启动可能需要几分钟）

5. 启动开发服务器

   ```bash
   # 启动后端
   make dev-backend

   # 在新终端启动前端
   make dev-frontend
   ```

6. 访问应用
   - 前端：http://localhost:5173
   - 后端 API：http://localhost:8000
   - API 文档：http://localhost:8000/docs

### 方式二：本地开发

#### 前提条件

- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Redis 7+
- Milvus 2.3+（可选，用于 RAG）

#### 安装步骤

1. 安装后端依赖
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. 安装前端依赖
   ```bash
   cd frontend
   npm install
   ```

3. 配置环境变量
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，配置数据库连接等
   ```

4. 启动服务
   ```bash
   # 后端
   cd backend
   uvicorn app.main:app --reload

   # 前端
   cd frontend
   npm run dev
   ```

## 📁 项目结构

```
agentex/
├── .devcontainer/     # DevContainer 配置
├── backend/           # FastAPI 后端
│   ├── app/
│   │   ├── api/       # API 路由
│   │   ├── core/      # 核心配置
│   │   ├── models/    # 数据模型
│   │   ├── schemas/   # Pydantic schemas
│   │   └── services/  # 业务逻辑
│   └── tests/         # 测试文件
├── frontend/          # Vue 3 前端
│   └── src/
│       ├── api/       # API 客户端
│       ├── components/# Vue 组件
│       ├── stores/    # Pinia stores
│       └── views/     # 页面组件
└── docs/              # 设计文档
```

## 🛠️ 开发命令

使用 Makefile 简化常用操作：

```bash
# 查看所有可用命令
make help

# 开发
make dev              # 启动前后端
make dev-backend      # 仅启动后端
make dev-frontend     # 仅启动前端

# 测试
make test             # 运行所有测试
make test-cov         # 运行测试并生成覆盖率报告

# 代码质量
make lint             # 运行代码检查
make format           # 格式化代码

# Docker 服务
make docker-up        # 启动依赖服务
make docker-down      # 停止服务
```

## 🐳 DevContainer 服务

DevContainer 包含以下服务：

| 服务 | 端口 | 说明 |
|------|------|------|
| PostgreSQL | 5432 | 主数据库 |
| Redis | 6379 | 缓存和会话 |
| Milvus | 19530 | 向量数据库 |
| MinIO | 9000/9001 | 对象存储 |

### 连接信息

- **PostgreSQL**
  - Host: `localhost` (容器外) / `postgres` (容器内)
  - Database: `agentex`
  - User: `agentex`
  - Password: `agentex123`

- **Redis**
  - Host: `localhost` (容器外) / `redis` (容器内)
  - Port: `6379`

- **Milvus**
  - Host: `localhost` (容器外) / `milvus-standalone` (容器内)
  - Port: `19530`

- **MinIO**
  - Console: http://localhost:9001
  - Access Key: `minioadmin`
  - Secret Key: `minioadmin`

## 📚 文档

详细设计文档位于 `docs/` 目录：

- [API 设计](docs/APIDesign.md) - REST API 规范
- [数据库设计](docs/DatabaseDesign.md) - 表结构设计
- [后端设计](docs/BackendDesign.md) - 服务接口设计
- [前端设计](docs/FrontendDesign.md) - UI/UX 设计
- [系统架构](docs/SystemArchitecture.md) - 整体架构
- [开发计划](docs/DevelopmentPlan.md) - 迭代计划

## 🤝 贡献

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request
