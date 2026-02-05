# Agentex 数据库设计

## 文档信息

| 项目 | 内容 |
|------|------|
| 产品名称 | Agentex |
| 版本 | 1.0.0 |
| 文档版本 | 1.0 |
| 更新日期 | 2026-02-03 |

---

## 1. 数据库概述

### 1.1 数据库选型

| 数据库 | 用途 | 说明 |
|--------|------|------|
| PostgreSQL | 主数据库 | 存储用户、会话、配置等结构化数据 |
| Redis | 缓存 | 会话缓存、Token 黑名单、实时状态 |
| Milvus/Qdrant | 向量数据库 | RAG 文档向量存储和检索 |

### 1.2 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 表名 | 小写，下划线分隔，复数 | `users`, `chat_sessions` |
| 字段名 | 小写，下划线分隔 | `created_at`, `user_id` |
| 主键 | `id`，UUID 类型 | `id` |
| 外键 | `<关联表单数>_id` | `user_id`, `session_id` |
| 索引 | `idx_<表名>_<字段名>` | `idx_users_email` |
| 唯一约束 | `uq_<表名>_<字段名>` | `uq_users_email` |

### 1.3 公共字段

所有表都包含以下公共字段：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | UUID | 主键 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

---

## 2. 用户模块

### 2.1 users 表（用户表）

存储系统用户信息。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 用户 ID |
| username | VARCHAR(50) | UNIQUE, NOT NULL | 用户名 |
| email | VARCHAR(255) | UNIQUE, NOT NULL | 邮箱 |
| password_hash | VARCHAR(255) | NOT NULL | 密码哈希 |
| avatar_url | VARCHAR(500) | | 头像 URL |
| role_id | UUID | FK → roles.id | 角色 ID |
| status | VARCHAR(20) | DEFAULT 'active' | 状态：active/disabled |
| last_login_at | TIMESTAMP | | 最后登录时间 |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT NOW() | 更新时间 |

**索引：**
- `idx_users_email` ON (email)
- `idx_users_username` ON (username)
- `idx_users_role_id` ON (role_id)

### 2.2 roles 表（角色表）

存储用户角色定义。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 角色 ID |
| name | VARCHAR(50) | UNIQUE, NOT NULL | 角色名称 |
| display_name | VARCHAR(100) | NOT NULL | 显示名称 |
| description | TEXT | | 角色描述 |
| is_system | BOOLEAN | DEFAULT FALSE | 是否系统内置 |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT NOW() | 更新时间 |

**预置数据：**
| name | display_name | description |
|------|--------------|-------------|
| admin | 超级管理员 | 拥有所有权限 |
| manager | 管理员 | 可管理用户和配置 |
| developer | 开发者 | 可管理资源和规则 |
| user | 普通用户 | 仅可使用 Agent |

### 2.3 permissions 表（权限表）

存储权限定义。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 权限 ID |
| module | VARCHAR(50) | NOT NULL | 模块名称 |
| action | VARCHAR(50) | NOT NULL | 操作类型 |
| name | VARCHAR(100) | UNIQUE, NOT NULL | 权限标识 |
| description | TEXT | | 权限描述 |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |

**预置数据示例：**
| module | action | name |
|--------|--------|------|
| models | view | models:view |
| models | create | models:create |
| models | edit | models:edit |
| models | delete | models:delete |
| mcp | view | mcp:view |
| ... | ... | ... |

### 2.4 role_permissions 表（角色权限关联表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 主键 |
| role_id | UUID | FK → roles.id | 角色 ID |
| permission_id | UUID | FK → permissions.id | 权限 ID |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |

**约束：**
- UNIQUE (role_id, permission_id)

### 2.5 user_permissions 表（用户自定义权限表）

存储用户的额外权限（覆盖角色权限）。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 主键 |
| user_id | UUID | FK → users.id | 用户 ID |
| permission_id | UUID | FK → permissions.id | 权限 ID |
| granted | BOOLEAN | NOT NULL | 是否授予（true=授予，false=撤销） |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |

