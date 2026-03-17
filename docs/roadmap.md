# Online Judge - 后续开发规划（Roadmap）

> 创建时间：2026-03-17
> 当前状态：MVP 已完成，项目暂停开发
> 本文档记录后续可继续开发的功能方向，供再次启动时参考

---

## 当前已完成功能（截止 2026-03-17）

- 用户认证与授权（注册/登录/JWT/三级角色）
- 题目管理（CRUD/测试用例/Markdown+KaTeX/标签/搜索分页）
- Docker 判题引擎（Celery + Redis，5 种语言）
- 实时判题结果展示（前端轮询）
- 提交记录与详情页
- 竞赛系统（ACM/OI 规则/排行榜/封榜）
- 题库导入（API + CLI + 内置 23 道题）

---

## Phase 4：高级功能

### 4.1 讨论区

**目标**：在题目页面下方提供发帖、回复、点赞功能。

**后端任务**
- 新增模型 `Discussion`（帖子）和 `Comment`（评论/回复）
  - `Discussion`：`id` / `problem_id` / `user_id` / `title` / `content` / `like_count` / `comment_count` / `is_pinned` / `created_at`
  - `Comment`：`id` / `discussion_id` / `user_id` / `parent_id`（支持嵌套）/ `content` / `like_count` / `created_at`
- Alembic 迁移
- 接口（`/api/v1/discussions`）：
  - `GET /discussions?problem_id=&page=`：帖子列表
  - `POST /discussions`：发帖（已登录）
  - `GET /discussions/{id}`：帖子详情 + 评论树
  - `POST /discussions/{id}/comments`：回复
  - `POST /discussions/{id}/like`：点赞

**前端任务**
- `ProblemDetail` 页面底部增加讨论区入口
- `DiscussionList` / `DiscussionDetail` 页面
- Markdown 编辑器（复用现有 `@uiw/react-md-editor`）

---

### 4.2 用户统计主页

**目标**：丰富个人中心页面，展示解题数据。

**后端任务**
- 统计接口 `GET /api/v1/users/{id}/stats`
  - 总提交数 / AC 数 / 通过率
  - 各难度（easy/medium/hard）通过题数
  - 过去 365 天每日提交热力图数据（`{date: count}` 格式）
  - 各标签 AC 题数

**前端任务**
- `Profile` 页面增强：
  - 提交热力图（可用 `react-calendar-heatmap` 或自行实现）
  - 难度分布饼图（Ant Design Charts 或 ECharts）
  - 标签掌握雷达图

---

### 4.3 Special Judge

**目标**：支持需要自定义判题逻辑的题目（如浮点精度、多解问题）。

**后端任务**
- `Problem` 模型新增字段：`is_special_judge: bool`、`checker_code: Text`
- Alembic 迁移
- `DockerJudger` 增加 checker 模式：
  - 将用户输出和期望输出都传给 checker 脚本
  - checker 返回 0 表示 AC，非 0 表示 WA

**前端任务**
- `ProblemEdit` 页面增加 Special Judge 开关和 checker 代码编辑区

---

## Phase 5：管理与运维

### 5.1 管理后台

**目标**：提供基础的系统管理界面。

- 用户列表：搜索 / 查看 / 封禁 / 修改角色
- 判题队列监控：当前 Celery 任务数、Redis 队列长度、最近判题日志
- 题目审核（可选）：新题目默认不公开，管理员审核后发布

**实现建议**：在现有前端新增 `/admin` 路由组，用 `admin` 角色守卫。

---

### 5.2 扩充题库

**目标**：100+ 道题目，覆盖常见算法分类。

- 编写 `src/backend/scripts/import_codeforces.py`
  - 调用 `https://codeforces.com/api/problemset.problems`
  - 转换为内部 JSON 格式
  - 复用现有 `import_problems.py` 逻辑导入
- 题目分类覆盖：数组/字符串/链表/树/图/动态规划/贪心/数学

---

## Phase 6：生产部署

### 6.1 数据库迁移（SQLite → PostgreSQL）

```bash
# 1. 修改 .env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/oj

# 2. 安装驱动
uv add asyncpg

# 3. 执行迁移
alembic upgrade head

# 4. 数据迁移（可选）
# 使用 pgloader 或手写脚本将 SQLite 数据导入 PostgreSQL
```

### 6.2 Docker Compose 生产配置

建议文件结构：

```yaml
# docker-compose.prod.yml
services:
  backend:
    build: ./src/backend
    environment:
      - DATABASE_URL=postgresql+asyncpg://...
      - SECRET_KEY=${SECRET_KEY}
    depends_on: [db, redis]

  celery_worker:
    build: ./src/judger
    command: celery -A celery_app worker -Q judge,celery -c 4
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    depends_on: [redis]

  frontend:
    build: ./src/frontend
    # Vite build → nginx serve

  nginx:
    image: nginx:alpine
    ports: ["80:80", "443:443"]
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./certs:/etc/nginx/certs

  db:
    image: postgres:15-alpine
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
```

### 6.3 安全加固清单

- [ ] `SECRET_KEY` 从环境变量读取（勿硬编码）
- [ ] HTTPS + Let's Encrypt
- [ ] 提交接口速率限制（`slowapi` 或 Nginx limit_req）
- [ ] 数据库定期备份（crontab + pg_dump）
- [ ] Docker 镜像非 root 用户运行

---

## 已知技术债务（待处理）

| 问题 | 严重程度 | 说明 |
|------|---------|------|
| 提交接口无速率限制 | 中 | 可能被滥用，建议用 `slowapi` 实现 |
| `Submission` 无 `contest_id` 字段 | 中 | 竞赛内提交与普通提交无法区分，排行榜计算依赖全量提交 |
| 竞赛内提交隔离 | 中 | 竞赛期间的提交应隔离，不计入普通题目通过率 |
| 单元测试覆盖率接近 0 | 中 | 建议先补 service 层测试 |
| 前端 useEffect 依赖警告 | 低 | 已用 `eslint-disable` 压制，后续应重构 |

---

## 优先级建议

再次启动开发时，建议按以下顺序推进：

1. **修复技术债务**（`contest_id`、速率限制）—— 影响数据正确性
2. **讨论区** —— 用户粘性最高的功能
3. **用户统计主页** —— 提升使用体验
4. **Special Judge** —— 题目类型扩展
5. **管理后台 + 扩充题库**
6. **生产部署**
