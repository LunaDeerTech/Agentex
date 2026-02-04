# Agentex - 智能AI Agent平台

## 项目概述

Agentex 是一个功能强大的 Web AI Agent 应用平台，集成了 MCP（Model Context Protocol）客户端能力、多模型管理、RAG 知识库、SKILL 技能管理、规则引擎等核心功能，为用户提供灵活、可扩展的 AI Agent 交互体验。

## 核心特性

### 🔌 MCP 能力
- **标准 MCP 客户端**：支持连接标准的 MCP Server（HTTP SSE 协议）
- **扩展 WS-MCP 客户端**：支持连接自定义的 WebSocket MCP Server，具备权限控制和事件通知能力

### 🎯 规则引擎
- 基于 WS-MCP-Server 事件触发的规则引擎
- 可视化规则配置界面
- 支持预定义任务的自动执行

### 🤖 模型管理
- 支持 OpenAI 协议兼容模型
- 支持 Anthropic 协议兼容模型
- 多模型统一管理与切换

### 📚 SKILL 能力
- SKILL.md 格式的技能定义
- 技能的创建、修改、管理
- 技能的调用与编排

### 📖 RAG 知识库
- 知识库的创建与管理
- 文档向量化与检索
- 多知识库支持

### 💬 Agent 交互
- 多种 Agent 架构支持（ReAct、AgenticRAG 等）
- 可视化思考与操作过程展示
- 灵活的工具与知识库选择

### 👥 多用户系统
- 用户认证与授权
- 细粒度权限控制
- 多用户资源隔离

## 技术栈

### 后端
| 组件 | 技术选型 | 说明 |
|------|---------|------|
| Web 框架 | FastAPI | 高性能异步 Web 框架 |
| 异步运行时 | asyncio + uvicorn | 异步 IO 支持 |
| 数据库 ORM | SQLAlchemy 2.0 | 异步 ORM 支持 |
| 数据库 | PostgreSQL | 主数据库 |
| 向量数据库 | Milvus / Qdrant | RAG 向量存储 |
| 缓存 | Redis | 会话缓存、任务队列 |
| 任务队列 | Celery | 异步任务处理 |
| WebSocket | FastAPI WebSocket | MCP 连接管理 |
| Agent 协议 | AG-UI (SSE) | Agent 流式通信 |

### 前端
| 组件 | 技术选型 | 说明 |
|------|---------|------|
| 框架 | Vue 3 | 前端框架 |
| 构建工具 | Vite | 快速构建 |
| 状态管理 | Pinia | Vue 3 状态管理 |
| UI 组件库 | Element Plus | UI 组件 |
| 路由 | Vue Router 4 | 前端路由 |
| HTTP 客户端 | Axios | API 请求 |
| Agent 通信 | AG-UI (SSE) | Agent 流式响应 |
| Markdown | markdown-it | Markdown 渲染 |
| 代码高亮 | highlight.js | 代码块高亮 |

## 文档目录

| 文档 | 说明 |
|------|------|
| [产品需求文档](./ProductRequirements.md) | 详细的产品功能需求说明 |
| [系统架构设计](./SystemArchitecture.md) | 系统整体架构与技术方案 |
| [后端模块设计](./BackendDesign.md) | 后端各模块的详细设计 |
| [前端界面设计](./FrontendDesign.md) | 前端页面与组件设计 |
| [数据库设计](./DatabaseDesign.md) | 数据库表结构设计 |
| [API 接口设计](./APIDesign.md) | RESTful API 接口规范 |
| [开发计划](./DevelopmentPlan.md) | 项目开发计划与里程碑 |
| [自定义WS协议](./CustomizeWsMessageProcotol.md) | 自定义 WebSocket MCP 协议规范 |

## 快速开始

### 环境要求
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Milvus 2.3+ 或 Qdrant 1.7+

### 后端启动
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

### 前端启动
```bash
cd frontend
npm install
npm run dev
```

## 项目结构

```
Agentex/
├── docs/                          # 项目文档
│   ├── README.md                  # 项目概述
│   ├── ProductRequirements.md    # 产品需求文档
│   ├── SystemArchitecture.md     # 系统架构设计
│   ├── BackendDesign.md          # 后端模块设计
│   ├── FrontendDesign.md         # 前端界面设计
│   ├── DatabaseDesign.md         # 数据库设计
│   ├── APIDesign.md              # API接口设计
│   ├── DevelopmentPlan.md        # 开发计划
│   └── CustomizeWsMessageProcotol.md  # WS-MCP协议
│
├── backend/                       # 后端代码
│   ├── app/
│   │   ├── api/                  # API 路由
│   │   ├── core/                 # 核心配置
│   │   ├── models/               # 数据模型
│   │   ├── services/             # 业务服务
│   │   ├── agents/               # Agent 架构实现
│   │   ├── mcp/                  # MCP 客户端
│   │   ├── rules/                # 规则引擎
│   │   ├── rag/                  # RAG 模块
│   │   └── skills/               # SKILL 管理
│   ├── tests/                    # 测试用例
│   ├── requirements.txt          # Python 依赖
│   └── main.py                   # 入口文件
│
└── frontend/                      # 前端代码
    ├── src/
    │   ├── api/                  # API 封装
    │   ├── assets/               # 静态资源
    │   ├── components/           # 公共组件
    │   ├── composables/          # 组合式函数
    │   ├── layouts/              # 布局组件
    │   ├── router/               # 路由配置
    │   ├── stores/               # 状态管理
    │   ├── views/                # 页面视图
    │   ├── App.vue               # 根组件
    │   └── main.ts               # 入口文件
    ├── package.json              # NPM 依赖
    └── vite.config.ts            # Vite 配置
```

## 许可证

MIT License

## 联系方式

- 项目维护：LunaDeerTech
- 问题反馈：通过 GitHub Issues