### 2.6 api_keys 表（API 密钥表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 密钥 ID |
| user_id | UUID | FK → users.id | 用户 ID |
| name | VARCHAR(100) | NOT NULL | 密钥名称 |
| key_hash | VARCHAR(255) | NOT NULL | 密钥哈希 |
| key_prefix | VARCHAR(10) | NOT NULL | 密钥前缀（用于展示） |
| last_used_at | TIMESTAMP | | 最后使用时间 |
| expires_at | TIMESTAMP | | 过期时间 |
| status | VARCHAR(20) | DEFAULT 'active' | 状态：active/revoked |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |

**索引：**
- `idx_api_keys_user_id` ON (user_id)
- `idx_api_keys_key_hash` ON (key_hash)

---

## 3. 会话模块

### 3.1 chat_sessions 表（对话会话表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 会话 ID |
| user_id | UUID | FK → users.id, NOT NULL | 用户 ID |
| title | VARCHAR(200) | | 会话标题 |
| config | JSONB | | 会话配置 |
| message_count | INTEGER | DEFAULT 0 | 消息数量 |
| last_message_at | TIMESTAMP | | 最后消息时间 |
| is_archived | BOOLEAN | DEFAULT FALSE | 是否归档 |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT NOW() | 更新时间 |

**config JSONB 结构：**
```json
{
  "agent_type": "react",
  "model_id": "uuid",
  "knowledge_base_ids": ["uuid1", "uuid2"],
  "mcp_connection_ids": ["uuid1"],
  "skill_ids": ["uuid1"],
  "temperature": 0.7,
  "max_tokens": 4096,
  "system_prompt": "..."
}
```

**索引：**
- `idx_chat_sessions_user_id` ON (user_id)
- `idx_chat_sessions_user_updated` ON (user_id, updated_at DESC)

### 3.2 chat_messages 表（对话消息表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 消息 ID |
| session_id | UUID | FK → chat_sessions.id, NOT NULL | 会话 ID |
| parent_id | UUID | FK → chat_messages.id | 父消息 ID（用于回复链） |
| role | VARCHAR(20) | NOT NULL | 角色：user/assistant/system |
| content | TEXT | | 消息内容 |
| content_type | VARCHAR(20) | DEFAULT 'text' | 内容类型：text/markdown |
| metadata | JSONB | | 元数据 |
| token_count | INTEGER | | Token 数量 |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |

**metadata JSONB 结构（assistant 消息）：**
```json
{
  "model_id": "uuid",
  "agent_type": "react",
  "thinking": [...],
  "tool_calls": [...],
  "retrievals": [...],
  "finish_reason": "stop",
  "usage": {
    "prompt_tokens": 100,
    "completion_tokens": 50
  }
}
```

**索引：**
- `idx_chat_messages_session_id` ON (session_id)
- `idx_chat_messages_session_created` ON (session_id, created_at)

### 3.3 message_attachments 表（消息附件表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 附件 ID |
| message_id | UUID | FK → chat_messages.id, NOT NULL | 消息 ID |
| file_name | VARCHAR(255) | NOT NULL | 文件名 |
| file_path | VARCHAR(500) | NOT NULL | 文件路径 |
| file_type | VARCHAR(50) | | 文件类型 |
| file_size | BIGINT | | 文件大小（字节） |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |

---

## 4. 模型模块

### 4.1 llm_models 表（LLM 模型配置表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 模型 ID |
| name | VARCHAR(100) | NOT NULL | 模型名称 |
| provider | VARCHAR(20) | NOT NULL | 提供商：openai/anthropic |
| base_url | VARCHAR(500) | NOT NULL | API 地址 |
| api_key_encrypted | TEXT | NOT NULL | 加密后的 API 密钥 |
| model_id | VARCHAR(100) | NOT NULL | 模型标识 |
| max_tokens | INTEGER | DEFAULT 4096 | 默认最大 Token |
| temperature | DECIMAL(3,2) | DEFAULT 0.70 | 默认温度 |
| extra_config | JSONB | | 额外配置 |
| enabled | BOOLEAN | DEFAULT TRUE | 是否启用 |
| is_default | BOOLEAN | DEFAULT FALSE | 是否默认 |
| created_by | UUID | FK → users.id | 创建者 |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT NOW() | 更新时间 |

