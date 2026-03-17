# Online Judge

一个现代化的在线判题系统，支持多种编程语言，提供完整的题目管理、竞赛组织和 Docker 沙箱代码评测功能。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ 已实现功能

- 🔐 **用户认证**：注册/登录/JWT Token，角色权限（user / admin / super_admin）
- 📚 **题目系统**：CRUD、Markdown 描述、测试用例管理、难度/标签筛选
- 📦 **题库导入**：JSON 批量导入（命令行 + 前端界面），内置 23 道经典算法题
- 🐳 **Docker 判题**：代码在隔离容器中运行，支持资源限制（时间/内存/网络）
- ⚡ **异步队列**：Celery + Redis，判题后自动回写结果
- 🌐 **多语言**：Python / C++ / Java / Go / JavaScript（5 种语言全部验证通过）
- 📊 **提交系统**：提交记录列表、详情页、前端实时轮询判题状态
- 🏆 **竞赛系统**：创建竞赛、管理题目、报名参赛、ACM/OI 规则排行榜

## 🛠️ 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | FastAPI 0.109+ (async) |
| 数据库 | SQLite (开发) / PostgreSQL (生产) |
| ORM | SQLAlchemy 2.0 (async) + Alembic |
| 队列 | Celery + Redis |
| 前端框架 | React 18 + TypeScript + Vite 5 |
| UI 组件库 | Ant Design 5 + TailwindCSS 3 |
| 状态管理 | Zustand 4 |
| 代码编辑器 | Monaco Editor |
| 判题沙箱 | Docker 容器隔离 |
| Python 包管理 | uv |
| JS 包管理 | bun |

## 📋 前置要求

- Python 3.11+
- bun 1.0+（或 Node.js 20+）
- Docker（用于判题沙箱和 Redis）
- Redis（判题队列）

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/DabRlin/OnlineJudge.git
cd OnlineJudge
```

### 2. 构建判题 Docker 镜像

```bash
cd src/docker
bash build-images.sh
```

### 3. 启动 Redis

```bash
docker run -d -p 6379:6379 --name oj-redis redis:7-alpine
```

### 4. 后端设置

```bash
cd src/backend

# 安装依赖（需先安装 uv：https://astral.sh/uv）
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt

# 数据库迁移
alembic upgrade head

# 创建管理员账号和测试数据
python scripts/create_test_data.py

# 导入经典题库（23 道题）
python scripts/import_problems.py

# 启动后端
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. 启动 Celery 判题 Worker

```bash
cd src/backend
source .venv/bin/activate
cd ../judger
celery -A celery_app worker -Q judge,celery -c 2 --loglevel=info
```

### 6. 前端设置

```bash
cd src/frontend

# 安装依赖（需先安装 bun：https://bun.sh）
bun install

# 启动开发服务器
bun run dev
```

前端：http://localhost:5173  
后端 API：http://localhost:8000  
API 文档：http://localhost:8000/api/docs

### 默认账号

| 账号 | 密码 | 角色 |
|------|------|------|
| admin | admin123456 | 超级管理员 |

## 📁 项目结构

```
OnlineJudge/
├── src/
│   ├── backend/              # FastAPI 后端
│   │   ├── app/
│   │   │   ├── api/v1/       # API 路由（auth, problems, submissions, contests）
│   │   │   ├── models/       # SQLAlchemy 模型
│   │   │   ├── schemas/      # Pydantic schemas
│   │   │   ├── services/     # 业务逻辑层
│   │   │   └── core/         # 配置、依赖、安全
│   │   ├── alembic/          # 数据库迁移
│   │   └── scripts/          # 工具脚本（导入题库等）
│   ├── frontend/             # React 前端
│   │   └── src/
│   │       ├── pages/        # 页面组件
│   │       ├── components/   # 通用组件
│   │       ├── services/     # API 服务层
│   │       ├── stores/       # Zustand 状态管理
│   │       └── types/        # TypeScript 类型定义
│   ├── judger/               # Celery 判题 Worker
│   └── docker/               # Docker 镜像构建脚本
└── docs/                     # 项目文档
```

## 📦 题库导入

内置 23 道经典算法题（JSON 格式，位于 `src/backend/scripts/classic_problems.json`）。

**命令行导入：**
```bash
cd src/backend
python scripts/import_problems.py                        # 导入默认题库
python scripts/import_problems.py path/to/problems.json  # 自定义文件
python scripts/import_problems.py --force                # 强制覆盖同名题目
```

**题目 JSON 格式：**
```json
{
  "problems": [
    {
      "title": "A + B Problem",
      "description": "给定两个整数 A 和 B，输出 A + B 的值。",
      "difficulty": "easy",
      "time_limit": 1000,
      "memory_limit": 256,
      "tags": ["入门", "数学"],
      "test_cases": [
        { "input": "1 2", "output": "3", "is_sample": true }
      ]
    }
  ]
}
```

## 🐳 Docker 判题镜像

| 语言 | 镜像名称 | 基础镜像 |
|------|----------|----------|
| Python | oj-judger-python | python:3.11-slim |
| C++ | oj-judger-cpp | gcc:13-bookworm |
| Java | oj-judger-java | eclipse-temurin:17-jdk |
| Go | oj-judger-go | golang:1.21-bookworm |
| JavaScript | oj-judger-js | node:20-slim |

## 📄 许可证

MIT License - 查看 [LICENSE](LICENSE) 文件

## 🙏 致谢

[FastAPI](https://fastapi.tiangolo.com/) · [React](https://react.dev/) · [Vite](https://vitejs.dev/) · [Ant Design](https://ant.design/) · [uv](https://github.com/astral-sh/uv) · [bun](https://bun.sh/)
