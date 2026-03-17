# Docker 判题引擎使用指南

## 📦 已构建的镜像

```bash
docker images | grep oj-judger
```

当前已构建的镜像：
- `oj-judger-python` (151MB) - Python 3.11
- `oj-judger-cpp` (1.36GB) - C++ 17 (GCC 13)
- `oj-judger-java` (412MB) - Java 17 (Eclipse Temurin)
- `oj-judger-go` (823MB) - Go 1.21
- `oj-judger-javascript` (223MB) - Node.js 20

## 🧪 测试判题引擎

### 方式一：直接测试（需要后端虚拟环境）

```bash
cd src/backend
source .venv/bin/activate
python test_judger_simple.py
```

### 方式二：在后端代码中使用

```python
from judger.docker_judger import DockerJudger, JudgeResult
from judger.languages import Language

# 创建判题器
judger = DockerJudger()

# 准备代码和测试用例
code = """
n = int(input())
print(n * 2)
"""

test_cases = [
    {"input": "5", "output": "10"},
    {"input": "10", "output": "20"},
]

# 执行判题
result = judger.judge(
    code=code,
    language=Language.PYTHON,
    test_cases=test_cases,
    time_limit=1000,  # 毫秒
    memory_limit=256,  # MB
)

# 检查结果
if result.status == JudgeResult.ACCEPTED:
    print(f"通过！分数: {result.score}")
else:
    print(f"失败: {result.status}")
```

## 🚀 Docker Compose 判题服务

### 启动判题服务

```bash
cd src/docker
docker-compose -f docker-compose.judger.yml up -d
```

### 服务说明

- **redis**: 消息队列，端口 6379
- **judger-worker**: Celery 判题工作进程（待实现）

### 停止服务

```bash
cd src/docker
docker-compose -f docker-compose.judger.yml down
```

## 📝 判题结果状态

- `PENDING` - 等待判题
- `JUDGING` - 判题中
- `ACCEPTED` - 通过
- `WRONG_ANSWER` - 答案错误
- `TIME_LIMIT_EXCEEDED` - 超时
- `MEMORY_LIMIT_EXCEEDED` - 内存超限
- `RUNTIME_ERROR` - 运行时错误
- `COMPILE_ERROR` - 编译错误
- `SYSTEM_ERROR` - 系统错误

## 🔧 资源限制

默认限制：
- CPU: 1 核
- 内存: 256MB (Java 为 512MB)
- 时间: 1000ms (可配置)
- 网络: 禁用

## ⚠️ 注意事项

1. **Docker 守护进程**: 确保 Docker 正在运行
2. **镜像构建**: 首次使用前需要构建镜像
3. **权限**: 确保当前用户有 Docker 权限
4. **OrbStack**: 已在 OrbStack 环境测试通过

## 🐛 常见问题

### 1. 无法连接到 Docker

```
RuntimeError: 无法连接到 Docker
```

**解决**: 确保 Docker/OrbStack 正在运行

### 2. 镜像不存在

```
docker.errors.ImageNotFound
```

**解决**: 运行 `cd src/docker && ./build-images.sh`

### 3. 权限错误

```
Permission denied
```

**解决**: 确保用户在 docker 组中，或使用 sudo

## 📚 下一步

1. ✅ 构建判题镜像
2. ⏳ 测试判题引擎
3. ⏳ 集成 Celery 异步任务
4. ⏳ 更新后端 API 使用判题引擎
5. ⏳ 导入真实题库
