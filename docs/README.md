# Online Judge 系统

一个现代化的在线判题系统，支持多种编程语言，提供完整的题目管理、竞赛组织和代码评测功能。

## ✨ 特性

- 🚀 **现代化技术栈**：FastAPI + React + TypeScript
- ⚡ **极速开发体验**：uv (Python) + bun (JavaScript) + Vite
- 🔒 **安全沙箱**：Docker 多层隔离（namespace + cgroup + seccomp + AppArmor）
- 🌐 **多语言支持**：C/C++, Python, Java, Go, JavaScript
- 📊 **实时判题**：异步任务队列，支持高并发
- 🎯 **类型安全**：全栈 TypeScript + Pydantic
- 📱 **响应式设计**：支持桌面和移动端

## 🛠️ 技术栈

### 后端
- **框架**：FastAPI 0.109+ (异步 Web 框架)
- **包管理**：uv (比 pip 快 10-100 倍)
- **数据库**：SQLite (开发) / PostgreSQL (生产)
- **ORM**：SQLAlchemy 2.0 (async)
- **缓存**：Redis 7+
- **异步任务**：Celery / ARQ

### 前端
- **框架**：React 18 + TypeScript 5
- **构建工具**：Vite 5.0
- **包管理**：bun (比 npm 快 20-30 倍)
- **UI 库**：Ant Design 5 + TailwindCSS 3
- **状态管理**：Zustand 4
- **数据请求**：TanStack Query 5

### 判题系统
- **沙箱**：Docker 容器隔离
- **队列**：Redis
- **支持语言**：C/C++, Python, Java, Go, JavaScript

## 📋 前置要求

### 必需
- **Python 3.11+**
- **bun 1.0+** (或 Node.js 20+)
- **Git**

### 可选（推荐）
- **Docker Desktop** (用于 Redis 和生产环境数据库)

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/OnlineJudge.git
cd OnlineJudge
```

### 2. 安装工具链

```bash
# 安装 uv (Python 包管理器)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装 bun (JavaScript 运行时和包管理器)
curl -fsSL https://bun.sh/install | bash
```

### 3. 后端设置

```bash
cd backend

# 创建虚拟环境并安装依赖（使用 uv，极速！）
uv venv
source .venv/bin/activate  # Linux/macOS
# 或 .venv\Scripts\activate  # Windows

uv pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件（默认使用 SQLite，无需额外配置）

# 运行数据库迁移
alembic upgrade head

# 启动开发服务器
uvicorn main:app --reload
```

后端 API 将运行在 http://localhost:8000
- API 文档：http://localhost:8000/api/docs
- ReDoc：http://localhost:8000/api/redoc

### 4. 前端设置

```bash
cd frontend

# 安装依赖（使用 bun，极速！）
bun install

# 配置环境变量
cp .env.example .env

# 启动开发服务器
bun run dev
```

前端应用将运行在 http://localhost:3000

### 5. 启动 Redis（可选，用于缓存和队列）

```bash
# 使用 Docker
docker run -d -p 6379:6379 redis:7-alpine

# 或使用 docker-compose
docker-compose up -d redis
```

## 📦 使用 Makefile（推荐）

我们提供了 Makefile 来简化常用操作：

```bash
# 查看所有可用命令
make help

# 初始化开发环境（安装所有依赖）
make setup

# 启动开发环境（后端 + 前端 + Redis）
make dev

# 运行测试
make test

# 构建生产版本
make build

# 清理临时文件
make clean
```

## 📁 项目结构

```
OnlineJudge/
├── backend/          # FastAPI 后端
│   ├── app/         # 应用代码
│   ├── alembic/     # 数据库迁移
│   └── tests/       # 测试
├── frontend/         # React 前端
│   ├── src/         # 源代码
│   └── public/      # 静态资源
├── judge-worker/     # 判题工作节点
├── docker/          # Docker 配置
├── doc/             # 设计文档
└── scripts/         # 工具脚本
```

## 🔧 开发指南

### 后端开发

```bash
cd backend

# 创建新的数据库迁移
alembic revision --autogenerate -m "描述"

# 运行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1

# 运行测试
pytest

# 代码格式化
ruff check --fix .
black .
```

### 前端开发

```bash
cd frontend

# 运行开发服务器
bun run dev

# 构建生产版本
bun run build

# 预览生产构建
bun run preview

# 运行测试
bun test

# 代码检查
bun run lint
```

## 🐳 Docker 部署

### 开发环境

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 生产环境

```bash
# 构建镜像
docker-compose -f docker-compose.prod.yml build

# 启动服务
docker-compose -f docker-compose.prod.yml up -d
```

## 📚 文档

详细的设计文档位于 `doc/` 目录：

- [项目概述](./doc/01-项目概述.md)
- [系统架构设计](./doc/02-系统架构设计.md)
- [数据库设计](./doc/03-数据库设计.md)
- [API 接口设计](./doc/04-API接口设计.md)
- [判题系统设计](./doc/05-判题系统设计.md)
- [前端设计](./doc/06-前端设计.md)
- [现代工具链集成 (uv & bun)](./doc/07-现代工具链集成-uv与bun.md)
- [沙箱技术深入解析](./doc/08-沙箱技术深入解析.md)
- [技术栈确定方案](./doc/09-技术栈确定方案.md)
- [项目结构设计](./doc/10-项目结构设计.md)
- [数据库选择方案](./doc/11-数据库选择方案.md)

## 🧪 测试

```bash
# 后端测试
cd backend
pytest

# 前端测试
cd frontend
bun test

# 测试覆盖率
cd backend
pytest --cov=app --cov-report=html
```

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Python Web 框架
- [React](https://react.dev/) - 用户界面库
- [Vite](https://vitejs.dev/) - 下一代前端构建工具
- [uv](https://github.com/astral-sh/uv) - 极速 Python 包管理器
- [bun](https://bun.sh/) - 极速 JavaScript 运行时
- [Ant Design](https://ant.design/) - 企业级 UI 组件库

## 📞 联系方式

- 项目主页：https://github.com/yourusername/OnlineJudge
- Issue 追踪：https://github.com/yourusername/OnlineJudge/issues
- 讨论区：https://github.com/yourusername/OnlineJudge/discussions

---

**开发状态**: 🚧 开发中

**版本**: 0.1.0

**最后更新**: 2024-03-15
