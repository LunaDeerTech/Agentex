# Agentex API 接口设计

## 文档信息

| 项目 | 内容 |
|------|------|
| 产品名称 | Agentex |
| 版本 | 1.0.0 |
| 文档版本 | 1.0 |
| 更新日期 | 2026-02-03 |

---

## 1. API 概述

### 1.1 基本信息

| 项目 | 值 |
|------|-----|
| 基础路径 | `/api/v1` |
| 协议 | HTTPS |
| 数据格式 | JSON |
| 字符编码 | UTF-8 |

### 1.2 认证方式

**Bearer Token 认证：**
```
Authorization: Bearer <access_token>
```

**API Key 认证（可选）：**
```
X-API-Key: <api_key>
```

### 1.3 通用响应格式

**成功响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": { ... }
}
```

**分页响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [ ... ],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "pages": 5
  }
}
```

**错误响应：**
```json
{
  "code": 40001,
  "message": "Invalid request parameters",
  "details": {
    "field": "email",
    "error": "Invalid email format"
  }
}
```

### 1.4 错误码定义

| 错误码范围 | 说明 |
|-----------|------|
| 0 | 成功 |
| 40001-40099 | 请求参数错误 |
| 40101-40199 | 认证错误 |
| 40301-40399 | 权限错误 |
| 40401-40499 | 资源不存在 |
| 40901-40999 | 资源冲突 |
| 50001-50099 | 服务器内部错误 |
| 50201-50299 | 外部服务错误 |

### 1.5 通用请求参数

**分页参数：**
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| page | int | 1 | 页码 |
| page_size | int | 20 | 每页数量（最大100） |

**排序参数：**
| 参数 | 类型 | 说明 |
|------|------|------|
| sort_by | string | 排序字段 |
| sort_order | string | 排序方向：asc/desc |

---

## 2. 认证接口

### 2.1 用户注册

**POST** `/api/v1/auth/register`

**请求体：**
```json
{
  "username": "zhangsan",
  "email": "zhangsan@example.com",
  "password": "Password123"
}
```

**响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "uuid",
    "username": "zhangsan",
    "email": "zhangsan@example.com",
    "role": "user",
    "created_at": "2026-02-03T10:00:00Z"
  }
}
```

### 2.2 用户登录

**POST** `/api/v1/auth/login`

**请求体：**
```json
{
  "username": "zhangsan",
  "password": "Password123"
}
```

**响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "access_token": "eyJhbGciOiJSUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJSUzI1NiIs...",
    "token_type": "Bearer",
    "expires_in": 1800,
    "user": {
      "id": "uuid",
      "username": "zhangsan",
      "email": "zhangsan@example.com",
      "role": "user",
      "avatar_url": null
    }
  }
}
```

### 2.3 刷新令牌

**POST** `/api/v1/auth/refresh`

**请求体：**
```json
{
  "refresh_token": "eyJhbGciOiJSUzI1NiIs..."
}
```

**响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "access_token": "eyJhbGciOiJSUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJSUzI1NiIs...",
    "token_type": "Bearer",
    "expires_in": 1800
  }
}
```

### 2.4 用户登出

**POST** `/api/v1/auth/logout`

**请求头：**
```
Authorization: Bearer <access_token>
```

**响应：**
```json
{
  "code": 0,
  "message": "success"
}
```

---

## 3. 用户接口

### 3.1 获取当前用户信息

**GET** `/api/v1/users/me`

**响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "uuid",
    "username": "zhangsan",
    "email": "zhangsan@example.com",
    "avatar_url": "https://...",
    "role": {
      "id": "uuid",
      "name": "developer",
      "display_name": "开发者"
    },
    "permissions": ["models:view", "mcp:view", "mcp:create", ...],
    "created_at": "2026-01-15T10:00:00Z"
  }
}
```

### 3.2 更新当前用户信息

**PUT** `/api/v1/users/me`

**请求体：**
```json
{
  "username": "zhangsan_new",
  "avatar_url": "https://..."
}
```

### 3.3 修改密码

**PUT** `/api/v1/users/me/password`

**请求体：**
```json
{
  "old_password": "OldPassword123",
  "new_password": "NewPassword456"
}
```

### 3.4 获取 API 密钥列表

**GET** `/api/v1/users/me/api-keys`

