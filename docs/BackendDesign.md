# Agentex 后端模块设计

## 文档信息

| 项目 | 内容 |
|------|------|
| 产品名称 | Agentex |
| 版本 | 1.0.0 |
| 文档版本 | 1.0 |
| 更新日期 | 2026-02-03 |

---

## 1. 模块概述

后端采用分层架构设计，各层职责清晰，便于维护和扩展。

```
┌─────────────────────────────────────────────────────────────────┐
│                         API 层 (Presentation)                    │
│   负责：HTTP 路由、AG-UI 处理、请求验证、响应格式化              │
├─────────────────────────────────────────────────────────────────┤
│                         服务层 (Service)                         │
│   负责：业务逻辑处理、事务管理、服务编排                         │
├─────────────────────────────────────────────────────────────────┤
│                         领域层 (Domain)                          │
│   负责：Agent 架构实现、规则引擎、核心算法                       │
├─────────────────────────────────────────────────────────────────┤
│                         集成层 (Integration)                     │
│   负责：外部服务对接、LLM 客户端、MCP 客户端                     │
├─────────────────────────────────────────────────────────────────┤
│                         数据层 (Data)                            │
│   负责：数据持久化、ORM 映射、缓存管理                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. 核心模块设计

### 2.1 用户服务模块 (UserService)

#### 2.1.1 功能职责

- 用户注册、登录、登出
- 用户信息管理
- 密码管理
- API 密钥管理
- 用户权限查询

#### 2.1.2 核心接口

```
UserService
├── register(username, email, password) → User
│   └── 注册新用户，默认分配 user 角色
│
├── login(username, password) → TokenPair
│   └── 用户登录，返回 access_token 和 refresh_token
│
├── logout(user_id, token) → void
│   └── 用户登出，使 token 失效
│
├── refresh_token(refresh_token) → TokenPair
│   └── 刷新访问令牌
│
├── get_user(user_id) → User
│   └── 获取用户信息
│
├── update_user(user_id, data) → User
│   └── 更新用户信息
│
├── change_password(user_id, old_pwd, new_pwd) → void
│   └── 修改密码
│
├── create_api_key(user_id, name) → ApiKey
│   └── 创建 API 密钥
│
├── list_api_keys(user_id) → List[ApiKey]
│   └── 获取用户的 API 密钥列表
│
├── revoke_api_key(user_id, key_id) → void
│   └── 撤销 API 密钥
│
└── get_permissions(user_id) → List[Permission]
    └── 获取用户权限列表
```

#### 2.1.3 业务规则

| 规则 | 说明 |
|------|------|
| 用户名唯一 | 用户名不可重复 |
| 邮箱唯一 | 邮箱不可重复 |
| 密码强度 | 至少 8 位，包含字母和数字 |
| Token 有效期 | access_token: 30分钟，refresh_token: 7天 |
| API 密钥上限 | 每用户最多 10 个 API 密钥 |

---

### 2.2 会话服务模块 (SessionService)

#### 2.2.1 功能职责

- 对话会话的创建、管理
- 消息的存储和检索
- 会话配置管理

#### 2.2.2 核心接口

```
SessionService
├── create_session(user_id, title, config) → Session
│   └── 创建新会话
│
├── list_sessions(user_id, page, limit) → PagedList[Session]
│   └── 获取用户会话列表
│
├── get_session(session_id, user_id) → Session
│   └── 获取会话详情（验证所有权）
│
├── update_session(session_id, user_id, data) → Session
│   └── 更新会话信息
│
├── delete_session(session_id, user_id) → void
│   └── 删除会话
│
├── get_messages(session_id, user_id, page, limit) → PagedList[Message]
│   └── 获取会话消息历史
│
├── add_message(session_id, role, content, metadata) → Message
│   └── 添加消息到会话
│
└── update_session_config(session_id, user_id, config) → Session
    └── 更新会话配置
