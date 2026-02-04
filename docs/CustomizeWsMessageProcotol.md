# WebSocket MCP 通信协议与流程

## 1. 协议概述

### 1.1 设计目标
- 基于 JSON-RPC 2.0 标准
- 与 HTTP SSE MCP 协议保持语义一致
- 扩展支持 WebSocket 特有的认证和心跳机制
- 全双工通信支持服务端推送

### 1.2 协议栈
```
┌─────────────────────────────────────┐
│           MCP Application           │
├─────────────────────────────────────┤
│          JSON-RPC 2.0               │
├─────────────────────────────────────┤
│     WebSocket Message Wrapper       │
├─────────────────────────────────────┤
│           WebSocket                 │
├─────────────────────────────────────┤
│           TCP/IP                    │
└─────────────────────────────────────┘
```

## 2. 消息格式

### 2.1 WebSocket 消息包装器

所有 WebSocket 消息都使用统一的包装格式：

```json
{
  "type": "<message_type>",
  "token": "<bearer_token>",       // 仅 auth 类型必填
  "sessionId": "<session_id>",     // 认证后由服务端分配
  "payload": { ... },              // JSON-RPC 消息负载
  "timestamp": 1234567890          // Unix 时间戳（毫秒）
}
```

### 2.2 消息类型（type）

| 类型 | 方向 | 说明 |
|------|------|------|
| `auth` | 双向 | 认证请求/响应 |
| `message` | 双向 | JSON-RPC 消息载体 |
| `ping` | S→C | 服务端心跳请求 |
| `pong` | C→S | 客户端心跳响应 |
| `error` | S→C | 错误通知 |
| `close` | 双向 | 关闭连接通知 |

### 2.3 详细消息结构

#### 2.3.1 认证请求（客户端 → 服务端）
```json
{
  "type": "auth",
  "token": "your-bearer-token",
  "clientInfo": {
    "name": "client-name",
    "version": "1.0.0"
  },
  "timestamp": 1234567890000
}
```

#### 2.3.2 认证响应（服务端 → 客户端）

**成功：**
```json
{
  "type": "auth",
  "sessionId": "ws-session-abc123",
  "status": "authenticated",
  "serverInfo": {
    "name": "mcp-server-default",
    "version": "1.0.0"
  },
  "heartbeatInterval": 30000,
  "timestamp": 1234567890000
}
```

**失败：**
```json
{
  "type": "auth",
  "status": "failed",
  "error": {
    "code": 401,
    "message": "Invalid authentication token"
  },
  "timestamp": 1234567890000
}
```

#### 2.3.3 JSON-RPC 消息（双向）
```json
{
  "type": "message",
  "sessionId": "ws-session-abc123",
  "payload": {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2025-11-25",
      "capabilities": {},
      "clientInfo": {
        "name": "test-client",
        "version": "1.0.0"
      }
    }
  },
  "timestamp": 1234567890000
}
```

#### 2.3.4 心跳消息

**Ping（服务端 → 客户端）：**
```json
{
  "type": "ping",
  "sessionId": "ws-session-abc123",
  "timestamp": 1234567890000
}
```

**Pong（客户端 → 服务端）：**
```json
{
  "type": "pong",
  "sessionId": "ws-session-abc123",
  "timestamp": 1234567890000
}
```

#### 2.3.5 错误消息（服务端 → 客户端）
```json
{
  "type": "error",
  "sessionId": "ws-session-abc123",
  "error": {
    "code": -32600,
    "message": "Invalid Request",
    "data": null
  },
  "timestamp": 1234567890000
}
```

#### 2.3.6 关闭消息（双向）
```json
{
  "type": "close",
  "sessionId": "ws-session-abc123",
  "reason": "Client disconnect",
  "timestamp": 1234567890000
}
```

## 3. 通信流程

### 3.1 完整连接生命周期