**索引：**
- `idx_llm_models_enabled` ON (enabled)

### 4.2 model_user_access 表（模型用户访问权限表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 主键 |
| model_id | UUID | FK → llm_models.id | 模型 ID |
| user_id | UUID | FK → users.id | 用户 ID |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |

**约束：**
- UNIQUE (model_id, user_id)

### 4.3 model_role_access 表（模型角色访问权限表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 主键 |
| model_id | UUID | FK → llm_models.id | 模型 ID |
| role_id | UUID | FK → roles.id | 角色 ID |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |

**约束：**
- UNIQUE (model_id, role_id)

---

## 5. MCP 模块

### 5.1 mcp_connections 表（MCP 连接配置表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 连接 ID |
| name | VARCHAR(100) | NOT NULL | 连接名称 |
| type | VARCHAR(20) | NOT NULL | 类型：standard/websocket |
| url | VARCHAR(500) | NOT NULL | 连接地址 |
| auth_type | VARCHAR(20) | | 认证类型：none/bearer/basic |
| auth_token_encrypted | TEXT | | 加密后的认证令牌 |
| config | JSONB | | 额外配置 |
| enabled | BOOLEAN | DEFAULT TRUE | 是否启用 |
| created_by | UUID | FK → users.id | 创建者 |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT NOW() | 更新时间 |

**config JSONB 结构（WebSocket 类型）：**
```json
{
  "heartbeat_interval": 30000,
  "reconnect_delay": 5000,
  "max_retries": 3
}
```

### 5.2 mcp_tools 表（MCP 工具缓存表）

缓存从 MCP Server 获取的工具列表。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 工具 ID |
| connection_id | UUID | FK → mcp_connections.id | 连接 ID |
| name | VARCHAR(100) | NOT NULL | 工具名称 |
| description | TEXT | | 工具描述 |
| input_schema | JSONB | | 输入参数 Schema |
| cached_at | TIMESTAMP | DEFAULT NOW() | 缓存时间 |

**约束：**
- UNIQUE (connection_id, name)

### 5.3 mcp_user_access 表（MCP 用户访问权限表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 主键 |
| connection_id | UUID | FK → mcp_connections.id | 连接 ID |
| user_id | UUID | FK → users.id | 用户 ID |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |

---

## 6. SKILL 模块

### 6.1 skills 表（SKILL 技能表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | SKILL ID |
| name | VARCHAR(100) | NOT NULL | SKILL 名称 |
| description | TEXT | | SKILL 描述 |
| content | TEXT | NOT NULL | Markdown 内容 |
| category | VARCHAR(50) | | 分类 |
| is_public | BOOLEAN | DEFAULT FALSE | 是否公开 |
| version | INTEGER | DEFAULT 1 | 版本号 |
| owner_id | UUID | FK → users.id, NOT NULL | 所有者 |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT NOW() | 更新时间 |

**索引：**
- `idx_skills_owner_id` ON (owner_id)
- `idx_skills_is_public` ON (is_public)

### 6.2 skill_tags 表（SKILL 标签表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 标签 ID |
| name | VARCHAR(50) | UNIQUE, NOT NULL | 标签名称 |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |

### 6.3 skill_tag_relations 表（SKILL 标签关联表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 主键 |
| skill_id | UUID | FK → skills.id | SKILL ID |
| tag_id | UUID | FK → skill_tags.id | 标签 ID |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |

**约束：**
- UNIQUE (skill_id, tag_id)