```

#### 2.2.3 会话配置结构

```
SessionConfig
├── agent_type: str              # Agent 架构类型
├── model_id: str                # 使用的模型 ID
├── knowledge_base_ids: List[str] # 启用的知识库
├── mcp_connection_ids: List[str] # 启用的 MCP 连接
├── skill_ids: List[str]         # 启用的 SKILL
├── temperature: float           # 温度参数
├── max_tokens: int              # 最大 Token 数
└── system_prompt: str           # 系统提示词
```

---

### 2.3 模型服务模块 (ModelService)

#### 2.3.1 功能职责

- LLM 模型配置管理
- 模型连接测试
- 模型调用统计

#### 2.3.2 核心接口

```
ModelService
├── create_model(data) → LLMModel
│   └── 创建模型配置（管理员）
│
├── list_models(user_id) → List[LLMModel]
│   └── 获取用户可用的模型列表
│
├── get_model(model_id) → LLMModel
│   └── 获取模型详情
│
├── update_model(model_id, data) → LLMModel
│   └── 更新模型配置（管理员）
│
├── delete_model(model_id) → void
│   └── 删除模型配置（管理员）
│
├── test_model(model_id) → TestResult
│   └── 测试模型连接
│
├── set_default_model(model_id) → void
│   └── 设置默认模型
│
└── get_client(model_id) → BaseLLMClient
    └── 获取模型客户端实例
```

#### 2.3.3 模型配置结构

```
LLMModelConfig
├── id: str                      # 模型 ID
├── name: str                    # 显示名称
├── provider: enum               # 提供商：openai/anthropic
├── base_url: str                # API 地址
├── api_key: str                 # API 密钥（加密存储）
├── model_id: str                # 模型标识
├── max_tokens: int              # 默认最大 Token
├── temperature: float           # 默认温度
├── enabled: bool                # 是否启用
├── is_default: bool             # 是否默认
└── allowed_roles: List[str]     # 允许使用的角色
```

---

### 2.4 MCP 服务模块 (MCPService)

#### 2.4.1 功能职责

- MCP 连接配置管理
- MCP 客户端生命周期管理
- 工具列表获取和调用
- WS-MCP 事件处理

#### 2.4.2 核心接口

```
MCPService
├── create_connection(data) → MCPConnection
│   └── 创建 MCP 连接配置
│
├── list_connections(user_id) → List[MCPConnection]
│   └── 获取用户可用的 MCP 连接列表
│
├── get_connection(conn_id) → MCPConnection
│   └── 获取连接详情
│
├── update_connection(conn_id, data) → MCPConnection
│   └── 更新连接配置
│
├── delete_connection(conn_id) → void
│   └── 删除连接配置
│
├── test_connection(conn_id) → TestResult
│   └── 测试连接
│
├── connect(conn_id) → void
│   └── 建立连接
│
├── disconnect(conn_id) → void
│   └── 断开连接
│
├── get_tools(conn_id) → List[Tool]
│   └── 获取可用工具列表
│
├── call_tool(conn_id, tool_name, params) → ToolResult
│   └── 调用工具
│
├── register_event_handler(conn_id, event_type, handler) → void
│   └── 注册事件处理器（WS-MCP）
│
└── get_client(conn_id) → BaseMCPClient
    └── 获取 MCP 客户端实例
```

#### 2.4.3 MCP 连接配置结构

**标准 MCP 连接：**
```
StandardMCPConnection
├── id: str
├── name: str
├── type: "standard"
├── url: str                     # HTTP SSE 地址
├── auth_type: enum              # none/bearer/basic
├── auth_token: str              # 认证令牌
├── enabled: bool
└── allowed_roles: List[str]
```

**WS-MCP 连接：**
```
WSMCPConnection
├── id: str
├── name: str
├── type: "websocket"
├── ws_url: str                  # WebSocket 地址
├── auth_token: str              # 认证令牌
├── heartbeat_interval: int      # 心跳间隔
├── reconnect_delay: int         # 重连延迟
├── max_retries: int             # 最大重试次数
├── enabled: bool
└── allowed_roles: List[str]
```

---

### 2.5 SKILL 服务模块 (SkillService)

#### 2.5.1 功能职责

- SKILL 的创建、管理
- SKILL 解析和验证
- SKILL 执行

#### 2.5.2 核心接口

```
SkillService
├── create_skill(user_id, data) → Skill
│   └── 创建 SKILL
│
├── list_skills(user_id, include_public) → List[Skill]
│   └── 获取 SKILL 列表
│
├── get_skill(skill_id, user_id) → Skill
│   └── 获取 SKILL 详情
│
├── update_skill(skill_id, user_id, data) → Skill
│   └── 更新 SKILL
│
├── delete_skill(skill_id, user_id) → void
│   └── 删除 SKILL
│
├── parse_skill(content) → SkillDefinition
│   └── 解析 SKILL Markdown 内容
│
├── validate_skill(skill_id) → ValidationResult
│   └── 验证 SKILL 定义
│
├── execute_skill(skill_id, params, context) → SkillResult
│   └── 执行 SKILL
│
└── export_skill(skill_id, user_id) → str
    └── 导出 SKILL 为 Markdown
