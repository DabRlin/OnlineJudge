# Online Judge 开发任务清单

> 项目启动时间：2026-03-15
> 最后更新：2026-03-17
> 当前状态：✅ MVP + 竞赛系统 + 题库导入 全部完成

---

## 📋 项目概览

基于 FastAPI + React + Vite 的现代化在线判题系统，支持多语言代码提交、实时判题、竞赛管理等功能。

### 技术栈
- **后端**: FastAPI + SQLAlchemy 2.0 (async) + PostgreSQL/SQLite + Redis + Celery
- **前端**: React 18 + Vite 5 + TypeScript + Ant Design + TailwindCSS
- **工具链**: uv (Python) + bun (JavaScript)
- **判题**: Docker 沙箱隔离

---

## 📚 题库数据来源方案

### 推荐来源

#### 1. **Codeforces API**（首选）
- **官方 API**: https://codeforces.com/apiHelp
- **优势**: 合法、稳定、数据质量高
- **内容**: 3000+ 竞赛题目
- **格式**: JSON，易于解析
- **实现**: 
  ```python
  # 获取题目列表
  GET https://codeforces.com/api/problemset.problems
  
  # 获取题目详情
  GET https://codeforces.com/api/contest.standings?contestId={id}
  ```

#### 2. **QDUOJ 开源题库**
- **GitHub**: https://github.com/QingdaoU/OnlineJudgeProblem
- **优势**: 开源免费、包含测试用例
- **内容**: 精选算法题目
- **格式**: FPS (Free Problem Set) 格式
- **许可**: MIT License

#### 3. **AtCoder Problems**
- **网站**: https://kenkoooo.com/atcoder/
- **优势**: 高质量日本竞赛题目
- **内容**: 5000+ 题目
- **获取**: 通过 API 或爬虫

#### 4. **LeetCode 题库**（参考）
- **来源**: 第三方整理的数据集
- **注意**: 仅供学习参考，注意版权
- **内容**: 算法面试题

### 导入格式标准

我们将支持以下格式：

#### **标准 JSON 格式**
```json
{
  "title": "两数之和",
  "description": "给定一个整数数组...",
  "difficulty": "easy",
  "time_limit": 1000,
  "memory_limit": 256,
  "tags": ["数组", "哈希表"],
  "source": "LeetCode",
  "test_cases": [
    {
      "input": "2 7 11 15\n9",
      "output": "0 1",
      "is_sample": true
    }
  ]
}
```

#### **FPS 格式**（兼容 QDUOJ）
- 支持 zip 包导入
- 包含题目描述、测试数据、配置文件

#### **Codeforces 格式**
- 直接从 API 获取并转换

### 初始题库计划

**Phase 1**: 导入 100 道基础题目
- 数组、字符串、链表等基础数据结构题目
- 来源：Codeforces + QDUOJ

**Phase 2**: 扩充到 500 道题目
- 覆盖常见算法分类
- 难度分布：Easy 40%, Medium 40%, Hard 20%

**Phase 3**: 持续更新
- 定期从 Codeforces 同步新题
- 支持用户贡献题目

---

## 🎯 开发阶段规划

### Phase 1: 核心基础功能 (MVP) - 预计 2-3 周

#### 1.1 用户认证与授权系统 ✅ **已完成** (2026-03-15)

**后端任务**
- [x] 创建 User 模型 (models/user.py)
  - [x] 字段：id, username, email, hashed_password, role, is_active, avatar, created_at, updated_at
  - [x] 添加索引和约束
  - [x] UserRole 枚举（user, admin, super_admin）
- [x] 实现用户注册接口 (api/v1/auth.py)
  - [x] 用户名唯一性检查
  - [x] 邮箱唯一性检查
  - [x] 密码加密存储（bcrypt）
- [x] 实现用户登录接口
  - [x] JWT token 生成
  - [x] OAuth2 密码流认证
  - [x] 密码验证
- [x] 实现用户信息接口
  - [x] 获取当前用户信息 (GET /auth/me)
  - [x] 更新用户资料 (PUT /auth/me)
  - [x] 修改密码 (POST /auth/me/password)
- [x] 实现权限控制
  - [x] JWT 认证依赖 (get_current_user)
  - [x] 用户角色系统
  - [x] Token 验证和解析
- [x] 用户 Service 层 (services/user_service.py)
  - [x] 创建用户
  - [x] 用户认证
  - [x] 查询用户（by id/username/email）
  - [x] 更新用户信息
  - [x] 修改密码

**前端任务**
- [x] 创建登录页面 (pages/Login)
  - [x] 登录表单（用户名/邮箱 + 密码）
  - [x] 表单验证
  - [x] 错误提示
  - [x] 美观的 UI 设计