### 6.4 skill_versions 表（SKILL 版本历史表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 版本 ID |
| skill_id | UUID | FK → skills.id | SKILL ID |
| version | INTEGER | NOT NULL | 版本号 |
| content | TEXT | NOT NULL | 版本内容 |
| change_note | TEXT | | 变更说明 |
| created_by | UUID | FK → users.id | 创建者 |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |

---

## 7. 自定义 Agent 模块

### 7.1 custom_agents 表（自定义 Agent 表）

存储用户自定义的 Agent 配置，允许用户预设 Agent 架构、系统提示词和默认资源。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | Agent ID |
| name | VARCHAR(100) | NOT NULL | Agent 名称 |
| description | TEXT | | Agent 描述 |
| agent_type | VARCHAR(50) | NOT NULL | Agent 架构类型：react/agentic_rag/plan_execute |
| system_prompt | TEXT | | 系统提示词 |
| icon | VARCHAR(100) | | Agent 图标（emoji 或图标名） |
| is_default | BOOLEAN | DEFAULT FALSE | 是否为系统默认 Agent |
| enabled | BOOLEAN | DEFAULT TRUE | 是否启用 |
| owner_id | UUID | FK → users.id | 所有者（系统默认时为 NULL） |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT NOW() | 更新时间 |

**索引：**
- `idx_custom_agents_owner_id` ON (owner_id)
- `idx_custom_agents_is_default` ON (is_default)
- `idx_custom_agents_agent_type` ON (agent_type)

**预置数据（系统默认 Agent）：**
| name | agent_type | description | is_default |
|------|------------|-------------|------------|
| ReAct Agent | react | 支持多轮思考和工具调用的通用 Agent | TRUE |
| RAG Agent | agentic_rag | 专注于知识库检索的 Agent | TRUE |
| Plan & Execute Agent | plan_execute | 先规划后执行的任务分解 Agent | TRUE |

### 7.2 agent_knowledge_bases 表（Agent 关联知识库表）

存储 Agent 默认关联的知识库。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 主键 |
| agent_id | UUID | FK → custom_agents.id, NOT NULL | Agent ID |
| knowledge_base_id | UUID | FK → knowledge_bases.id, NOT NULL | 知识库 ID |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |

**约束：**
- UNIQUE (agent_id, knowledge_base_id)
- ON DELETE CASCADE (agent_id, knowledge_base_id)

### 7.3 agent_mcp_connections 表（Agent 关联 MCP 连接表）

存储 Agent 默认关联的 MCP 连接。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 主键 |
| agent_id | UUID | FK → custom_agents.id, NOT NULL | Agent ID |
| mcp_connection_id | UUID | FK → mcp_connections.id, NOT NULL | MCP 连接 ID |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |

**约束：**
- UNIQUE (agent_id, mcp_connection_id)
- ON DELETE CASCADE (agent_id, mcp_connection_id)

### 7.4 agent_skills 表（Agent 关联 SKILL 表）

存储 Agent 默认关联的 SKILL。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 主键 |
| agent_id | UUID | FK → custom_agents.id, NOT NULL | Agent ID |
| skill_id | UUID | FK → skills.id, NOT NULL | SKILL ID |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |

**约束：**
- UNIQUE (agent_id, skill_id)
- ON DELETE CASCADE (agent_id, skill_id)

---

## 8. 知识库模块

### 8.1 knowledge_bases 表（知识库表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 知识库 ID |
| name | VARCHAR(100) | NOT NULL | 知识库名称 |
| description | TEXT | | 知识库描述 |
| embedding_model | VARCHAR(100) | NOT NULL | 向量化模型 |
| chunk_size | INTEGER | DEFAULT 500 | 分块大小 |
| chunk_overlap | INTEGER | DEFAULT 50 | 分块重叠 |
| vector_collection | VARCHAR(100) | NOT NULL | 向量集合名称 |
| document_count | INTEGER | DEFAULT 0 | 文档数量 |
| is_public | BOOLEAN | DEFAULT FALSE | 是否公开 |
| enabled | BOOLEAN | DEFAULT TRUE | 是否启用 |
| owner_id | UUID | FK → users.id, NOT NULL | 所有者 |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT NOW() | 更新时间 |

