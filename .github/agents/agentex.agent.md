---
description: 'Describe what this custom agent does and when to use it.'
tools: ['vscode', 'execute', 'read', 'edit', 'search', 'web', 'agent', 'ms-azuretools.vscode-containers/containerToolsConfig', 'ms-python.python/getPythonEnvironmentInfo', 'ms-python.python/getPythonExecutableCommand', 'ms-python.python/installPythonPackage', 'ms-python.python/configurePythonEnvironment', 'ms-toolsai.jupyter/configureNotebook', 'ms-toolsai.jupyter/listNotebookPackages', 'ms-toolsai.jupyter/installNotebookPackages', 'vscjava.vscode-java-debug/debugJavaApplication', 'vscjava.vscode-java-debug/setJavaBreakpoint', 'vscjava.vscode-java-debug/debugStepOperation', 'vscjava.vscode-java-debug/getDebugVariables', 'vscjava.vscode-java-debug/getDebugStackTrace', 'vscjava.vscode-java-debug/evaluateDebugExpression', 'vscjava.vscode-java-debug/getDebugThreads', 'vscjava.vscode-java-debug/removeJavaBreakpoints', 'vscjava.vscode-java-debug/stopDebugSession', 'vscjava.vscode-java-debug/getDebugSessionInfo', 'todo']
---
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