**响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": "uuid",
        "name": "开发测试",
        "key_prefix": "sk-...abc",
        "last_used_at": "2026-02-01T10:00:00Z",
        "created_at": "2026-01-20T10:00:00Z"
      }
    ],
    "total": 1
  }
}
```

### 3.5 创建 API 密钥

**POST** `/api/v1/users/me/api-keys`

**请求体：**
```json
{
  "name": "生产环境"
}
```

**响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "uuid",
    "name": "生产环境",
    "key": "sk-xxxxxxxxxxxxxxxxxxxxxxxx",
    "created_at": "2026-02-03T10:00:00Z"
  }
}
```

> ⚠️ 注意：API 密钥只在创建时返回完整值，之后无法再次获取。

### 3.6 撤销 API 密钥

**DELETE** `/api/v1/users/me/api-keys/{key_id}`

---

## 4. 用户管理接口（管理员）

### 4.1 获取用户列表

**GET** `/api/v1/admin/users`

**查询参数：**
| 参数 | 类型 | 说明 |
|------|------|------|
| search | string | 搜索用户名/邮箱 |
| role_id | uuid | 按角色筛选 |
| status | string | 按状态筛选：active/disabled |

**响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": "uuid",
        "username": "zhangsan",
        "email": "zhangsan@example.com",
        "role": {
          "id": "uuid",
          "name": "developer"
        },
        "status": "active",
        "last_login_at": "2026-02-03T08:00:00Z",
        "created_at": "2026-01-15T10:00:00Z"
      }
    ],
    "total": 10,
    "page": 1,
    "page_size": 20
  }
}
```

### 4.2 获取用户详情

**GET** `/api/v1/admin/users/{user_id}`

### 4.3 创建用户

**POST** `/api/v1/admin/users`

**请求体：**
```json
{
  "username": "lisi",
  "email": "lisi@example.com",
  "password": "InitialPassword123",
  "role_id": "uuid"
}
```

### 4.4 更新用户

**PUT** `/api/v1/admin/users/{user_id}`

**请求体：**
```json
{
  "role_id": "uuid",
  "status": "active",
  "custom_permissions": {
    "grants": ["permission_id_1"],
    "revokes": ["permission_id_2"]
  },
  "model_access": ["model_id_1", "model_id_2"],
  "mcp_access": ["connection_id_1"]
}
```

### 4.5 删除用户

**DELETE** `/api/v1/admin/users/{user_id}`

---

## 5. 会话接口

### 5.1 获取会话列表

**GET** `/api/v1/sessions`

**查询参数：**
| 参数 | 类型 | 说明 |
|------|------|------|
| is_archived | bool | 是否归档 |

**响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": "uuid",
        "title": "服务器状态查询",
        "message_count": 10,
        "last_message_at": "2026-02-03T10:00:00Z",
        "config": {
          "agent_type": "react",
          "model_id": "uuid"
        },
        "created_at": "2026-02-03T09:00:00Z"
      }
    ],
    "total": 5,
    "page": 1,
    "page_size": 20
  }
}
```

### 5.2 创建会话

**POST** `/api/v1/sessions`

**请求体：**
```json
{
  "title": "新对话",
  "config": {
    "agent_type": "react",
    "model_id": "uuid",
    "knowledge_base_ids": [],
    "mcp_connection_ids": [],
    "skill_ids": []
  }
}
```

### 5.3 获取会话详情

**GET** `/api/v1/sessions/{session_id}`

### 5.4 更新会话

**PUT** `/api/v1/sessions/{session_id}`

**请求体：**
```json
{
  "title": "新标题",
  "config": { ... }
}
```

### 5.5 删除会话

**DELETE** `/api/v1/sessions/{session_id}`

### 5.6 获取会话消息

**GET** `/api/v1/sessions/{session_id}/messages`

**查询参数：**
| 参数 | 类型 | 说明 |
|------|------|------|
| before_id | uuid | 获取此消息之前的消息 |
| limit | int | 数量限制（默认50） |