```
┌──────────┐                                      ┌──────────┐
│  Client  │                                      │  Server  │
└────┬─────┘                                      └────┬─────┘
     │                                                 │
     │  ─────────── TCP Connection ──────────────────► │
     │                                                 │
     │  ◄──────── WebSocket Upgrade ─────────────────  │
     │                                                 │
     │                【认证阶段】                       │
     │  ──────────── auth request ───────────────────► │
     │                                                 │ 验证 token
     │  ◄─────────── auth response ──────────────────  │
     │                                                 │
     │              【MCP 初始化阶段】                   │
     │  ──────────── initialize ─────────────────────► │
     │  ◄─────────── initialize response ────────────  │
     │  ──────────── notifications/initialized ──────► │
     │                                                 │
     │              【操作阶段】                         │
     │  ──────────── tools/list ─────────────────────► │
     │  ◄─────────── tools/list response ────────────  │
     │  ──────────── tools/call ─────────────────────► │
     │  ◄─────────── tools/call response ────────────  │
     │                                                 │
     │              【心跳维护】                         │
     │  ◄──────────────── ping ──────────────────────  │
     │  ─────────────────── pong ───────────────────►  │
     │                                                 │
     │              【关闭阶段】                         │
     │  ──────────────── close ──────────────────────► │
     │  ◄───────────── close ack ────────────────────  │
     │                                                 │
     │  ────────── TCP Connection Close ────────────►  │
     │                                                 │
```

### 3.2 认证流程详解

```
┌──────────┐                                      ┌──────────┐
│  Client  │                                      │  Server  │
└────┬─────┘                                      └────┬─────┘
     │                                                 │
     │  1. WebSocket 连接建立                           │
     │  ═══════════════════════════════════════════►   │
     │                                                 │
     │                              2. 等待认证消息     │
     │                                   (超时 30s)    │
     │                                                 │
     │  3. 发送 auth 消息                               │
     │  {                                              │
     │    "type": "auth",                              │
     │    "token": "ChangeMe!",                        │
     │    "clientInfo": {...}                          │
     │  }                                              │
     │  ────────────────────────────────────────────►  │
     │                                                 │
     │                              4. 验证 token       │
     │                                 ├─ 成功: 创建会话 │
     │                                 └─ 失败: 关闭连接 │
     │                                                 │
     │  5. 返回认证结果                                 │
     │  {                                              │
     │    "type": "auth",                              │
     │    "sessionId": "ws-xxx",                       │
     │    "status": "authenticated"                    │
     │  }                                              │
     │  ◄────────────────────────────────────────────  │
     │                                                 │
     │  6. 可以开始发送 MCP 消息                        │
     │                                                 │
```

### 3.3 MCP 协议流程（通过 WebSocket 传输）

```
┌──────────┐                                      ┌──────────┐
│  Client  │                                      │  Server  │
└────┬─────┘                                      └────┬─────┘
     │                                                 │
     │  【已完成认证】                                   │
     │                                                 │
     │  1. initialize 请求                             │
     │  {                                              │
     │    "type": "message",                           │
     │    "sessionId": "ws-xxx",                       │
     │    "payload": {                                 │
     │      "jsonrpc": "2.0",                          │
     │      "id": 1,                                   │
     │      "method": "initialize",                    │
     │      "params": {                                │
     │        "protocolVersion": "2025-11-25",         │
     │        "capabilities": {},                      │
     │        "clientInfo": {...}                      │
     │      }                                          │
     │    }                                            │
     │  }                                              │
     │  ────────────────────────────────────────────►  │
     │                                                 │
     │  2. initialize 响应                             │
     │  {                                              │
     │    "type": "message",                           │
     │    "sessionId": "ws-xxx",                       │
     │    "payload": {                                 │
     │      "jsonrpc": "2.0",                          │
     │      "id": 1,                                   │
     │      "result": {                                │
     │        "protocolVersion": "2025-11-25",         │
     │        "capabilities": {...},                   │
     │        "serverInfo": {...}                      │
     │      }                                          │
     │    }                                            │
     │  }                                              │
     │  ◄────────────────────────────────────────────  │
     │                                                 │
     │  3. initialized 通知                            │
     │  {                                              │
     │    "type": "message",                           │
     │    "sessionId": "ws-xxx",                       │
     │    "payload": {                                 │
     │      "jsonrpc": "2.0",                          │
     │      "method": "notifications/initialized"      │
     │    }                                            │
     │  }                                              │
     │  ────────────────────────────────────────────►  │
     │                                                 │
     │  【会话进入 OPERATING 状态】                      │
     │                                                 │
```

