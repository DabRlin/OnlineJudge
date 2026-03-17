# Online Judge 系统 - 现代工具链集成：uv 与 bun

## 1. 工具链概述

### 1.1 uv - 极速 Python 包管理器

**uv** 是由 Astral 团队（Ruff 的开发者）开发的新一代 Python 包管理器和项目管理工具，使用 Rust 编写。

**核心特性：**
- ⚡ **极快速度**：比 pip 快 10-100 倍
- 🔒 **可靠性**：确定性的依赖解析
- 🎯 **兼容性**：完全兼容 pip 和 requirements.txt
- 📦 **统一工具**：包管理 + 虚拟环境 + 项目管理
- 🚀 **零配置**：开箱即用

**官方网站：** https://github.com/astral-sh/uv

### 1.2 bun - 全能 JavaScript 运行时

**bun** 是一个现代化的 JavaScript 运行时、包管理器、打包工具和测试运行器的集合。

**核心特性：**
- ⚡ **极速**：启动速度比 Node.js 快 4 倍
- 📦 **内置包管理**：比 npm/yarn/pnpm 快 20-30 倍
- 🔧 **内置工具**：打包、转译、测试一体化
- 🔌 **兼容性**：兼容 Node.js API 和 npm 包
- 🎯 **TypeScript 原生支持**：无需配置

**官方网站：** https://bun.sh

## 2. 在 OJ 系统中的应用场景

### 2.1 uv 的应用场景

#### 场景 1：后端开发环境管理

```bash
# 初始化项目
uv init backend

# 创建虚拟环境（极速）
uv venv

# 安装依赖（比 pip 快 10-100 倍）
uv pip install django djangorestframework psycopg2-binary redis celery

# 添加开发依赖
uv pip install --dev pytest black ruff mypy

# 生成锁文件（确保依赖一致性）
uv pip freeze > requirements.txt
```

#### 场景 2：判题系统 Python 环境

在判题系统中，需要为 Python 提交创建隔离环境：

```python
# 使用 uv 快速创建判题环境
import subprocess

def create_judge_env(submission_id):
    """为每个 Python 提交创建独立环境"""
    env_path = f"/tmp/judge/{submission_id}/venv"
    
    # 使用 uv 创建虚拟环境（毫秒级）
    subprocess.run(["uv", "venv", env_path], check=True)
    
    # 安装允许的包（如 numpy, scipy）
    subprocess.run([
        "uv", "pip", "install",
        "--python", f"{env_path}/bin/python",
        "numpy", "scipy"
    ], check=True)
    
    return env_path
```

#### 场景 3：CI/CD 加速

```yaml
# .github/workflows/backend-test.yml
name: Backend Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      # 安装 uv（极速）
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      
      # 创建虚拟环境并安装依赖（比传统方式快 10 倍）
      - name: Setup Python environment
        run: |
          uv venv
          uv pip install -r requirements.txt
          uv pip install -r requirements-dev.txt
      
      # 运行测试
      - name: Run tests
        run: |
          source .venv/bin/activate
          pytest
```

### 2.2 bun 的应用场景

#### 场景 1：前端开发环境

```bash
# 创建 React 项目（使用 bun）
bun create react frontend
cd frontend

# 安装依赖（比 npm 快 20-30 倍）
bun install

# 添加依赖
bun add react-router-dom @tanstack/react-query zustand
bun add -d @types/react @types/react-dom typescript

# 开发服务器（启动极快）
bun run dev

# 构建（比 Vite 更快）
bun run build
```

#### 场景 2：判题系统 JavaScript/TypeScript 支持

```typescript
// judge-worker/src/languages/javascript.ts
import { $ } from "bun";

export async function judgeJavaScript(
  code: string,
  input: string,
  timeLimit: number,
  memoryLimit: number
): Promise<JudgeResult> {
  // 写入代码文件
  await Bun.write("/tmp/solution.js", code);
  
  // 使用 bun 运行（比 Node.js 快）
  const proc = Bun.spawn({
    cmd: ["bun", "run", "/tmp/solution.js"],
    stdin: "pipe",
    stdout: "pipe",
    stderr: "pipe",
  });
  
  // 写入测试输入
  proc.stdin.write(input);
  proc.stdin.end();
  
  // 设置超时
  const timeout = setTimeout(() => proc.kill(), timeLimit);
  
  try {
    const output = await new Response(proc.stdout).text();
    const error = await new Response(proc.stderr).text();
    
    clearTimeout(timeout);
    
    return {
      status: error ? "RE" : "AC",
      output,
      error,
      timeUsed: proc.resourceUsage().userCPUTime,
      memoryUsed: proc.resourceUsage().maxRSS,
    };
  } catch (e) {
    return { status: "TLE" };
  }
}
```