**响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": "uuid",
        "role": "user",
        "content": "查询服务器状态",
        "content_type": "text",
        "created_at": "2026-02-03T10:00:00Z"
      },
      {
        "id": "uuid",
        "role": "assistant",
        "content": "服务器当前状态正常...",
        "content_type": "markdown",
        "metadata": {
          "model_id": "uuid",
          "agent_type": "react",
          "thinking": [
            {
              "type": "thought",
              "content": "用户想查询服务器状态"
            },
            {
              "type": "action",
              "tool": "server_status",
              "input": {}
            }
          ],
          "tool_calls": [
            {
              "tool": "server_status",
              "input": {},
              "output": {"status": "online"},
              "duration": 120
            }
          ],
          "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50
          }
        },
        "created_at": "2026-02-03T10:00:05Z"
      }
    ],
    "has_more": false
  }
}
```

---

## 6. 模型接口

### 6.1 获取可用模型列表

**GET** `/api/v1/models`

**响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": "uuid",
        "name": "GPT-4o",
        "provider": "openai",
        "model_id": "gpt-4o",
        "max_tokens": 4096,
        "temperature": 0.7,
        "is_default": true,
        "enabled": true
      }
    ]
  }
}
```

### 6.2 创建模型配置（管理员）

**POST** `/api/v1/admin/models`

**请求体：**
```json
{
  "name": "GPT-4o",
  "provider": "openai",
  "base_url": "https://api.openai.com/v1",
  "api_key": "sk-...",
  "model_id": "gpt-4o",
  "max_tokens": 4096,
  "temperature": 0.7,
  "is_default": false,
  "enabled": true,
  "role_access": ["role_id_1", "role_id_2"],
  "user_access": ["user_id_1"]
}
```

### 6.3 更新模型配置（管理员）

**PUT** `/api/v1/admin/models/{model_id}`

### 6.4 删除模型配置（管理员）

**DELETE** `/api/v1/admin/models/{model_id}`

### 6.5 测试模型连接

**POST** `/api/v1/models/{model_id}/test`

**响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "success": true,
    "latency": 150,
    "message": "Connection successful"
  }
}
```

---

## 7. MCP 接口

### 7.1 获取 MCP 连接列表

**GET** `/api/v1/mcp/connections`

**响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": "uuid",
        "name": "Minecraft MCP",
        "type": "websocket",
        "url": "ws://localhost:8765",
        "status": "connected",
        "tool_count": 12,
        "enabled": true
      }
    ]
  }
}
```

### 7.2 创建 MCP 连接

**POST** `/api/v1/mcp/connections`

**请求体（标准 MCP）：**
```json
{
  "name": "File System",
  "type": "standard",
  "url": "http://localhost:3001",
  "auth_type": "bearer",
  "auth_token": "token-xxx",
  "enabled": true
}
```

**请求体（WebSocket MCP）：**
```json
{
  "name": "Minecraft MCP",
  "type": "websocket",
  "url": "ws://localhost:8765",
  "auth_token": "token-xxx",
  "config": {
    "heartbeat_interval": 30000,
    "reconnect_delay": 5000,
    "max_retries": 3
  },
  "enabled": true
}
```

### 7.3 更新 MCP 连接

**PUT** `/api/v1/mcp/connections/{connection_id}`

### 7.4 删除 MCP 连接

**DELETE** `/api/v1/mcp/connections/{connection_id}`

### 7.5 测试 MCP 连接

**POST** `/api/v1/mcp/connections/{connection_id}/test`

### 7.6 获取 MCP 工具列表

**GET** `/api/v1/mcp/connections/{connection_id}/tools`

**响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "name": "block_set",
        "description": "在指定位置放置方块",
        "input_schema": {
          "type": "object",
          "properties": {
            "location": { "type": "object" },
            "material": { "type": "string" }
          },
          "required": ["location", "material"]
        }
      }
    ]
  }
}
```

### 7.7 手动调用 MCP 工具

**POST** `/api/v1/mcp/connections/{connection_id}/tools/{tool_name}/call`

**请求体：**
```json
{
  "params": {
    "location": { "world": "world", "x": 0, "y": 64, "z": 0 },
    "material": "STONE"
  }
}
```

**响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "result": { ... },
    "duration": 120
  }
}
```

---

## 8. SKILL 接口

### 8.1 获取 SKILL 列表

**GET** `/api/v1/skills`

**查询参数：**
| 参数 | 类型 | 说明 |
|------|------|------|
| include_public | bool | 是否包含公开 SKILL |
| category | string | 分类筛选 |
| tag | string | 标签筛选 |

