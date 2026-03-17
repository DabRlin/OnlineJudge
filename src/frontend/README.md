# Online Judge Frontend

React + TypeScript + Vite + Ant Design 前端应用

## 特性

- ⚡ **Vite**: 极速的开发服务器和构建工具
- ⚛️ **React 18**: 最新的 React 特性
- 🔷 **TypeScript**: 类型安全
- 🎨 **Ant Design**: 企业级 UI 组件库
- 🎨 **TailwindCSS**: 实用优先的 CSS 框架
- 🔄 **TanStack Query**: 强大的数据同步
- 🗂️ **Zustand**: 轻量级状态管理
- 📝 **Monaco Editor**: VS Code 同款代码编辑器
- 🧪 **Vitest**: 快速的单元测试框架

## 快速开始

### 前置要求

- bun 1.0+ (推荐) 或 Node.js 20+

### 安装

```bash
# 安装 bun (如果未安装)
curl -fsSL https://bun.sh/install | bash

# 安装依赖 (使用 bun - 极速！)
bun install

# 复制环境变量
cp .env.example .env

# 编辑 .env 配置后端 API 地址
vim .env
```

### 开发

```bash
# 启动开发服务器
bun run dev

# 应用将运行在 http://localhost:3000
```

### 构建

```bash
# 类型检查
bun run type-check

# 构建生产版本
bun run build

# 预览生产构建
bun run preview
```

### 代码质量

```bash
# ESLint 检查
bun run lint

# Prettier 格式化
bun run format
```

### 测试

```bash
# 运行测试
bun test

# 测试覆盖率
bun test --coverage
```

## 项目结构

```
src/
├── pages/          # 页面组件
│   └── Home/      # 首页
├── components/     # 通用组件
│   └── Layout/    # 布局组件
├── services/       # API 服务
│   └── api.ts     # Axios 配置
├── stores/         # Zustand 状态管理
├── hooks/          # 自定义 Hooks
├── types/          # TypeScript 类型定义
├── utils/          # 工具函数
├── constants/      # 常量定义
├── styles/         # 全局样式
│   └── index.css  # Tailwind CSS
├── App.tsx        # 根组件
└── main.tsx       # 应用入口
```

## 技术栈

- **React 18.2** - UI 框架
- **TypeScript 5.3** - 类型系统
- **Vite 5.0** - 构建工具
- **Ant Design 5.12** - UI 组件库
- **TailwindCSS 3.4** - CSS 框架
- **React Router 6.21** - 路由
- **TanStack Query 5.17** - 数据获取
- **Zustand 4.4** - 状态管理
- **Axios 1.6** - HTTP 客户端
- **Monaco Editor 4.6** - 代码编辑器
- **Lucide React** - 图标库

## 环境变量

```bash
# API 配置
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_BASE_URL=ws://localhost:8000/ws

# 应用配置
VITE_APP_NAME=Online Judge
VITE_APP_VERSION=0.1.0
```

## 开发指南

### 添加新页面

1. 在 `src/pages/` 创建页面目录
2. 创建 `index.tsx` 文件
3. 在 `src/App.tsx` 添加路由

### 添加 API 服务

1. 在 `src/services/` 创建服务文件
2. 使用 `api` 实例发起请求
3. 配合 TanStack Query 使用

### 状态管理

使用 Zustand 创建 store：

```typescript
import { create } from 'zustand'

interface AuthState {
  user: User | null
  login: (user: User) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>(set => ({
  user: null,
  login: user => set({ user }),
  logout: () => set({ user: null }),
}))
```

## 性能优化

- 代码分割：自动按路由分割
- 懒加载：使用 `React.lazy()`
- 图片优化：使用 WebP 格式
- 缓存策略：TanStack Query 自动缓存

## 浏览器支持

- Chrome (最新版)
- Firefox (最新版)
- Safari (最新版)
- Edge (最新版)

## License

MIT
