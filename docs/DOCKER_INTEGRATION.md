# Docker 判题引擎集成指南

## ✅ 已完成的工作

### 1. Celery 异步任务系统
- ✅ `src/judger/celery_app.py` - Celery 应用配置
- ✅ `src/judger/tasks.py` - 判题任务定义
- ✅ Redis 消息队列配置

### 2. Docker 判题服务
- ✅ `src/backend/app/services/docker_judge_service.py` - 判题服务
- ✅ 后端 API 集成 (`app/api/v1/submissions.py`)
- ✅ 支持同步/异步两种模式

### 3. Docker Compose 配置
- ✅ `src/docker/docker-compose.judger.yml` - 判题服务编排
- ✅ Redis 服务
- ✅ Celery Worker 服务

---

## 🚀 启动判题服务

### 方式一：使用 Docker Compose（推荐）

```bash
# 1. 确保判题镜像已构建
cd src/docker
./build-images.sh

# 2. 启动 Redis 和 Celery Worker
docker-compose -f docker-compose.judger.yml up -d

# 3. 查看服务状态
docker-compose -f docker-compose.judger.yml ps

# 4. 查看 Worker 日志
docker-compose -f docker-compose.judger.yml logs -f judger-worker
```

### 方式二：本地开发模式

```bash
# 1. 启动 Redis
docker run -d -p 6379:6379 redis:7-alpine

# 2. 启动 Celery Worker（在后端虚拟环境中）
cd src/backend
source .venv/bin/activate
export PYTHONPATH=/Users/dang/code/OnlineJudge/src
celery -A judger.celery_app worker --loglevel=info --concurrency=2

# 3. 启动后端服务
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🔄 工作流程

### 1. 用户提交代码
```
前端 → POST /api/v1/submissions
```

### 2. 后端处理
```python
# app/api/v1/submissions.py
submission = await service.create_submission(...)
judge_service = DockerJudgeService(db)
task_id = await judge_service.submit_judge_task(submission.id)
```

### 3. Celery 异步判题
```python
# judger/tasks.py
@celery_app.task
def judge_submission(submission_id, code, language, test_cases, ...):
    judger = DockerJudger()
    result = judger.judge(...)
    return result
```

### 4. Docker 容器执行
```
Celery Worker → Docker SDK → 判题容器 → 执行代码 → 返回结果
```

### 5. 更新数据库
```
结果回调 → 更新 submission 状态 → 更新题目统计
```

---

## 📝 配置说明

### 环境变量

在 `src/backend/.env` 中配置：

```bash
# Celery 配置
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# 数据库
DATABASE_URL=sqlite:///./oj.db
```

### Celery 配置

在 `src/judger/celery_app.py` 中：

```python
celery_app.conf.update(
    result_expires=3600,           # 结果过期时间
    task_serializer='json',        # 序列化方式
    timezone='Asia/Shanghai',      # 时区
    worker_prefetch_multiplier=1,  # 预取任务数
)
```

---

## 🧪 测试判题引擎

### 1. 测试 Docker 判题器（不需要 Celery）

```bash
cd src/backend
source .venv/bin/activate
python test_judger_simple.py
```

### 2. 测试完整流程（需要 Celery）

```bash
# 1. 启动所有服务
docker-compose -f src/docker/docker-compose.judger.yml up -d
cd src/backend && source .venv/bin/activate && uvicorn main:app --reload

# 2. 提交代码（通过前端或 API）
curl -X POST http://localhost:8000/api/v1/submissions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "problem_id": 1,
    "code": "n = int(input())\nprint(n * 2)",
    "language": "python"
  }'

# 3. 查看判题结果
curl http://localhost:8000/api/v1/submissions/1
```

---

## 🐛 故障排查

### 1. Celery Worker 无法连接 Redis

**症状**: `Error: Cannot connect to redis://redis:6379/0`

**解决**:
```bash
# 检查 Redis 是否运行
docker ps | grep redis

# 检查网络连接
docker network ls
docker network inspect oj-network
```

### 2. Worker 无法访问 Docker

**症状**: `RuntimeError: 无法连接到 Docker`

**解决**:
```bash
# 确保挂载了 Docker socket
# 在 docker-compose.judger.yml 中:
volumes:
  - /var/run/docker.sock:/var/run/docker.sock
```

### 3. 判题镜像不存在

**症状**: `docker.errors.ImageNotFound: oj-judger-python`

**解决**:
```bash
cd src/docker
./build-images.sh
docker images | grep oj-judger
```

### 4. 模块导入错误

**症状**: `ModuleNotFoundError: No module named 'judger'`

**解决**:
```bash
# 设置 PYTHONPATH
export PYTHONPATH=/path/to/OnlineJudge/src

# 或在 docker-compose.yml 中:
environment:
  - PYTHONPATH=/app
```

---

## 📊 监控和日志

### 查看 Celery Worker 日志

```bash
docker-compose -f src/docker/docker-compose.judger.yml logs -f judger-worker
```

### 查看 Redis 日志

```bash
docker-compose -f src/docker/docker-compose.judger.yml logs -f redis
```

### Celery 任务监控

```bash
# 安装 Flower（可选）
pip install flower

# 启动 Flower
celery -A judger.celery_app flower --port=5555

# 访问 http://localhost:5555
```

---

## 🎯 下一步

1. ✅ Docker 判题引擎集成完成
2. ⏳ 启动服务测试
3. ⏳ 导入真实题库
4. ⏳ 性能优化
5. ⏳ 监控和日志完善

---

## 💡 注意事项

1. **资源限制**: 每个判题容器限制 256MB 内存、1 核 CPU
2. **并发控制**: Celery Worker 默认 2 个并发
3. **安全隔离**: 判题容器禁用网络访问
4. **结果缓存**: 判题结果在 Redis 中保存 1 小时
5. **错误处理**: 判题失败会自动标记为 SYSTEM_ERROR