```

#### 2.5.3 SKILL 数据结构

```
Skill
├── id: str
├── name: str
├── description: str
├── content: str                 # Markdown 内容
├── category: str                # 分类
├── tags: List[str]              # 标签
├── is_public: bool              # 是否公开
├── owner_id: str                # 所有者
├── version: int                 # 版本号
├── created_at: datetime
└── updated_at: datetime

SkillDefinition（解析后的结构）
├── name: str
├── description: str
├── trigger_conditions: List[str]
├── input_params: List[ParamDef]
├── steps: List[StepDef]
├── output_format: str
└── examples: List[str]
```

---

### 2.6 RAG 服务模块 (RAGService)

#### 2.6.1 功能职责

- 知识库的创建和管理
- 文档的上传和处理
- 文档向量化
- 相似度检索

#### 2.6.2 核心接口

```
RAGService
├── create_knowledge_base(user_id, data) → KnowledgeBase
│   └── 创建知识库
│
├── list_knowledge_bases(user_id) → List[KnowledgeBase]
│   └── 获取知识库列表
│
├── get_knowledge_base(kb_id, user_id) → KnowledgeBase
│   └── 获取知识库详情
│
├── update_knowledge_base(kb_id, user_id, data) → KnowledgeBase
│   └── 更新知识库配置
│
├── delete_knowledge_base(kb_id, user_id) → void
│   └── 删除知识库
│
├── upload_document(kb_id, user_id, file) → Document
│   └── 上传文档
│
├── list_documents(kb_id, user_id) → List[Document]
│   └── 获取文档列表
│
├── delete_document(kb_id, doc_id, user_id) → void
│   └── 删除文档
│
├── process_document(doc_id) → void
│   └── 处理文档（分块、向量化）- 异步任务
│
├── search(kb_ids, query, top_k) → List[SearchResult]
│   └── 相似度检索
│
└── get_document_status(doc_id) → DocumentStatus
    └── 获取文档处理状态
```

#### 2.6.3 知识库数据结构

```
KnowledgeBase
├── id: str
├── name: str
├── description: str
├── embedding_model: str         # 向量化模型
├── chunk_size: int              # 分块大小
├── chunk_overlap: int           # 分块重叠
├── is_public: bool              # 是否公开
├── owner_id: str                # 所有者
├── document_count: int          # 文档数量
├── enabled: bool
├── created_at: datetime
└── updated_at: datetime

Document
├── id: str
├── knowledge_base_id: str
├── name: str
├── file_path: str
├── file_type: str
├── file_size: int
├── status: enum                 # pending/processing/completed/failed
├── chunk_count: int             # 分块数量
├── error_message: str           # 错误信息
├── created_at: datetime
└── updated_at: datetime

SearchResult
├── document_id: str
├── document_name: str
├── chunk_id: str
├── content: str
├── score: float
└── metadata: dict
```

---

### 2.7 规则引擎模块 (RuleService)

#### 2.7.1 功能职责

- 规则的创建和管理
- 事件监听和规则匹配
- 规则条件评估
- 规则动作执行
- 执行日志记录

#### 2.7.2 核心接口

```
RuleService
├── create_rule(user_id, data) → Rule
│   └── 创建规则
│
├── list_rules(user_id) → List[Rule]
│   └── 获取规则列表
│
├── get_rule(rule_id, user_id) → Rule
│   └── 获取规则详情
│
├── update_rule(rule_id, user_id, data) → Rule
│   └── 更新规则
│
├── delete_rule(rule_id, user_id) → void
│   └── 删除规则
│
├── enable_rule(rule_id, user_id) → void
│   └── 启用规则
│
├── disable_rule(rule_id, user_id) → void
│   └── 禁用规则
│
├── test_rule(rule_id, test_event) → TestResult
│   └── 测试规则
│
├── get_logs(rule_id, user_id, page, limit) → PagedList[RuleLog]
│   └── 获取规则执行日志
│
└── process_event(event) → void
    └── 处理事件（内部方法）
