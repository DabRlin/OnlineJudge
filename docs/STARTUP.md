# 项目启动指南

## 📋 快速启动

### 方式一：使用 Makefile（推荐）

```bash
# 在项目根目录执行

# 1. 启动后端（新终端窗口）
make backend-dev

# 2. 启动前端（新终端窗口）
make frontend-dev

# 或者同时启动（后台运行）
make dev
```

### 方式二：手动启动

#### 1. 启动后端服务

```bash
# 进入后端目录
cd src/backend

# 激活虚拟环境并启动
source .venv/bin/activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**后端地址**: http://localhost:8000  
**API 文档**: http://localhost:8000/api/docs  
**健康检查**: http://localhost:8000/api/v1/health

#### 2. 启动前端服务

```bash
# 新开终端，进入前端目录
cd src/frontend

# 启动开发服务器
bun run dev
```

**前端地址**: http://localhost:3000

---

## 🗄️ 数据库配置

### 当前使用：SQLite（开发环境）

- **优点**: 零配置，自动创建数据库文件
- **数据库文件**: `src/backend/oj.db`
- **配置**: `.env` 中的 `DATABASE_URL=sqlite+aiosqlite:///./oj.db`

### 切换到 PostgreSQL（生产环境）

1. **启动 PostgreSQL 服务**:
   ```bash
   # 使用 docker-compose
   docker-compose up -d postgres redis
   
   # 或使用 Makefile
   make postgres
   make redis
   ```

2. **修改 `.env` 配置**:
   ```bash
   # 注释掉 SQLite
   # DATABASE_URL=sqlite+aiosqlite:///./oj.db
   
   # 启用 PostgreSQL
   DATABASE_URL=postgresql+asyncpg://oj:password@localhost:5432/oj
   ```

3. **运行数据库迁移**:
   ```bash
   cd src/backend
   source .venv/bin/activate
   alembic upgrade head
   ```

---

## 🔄 数据库迁移

### 创建新迁移

```bash
cd src/backend
source .venv/bin/activate

# 自动生成迁移文件
alembic revision --autogenerate -m "描述你的修改"

# 应用迁移
alembic upgrade head
```

### 回滚迁移

```bash
# 回滚一个版本
alembic downgrade -1

# 回滚到指定版本
alembic downgrade <revision_id>

# 回滚所有
alembic downgrade base
```

---

## 🧪 测试

### 后端测试

```bash
cd src/backend
source .venv/bin/activate

# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_auth.py

# 查看覆盖率
pytest --cov=app --cov-report=html
```

### 前端测试

```bash
cd src/frontend

# 运行测试
bun test

# 运行测试（watch 模式）
bun test --watch
```

---

## 🛠️ 常用命令

### 后端

```bash
# 代码格式化
cd src/backend
source .venv/bin/activate
ruff format .

# 代码检查
ruff check .

# 类型检查
mypy app
```

### 前端

```bash
cd src/frontend

# 代码格式化
bun run format

# 代码检查
bun run lint

# 构建生产版本
bun run build

# 预览生产版本
bun run preview
```

---

## 📊 访问地址汇总

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端应用 | http://localhost:3000 | React 应用 |
| 后端 API | http://localhost:8000 | FastAPI 服务 |
| API 文档 | http://localhost:8000/api/docs | Swagger UI |
| API 文档（备选） | http://localhost:8000/api/redoc | ReDoc |
| PostgreSQL | localhost:5432 | 数据库（如启用） |
| Redis | localhost:6379 | 缓存（如启用） |

---

## 🐛 常见问题

### 1. 端口被占用

```bash
# 查找占用端口的进程
lsof -i :8000  # 后端
lsof -i :3000  # 前端

# 杀死进程
kill -9 <PID>
```

### 2. 数据库连接失败

- 检查 `.env` 文件中的 `DATABASE_URL` 配置
- 如使用 PostgreSQL，确保服务已启动：`docker-compose ps`
- 检查数据库迁移是否已执行：`alembic current`

### 3. 前端依赖问题

```bash
cd src/frontend
rm -rf node_modules
bun install
```

### 4. 后端依赖问题

```bash
cd src/backend
rm -rf .venv
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

---

## 🔐 环境变量

确保 `src/backend/.env` 文件存在并配置正确：

```bash
# 如果不存在，从示例复制
cp src/backend/.env.example src/backend/.env

# 修改必要的配置
# - SECRET_KEY: 生产环境必须修改
# - DATABASE_URL: 根据需要选择 SQLite 或 PostgreSQL
# - CORS_ORIGINS: 添加允许的前端域名
```

---

## 📝 开发工作流

1. **启动服务**: `make dev` 或手动启动前后端
2. **修改代码**: 热重载会自动生效
3. **测试功能**: 访问 http://localhost:3000
4. **提交代码**: 
   ```bash
   git add .
   git commit -m "描述你的修改"
   git push
   ```

---

## 🎯 下一步

- 访问 http://localhost:3000 测试用户注册和登录功能
- 查看 API 文档：http://localhost:8000/api/docs
- 阅读 `task.md` 了解开发计划
- 阅读 `spec.md` 了解技术规范
- 阅读 `skill.md` 了解最佳实践