**索引：**
- `idx_knowledge_bases_owner_id` ON (owner_id)

### 8.2 kb_documents 表（知识库文档表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 文档 ID |
| knowledge_base_id | UUID | FK → knowledge_bases.id | 知识库 ID |
| name | VARCHAR(255) | NOT NULL | 文档名称 |
| file_path | VARCHAR(500) | NOT NULL | 文件路径 |
| file_type | VARCHAR(50) | | 文件类型 |
| file_size | BIGINT | | 文件大小（字节） |
| status | VARCHAR(20) | DEFAULT 'pending' | 状态 |
| chunk_count | INTEGER | DEFAULT 0 | 分块数量 |
| error_message | TEXT | | 错误信息 |
| processed_at | TIMESTAMP | | 处理完成时间 |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT NOW() | 更新时间 |

**status 枚举值：**
- pending：待处理
- processing：处理中
- completed：已完成
- failed：处理失败

**索引：**
- `idx_kb_documents_knowledge_base_id` ON (knowledge_base_id)
- `idx_kb_documents_status` ON (status)

### 8.3 kb_chunks 表（知识库分块表）

存储文档分块的元数据（向量存储在 Milvus/Qdrant）。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 分块 ID |
| document_id | UUID | FK → kb_documents.id | 文档 ID |
| chunk_index | INTEGER | NOT NULL | 分块索引 |
| content | TEXT | NOT NULL | 分块内容 |
| metadata | JSONB | | 元数据 |
| vector_id | VARCHAR(100) | | 向量数据库中的 ID |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |

**索引：**
- `idx_kb_chunks_document_id` ON (document_id)
- `idx_kb_chunks_vector_id` ON (vector_id)

---

## 9. 规则引擎模块

### 9.1 rules 表（规则表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 规则 ID |
| name | VARCHAR(100) | NOT NULL | 规则名称 |
| description | TEXT | | 规则描述 |
| trigger_config | JSONB | NOT NULL | 触发配置 |
| conditions | JSONB | | 条件配置 |
| actions | JSONB | NOT NULL | 动作配置 |
| cooldown | INTEGER | DEFAULT 0 | 冷却时间（毫秒） |
| enabled | BOOLEAN | DEFAULT TRUE | 是否启用 |
| last_triggered_at | TIMESTAMP | | 最后触发时间 |
| trigger_count | INTEGER | DEFAULT 0 | 触发次数 |
| owner_id | UUID | FK → users.id, NOT NULL | 所有者 |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT NOW() | 更新时间 |

**trigger_config JSONB 结构：**
```json
{
  "event_type": "player_join",
  "source_id": "mcp-connection-uuid",
  "filter": {}
}
```

**conditions JSONB 结构：**
```json
[
  {
    "field": "player.name",
    "operator": "!=",
    "value": "admin",
    "logic": "AND"
  }
]
```

**actions JSONB 结构：**
```json
[
  {
    "type": "mcp_call",
    "target": "chat_broadcast",
    "params": {
      "message": "欢迎 {{player.name}} 进入游戏！"
    },
    "on_error": "continue"
  }
]
```

**索引：**
- `idx_rules_owner_id` ON (owner_id)
- `idx_rules_enabled` ON (enabled)

### 9.2 rule_logs 表（规则执行日志表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 日志 ID |
| rule_id | UUID | FK → rules.id | 规则 ID |
| event_data | JSONB | | 触发事件数据 |
| conditions_met | BOOLEAN | | 条件是否满足 |
| actions_result | JSONB | | 动作执行结果 |
| status | VARCHAR(20) | NOT NULL | 状态 |
| error_message | TEXT | | 错误信息 |
| execution_time | INTEGER | | 执行耗时（毫秒） |
| executed_at | TIMESTAMP | DEFAULT NOW() | 执行时间 |

**status 枚举值：**
- success：成功
- partial：部分成功
- failed：失败
- skipped：跳过（条件不满足）

