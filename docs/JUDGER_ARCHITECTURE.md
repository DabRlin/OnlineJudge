# 判题服务架构说明

## 🏗️ 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                    用户提交代码                              │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  前端 (React)                                                │
│  http://localhost:3000                                       │
│  - 用户界面、代码编辑器                                      │
└────────────────────────┬────────────────────────────────────┘
                         │ POST /api/v1/submissions
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  后端 (FastAPI)                                              │
│  http://localhost:8000                                       │
│  - 接收提交、创建记录、提交判题任务                          │
└────────────────────────┬────────────────────────────────────┘
                         │ 提交到队列
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Redis (Docker 容器)                                         │
│  localhost:6379                                              │
│  - 消息队列、任务存储                                        │
└────────────────────────┬────────────────────────────────────┘
                         │ 拉取任务
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Celery Worker (本地进程)                                    │
│  - 异步判题任务、调用 Docker 判题引擎                        │
└────────────────────────┬────────────────────────────────────┘
                         │ 创建容器
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  判题容器 (临时 Docker 容器)                                 │
│  - oj-judger-python/cpp/java/go/javascript                  │
│  - 编译、运行、测试、返回结果                                │
└────────────────────────┬────────────────────────────────────┘
                         │ 返回结果
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  数据库 (SQLite)                                             │
│  - 更新提交状态、分数、时间、内存                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 组件说明

### 1. 前端 (React + Vite)
- **位置**: `src/frontend/`
- **运行**: 本地进程 (bun dev)
- **端口**: 3000
- **作用**: 用户界面、代码编辑、结果展示

### 2. 后端 (FastAPI)
- **位置**: `src/backend/`
- **运行**: 本地进程 (uvicorn)
- **端口**: 8000
- **作用**: API 服务、业务逻辑、任务调度

### 3. Redis
- **位置**: Docker 容器
- **运行**: `docker-compose -f docker-compose.judger.yml up -d`
- **端口**: 6379
- **作用**: Celery 消息队列、任务结果缓存

### 4. Celery Worker
- **位置**: `src/judger/`
- **运行**: 本地进程 (celery worker)
- **作用**: 异步判题任务、调用 Docker SDK

### 5. 判题容器
- **位置**: 临时 Docker 容器
- **镜像**: 
  - `oj-judger-python` (151MB)
  - `oj-judger-cpp` (1.36GB)
  - `oj-judger-java` (412MB)
  - `oj-judger-go` (823MB)
  - `oj-judger-javascript` (223MB)
- **作用**: 安全隔离执行用户代码

---

## 🔄 判题流程详解

### Step 1: 用户提交代码
```javascript
// 前端
POST /api/v1/submissions
{
  "problem_id": 1,
  "code": "n = int(input())\nprint(n * 2)",
  "language": "python"
}
```

### Step 2: 后端处理
```python
# app/api/v1/submissions.py
submission = await service.create_submission(...)  # 创建记录
judge_service = DockerJudgeService(db)
task_id = await judge_service.submit_judge_task(submission.id)  # 提交任务
```

### Step 3: 任务入队
```python
# app/services/docker_judge_service.py
task = judge_submission.delay(
    submission_id=submission_id,
    code=code,
    language="python",
    test_cases=[{"input": "5", "output": "10"}],
    time_limit=1000,
    memory_limit=256
)
# 任务被发送到 Redis 队列
```

### Step 4: Celery Worker 处理
```python
# judger/tasks.py
@celery_app.task
def judge_submission(submission_id, code, language, test_cases, ...):
    judger = DockerJudger()  # 创建判题器
    result = judger.judge(...)  # 执行判题
    return result
```

### Step 5: Docker 判题
```python
# judger/docker_judger.py
def judge(code, language, test_cases, ...):
    # 1. 创建临时目录
    work_dir = tempfile.mkdtemp()
    
    # 2. 保存代码
    with open(f"{work_dir}/solution.py", 'w') as f:
        f.write(code)
    
    # 3. 编译 (如果需要)
    # ...
    
    # 4. 运行测试用例
    for test_case in test_cases:
        container = docker_client.containers.run(
            image="oj-judger-python:latest",
            command="python3 solution.py < input.txt",
            volumes={work_dir: {'bind': '/workspace'}},
            mem_limit="256m",
            cpu_quota=100000,
            network_mode="none",  # 禁用网络
            detach=True
        )
        # 等待执行、比对结果
    
    # 5. 返回结果
    return JudgeResult(status="accepted", score=100, ...)
```

### Step 6: 更新数据库
```python
# app/services/docker_judge_service.py
await submission_service.update_submission(
    submission_id,
    SubmissionUpdate(
        status=SubmissionStatus.ACCEPTED,
        score=100,
        time_used=50,
        memory_used=1024
    )
)
```

---

## 🚀 启动顺序

### 1. 启动 Redis
```bash
cd src/docker
docker-compose -f docker-compose.judger.yml up -d
```

### 2. 启动 Celery Worker
```bash
cd src/backend
source .venv/bin/activate
export PYTHONPATH=$(pwd)/..
celery -A judger.celery_app worker --loglevel=info --concurrency=2
```

### 3. 启动后端
```bash
cd src/backend
source .venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 启动前端
```bash
cd src/frontend
bun run dev
```

---

## 🔧 关键配置

### Celery 配置 (`judger/celery_app.py`)
```python
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

celery_app.conf.update(
    result_expires=3600,           # 结果保留 1 小时
    task_serializer='json',
    worker_prefetch_multiplier=1,  # 每次只拉取 1 个任务
)
```

### Docker 资源限制
```python
# 每个判题容器
mem_limit="256m"      # 内存限制 256MB
cpu_quota=100000      # CPU 限制 1 核
network_mode="none"   # 禁用网络
```

---

## 🐛 常见问题

### Q1: Celery Worker 无法连接 Redis
**检查**: `docker ps | grep redis`  
**解决**: 确保 Redis 容器正在运行

### Q2: 判题镜像不存在
**检查**: `docker images | grep oj-judger`  
**解决**: `cd src/docker && ./build-images.sh`

### Q3: 模块导入错误
**检查**: `echo $PYTHONPATH`  
**解决**: `export PYTHONPATH=/path/to/OnlineJudge/src`

---

## 📊 性能指标

- **并发判题**: 2 个 Worker，每个处理 1 个任务
- **判题速度**: Python ~1s, C++ ~2s (含编译)
- **资源占用**: 每个容器 256MB 内存
- **队列容量**: Redis 默认无限制

---

## 🔒 安全措施

1. **网络隔离**: 判题容器禁用网络访问
2. **资源限制**: CPU、内存、时间严格限制
3. **文件系统**: 只读挂载，临时目录用完即删
4. **用户隔离**: 容器内使用非 root 用户
5. **代码沙箱**: Docker 容器完全隔离

---

## 📝 下一步优化

1. ⏳ WebSocket 实时推送判题结果
2. ⏳ 判题队列优先级
3. ⏳ 分布式 Worker (多机部署)
4. ⏳ 判题结果缓存
5. ⏳ 监控和日志系统