#### 场景 3：API 测试和脚本

```typescript
// scripts/seed-database.ts
// 使用 bun 运行数据库种子脚本

import { Database } from "bun:sqlite";

const db = new Database("oj.db");

// 插入测试数据
const problems = [
  { title: "两数之和", difficulty: "easy" },
  { title: "三数之和", difficulty: "medium" },
  { title: "四数之和", difficulty: "hard" },
];

for (const problem of problems) {
  db.run(
    "INSERT INTO problems (title, difficulty) VALUES (?, ?)",
    [problem.title, problem.difficulty]
  );
}

console.log("✅ Database seeded successfully!");

// 运行：bun run scripts/seed-database.ts
```

## 3. 项目结构调整

### 3.1 后端项目结构（使用 uv）

```
backend/
├── pyproject.toml          # uv 项目配置
├── uv.lock                 # 依赖锁文件
├── .python-version         # Python 版本
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   ├── models/
│   ├── services/
│   └── utils/
├── tests/
├── requirements.txt        # 兼容传统工具
└── requirements-dev.txt
```

**pyproject.toml 示例：**

```toml
[project]
name = "oj-backend"
version = "0.1.0"
description = "Online Judge Backend System"
requires-python = ">=3.11"
dependencies = [
    "django>=5.0",
    "djangorestframework>=3.14",
    "psycopg2-binary>=2.9",
    "redis>=5.0",
    "celery>=5.3",
    "pyjwt>=2.8",
    "pydantic>=2.5",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4",
    "pytest-django>=4.7",
    "black>=23.12",
    "ruff>=0.1",
    "mypy>=1.7",
]

[tool.uv]
dev-dependencies = [
    "pytest>=7.4",
    "black>=23.12",
]

[tool.ruff]
line-length = 88
target-version = "py311"

[tool.black]
line-length = 88
target-version = ["py311"]
```

### 3.2 前端项目结构（使用 bun）

```
frontend/
├── package.json
├── bun.lockb              # bun 锁文件
├── tsconfig.json
├── vite.config.ts
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── pages/
│   ├── components/
│   ├── hooks/
│   ├── services/
│   ├── stores/
│   └── utils/
└── public/
```

**package.json 示例：**

```json
{
  "name": "oj-frontend",
  "version": "0.1.0",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "bun test",
    "lint": "eslint src --ext ts,tsx"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.21.0",
    "@tanstack/react-query": "^5.17.0",
    "zustand": "^4.4.7",
    "antd": "^5.12.0",
    "@monaco-editor/react": "^4.6.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.2.0"
  }
}
```

## 4. 开发工作流

### 4.1 后端开发流程（uv）

```bash
# 1. 克隆项目
git clone <repo-url>
cd backend

# 2. 安装 uv（如果还没有）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. 创建虚拟环境并安装依赖（秒级完成）
uv venv
uv pip install -r requirements.txt

# 4. 激活虚拟环境
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate     # Windows

# 5. 运行开发服务器
python manage.py runserver

# 6. 添加新依赖
uv pip install celery
uv pip freeze > requirements.txt

# 7. 运行测试
pytest

# 8. 代码格式化
black .
ruff check --fix .
```

### 4.2 前端开发流程（bun）

```bash
# 1. 克隆项目
git clone <repo-url>
cd frontend

# 2. 安装 bun（如果还没有）
curl -fsSL https://bun.sh/install | bash

# 3. 安装依赖（秒级完成）
bun install

# 4. 运行开发服务器
bun run dev

# 5. 添加新依赖
bun add @tanstack/react-table

# 6. 运行测试
bun test

# 7. 构建生产版本
bun run build
```

## 5. Docker 集成

### 5.1 后端 Dockerfile（使用 uv）

```dockerfile
# 多阶段构建
FROM python:3.11-slim as builder

# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 创建虚拟环境并安装依赖（极速）
RUN uv venv /opt/venv && \
    uv pip install --python /opt/venv/bin/python -r requirements.txt

# 最终镜像
FROM python:3.11-slim

# 复制虚拟环境
COPY --from=builder /opt/venv /opt/venv

# 设置环境变量
ENV PATH="/opt/venv/bin:$PATH"

# 复制应用代码
WORKDIR /app
COPY . .

# 运行应用
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### 5.2 前端 Dockerfile（使用 bun）

```dockerfile
# 构建阶段
FROM oven/bun:1 as builder