```

#### 2.7.3 规则数据结构

```
Rule
├── id: str
├── name: str
├── description: str
├── enabled: bool
├── trigger: RuleTrigger
├── conditions: List[Condition]
├── actions: List[Action]
├── cooldown: int                # 冷却时间（毫秒）
├── last_triggered_at: datetime
├── owner_id: str
├── created_at: datetime
└── updated_at: datetime

RuleTrigger
├── event_type: str              # 事件类型
├── source: str                  # 事件来源（MCP 连接 ID）
└── filter: dict                 # 初步过滤条件

Condition
├── field: str                   # 字段路径
├── operator: enum               # 操作符
├── value: any                   # 比较值
└── logic: enum                  # AND/OR

Action
├── type: enum                   # mcp_call/skill_execute/notify/chain
├── target: str                  # 目标（工具名/SKILL ID等）
├── params: dict                 # 参数（支持模板变量）
└── on_error: enum               # continue/stop

RuleLog
├── id: str
├── rule_id: str
├── event: dict
├── conditions_met: bool
├── actions_executed: List[ActionResult]
├── status: enum                 # success/partial/failed
├── error_message: str
└── executed_at: datetime
```

#### 2.7.4 规则引擎处理流程

```
EventProcessor
│
├── 1. 接收事件
│   └── 从 WS-MCP 客户端接收事件通知
│
├── 2. 查找规则
│   ├── 根据事件类型和来源查找规则
│   └── 过滤已启用的规则
│
├── 3. 遍历规则
│   │
│   ├── 3.1 检查冷却
│   │   └── 判断是否在冷却期内
│   │
│   ├── 3.2 评估条件
│   │   ├── 解析条件表达式
│   │   ├── 从事件数据中提取字段值
│   │   └── 计算条件结果
│   │
│   └── 3.3 执行动作
│       ├── 模板变量替换
│       ├── 调用目标服务
│       └── 记录执行结果
│
├── 4. 更新状态
│   └── 更新规则的 last_triggered_at
│
└── 5. 记录日志
    └── 保存执行日志
```

---

## 3. Agent 架构模块设计

### 3.1 Agent 基类

```
BaseAgent (抽象类)
│
├── 属性
│   ├── llm_client: BaseLLMClient    # LLM 客户端
│   ├── tools: List[Tool]             # 可用工具
│   ├── knowledge_bases: List[str]    # 知识库 ID
│   ├── skills: List[Skill]           # 可用 SKILL
│   ├── config: AgentConfig           # Agent 配置
│   └── context: AgentContext         # 运行时上下文
│
├── 核心方法
│   ├── run(message, history) → AsyncGenerator
│   │   └── 执行入口，返回流式响应
│   │
│   ├── think(message, context) → ThinkResult [抽象]
│   │   └── 思考过程，由子类实现
│   │
│   ├── act(action) → ActionResult [抽象]
│   │   └── 执行动作，由子类实现
│   │
│   └── reflect(result) → ReflectResult [可选]
│       └── 反思过程，用于自我改进
│
└── 辅助方法
    ├── retrieve(query) → List[Document]
    │   └── RAG 检索
    │
    ├── call_tool(tool_name, params) → ToolResult
    │   └── 调用工具
    │
    ├── execute_skill(skill_id, params) → SkillResult
    │   └── 执行 SKILL
    │
    └── stream_response(content) → void
        └── 流式输出响应
