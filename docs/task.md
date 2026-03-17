# Online Judge 开发任务清单

> 项目启动时间：2026-03-15
> 最后更新：2026-03-17
> 当前状态：✅ MVP 全部完成（用户 / 题目 / 判题 / 竞赛 / 题库导入）

---

## 📊 已完成功能总览

| 模块 | 完成时间 | 说明 |
|------|---------|------|
| 用户认证与授权 | 2026-03-15 | 注册/登录/JWT/角色权限 |
| 题目管理系统 | 2026-03-16 | CRUD/测试用例/Markdown/标签 |
| Docker 判题引擎 | 2026-03-17 | Celery + Redis + Docker 沙箱 |
| 多语言支持（5种） | 2026-03-17 | Python / C++ / Java / Go / JavaScript |
| 实时判题结果展示 | 2026-03-17 | 前端轮询，终态自动停止 |
| 提交记录与详情页 | 2026-03-17 | 列表/筛选/代码高亮/测试点详情 |
| 竞赛系统 | 2026-03-17 | CRUD/报名/ACM-OI排行榜/封榜 |
| 题库导入工具 | 2026-03-17 | API + CLI 脚本 + 内置 23 道题 |

---

## ✅ 已实现功能详细

### 用户系统
- 注册 / 登录 / JWT Bearer Token 认证
- 三级角色：`user` / `admin` / `super_admin`
- 修改密码、个人信息更新
- 个人中心页面

### 题目系统
- 题目 CRUD（管理员），Markdown + KaTeX 描述
- 测试用例在线管理（增删改查、样例标记）
- 难度筛选 / 标签筛选 / 全文搜索 / 分页
- 通过率统计（`acceptance_rate` 属性）

### 判题系统
- Docker 容器沙箱（`network_mode=none`，CPU/内存限制）
- Celery 5 + Redis 7 异步任务队列
- 5 种语言全验证：Python 3.11 / C++ (GCC 13) / Java 17 / Go 1.21 / Node.js 20
- 判题结果：AC / WA / TLE / MLE / RE / CE / SE
- 前端轮询（1.5s 间隔，最多 30 次，终态自动停止）
- 管理员 rejudge 接口

### 竞赛系统
- 竞赛 CRUD（管理员），公开 / 私有 / 密码赛
- ACM 规则（通过题数 + 罚时）/ OI 规则（总分）
- 竞赛报名、题目管理（编号 A/B/C...）
- 实时排行榜（分页）、封榜机制（freeze_time）

### 题库导入
- `POST /api/v1/problems/import`（仅 admin）
- CLI 脚本 `src/backend/scripts/import_problems.py`（`--force` 覆盖）
- 内置 `classic_problems.json`（23 道：简单 8 / 中等 14 / 困难 1）
- 前端拖拽上传 / 粘贴 JSON 导入界面

---

## 🚧 下一阶段任务（按优先级）

### 中优先级

#### 1. 讨论区
- [ ] **后端**：`Discussion` / `Comment` 模型 + Alembic 迁移
- [ ] **后端**：讨论 CRUD 接口（`/api/v1/discussions`）
  - 发帖（绑定题目）、回复（支持嵌套）、点赞
  - 分页查询、按题目筛选
- [ ] **前端**：题目详情页下方添加讨论区模块
- [ ] **前端**：`DiscussionList` / `DiscussionDetail` 页面

#### 2. 用户统计主页
- [ ] **后端**：统计接口（提交数/AC 数/难度分布/每日提交热力图数据）
- [ ] **前端**：Profile 页面增强
  - 提交热力图（类 GitHub contribution graph）
  - 难度分布饼图（easy/medium/hard 通过题数）
  - 标签掌握雷达图

#### 3. Special Judge
- [ ] **judger**：支持自定义 checker 脚本
- [ ] **后端**：题目增加 `checker_code` 字段
- [ ] **前端**：题目编辑页增加 checker 配置

### 低优先级

#### 4. 管理后台
- [ ] 用户列表 / 封禁 / 修改角色
- [ ] 判题队列状态监控（Celery 任务数、Redis 队列长度）

#### 5. 扩充题库
- [ ] Codeforces API 导入脚本（`scripts/import_codeforces.py`）
- [ ] 目标：100+ 道题目，覆盖常见算法分类

#### 6. 生产部署
- [ ] SQLite → PostgreSQL 迁移（`DATABASE_URL` 切换 + alembic）
- [ ] Docker Compose 生产配置（backend + frontend + redis + nginx）
- [ ] Nginx 反向代理 + HTTPS
- [ ] 环境变量与 Secrets 管理

---

## 🔧 已知技术债务

| 问题 | 优先级 | 说明 |
|------|--------|------|
| 单元测试覆盖率低 | 中 | `tests/` 目录仅有 conftest，无实际用例 |
| 无速率限制 | 中 | 提交接口未做频率限制，可能被滥用 |
| `contest_id` 提交关联缺失 | 低 | Submission 模型无 contest_id 字段，竞赛内提交无法区分 |
| 竞赛内提交隔离 | 低 | 竞赛进行中的提交应只计入竞赛排名，不影响普通提交记录 |
| 前端 useEffect 依赖警告 | 低 | 用 eslint-disable 暂时压制，后续重构 |

---

## 📝 Git 提交规范

| 前缀 | 用途 |
|------|------|
| `feat` | 新功能 |
| `fix` | 修复 bug |
| `docs` | 文档更新 |
| `refactor` | 重构（无功能变化） |
| `style` | 代码格式调整 |
| `test` | 测试相关 |
| `chore` | 构建 / 工具链 |

---

## 🚀 快速启动

```bash
# 1. 启动 Redis
docker run -d -p 6379:6379 redis:7-alpine

# 2. 后端（新终端）
cd src/backend && source .venv/bin/activate
uvicorn main:app --port 8000 --reload

# 3. Celery Worker（新终端）
cd src/judger
celery -A celery_app worker -Q judge,celery -c 2 --loglevel=info

# 4. 前端（新终端）
cd src/frontend && bun run dev
```

默认管理员账号：`admin` / `admin123456`

---

**维护者**：DabRlin  
**仓库**：https://github.com/DabRlin/OnlineJudge