**索引：**
- `idx_rule_logs_rule_id` ON (rule_id)
- `idx_rule_logs_executed_at` ON (executed_at DESC)

---

## 10. 系统模块

### 10.1 system_configs 表（系统配置表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 配置 ID |
| key | VARCHAR(100) | UNIQUE, NOT NULL | 配置键 |
| value | JSONB | NOT NULL | 配置值 |
| description | TEXT | | 配置描述 |
| is_public | BOOLEAN | DEFAULT FALSE | 是否公开（前端可读） |
| updated_by | UUID | FK → users.id | 更新者 |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT NOW() | 更新时间 |

### 10.2 operation_logs 表（操作日志表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 日志 ID |
| user_id | UUID | FK → users.id | 操作用户 |
| action | VARCHAR(50) | NOT NULL | 操作类型 |
| resource_type | VARCHAR(50) | NOT NULL | 资源类型 |
| resource_id | UUID | | 资源 ID |
| details | JSONB | | 操作详情 |
| ip_address | VARCHAR(45) | | IP 地址 |
| user_agent | TEXT | | User Agent |
| created_at | TIMESTAMP | DEFAULT NOW() | 操作时间 |

**索引：**
- `idx_operation_logs_user_id` ON (user_id)
- `idx_operation_logs_created_at` ON (created_at DESC)
- `idx_operation_logs_resource` ON (resource_type, resource_id)

---

## 11. Redis 数据结构

### 11.1 会话缓存

| Key 模式 | 类型 | TTL | 说明 |
|---------|------|-----|------|
| `user:session:{user_id}` | String | 30min | 用户会话信息 |
| `token:blacklist:{token_jti}` | String | 7d | Token 黑名单 |
| `user:permissions:{user_id}` | Hash | 5min | 用户权限缓存 |

### 11.2 实时状态

| Key 模式 | 类型 | TTL | 说明 |
|---------|------|-----|------|
| `ws:connection:{user_id}` | String | - | WebSocket 连接状态 |
| `mcp:status:{connection_id}` | Hash | - | MCP 连接状态 |
| `agent:task:{session_id}` | Hash | 1h | Agent 任务状态 |

### 11.3 规则引擎

| Key 模式 | 类型 | TTL | 说明 |
|---------|------|-----|------|
| `rule:cooldown:{rule_id}` | String | 动态 | 规则冷却状态 |
| `rule:event_mapping:{event_type}` | Set | - | 事件类型到规则 ID 的映射 |

### 11.4 限流

| Key 模式 | 类型 | TTL | 说明 |
|---------|------|-----|------|
| `ratelimit:api:{user_id}:{endpoint}` | String | 1min | API 限流计数 |
| `ratelimit:login:{ip}` | String | 5min | 登录限流计数 |

---

## 12. 向量数据库结构

### 12.1 Milvus Collection 设计

**知识库向量集合：**

```
Collection: kb_{knowledge_base_id}

字段：
- id: VARCHAR(36)       # 分块 ID（对应 kb_chunks.id）
- document_id: VARCHAR(36)  # 文档 ID
- chunk_index: INT64    # 分块索引
- content: VARCHAR(8192) # 分块内容
- vector: FLOAT_VECTOR[1536]  # 向量（维度取决于模型）

索引：
- vector 字段：IVF_FLAT 索引，nlist=1024
```

### 12.2 Qdrant Collection 设计（备选）

```
Collection: kb_{knowledge_base_id}

Vector Config:
- size: 1536 (或根据模型确定)
- distance: Cosine

Payload:
- document_id: string
- chunk_index: integer
- content: string
- metadata: object
```

---