**响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": "uuid",
        "name": "代码审查",
        "description": "对提交的代码进行审查...",
        "category": "开发工具",
        "tags": ["代码", "审查"],
        "is_public": false,
        "version": 2,
        "owner": {
          "id": "uuid",
          "username": "zhangsan"
        },
        "created_at": "2026-01-15T10:00:00Z",
        "updated_at": "2026-02-01T10:00:00Z"
      }
    ]
  }
}
```

### 8.2 获取 SKILL 详情

**GET** `/api/v1/skills/{skill_id}`

**响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "uuid",
    "name": "代码审查",
    "description": "...",
    "content": "# SKILL: 代码审查\n\n## 描述\n...",
    "category": "开发工具",
    "tags": ["代码", "审查"],
    "is_public": false,
    "version": 2,
    "owner": {
      "id": "uuid",
      "username": "zhangsan"
    },
    "created_at": "2026-01-15T10:00:00Z",
    "updated_at": "2026-02-01T10:00:00Z"
  }
}
```

### 8.3 创建 SKILL

**POST** `/api/v1/skills`

**请求体：**
```json
{
  "name": "日报生成",
  "description": "根据今日工作内容生成工作日报",
  "content": "# SKILL: 日报生成\n\n## 描述\n...",
  "category": "效率工具",
  "tags": ["日报", "工作"],
  "is_public": false
}
```

### 8.4 更新 SKILL

**PUT** `/api/v1/skills/{skill_id}`

**请求体：**
```json
{
  "name": "日报生成",
  "content": "# SKILL: 日报生成\n\n## 描述\n...(更新后)",
  "change_note": "修复了日期格式问题"
}
```

### 8.5 删除 SKILL

**DELETE** `/api/v1/skills/{skill_id}`

### 8.6 验证 SKILL

**POST** `/api/v1/skills/validate`

**请求体：**
```json
{
  "content": "# SKILL: 测试\n\n## 描述\n..."
}
```

**响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "valid": true,
    "parsed": {
      "name": "测试",
      "description": "...",
      "trigger_conditions": [...],
      "input_params": [...],
      "steps": [...]
    },
    "warnings": []
  }
}
```

### 8.7 导出 SKILL

**GET** `/api/v1/skills/{skill_id}/export`

**响应：**
```
Content-Type: text/markdown
Content-Disposition: attachment; filename="skill_name.md"

# SKILL: ...
```

### 8.8 获取 SKILL 版本历史

**GET** `/api/v1/skills/{skill_id}/versions`

---

## 9. 知识库接口

### 9.1 获取知识库列表

**GET** `/api/v1/knowledge-bases`

**响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": "uuid",
        "name": "产品文档知识库",
        "description": "包含产品相关的所有文档",
        "embedding_model": "text-embedding-3-small",
        "document_count": 15,
        "is_public": false,
        "enabled": true,
        "created_at": "2026-01-10T10:00:00Z"
      }
    ]
  }
}
```

### 9.2 创建知识库

**POST** `/api/v1/knowledge-bases`

**请求体：**
```json
{
  "name": "技术文档知识库",
  "description": "技术相关文档",
  "embedding_model": "text-embedding-3-small",
  "chunk_size": 500,
  "chunk_overlap": 50,
  "is_public": false
}
```

### 9.3 获取知识库详情

**GET** `/api/v1/knowledge-bases/{kb_id}`

### 9.4 更新知识库

**PUT** `/api/v1/knowledge-bases/{kb_id}`

### 9.5 删除知识库

**DELETE** `/api/v1/knowledge-bases/{kb_id}`

### 9.6 获取知识库文档列表

**GET** `/api/v1/knowledge-bases/{kb_id}/documents`

**响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": "uuid",
        "name": "产品介绍.md",
        "file_type": "markdown",
        "file_size": 12288,
        "status": "completed",
        "chunk_count": 25,
        "created_at": "2026-01-15T10:00:00Z"
      }
    ]
  }
}
```

### 9.7 上传文档

**POST** `/api/v1/knowledge-bases/{kb_id}/documents`

**请求：**
```
Content-Type: multipart/form-data

file: (binary)
```

**响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "uuid",
    "name": "新文档.pdf",
    "status": "pending",
    "created_at": "2026-02-03T10:00:00Z"
  }
}
```