- [x] 创建注册页面 (pages/Register)
  - [x] 注册表单（用户名 + 邮箱 + 密码）
  - [x] 密码确认验证
  - [x] 表单验证规则
  - [x] 美观的 UI 设计
- [x] 创建用户中心页面 (pages/Profile)
  - [x] 个人信息展示
  - [x] 用户角色标签
  - [x] 账号状态显示
  - [x] 统计数据展示（占位）
  - [x] 退出登录功能
- [x] 实现认证状态管理 (stores/authStore.ts)
  - [x] Zustand Store 创建
  - [x] Token 持久化存储
  - [x] 登录/注册/登出逻辑
  - [x] 用户信息获取
  - [x] 状态更新
- [x] 实现 API 服务层
  - [x] 认证 API (services/auth.ts)
  - [x] Axios 拦截器配置
  - [x] 自动添加 Token
  - [x] 错误处理
- [x] 更新导航栏 (components/Layout/Navbar.tsx)
  - [x] 用户头像和用户名显示
  - [x] 用户下拉菜单
  - [x] 登录/注册按钮
  - [x] 响应式设计
- [x] 路由配置
  - [x] 登录路由 (/login)
  - [x] 注册路由 (/register)
  - [x] 用户中心路由 (/profile)
  - [x] 布局路由分离

**数据库迁移**
- [x] 创建 users 表迁移文件
- [x] 应用迁移到数据库
- [x] 测试数据库连接

**测试**
- [x] 后端 API 测试
  - [x] 用户注册 API
  - [x] 用户登录 API
  - [x] 获取当前用户 API
  - [x] 更新用户信息 API
- [ ] 前端功能测试（待用户测试）
  - [ ] 注册流程
  - [ ] 登录流程
  - [ ] 用户中心访问
  - [ ] 状态持久化

**文档**
- [x] 创建 STARTUP.md 启动指南
- [x] API 文档自动生成（Swagger）

---

#### 1.2 题目管理系统 ✅
**后端任务**
- [x] 创建 Problem 模型 (models/problem.py)
  - [x] 基础字段：id, title, description, difficulty, time_limit, memory_limit
  - [x] 扩展字段：input_format, output_format, constraints, tags
  - [x] 统计字段：submission_count, accepted_count, acceptance_rate
  - [x] 来源字段：source (标注题目来源，如 LeetCode, Codeforces 等)
- [x] 创建 TestCase 模型 (models/problem.py)
  - [x] 字段：id, problem_id, input, output, is_sample, score
  - [x] 外键关联和级联删除
- [x] 实现题目 CRUD 接口 (api/v1/problems.py)
  - [x] 获取题目列表（分页、筛选、排序）
  - [x] 获取题目详情
  - [x] 创建题目（管理员）
  - [x] 更新题目（管理员）
  - [x] 删除题目（管理员）
- [x] 实现测试用例管理接口
  - [x] 添加单个测试用例
  - [ ] 上传测试用例文件（待完善）
  - [ ] 批量导入（待完善）
  - [ ] 下载测试用例（待完善）
- [x] 实现题目标签系统（基础版本）
  - [x] 标签存储（JSON 数组）
  - [x] 按标签筛选
  - [ ] 独立标签管理（待完善）
- [ ] **实现题库导入工具** (utils/problem_importer.py) - 待开发
  - [ ] JSON 格式导入（支持自定义格式）
  - [ ] Codeforces API 导入
  - [ ] FPS (Free Problem Set) 格式导入
  - [ ] 批量导入命令行工具
  - [ ] 导入日志和错误处理

**前端任务**
- [x] 创建题库页面 (pages/Problems)
  - [x] 题目列表展示
  - [x] 难度筛选
  - [x] 标签筛选
  - [x] 搜索功能
  - [x] 分页组件
- [x] 创建题目详情页 (pages/ProblemDetail)
  - [x] 题目描述渲染（Markdown 支持）
  - [x] 示例输入输出
  - [x] 通过率统计
  - [x] 标签展示
  - [x] 管理员编辑按钮
  - [ ] 提交历史（占位，待 Phase 1.3）
- [x] 创建题目编辑页 (pages/ProblemEdit) - 管理员
  - [x] Markdown 编辑器（实时预览）
  - [x] 测试用例管理（增删改）
  - [x] 题目配置表单
  - [x] 权限控制
- [ ] 创建代码编辑器组件 (components/CodeEditor) - 移至 Phase 1.3
  - [ ] Monaco Editor 集成
  - [ ] 语言选择
  - [ ] 主题切换
  - [ ] 代码模板

**数据库迁移**
- [x] 创建 problems 表迁移
- [x] 创建 test_cases 表迁移
- [x] 标签系统（使用 JSON 字段，未创建独立表）