### 3.4 心跳机制

```
┌──────────┐                                      ┌──────────┐
│  Client  │                                      │  Server  │
└────┬─────┘                                      └────┬─────┘
     │                                                 │
     │  【操作阶段】                                    │
     │                                                 │
     │           ┌─────────────────────────────────┐   │
     │           │ 心跳定时器 (heartbeatInterval)   │   │
     │           │ 默认: 30000ms                   │   │
     │           └─────────────────────────────────┘   │
     │                                                 │
     │  ping                                           │
     │  ◄────────────────────────────────────────────  │
     │                                                 │
     │  pong (应在收到后立即响应)                       │
     │  ────────────────────────────────────────────►  │
     │                                                 │
     │                              更新 lastPongTime  │
     │                                                 │
     │           ┌─────────────────────────────────┐   │
     │           │ 超时检测 (heartbeatTimeout)     │   │
     │           │ 默认: 90000ms                   │   │
     │           │ 如果超过 90s 没收到 pong        │   │
     │           │ → 判定连接断开，清理会话         │   │
     │           └─────────────────────────────────┘   │
     │                                                 │
```

### 3.5 错误处理流程

```
┌──────────┐                                      ┌──────────┐
│  Client  │                                      │  Server  │
└────┬─────┘                                      └────┬─────┘
     │                                                 │
     │  【场景1: 未认证发送消息】                        │
     │  {                                              │
     │    "type": "message",                           │
     │    "payload": {...}                             │
     │  }                                              │
     │  ────────────────────────────────────────────►  │
     │                                                 │
     │  error + 关闭连接                               │
     │  {                                              │
     │    "type": "error",                             │
     │    "error": {                                   │
     │      "code": 401,                               │
     │      "message": "Not authenticated"             │
     │    }                                            │
     │  }                                              │
     │  ◄════════════════════════════════════════════  │
     │  Connection Closed                              │
     │                                                 │
     │  【场景2: 无效消息格式】                          │
     │  invalid json                                   │
     │  ────────────────────────────────────────────►  │
     │                                                 │
     │  error                                          │
     │  {                                              │
     │    "type": "error",                             │
     │    "error": {                                   │
     │      "code": -32700,                            │
     │      "message": "Parse error"                   │
     │    }                                            │
     │  }                                              │
     │  ◄────────────────────────────────────────────  │
     │                                                 │
     │  【场景3: 未知方法】                              │
     │  {                                              │
     │    "type": "message",                           │
     │    "payload": {                                 │
     │      "method": "unknown/method"                 │
     │    }                                            │
     │  }                                              │
     │  ────────────────────────────────────────────►  │
     │                                                 │
     │  message (JSON-RPC error)                       │
     │  {                                              │
     │    "type": "message",                           │
     │    "payload": {                                 │
     │      "jsonrpc": "2.0",                          │
     │      "id": 1,                                   │
     │      "error": {                                 │
     │        "code": -32601,                          │
     │        "message": "Method not found"            │
     │      }                                          │
     │    }                                            │
     │  }                                              │
     │  ◄────────────────────────────────────────────  │
     │                                                 │
```

## 4. 错误代码

### 4.1 WebSocket 层错误
| 代码 | 含义 | 处理方式 |
|------|------|----------|
| 400 | 消息格式错误 | 发送 error 消息 |
| 401 | 未认证/认证失败 | 发送 error 消息并关闭连接 |
| 403 | 权限不足 | 发送 error 消息 |
| 408 | 认证超时 | 关闭连接 |
| 429 | 连接数超限 | 拒绝连接 |
| 503 | 服务不可用 | 拒绝连接 |