### 9.8 获取文档状态

**GET** `/api/v1/knowledge-bases/{kb_id}/documents/{doc_id}`

### 9.9 删除文档

**DELETE** `/api/v1/knowledge-bases/{kb_id}/documents/{doc_id}`

### 9.10 测试检索

**POST** `/api/v1/knowledge-bases/{kb_id}/search`

**请求体：**
```json
{
  "query": "服务器配置要求",
  "top_k": 5
}
```

**响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "results": [
      {
        "document_id": "uuid",
        "document_name": "部署文档.md",
        "chunk_id": "uuid",
        "content": "服务器最低配置要求...",
        "score": 0.92
      }
    ]
  }
}
```

---

## 10. 规则引擎接口

### 10.1 获取规则列表

**GET** `/api/v1/rules`

**响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": "uuid",
        "name": "玩家进入欢迎",
        "description": "当玩家进入游戏时发送欢迎消息",
        "trigger_config": {
          "event_type": "player_join",
          "source_id": "uuid"
        },
        "enabled": true,
        "trigger_count": 156,
        "last_triggered_at": "2026-02-03T09:50:00Z",
        "created_at": "2026-01-20T10:00:00Z"
      }
    ]
  }
}
```

### 10.2 获取规则详情

**GET** `/api/v1/rules/{rule_id}`

**响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "uuid",
    "name": "玩家进入欢迎",
    "description": "当玩家进入游戏时发送欢迎消息",
    "trigger_config": {
      "event_type": "player_join",
      "source_id": "uuid"
    },
    "conditions": [
      {
        "field": "player.name",
        "operator": "!=",
        "value": "admin",
        "logic": "AND"
      }
    ],
    "actions": [
      {
        "type": "mcp_call",
        "target": "chat_broadcast",
        "params": {
          "message": "欢迎 {{player.name}} 进入游戏！",
          "color": "green"
        },
        "on_error": "continue"
      }
    ],
    "cooldown": 5000,
    "enabled": true,
    "trigger_count": 156,
    "last_triggered_at": "2026-02-03T09:50:00Z",
    "created_at": "2026-01-20T10:00:00Z"
  }
}
```

### 10.3 创建规则

**POST** `/api/v1/rules`

**请求体：**
```json
{
  "name": "低血量警告",
  "description": "当玩家血量低于20%时发送警告",
  "trigger_config": {
    "event_type": "player_damage",
    "source_id": "uuid"
  },
  "conditions": [
    {
      "field": "player.health_percent",
      "operator": "<",
      "value": 20,
      "logic": "AND"
    }
  ],
  "actions": [
    {
      "type": "mcp_call",
      "target": "chat_send_player",
      "params": {
        "playerName": "{{player.name}}",
        "message": "⚠️ 警告：你的血量低于20%！"
      },
      "on_error": "continue"
    }
  ],
  "cooldown": 10000,
  "enabled": true
}
```

### 10.4 更新规则

**PUT** `/api/v1/rules/{rule_id}`

### 10.5 删除规则

**DELETE** `/api/v1/rules/{rule_id}`

### 10.6 启用/禁用规则

**PUT** `/api/v1/rules/{rule_id}/enabled`

**请求体：**
```json
{
  "enabled": true
}
```

### 10.7 测试规则

**POST** `/api/v1/rules/{rule_id}/test`

**请求体：**
```json
{
  "test_event": {
    "type": "player_join",
    "data": {
      "player": {
        "name": "testPlayer",
        "uuid": "xxx"
      }
    }
  }
}
```

**响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "conditions_met": true,
    "would_execute": true,
    "dry_run_result": {
      "actions": [
        {
          "type": "mcp_call",
          "target": "chat_broadcast",
          "rendered_params": {
            "message": "欢迎 testPlayer 进入游戏！",
            "color": "green"
          }
        }
      ]
    }
  }
}
```

### 10.8 获取规则执行日志

**GET** `/api/v1/rules/{rule_id}/logs`

**查询参数：**
| 参数 | 类型 | 说明 |
|------|------|------|
| status | string | 按状态筛选 |
| start_time | datetime | 开始时间 |
| end_time | datetime | 结束时间 |