WORKDIR /app

# 复制依赖文件
COPY package.json bun.lockb ./

# 安装依赖（极速）
RUN bun install --frozen-lockfile

# 复制源代码
COPY . .

# 构建
RUN bun run build

# 生产阶段
FROM nginx:alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

## 6. 性能对比

### 6.1 uv vs pip

| 操作 | pip | uv | 提升 |
|------|-----|-----|------|
| 安装 Django + DRF + 依赖 | 45s | 2s | **22x** |
| 创建虚拟环境 | 3s | 0.1s | **30x** |
| 依赖解析 | 20s | 0.5s | **40x** |
| 冷缓存安装 | 60s | 5s | **12x** |

### 6.2 bun vs npm/yarn

| 操作 | npm | yarn | pnpm | bun | 提升 |
|------|-----|------|------|-----|------|
| 安装依赖（冷） | 51s | 37s | 24s | 1.2s | **42x vs npm** |
| 安装依赖（热） | 5s | 3s | 2s | 0.15s | **33x vs npm** |
| 运行脚本 | 400ms | 350ms | 300ms | 28ms | **14x vs npm** |
| 启动时间 | 600ms | 550ms | 500ms | 150ms | **4x vs npm** |

## 7. 最佳实践

### 7.1 uv 最佳实践

```bash
# 1. 使用 pyproject.toml 管理项目
uv init

# 2. 固定 Python 版本
echo "3.11" > .python-version

# 3. 分离开发和生产依赖
uv pip install --dev pytest black ruff

# 4. 使用锁文件确保一致性
uv pip compile requirements.in -o requirements.txt

# 5. 定期更新依赖
uv pip install --upgrade-package django
```

### 7.2 bun 最佳实践

```bash
# 1. 使用 bun.lockb 确保一致性
bun install --frozen-lockfile

# 2. 利用 bun 的内置功能
bun test                    # 内置测试运行器
bun run --watch src/main.ts # 热重载

# 3. TypeScript 原生支持
bun run src/script.ts       # 无需编译

# 4. 使用 bun 的 API
import { $ } from "bun";    # Shell 命令
import { file } from "bun"; # 文件操作
```

## 8. 迁移指南

### 8.1 从 pip 迁移到 uv

```bash
# 1. 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 创建虚拟环境
uv venv

# 3. 从现有 requirements.txt 安装
uv pip install -r requirements.txt

# 4. 生成新的锁文件
uv pip freeze > requirements.txt

# 5. 更新 CI/CD 配置
# 将 pip install 替换为 uv pip install
```

### 8.2 从 npm/yarn 迁移到 bun

```bash
# 1. 安装 bun
curl -fsSL https://bun.sh/install | bash

# 2. 从 package-lock.json 或 yarn.lock 安装
bun install

# 3. 生成 bun.lockb
# 自动生成

# 4. 更新脚本
# package.json 中的脚本无需修改，直接用 bun run

# 5. 更新 CI/CD
# 将 npm install 替换为 bun install
```

## 9. 潜在问题和解决方案

### 9.1 uv 兼容性

**问题**：某些包可能与 uv 不完全兼容

**解决方案**：
```bash
# 回退到 pip 安装特定包
pip install problematic-package

# 或使用 uv 的兼容模式
uv pip install --legacy-resolver problematic-package
```

### 9.2 bun 兼容性

**问题**：某些 Node.js 原生模块可能不兼容

**解决方案**：
```json
{
  "trustedDependencies": ["sharp", "sqlite3"],
  "scripts": {
    "postinstall": "bun run build-native"
  }
}
```

## 10. 总结

### 为什么选择 uv 和 bun？

**uv 的优势：**
- ⚡ 开发效率提升 10-100 倍
- 🔒 更可靠的依赖管理
- 🚀 CI/CD 时间大幅缩短
- 💰 节省云计算成本

**bun 的优势：**
- ⚡ 极速的开发体验
- 🔧 一体化工具链
- 📦 更小的 node_modules
- 🎯 TypeScript 原生支持

**在 OJ 系统中的价值：**
- 开发环境搭建从分钟级降到秒级
- CI/CD 流程大幅加速
- 判题系统性能提升
- 更好的开发者体验

这两个工具代表了现代开发工具链的发展方向，值得在新项目中采用！