```

### 3.2 ReAct Agent

ReAct (Reasoning and Acting) 是一种交替进行推理和行动的 Agent 架构。

```
ReActAgent extends BaseAgent
│
├── 核心循环
│   ├── Thought: 分析当前状态，决定下一步
│   ├── Action: 执行选定的动作
│   ├── Observation: 观察动作结果
│   └── 重复直到完成或达到最大步数
│
├── think(message, context)
│   ├── 构建提示词（包含工具描述、历史记录）
│   ├── 调用 LLM 获取思考结果
│   └── 解析决策（继续思考/调用工具/给出答案）
│
└── act(action)
    ├── 解析动作类型和参数
    ├── 调用对应服务执行
    └── 返回执行结果
```

**ReAct 提示词模板（伪代码）：**
```
你是一个智能助手，可以使用以下工具来帮助用户：

{工具列表描述}

请按照以下格式思考和行动：

Thought: 分析用户问题，思考需要做什么
Action: 选择要使用的工具 [tool_name]
Action Input: 工具的输入参数 {json}
Observation: 工具返回的结果

...（重复以上步骤）

Thought: 我现在知道最终答案了
Final Answer: 给用户的最终回答
```

### 3.3 AgenticRAG Agent

AgenticRAG 是增强了 RAG 能力的 Agent，能够主动决定何时检索知识库。

```
AgenticRAGAgent extends BaseAgent
│
├── 核心流程
│   ├── 1. 分析用户问题
│   ├── 2. 决定是否需要检索
│   ├── 3. 如需要，执行 RAG 检索
│   ├── 4. 结合检索结果回答
│   └── 5. 如不足，继续检索或使用工具
│
├── think(message, context)
│   ├── 判断是否需要检索
│   ├── 如需要，生成检索查询
│   └── 执行检索并整合结果
│
└── act(action)
    ├── 如果是检索动作，调用 RAG 服务
    └── 如果是工具动作，调用工具服务
```

### 3.4 PlanAndExecute Agent

计划执行 Agent 先制定计划，再逐步执行。

```
PlanAndExecuteAgent extends BaseAgent
│
├── 核心流程
│   ├── 1. 规划阶段：分解任务为子任务列表
│   ├── 2. 执行阶段：逐个执行子任务
│   ├── 3. 监控阶段：检查执行进度
│   └── 4. 调整阶段：根据结果调整计划
│
├── plan(message) → List[Task]
│   └── 生成执行计划
│
├── execute(task) → TaskResult
│   └── 执行单个任务
│
└── replan(results) → List[Task]
    └── 根据执行结果重新规划
```

### 3.5 Reflexion Agent

反思 Agent 具备自我改进能力。

```
ReflexionAgent extends BaseAgent
│
├── 核心流程
│   ├── 1. 初次尝试：执行任务
│   ├── 2. 评估结果：判断是否成功
│   ├── 3. 反思分析：分析失败原因
│   ├── 4. 改进策略：生成改进建议
│   └── 5. 重新尝试：应用改进再次执行
│
├── evaluate(result) → EvaluationResult
│   └── 评估执行结果
│
├── reflect(evaluation) → ReflectionResult
│   └── 反思并生成改进建议
│
└── retry(reflection) → Result
    └── 应用改进重新执行
```

### 3.6 Agent 工厂

```
AgentFactory
│
├── agents: Dict[str, Type[BaseAgent]]
│   └── 注册的 Agent 类型
│
├── register(agent_type, agent_class) → void
│   └── 注册新的 Agent 类型
│
├── create(agent_type, config) → BaseAgent
│   ├── 验证 agent_type 是否存在
│   ├── 创建 LLM 客户端
│   ├── 加载工具列表
│   ├── 加载知识库配置
│   ├── 加载 SKILL 列表
│   └── 实例化 Agent
│
└── list_types() → List[AgentTypeInfo]
    └── 获取支持的 Agent 类型列表
```

---

## 4. 集成模块设计

### 4.1 LLM 客户端

#### 4.1.1 基类设计

```
BaseLLMClient (抽象类)
│
├── chat(messages, tools, config) → Response
│   └── 同步对话
│
├── chat_stream(messages, tools, config) → AsyncGenerator
│   └── 流式对话
│
├── get_embeddings(texts) → List[List[float]]
│   └── 获取文本向量
│
└── validate_config() → bool
    └── 验证配置