### 4.2 JSON-RPC 层错误（复用标准错误码）
| 代码 | 含义 |
|------|------|
| -32700 | Parse error - 无效的 JSON |
| -32600 | Invalid Request - 无效的请求对象 |
| -32601 | Method not found - 方法不存在 |
| -32602 | Invalid params - 无效的方法参数 |
| -32603 | Internal error - 内部错误 |

## 5. 与 HTTP SSE 对比

| 特性 | HTTP SSE | WebSocket |
|------|----------|-----------|
| 连接方式 | 短连接 + SSE 长连接 | 单一双工长连接 |
| 认证方式 | HTTP Header (Authorization: Bearer) | 首条消息携带 token |
| 消息格式 | 纯 JSON-RPC | WebSocket Message 包装 JSON-RPC |
| 服务端推送 | 通过 SSE | 通过 WebSocket 消息 |
| 心跳机制 | HTTP Keep-Alive | 显式 ping/pong |
| 会话管理 | X-Session-Id Header | sessionId 字段 |
| 适用场景 | HTTP/2 环境、代理友好 | 低延迟、双向通信 |

## 6. 安全考虑

### 6.1 Token 安全
- Token 仅在认证消息中传输一次
- 认证成功后使用 sessionId 标识会话
- 建议使用强随机 token（非默认值 "ChangeMe!"）

### 6.2 连接安全
- 默认绑定 127.0.0.1，仅允许本地连接
- 生产环境建议使用 WSS (WebSocket Secure)
- 限制最大连接数（默认 1）

### 6.3 会话安全
- 会话有超时机制
- 心跳超时自动断开
- 服务端主动清理僵尸连接

## 7. 客户端实现指南

### 7.1 连接建立
```javascript
// 伪代码示例
const ws = new WebSocket("ws://127.0.0.1:8765");

ws.onopen = () => {
  // 立即发送认证消息
  ws.send(JSON.stringify({
    type: "auth",
    token: "your-token",
    clientInfo: {
      name: "my-client",
      version: "1.0.0"
    },
    timestamp: Date.now()
  }));
};
```

### 7.2 消息处理
```javascript
ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  
  switch (msg.type) {
    case "auth":
      if (msg.status === "authenticated") {
        this.sessionId = msg.sessionId;
        this.startMcpInitialization();
      }
      break;
      
    case "message":
      this.handleJsonRpcMessage(msg.payload);
      break;
      
    case "ping":
      ws.send(JSON.stringify({
        type: "pong",
        sessionId: this.sessionId,
        timestamp: Date.now()
      }));
      break;
      
    case "error":
      this.handleError(msg.error);
      break;
  }
};
```

### 7.3 发送 MCP 消息
```javascript
function sendMcpRequest(method, params) {
  return new Promise((resolve, reject) => {
    const id = this.nextRequestId++;
    
    ws.send(JSON.stringify({
      type: "message",
      sessionId: this.sessionId,
      payload: {
        jsonrpc: "2.0",
        id: id,
        method: method,
        params: params
      },
      timestamp: Date.now()
    }));
    
    this.pendingRequests.set(id, { resolve, reject });
  });
}

// 使用示例
await sendMcpRequest("initialize", {
  protocolVersion: "2025-11-25",
  capabilities: {},
  clientInfo: { name: "test", version: "1.0" }
});
```

## 8. 配置参考

```yaml
# config.yml
websocketServer:
  enableOnStart: true
  host: "127.0.0.1"
  port: 8765
  authToken: "your-secure-token"
  heartbeatInterval: 30000    # 30 秒
  heartbeatTimeout: 90000     # 90 秒
  reconnectDelay: 5000        # 5 秒
  maxRetries: 3
  maxConnections: 1
```