**测试数据**
- [x] 创建管理员账号（admin / admin123456）
- [x] 创建测试题目（3道简单题，Markdown 格式）
- [x] 创建测试用例（包含样例）

**✅ Phase 1.2 核心功能已完成**
- ✅ 完整的题目 CRUD 功能（前后端）
- ✅ Markdown 渲染支持（代码高亮、数学公式）
- ✅ 题目编辑页面（管理员专用，带实时预览）
- ✅ 测试用例在线管理（增删改查）
- ✅ 权限控制和路由保护

**⚠️ 待完善功能（可选，不影响核心流程）**
- 测试用例文件上传/下载
- 批量导入测试用例
- 独立标签管理系统
- 题库导入工具（Codeforces API、FPS 格式）

---

#### 1.3 代码提交与判题系统 ✅ **已完成** (2026-03-17)

**后端任务**
- [x] 创建 Submission 模型 (models/submission.py)
- [x] 实现提交接口 (api/v1/submissions.py)
  - [x] 代码提交（异步 Celery 判题）
  - [x] 提交列表（分页、筛选）
  - [x] 提交详情、重新判题
- [x] Docker 沙箱判题引擎 (judger/docker_judger.py)
  - [x] Python 判题（Docker 容器隔离）
  - [x] 资源限制（时间/内存）
  - [x] 网络隔离（network_mode=none）
  - [x] OrbStack socket 自动检测
- [x] Celery + Redis 异步任务队列
  - [x] judger/celery_app.py 配置
  - [x] judger/tasks.py 判题任务
  - [x] 判题结果直接写回 SQLite
- [x] 修复 docker-py 7.0→7.1 兼容性 bug

**前端任务**
- [x] Monaco Editor 代码编辑器
- [x] 双列布局（题目描述 + 编辑器）
- [x] 提交 API 服务 (services/submission.ts)
- [x] 现代化 UI（圆角、阴影、全屏布局）

**数据库**
- [x] submissions 表、索引
- [x] 测试数据 3 道题（两数之和、回文数、最长公共前缀）

**⚠️ 注意**：提交代码需使用**标准 IO 格式**（stdin/stdout），非 LeetCode 函数风格。

---

#### 1.4 判题结果实时展示 ⏳ **待开发（最高优先级）**

**问题描述**：用户提交代码后，前端只显示"判题中"，无法看到最终 AC/WA 结果。

**后端任务**
- [ ] 提交状态轮询接口已存在（GET /api/v1/submissions/{id}）✅ 无需额外开发

**前端任务**
- [ ] 提交后自动轮询状态（每 1-2 秒）
  - [ ] 状态从 JUDGING → 最终结果时停止轮询
  - [ ] 显示 AC/WA/TLE/RE 等状态标签
  - [ ] 超时保护（最多轮询 30 秒）
- [ ] 创建提交记录页 (pages/Submissions)
  - [ ] 列表展示（状态、语言、时间、得分）
  - [ ] 状态颜色标签
  - [ ] 分页
- [ ] 创建提交详情页 (pages/SubmissionDetail)
  - [ ] 代码高亮显示
  - [ ] 每个测试用例通过情况
  - [ ] 错误信息展示（RE/CE）
  - [ ] 期望输出 vs 实际输出（WA 时）

---

### Phase 2: 提交体验完善与多语言支持

#### 2.1 多语言判题验证 ⏳

- [ ] 确认判题镜像已构建（oj-judger-cpp, oj-judger-java, oj-judger-go, oj-judger-js）
- [ ] 测试 C++ 判题（编译 + 运行）
- [ ] 测试 Java 判题
- [ ] 测试 Go 判题
- [ ] 测试 JavaScript 判题
- [ ] 前端语言选择器补充（目前可能缺少 Go/JS）

#### 2.2 题目管理完善 ⏳

- [ ] 测试用例批量上传（zip 包）
- [ ] 题库导入工具
  - [ ] JSON 格式批量导入
  - [ ] Codeforces API 导入
- [ ] Special Judge 支持

---

### Phase 3: 竞赛系统

#### 3.1 竞赛后端 ⏳

**模型已建（contest.py），需要补充接口：**
- [ ] 竞赛 CRUD 接口 (api/v1/contests.py)
  - [ ] 竞赛列表、详情
  - [ ] 创建/编辑竞赛（管理员）
  - [ ] 报名参赛、密码验证
- [ ] 排行榜接口
  - [ ] ACM/OI 规则计分
  - [ ] 实时排名
  - [ ] 封榜机制

#### 3.2 竞赛前端 ⏳

- [ ] 竞赛列表页 (pages/Contests)
- [ ] 竞赛详情页 (pages/ContestDetail)
  - [ ] 题目列表、倒计时、排行榜
- [ ] 竞赛管理页（管理员）

---

### Phase 4: 高级功能