```

#### 4.1.2 OpenAI 客户端

```
OpenAIClient extends BaseLLMClient
│
├── 配置
│   ├── base_url: str
│   ├── api_key: str
│   ├── model: str
│   ├── max_tokens: int
│   └── temperature: float
│
├── chat(messages, tools, config)
│   ├── 构建请求体
│   ├── 发送 HTTP 请求
│   └── 解析响应
│
└── chat_stream(messages, tools, config)
    ├── 构建流式请求
    └── 逐块解析 SSE 响应
```

#### 4.1.3 Anthropic 客户端

```
AnthropicClient extends BaseLLMClient
│
├── 配置
│   ├── base_url: str
│   ├── api_key: str
│   ├── model: str
│   ├── max_tokens: int
│   └── temperature: float
│
├── chat(messages, tools, config)
│   ├── 转换消息格式（适配 Anthropic API）
│   ├── 发送 HTTP 请求
│   └── 解析响应
│
└── chat_stream(messages, tools, config)
    ├── 构建流式请求
    └── 解析 SSE 响应
```

### 4.2 MCP 客户端

#### 4.2.1 标准 MCP 客户端

```
StandardMCPClient extends BaseMCPClient
│
├── 属性
│   ├── url: str
│   ├── auth_type: str
│   ├── auth_token: str
│   ├── session_id: str
│   └── tools: List[Tool]
│
├── connect()
│   ├── 发送 initialize 请求
│   ├── 处理 initialize 响应
│   ├── 发送 notifications/initialized
│   └── 保存 session_id
│
├── disconnect()
│   └── 关闭 SSE 连接
│
├── list_tools()
│   ├── 发送 tools/list 请求
│   └── 解析工具列表
│
└── call_tool(tool_name, params)
    ├── 发送 tools/call 请求
    └── 返回执行结果
```

#### 4.2.2 WS-MCP 客户端

```
WebSocketMCPClient extends BaseMCPClient
│
├── 属性
│   ├── ws_url: str
│   ├── auth_token: str
│   ├── session_id: str
│   ├── heartbeat_interval: int
│   ├── reconnect_delay: int
│   ├── max_retries: int
│   ├── websocket: WebSocket
│   ├── tools: List[Tool]
│   └── event_handlers: Dict[str, List[Callable]]
│
├── connect()
│   ├── 建立 WebSocket 连接
│   ├── 发送 auth 消息
│   ├── 等待 auth 响应
│   ├── 启动心跳任务
│   ├── 发送 MCP initialize
│   └── 启动消息监听循环
│
├── disconnect()
│   ├── 停止心跳任务
│   ├── 发送 close 消息
│   └── 关闭 WebSocket
│
├── list_tools()
│   ├── 发送 tools/list 请求
│   └── 等待并返回结果
│
├── call_tool(tool_name, params)
│   ├── 发送 tools/call 请求
│   └── 等待并返回结果
│
├── on_event(event_type, handler)
│   └── 注册事件处理器
│
├── _handle_message(message)
│   ├── 解析消息类型
│   ├── 处理 ping → 发送 pong
│   ├── 处理 message → 分发到对应处理器
│   └── 处理 event → 触发事件处理器
│
├── _heartbeat_loop()
│   └── 定期检查 pong 响应
│
└── _reconnect()
    └── 断线重连逻辑
```

### 4.3 向量存储客户端

```
BaseVectorStore (抽象类)
│
├── create_collection(name, dimension) → void
│   └── 创建集合
│
├── drop_collection(name) → void
│   └── 删除集合
│
├── insert(collection, vectors, metadata) → List[str]
│   └── 插入向量
│
├── search(collection, query_vector, top_k) → List[SearchResult]
│   └── 相似度搜索
│
├── delete(collection, ids) → void
│   └── 删除向量
│
└── get_collection_info(name) → CollectionInfo
    └── 获取集合信息