**响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": "uuid",
        "event_data": {...},
        "conditions_met": true,
        "actions_result": [...],
        "status": "success",
        "execution_time": 150,
        "executed_at": "2026-02-03T09:50:00Z"
      }
    ],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

### 10.9 获取可用事件类型

**GET** `/api/v1/rules/event-types`

**查询参数：**
| 参数 | 类型 | 说明 |
|------|------|------|
| source_id | uuid | MCP 连接 ID |

**响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "event_types": [
      {
        "type": "player_join",
        "description": "玩家加入游戏",
        "schema": {
          "player": {
            "name": "string",
            "uuid": "string"
          }
        }
      }
    ]
  }
}
```

---

## 11. 系统配置接口（管理员）

### 11.1 获取系统配置

**GET** `/api/v1/admin/system/config`

**响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "key": "max_sessions_per_user",
        "value": 100,
        "description": "每用户最大会话数"
      }
    ]
  }
}
```

### 11.2 更新系统配置

**PUT** `/api/v1/admin/system/config/{key}`

**请求体：**
```json
{
  "value": 200
}
```

### 11.3 获取系统信息

**GET** `/api/v1/admin/system/info`

**响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "version": "1.0.0",
    "uptime": 86400,
    "user_count": 50,
    "session_count": 1200,
    "database_size": "1.2 GB",
    "vector_db_size": "500 MB"
  }
}
```

---

## 12. AG-UI 对话接口

AG-UI（Agent-User Interaction Protocol）是一个开放的、事件驱动的协议，用于标准化 AI Agent 与用户前端应用之间的通信。本系统采用 AG-UI 协议替代传统 WebSocket 实现 Agent 对话功能。

### 12.1 接口端点

**POST** `/api/v1/agent/run`

**Content-Type:** `application/json`
**Accept:** `text/event-stream`（SSE）或 `application/octet-stream`（二进制）

**请求头：**
```
Authorization: Bearer <access_token>
Accept: text/event-stream
```

### 12.2 请求格式（RunAgentInput）

```json
{
  "thread_id": "session-uuid",
  "run_id": "run-uuid",
  "state": {},
  "messages": [
    {
      "id": "msg-uuid",
      "role": "user",
      "content": "用户消息内容"
    }
  ],
  "tools": [
    {
      "name": "world_tps_get",
      "description": "获取服务器 TPS",
      "parameters": {
        "type": "object",
        "properties": {}
      }
    }
  ],
  "context": [
    {
      "description": "当前会话上下文",
      "value": "..."
    }
  ],
  "forwarded_props": {
    "agent_type": "react",
    "model_id": "model-uuid",
    "knowledge_base_ids": ["kb-uuid"],
    "mcp_connection_ids": ["mcp-uuid"],
    "skill_ids": ["skill-uuid"]
  }
}
```

**字段说明：**
| 字段 | 类型 | 说明 |
|------|------|------|
| thread_id | string | 会话线程 ID |
| run_id | string | 本次运行 ID |
| state | object | Agent 状态数据 |
| messages | array | 消息历史列表 |
| tools | array | 可用工具列表 |
| context | array | 上下文信息 |
| forwarded_props | object | 扩展属性（Agent 配置等） |

### 12.3 响应格式（SSE 事件流）

服务端通过 Server-Sent Events 流式返回 AG-UI 标准事件。

**响应头：**
```
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
```

### 12.4 事件类型

#### 12.4.1 生命周期事件

| 事件类型 | 说明 |
|---------|------|
| RUN_STARTED | Agent 运行开始 |
| RUN_FINISHED | Agent 运行成功完成 |
| RUN_ERROR | Agent 运行出错 |
| STEP_STARTED | 步骤开始（思考过程） |
| STEP_FINISHED | 步骤完成 |

**RUN_STARTED：**
```
event: RUN_STARTED
data: {"type":"RUN_STARTED","thread_id":"session-uuid","run_id":"run-uuid","timestamp":1738569600000}
```

**RUN_FINISHED：**
```
event: RUN_FINISHED
data: {"type":"RUN_FINISHED","thread_id":"session-uuid","run_id":"run-uuid","result":{"usage":{"prompt_tokens":100,"completion_tokens":50}}}
```

**RUN_ERROR：**
```
event: RUN_ERROR
data: {"type":"RUN_ERROR","message":"模型调用失败","code":"LLM_ERROR"}
```

**STEP_STARTED / STEP_FINISHED：**
```
event: STEP_STARTED
data: {"type":"STEP_STARTED","step_name":"thinking"}