#### 4.1 讨论区 ⏳
- [ ] 题目讨论（发帖、回复、点赞）
- [ ] Markdown 支持

#### 4.2 用户统计与个人主页 ⏳
- [ ] 提交热力图（类似 GitHub contribution）
- [ ] 各难度通过题数统计
- [ ] 标签掌握情况

#### 4.3 管理后台 ⏳
- [ ] 用户管理（封禁、修改角色）
- [ ] 系统运行状态监控

---

### Phase 5: 部署优化

#### 5.1 数据库迁移 ⏳
- [ ] 从 SQLite 迁移到 PostgreSQL（生产环境）
- [ ] 数据迁移脚本

#### 5.2 生产环境部署 ⏳
- [ ] Docker Compose 完整生产配置
- [ ] Nginx 反向代理
- [ ] HTTPS 证书
- [ ] 数据库备份策略

#### 5.3 性能优化 ⏳
- [ ] 数据库查询优化、索引
- [ ] Redis 缓存策略
- [ ] 前端代码分割、CDN

---

## 🔧 技术债务与改进

### 代码质量
- [ ] 单元测试覆盖率 > 80%
- [ ] E2E 测试（Playwright）
- [ ] API 文档完善
- [ ] 代码注释和文档

### 安全性
- [ ] SQL 注入防护
- [ ] XSS 防护
- [ ] CSRF 防护
- [ ] 速率限制
- [ ] 敏感信息加密

### 可维护性
- [ ] 错误处理统一化
- [ ] 日志规范化
- [ ] 配置管理优化
- [ ] CI/CD 流程

---

## 📊 开发进度追踪

| 阶段 | 进度 | 实际完成时间 |
|------|------|--------------|
| Phase 1.1 用户认证 | ✅ 100% | 2026-03-15 |
| Phase 1.2 题目管理 | ✅ 100% | 2026-03-16 |
| Phase 1.3 判题系统（Docker + Celery） | ✅ 100% | 2026-03-17 |
| Phase 1.4 判题结果实时展示 | ✅ 100% | 2026-03-17 |
| Phase 2.1 提交记录页面与详情 | ✅ 100% | 2026-03-17 |
| Phase 2.2 多语言判题验证（5/5） | ✅ 100% | 2026-03-17 |
| Phase 3.1 竞赛系统后端 | ✅ 100% | 2026-03-17 |
| Phase 3.2 竞赛系统前端 | ✅ 100% | 2026-03-17 |
| Phase 3.3 题库导入工具 | ✅ 100% | 2026-03-17 |
| Phase 4.1 讨论区 | ⏳ 0% | - |
| Phase 4.2 用户统计与个人主页 | ⏳ 0% | - |
| Phase 4.3 管理后台 | ⏳ 0% | - |
| Phase 5 生产部署 | ⏳ 0% | - |

---

## 🎯 当前优先级（2026-03-17 更新）

### MVP 已全部完成 ✅

以下功能均已实现并验证：
- 用户认证、题目管理、Docker 判题、多语言支持
- 实时判题结果、提交记录、竞赛系统、题库导入工具

### 下一阶段目标（按优先级排序）

**� 中优先级**
1. **讨论区** - 题目评论和解题讨论（发帖、回复、点赞）
2. **用户统计** - 个人主页热力图、各难度通过题数
3. **Special Judge** - 自定义 checker，支持浮点精度判断

**🟢 低优先级**
4. **管理后台** - 用户管理、系统状态监控
5. **扩充题库** - Codeforces API 导入，目标 100+ 道题目
6. **生产部署** - PostgreSQL 迁移、Docker Compose 生产配置、Nginx + HTTPS

---

## 📝 开发规范

### Git 提交规范
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具相关

### 分支策略
- `main`: 生产环境
- `develop`: 开发环境
- `feature/*`: 功能分支
- `hotfix/*`: 紧急修复

### Code Review
- 所有代码必须经过 Review
- 至少一个 Approve 才能合并
- 保持代码风格一致

---

## 🚀 快速开始开发

### 启动开发环境
```bash
# 后端
cd src/backend
source .venv/bin/activate
uvicorn main:app --reload

# 前端
cd src/frontend
bun run dev
```

### 创建新功能
1. 创建 feature 分支
2. 实现功能（后端 + 前端）
3. 编写测试
4. 提交 PR
5. Code Review
6. 合并到 develop

---

## 📚 相关文档

- [项目概述](doc/01-项目概述.md)
- [技术栈方案](doc/09-技术栈确定方案.md)
- [项目结构设计](doc/10-项目结构设计.md)
- [数据库方案](doc/11-数据库选择方案.md)
- [后端 README](src/backend/README.md)
- [前端 README](src/frontend/README.md)

---

**最后更新**: 2026-03-15  
**维护者**: Development Team