MilvusStore extends BaseVectorStore
QdrantStore extends BaseVectorStore
```

---

## 5. AG-UI 处理模块

本系统采用 AG-UI（Agent-User Interaction Protocol）协议实现 Agent 与前端的通信。AG-UI 是一个开放的、事件驱动的协议，基于 HTTP SSE 实现流式响应。

### 5.1 AG-UI 端点处理

```
AGUIHandler
│
├── run_agent(input: RunAgentInput, request: Request) → StreamingResponse
│   ├── 验证 Token 和权限
│   ├── 解析 RunAgentInput 请求体
│   ├── 获取 forwarded_props 中的 Agent 配置
│   ├── 创建 Agent 实例
│   ├── 执行 Agent.run() 并生成事件流
│   └── 返回 SSE StreamingResponse
│
├── stop_run(run_id, user_id) → void
│   └── 停止指定的运行
│
└── active_runs: Dict[str, AgentRun]
    └── run_id → AgentRun 实例映射
```

### 5.2 事件生成器

```
AGUIEventGenerator
│
├── encoder: EventEncoder
│   └── 事件编码器（SSE 或 Binary 格式）
│
├── emit_run_started(thread_id, run_id) → bytes
│   └── 发射 RUN_STARTED 事件
│
├── emit_run_finished(thread_id, run_id, result) → bytes
│   └── 发射 RUN_FINISHED 事件
│
├── emit_run_error(message, code) → bytes
│   └── 发射 RUN_ERROR 事件
│
├── emit_step_started(step_name) → bytes
│   └── 发射 STEP_STARTED 事件（用于思考过程）
│
├── emit_step_finished(step_name) → bytes
│   └── 发射 STEP_FINISHED 事件
│
├── emit_text_message_start(message_id, role) → bytes
│   └── 发射 TEXT_MESSAGE_START 事件
│
├── emit_text_message_content(message_id, delta) → bytes
│   └── 发射 TEXT_MESSAGE_CONTENT 事件（流式文本）
│
├── emit_text_message_end(message_id) → bytes
│   └── 发射 TEXT_MESSAGE_END 事件
│
├── emit_tool_call_start(tool_call_id, tool_name, parent_msg_id) → bytes
│   └── 发射 TOOL_CALL_START 事件
│
├── emit_tool_call_args(tool_call_id, delta) → bytes
│   └── 发射 TOOL_CALL_ARGS 事件
│
├── emit_tool_call_end(tool_call_id) → bytes
│   └── 发射 TOOL_CALL_END 事件
│
├── emit_tool_call_result(message_id, tool_call_id, content) → bytes
│   └── 发射 TOOL_CALL_RESULT 事件
│
├── emit_state_snapshot(snapshot) → bytes
│   └── 发射 STATE_SNAPSHOT 事件
│
└── emit_state_delta(delta) → bytes
    └── 发射 STATE_DELTA 事件（JSON Patch 格式）
```

### 5.3 AG-UI 事件类型

| 事件类型 | 说明 | 用途 |
|---------|------|------|
| RUN_STARTED | 运行开始 | 标识 Agent 执行开始 |
| RUN_FINISHED | 运行完成 | 标识 Agent 执行成功结束 |
| RUN_ERROR | 运行错误 | 标识 Agent 执行出错 |
| STEP_STARTED | 步骤开始 | 思考过程开始 |
| STEP_FINISHED | 步骤结束 | 思考过程结束 |
| TEXT_MESSAGE_START | 消息开始 | 开始一条新消息 |
| TEXT_MESSAGE_CONTENT | 消息内容 | 流式文本片段 |
| TEXT_MESSAGE_END | 消息结束 | 消息发送完毕 |
| TOOL_CALL_START | 工具调用开始 | 开始调用工具 |
| TOOL_CALL_ARGS | 工具参数 | 流式工具参数 |
| TOOL_CALL_END | 工具调用结束 | 工具参数发送完毕 |
| TOOL_CALL_RESULT | 工具结果 | 工具执行结果 |
| STATE_SNAPSHOT | 状态快照 | 完整状态 |
| STATE_DELTA | 状态增量 | 增量状态更新 |

### 5.4 AG-UI 与 Agent 集成

```
# Agent 执行流程伪代码