event: STEP_FINISHED
data: {"type":"STEP_FINISHED","step_name":"thinking"}
```

#### 12.4.2 文本消息事件

| 事件类型 | 说明 |
|---------|------|
| TEXT_MESSAGE_START | 消息开始 |
| TEXT_MESSAGE_CONTENT | 消息内容片段（流式） |
| TEXT_MESSAGE_END | 消息结束 |

**示例：**
```
event: TEXT_MESSAGE_START
data: {"type":"TEXT_MESSAGE_START","message_id":"msg-uuid","role":"assistant"}

event: TEXT_MESSAGE_CONTENT
data: {"type":"TEXT_MESSAGE_CONTENT","message_id":"msg-uuid","delta":"服务器"}

event: TEXT_MESSAGE_CONTENT
data: {"type":"TEXT_MESSAGE_CONTENT","message_id":"msg-uuid","delta":"当前状态"}

event: TEXT_MESSAGE_CONTENT
data: {"type":"TEXT_MESSAGE_CONTENT","message_id":"msg-uuid","delta":"正常"}

event: TEXT_MESSAGE_END
data: {"type":"TEXT_MESSAGE_END","message_id":"msg-uuid"}
```

#### 12.4.3 工具调用事件

| 事件类型 | 说明 |
|---------|------|
| TOOL_CALL_START | 工具调用开始 |
| TOOL_CALL_ARGS | 工具参数（流式） |
| TOOL_CALL_END | 工具调用参数完成 |
| TOOL_CALL_RESULT | 工具执行结果 |

**示例：**
```
event: TOOL_CALL_START
data: {"type":"TOOL_CALL_START","tool_call_id":"tc-uuid","tool_call_name":"world_tps_get","parent_message_id":"msg-uuid"}

event: TOOL_CALL_ARGS
data: {"type":"TOOL_CALL_ARGS","tool_call_id":"tc-uuid","delta":"{}"}

event: TOOL_CALL_END
data: {"type":"TOOL_CALL_END","tool_call_id":"tc-uuid"}

event: TOOL_CALL_RESULT
data: {"type":"TOOL_CALL_RESULT","message_id":"result-msg-uuid","tool_call_id":"tc-uuid","content":"{\"tps\":20.0}","role":"tool"}
```

#### 12.4.4 状态管理事件

| 事件类型 | 说明 |
|---------|------|
| STATE_SNAPSHOT | 完整状态快照 |
| STATE_DELTA | 增量状态更新（JSON Patch） |
| MESSAGES_SNAPSHOT | 消息历史快照 |

**示例：**
```
event: STATE_SNAPSHOT
data: {"type":"STATE_SNAPSHOT","snapshot":{"current_step":"thinking","tools_used":[]}}

event: STATE_DELTA
data: {"type":"STATE_DELTA","delta":[{"op":"add","path":"/tools_used/-","value":"world_tps_get"}]}
```

### 12.5 完整对话流程示例

```
Client → Server (HTTP POST):
POST /api/v1/agent/run
Content-Type: application/json
Authorization: Bearer <token>
Accept: text/event-stream

{
  "thread_id": "session-uuid",
  "run_id": "run-uuid",
  "messages": [
    {"id": "user-msg", "role": "user", "content": "查询服务器状态"}
  ],
  "tools": [
    {"name": "world_tps_get", "description": "获取服务器 TPS", "parameters": {}}
  ],
  "forwarded_props": {
    "agent_type": "react",
    "model_id": "model-uuid",
    "mcp_connection_ids": ["mcp-uuid"]
  }
}

Server → Client (SSE Stream):

event: RUN_STARTED
data: {"type":"RUN_STARTED","thread_id":"session-uuid","run_id":"run-uuid"}

event: STEP_STARTED
data: {"type":"STEP_STARTED","step_name":"thinking"}

event: TEXT_MESSAGE_START
data: {"type":"TEXT_MESSAGE_START","message_id":"think-msg","role":"assistant"}

event: TEXT_MESSAGE_CONTENT
data: {"type":"TEXT_MESSAGE_CONTENT","message_id":"think-msg","delta":"用户想要查询服务器状态，我需要调用工具。"}

