# 项目目录结构

```
OnlineJudge/
├── README.md                    # 项目说明
├── LICENSE                      # 开源协议
├── Makefile                     # 便捷命令
├── .gitignore                   # Git 忽略配置
│
├── docs/                        # 📚 文档目录
│   ├── 01-项目概述.md
│   ├── 02-系统架构设计.md
│   ├── 03-数据库设计.md
│   ├── 04-API接口设计.md
│   ├── 05-判题系统设计.md
│   ├── STARTUP.md              # 启动指南
│   ├── task.md                 # 开发任务
│   └── PROJECT_STRUCTURE.md    # 本文件
│
├── src/                         # 💻 源代码目录
│   ├── backend/                # 后端 FastAPI
│   │   ├── app/
│   │   ├── alembic/
│   │   ├── main.py
│   │   └── requirements.txt
│   │
│   ├── frontend/               # 前端 React
│   │   ├── src/
│   │   ├── public/
│   │   ├── package.json
│   │   └── vite.config.ts
│   │
│   ├── judger/                 # 判题引擎
│   │   ├── __init__.py
│   │   ├── docker_judger.py
│   │   ├── languages.py
│   │   └── tasks.py
│   │
│   └── docker/                 # Docker 配置
│       ├── images/             # 判题镜像
│       │   ├── python.Dockerfile
│       │   ├── cpp.Dockerfile
│       │   ├── java.Dockerfile
│       │   ├── go.Dockerfile
│       │   └── javascript.Dockerfile
│       ├── docker-compose.yml
│       ├── docker-compose.judger.yml
│       └── build-images.sh
│
└── tests/                       # 🧪 测试目录
    ├── backend/                # 后端测试
    ├── frontend/               # 前端测试
    └── integration/            # 集成测试
```

## 目录说明

### `/docs` - 文档
所有项目文档集中在此目录

### `/src/backend` - 后端
FastAPI 后端应用代码

### `/src/frontend` - 前端  
React 前端应用代码

### `/src/judger` - 判题引擎
Docker 判题引擎核心代码

### `/src/docker` - Docker 配置
所有 Docker 相关配置，包括镜像和编排文件

### `/tests` - 测试
所有测试代码

## 启动方式

详见 `docs/STARTUP.md`
