# Docker 配置说明

## 📁 目录结构

```
src/docker/
├── images/                      # 判题镜像 Dockerfile
│   ├── python.Dockerfile
│   ├── cpp.Dockerfile
│   ├── java.Dockerfile
│   ├── go.Dockerfile
│   └── javascript.Dockerfile
├── docker-compose.yml           # 主服务 (暂未使用)
├── docker-compose.judger.yml    # 判题服务 (Redis)
├── build-images.sh              # 构建判题镜像脚本
└── README.md                    # 本文件
```

## 🚀 快速开始

### 1. 构建判题镜像
```bash
./build-images.sh
```

### 2. 启动 Redis
```bash
docker-compose -f docker-compose.judger.yml up -d
```

### 3. 查看服务状态
```bash
docker-compose -f docker-compose.judger.yml ps
docker-compose -f docker-compose.judger.yml logs -f
```

### 4. 停止服务
```bash
docker-compose -f docker-compose.judger.yml down
```

## 📦 判题镜像说明

| 镜像 | 大小 | 语言版本 | 用途 |
|------|------|---------|------|
| oj-judger-python | 151MB | Python 3.11 | 执行 Python 代码 |
| oj-judger-cpp | 1.36GB | GCC 13, C++17 | 编译执行 C++ 代码 |
| oj-judger-java | 412MB | Java 17 | 编译执行 Java 代码 |
| oj-judger-go | 823MB | Go 1.21 | 编译执行 Go 代码 |
| oj-judger-javascript | 223MB | Node.js 20 | 执行 JavaScript 代码 |

## 🔧 服务说明

### docker-compose.judger.yml

**包含服务**:
- `redis`: 消息队列，用于 Celery 任务调度

**注意**:
- Celery Worker 在本地运行，不在容器中
- 判题容器由 Celery Worker 动态创建，不在 compose 文件中

## 📝 相关文档

- [判题服务架构](../../docs/JUDGER_ARCHITECTURE.md)
- [Docker 判题引擎集成](../../docs/DOCKER_INTEGRATION.md)
- [项目结构](../../docs/PROJECT_STRUCTURE.md)