event: TEXT_MESSAGE_END
data: {"type":"TEXT_MESSAGE_END","message_id":"think-msg"}

event: STEP_FINISHED
data: {"type":"STEP_FINISHED","step_name":"thinking"}

event: TOOL_CALL_START
data: {"type":"TOOL_CALL_START","tool_call_id":"tc-1","tool_call_name":"world_tps_get","parent_message_id":"think-msg"}

event: TOOL_CALL_ARGS
data: {"type":"TOOL_CALL_ARGS","tool_call_id":"tc-1","delta":"{}"}

event: TOOL_CALL_END
data: {"type":"TOOL_CALL_END","tool_call_id":"tc-1"}

event: TOOL_CALL_RESULT
data: {"type":"TOOL_CALL_RESULT","message_id":"tool-result","tool_call_id":"tc-1","content":"{\"tps\":20.0}","role":"tool"}

event: TEXT_MESSAGE_START
data: {"type":"TEXT_MESSAGE_START","message_id":"response-msg","role":"assistant"}

event: TEXT_MESSAGE_CONTENT
data: {"type":"TEXT_MESSAGE_CONTENT","message_id":"response-msg","delta":"服务器"}

event: TEXT_MESSAGE_CONTENT
data: {"type":"TEXT_MESSAGE_CONTENT","message_id":"response-msg","delta":"当前 TPS 为 20.0，"}

event: TEXT_MESSAGE_CONTENT
data: {"type":"TEXT_MESSAGE_CONTENT","message_id":"response-msg","delta":"运行状态正常。"}

event: TEXT_MESSAGE_END
data: {"type":"TEXT_MESSAGE_END","message_id":"response-msg"}

event: RUN_FINISHED
data: {"type":"RUN_FINISHED","thread_id":"session-uuid","run_id":"run-uuid","result":{"usage":{"prompt_tokens":150,"completion_tokens":80}}}
```

### 12.6 停止生成

**POST** `/api/v1/agent/run/{run_id}/stop`

**请求头：**
```
Authorization: Bearer <access_token>
```

**响应：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "run_id": "run-uuid",
    "stopped": true
  }
}
```

### 12.7 Python SDK 集成示例

后端使用 `ag-ui-protocol` Python SDK：

```python
from ag_ui.core import (
    RunAgentInput, EventType,
    RunStartedEvent, RunFinishedEvent, RunErrorEvent,
    TextMessageStartEvent, TextMessageContentEvent, TextMessageEndEvent,
    ToolCallStartEvent, ToolCallArgsEvent, ToolCallEndEvent, ToolCallResultEvent,
    StepStartedEvent, StepFinishedEvent
)
from ag_ui.encoder import EventEncoder

# 伪代码示例
async def agent_run_endpoint(input_data: RunAgentInput, request: Request):
    encoder = EventEncoder(accept=request.headers.get("accept"))
    
    async def event_generator():
        yield encoder.encode(RunStartedEvent(
            type=EventType.RUN_STARTED,
            thread_id=input_data.thread_id,
            run_id=input_data.run_id
        ))
        
        # Agent 执行逻辑...
        
        yield encoder.encode(RunFinishedEvent(
            type=EventType.RUN_FINISHED,
            thread_id=input_data.thread_id,
            run_id=input_data.run_id
        ))
    
    return StreamingResponse(event_generator(), media_type=encoder.get_content_type())
```

---

## 13. 附录

### 13.1 Agent 类型

| 类型标识 | 名称 | 说明 |
|---------|------|------|
| react | ReAct | 思考-行动循环模式 |
| agentic_rag | AgenticRAG | RAG 增强的 Agent |
| plan_execute | PlanAndExecute | 计划-执行模式 |
| reflexion | Reflexion | 反思改进模式 |

### 13.2 相关文档

- [产品需求文档](./ProductRequirements.md)
- [系统架构设计](./SystemArchitecture.md)
- [后端模块设计](./BackendDesign.md)
- [前端界面设计](./FrontendDesign.md)
- [数据库设计](./DatabaseDesign.md)
- [开发计划](./DevelopmentPlan.md)
- [WS-MCP 协议规范](./CustomizeWsMessageProcotol.md)