async def run_agent_with_agui(input: RunAgentInput) → AsyncGenerator[bytes, None]:
    encoder = EventEncoder(accept="text/event-stream")
    
    # 1. 运行开始
    yield encoder.encode(RunStartedEvent(
        type=EventType.RUN_STARTED,
        thread_id=input.thread_id,
        run_id=input.run_id
    ))
    
    # 2. 创建 Agent 并执行
    agent = AgentFactory.create(input.forwarded_props.agent_type)
    
    async for event in agent.run_stream(input):
        if event.type == "thinking":
            yield encoder.encode(StepStartedEvent(step_name="thinking"))
            yield encoder.encode(TextMessageStartEvent(...))
            for chunk in event.content:
                yield encoder.encode(TextMessageContentEvent(delta=chunk))
            yield encoder.encode(TextMessageEndEvent(...))
            yield encoder.encode(StepFinishedEvent(step_name="thinking"))
        
        elif event.type == "tool_call":
            yield encoder.encode(ToolCallStartEvent(...))
            yield encoder.encode(ToolCallArgsEvent(...))
            yield encoder.encode(ToolCallEndEvent(...))
            # 执行工具
            result = await execute_tool(event.tool_name, event.args)
            yield encoder.encode(ToolCallResultEvent(content=result))
        
        elif event.type == "response":
            yield encoder.encode(TextMessageStartEvent(role="assistant"))
            for chunk in event.content:
                yield encoder.encode(TextMessageContentEvent(delta=chunk))
            yield encoder.encode(TextMessageEndEvent(...))
    
    # 3. 运行结束
    yield encoder.encode(RunFinishedEvent(
        type=EventType.RUN_FINISHED,
        thread_id=input.thread_id,
        run_id=input.run_id,
        result={"usage": {...}}
    ))
```

---

## 6. 依赖注入与配置

### 6.1 依赖注入

使用 FastAPI 的依赖注入系统：

```
# 数据库会话
async def get_db() → AsyncSession:
    async with async_session() as session:
        yield session

# 当前用户
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) → User:
    # 验证 Token，返回用户

# 权限检查
def require_permission(permission: str):
    async def checker(user: User = Depends(get_current_user)):
        if permission not in user.permissions:
            raise HTTPException(403)
        return user
    return checker

# 服务实例
def get_user_service(db: AsyncSession = Depends(get_db)) → UserService:
    return UserService(db)
```

### 6.2 配置管理

```
Settings (Pydantic BaseSettings)
│
├── 数据库配置
│   ├── DATABASE_URL: str
│   └── DATABASE_POOL_SIZE: int
│
├── Redis 配置
│   ├── REDIS_URL: str
│   └── REDIS_MAX_CONNECTIONS: int
│
├── 向量数据库配置
│   ├── VECTOR_DB_TYPE: str  # milvus/qdrant
│   ├── VECTOR_DB_HOST: str
│   └── VECTOR_DB_PORT: int
│
├── 安全配置
│   ├── SECRET_KEY: str
│   ├── JWT_ALGORITHM: str
│   ├── ACCESS_TOKEN_EXPIRE_MINUTES: int
│   └── REFRESH_TOKEN_EXPIRE_DAYS: int
│
├── 文件存储配置
│   ├── STORAGE_TYPE: str  # local/minio
│   ├── STORAGE_PATH: str
│   └── MINIO_*: ...
│
└── 其他配置
    ├── DEBUG: bool
    ├── LOG_LEVEL: str
    └── CORS_ORIGINS: List[str]
```

---

## 7. 错误处理

### 7.1 异常层级

```
AgentexException (基础异常)
├── AuthenticationError          # 认证错误
├── AuthorizationError           # 授权错误
├── ValidationError              # 验证错误
├── NotFoundError                # 资源不存在
├── ConflictError                # 资源冲突
├── ExternalServiceError         # 外部服务错误
│   ├── LLMServiceError          # LLM 服务错误
│   ├── MCPServiceError          # MCP 服务错误
│   └── VectorDBError            # 向量数据库错误
└── InternalError                # 内部错误
```

### 7.2 全局异常处理

```
@app.exception_handler(AgentexException)
async def agentex_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )
```

---

## 8. 附录

### 8.1 相关文档

- [产品需求文档](./ProductRequirements.md)
- [系统架构设计](./SystemArchitecture.md)
- [前端界面设计](./FrontendDesign.md)
- [数据库设计](./DatabaseDesign.md)
- [API 接口设计](./APIDesign.md)
- [开发计划](./DevelopmentPlan.md)
