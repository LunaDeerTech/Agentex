# Agentex Frontend

Vue 3 + TypeScript + Vite 前端项目

## 技术栈

- **Vue 3.4+** - 渐进式 JavaScript 框架
- **TypeScript 5.3+** - 类型安全
- **Vite 5.0+** - 下一代前端构建工具
- **Pinia** - Vue 3 状态管理
- **Vue Router 4** - 官方路由
- **Element Plus** - Vue 3 UI 组件库
- **Axios** - HTTP 客户端

## 项目结构

```
src/
├── api/              # Axios 请求封装
├── components/       # 可复用组件
├── composables/      # 组合式函数
├── router/           # 路由配置
├── stores/           # Pinia 状态管理
├── styles/           # 全局样式
├── views/            # 页面组件
│   ├── auth/         # 认证相关页面
│   └── settings/     # 设置相关页面
└── main.ts           # 应用入口
```

## 开发

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:5173

### 构建生产版本

```bash
npm run build
```

### 代码检查

```bash
npm run lint
```

### 格式化代码

```bash
npm run format
```

## 配置说明

### 环境变量

创建 `.env.local` 文件配置本地环境变量：

```env
VITE_API_BASE_URL=/api
VITE_APP_TITLE=Agentex
```

### API 代理

开发环境下，`/api` 路径会自动代理到 `http://localhost:8000`（后端服务）。

## 设计规范

详见 [FrontendDesign.md](../docs/FrontendDesign.md)

### 色彩规范

| 类型 | 色值 | 用途 |
|------|------|------|
| 主色调 | #409EFF | 主要按钮、链接、强调 |
| 成功色 | #67C23A | 成功状态 |
| 警告色 | #E6A23C | 警告提示 |
| 危险色 | #F56C6C | 错误、删除 |
| 信息色 | #909399 | 辅助信息 |

### 字体规范

- 正文：14px，PingFang SC / Microsoft YaHei
- 代码：13px，Consolas / Monaco