## 13. ER 图

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                   用户模块                                       │
│                                                                                  │
│  ┌─────────┐     ┌─────────┐     ┌─────────────────┐     ┌─────────────┐       │
│  │  users  │────►│  roles  │◄────│ role_permissions│────►│ permissions │       │
│  └────┬────┘     └─────────┘     └─────────────────┘     └─────────────┘       │
│       │                                                          ▲              │
│       │          ┌─────────────────┐                             │              │
│       └─────────►│ user_permissions│─────────────────────────────┘              │
│       │          └─────────────────┘                                            │
│       │                                                                          │
│       │          ┌─────────┐                                                    │
│       └─────────►│ api_keys│                                                    │
│                  └─────────┘                                                    │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                                   会话模块                                       │
│                                                                                  │
│  ┌───────────────┐     ┌───────────────┐     ┌─────────────────────┐           │
│  │ chat_sessions │────►│ chat_messages │────►│ message_attachments │           │
│  └───────┬───────┘     └───────────────┘     └─────────────────────┘           │
│          │                                                                       │
│          └── FK: user_id → users.id                                             │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                                   模型模块                                       │
│                                                                                  │
│  ┌────────────┐     ┌───────────────────┐     ┌───────────────────┐            │
│  │ llm_models │────►│ model_user_access │     │ model_role_access │            │
│  └────────────┘     └───────────────────┘     └───────────────────┘            │
│                              │                        │                         │
│                              └── FK: user_id ─────────┴── FK: role_id          │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                                   MCP 模块                                       │
│                                                                                  │
│  ┌─────────────────┐     ┌───────────┐     ┌─────────────────┐                 │
│  │ mcp_connections │────►│ mcp_tools │     │ mcp_user_access │                 │
│  └─────────────────┘     └───────────┘     └─────────────────┘                 │
│                                                     │                           │
│                                                     └── FK: user_id             │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                                  SKILL 模块                                      │
│                                                                                  │
│  ┌────────┐     ┌─────────────────────┐     ┌────────────┐                     │
│  │ skills │────►│ skill_tag_relations │◄────│ skill_tags │                     │
│  └───┬────┘     └─────────────────────┘     └────────────┘                     │
│      │                                                                          │
│      │          ┌─────────────────┐                                            │
│      └─────────►│ skill_versions  │                                            │
│                 └─────────────────┘                                            │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                               自定义 Agent 模块                                  │
│                                                                                  │
│  ┌───────────────┐     ┌───────────────────────┐                               │
│  │ custom_agents │────►│ agent_knowledge_bases │────► knowledge_bases          │
│  └───────┬───────┘     └───────────────────────┘                               │
│          │                                                                       │
│          │             ┌───────────────────────┐                               │
│          ├────────────►│ agent_mcp_connections │────► mcp_connections          │
│          │             └───────────────────────┘                               │
│          │                                                                       │
│          │             ┌───────────────────────┐                               │
│          └────────────►│    agent_skills       │────► skills                   │
│                        └───────────────────────┘                               │
│                                                                                  │
│          └── FK: owner_id → users.id (可为 NULL 表示系统默认)                   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                                  知识库模块                                      │
│                                                                                  │
│  ┌─────────────────┐     ┌──────────────┐     ┌───────────┐                    │
│  │ knowledge_bases │────►│ kb_documents │────►│ kb_chunks │                    │
│  └─────────────────┘     └──────────────┘     └───────────┘                    │
│                                                      │                          │
│                                                      └── vector_id → Milvus    │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                                  规则引擎模块                                    │
│                                                                                  │
│  ┌─────────┐     ┌───────────┐                                                 │
│  │  rules  │────►│ rule_logs │                                                 │
│  └─────────┘     └───────────┘                                                 │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 14. 附录

### 13.1 数据库迁移

使用 Alembic 进行数据库迁移管理。

```
alembic/
├── versions/           # 迁移脚本
├── env.py             # 环境配置
└── alembic.ini        # Alembic 配置
```

### 13.2 相关文档

- [产品需求文档](./ProductRequirements.md)
- [系统架构设计](./SystemArchitecture.md)
- [后端模块设计](./BackendDesign.md)
- [前端界面设计](./FrontendDesign.md)
- [API 接口设计](./APIDesign.md)
- [开发计划](./DevelopmentPlan.md)
