# Online Judge - API 接口设计

> 最后更新：2026-03-17

## 1. 基本规范

- **Base URL**：`http://localhost:8000/api/v1`
- **认证方式**：Bearer Token（JWT），Header `Authorization: Bearer <token>`
- **统一响应格式**：

```json
{
  "code": 0,
  "message": "success",
  "data": { ... }
}
```

- **分页响应**：

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20
}
```

- **错误响应**：HTTP 状态码 + `detail` 字段

---

## 2. 认证接口（/auth）

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| POST | `/auth/register` | 用户注册 | 否 |
| POST | `/auth/login` | 用户登录，返回 JWT | 否 |
| GET  | `/auth/me` | 获取当前用户信息 | 是 |
| PUT  | `/auth/me` | 更新当前用户信息 | 是 |
| POST | `/auth/change-password` | 修改密码 | 是 |

### POST /auth/register
```json
// Request
{ "username": "alice", "email": "alice@example.com", "password": "123456" }

// Response 201
{ "id": 1, "username": "alice", "email": "alice@example.com", "role": "user" }
```

### POST /auth/login
```json
// Request
{ "username": "alice", "password": "123456" }

// Response 200
{ "access_token": "eyJ...", "token_type": "bearer", "user": { ... } }
```

---

## 3. 题目接口（/problems）

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET    | `/problems` | 题目列表（分页/筛选） | 公开 |
| POST   | `/problems` | 创建题目 | admin |
| GET    | `/problems/{id}` | 题目详情（含样例） | 公开 |
| PUT    | `/problems/{id}` | 更新题目 | admin |
| DELETE | `/problems/{id}` | 删除题目 | admin |
| POST   | `/problems/{id}/test-cases` | 新增测试用例 | admin |
| PUT    | `/problems/{id}/test-cases/{tc_id}` | 更新测试用例 | admin |
| DELETE | `/problems/{id}/test-cases/{tc_id}` | 删除测试用例 | admin |
| POST   | `/problems/import` | 批量导入题目（JSON） | admin |

### GET /problems 查询参数
| 参数 | 类型 | 说明 |
|------|------|------|
| page | int | 页码，默认 1 |
| page_size | int | 每页数量，默认 20，最大 100 |
| difficulty | string | easy / medium / hard |
| search | string | 标题关键词搜索 |
| tags | string | 标签，逗号分隔 |

### POST /problems/import Request Body
```json
{
  "problems": [
    {
      "title": "两数之和",
      "description": "给定数组...",
      "difficulty": "easy",
      "time_limit": 1000,
      "memory_limit": 256,
      "tags": ["数组", "哈希表"],
      "test_cases": [
        { "input": "4\n2 7 11 15\n9", "output": "0 1", "is_sample": true, "score": 20 }
      ]
    }
  ],
  "force_update": false
}
```

---

## 4. 提交接口（/submissions）

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| POST | `/submissions` | 提交代码 | 已登录 |
| GET  | `/submissions` | 提交记录列表 | 已登录 |
| GET  | `/submissions/{id}` | 提交详情 | 已登录 |
| POST | `/submissions/{id}/rejudge` | 重新判题 | admin |
| GET  | `/submissions/user/{user_id}` | 指定用户提交记录 | 已登录 |

### POST /submissions Request Body
```json
{
  "problem_id": 1,
  "language": "python",
  "code": "n = int(input())\nprint(n)"
}
```

### GET /submissions 查询参数
| 参数 | 说明 |
|------|------|
| page / page_size | 分页 |
| problem_id | 按题目筛选 |
| user_id | 按用户筛选 |
| language | 按语言筛选 |
| status | 按状态筛选 |

### 提交状态枚举
| 值 | 含义 |
|----|------|
| pending | 等待判题 |
| judging | 判题中 |
| accepted | 通过 (AC) |
| wrong_answer | 答案错误 (WA) |
| time_limit_exceeded | 超时 (TLE) |
| memory_limit_exceeded | 内存超限 (MLE) |
| runtime_error | 运行错误 (RE) |
| compile_error | 编译错误 (CE) |
| system_error | 系统错误 (SE) |

---

## 5. 竞赛接口（/contests）

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET    | `/contests` | 竞赛列表（分页/状态筛选） | 公开 |
| POST   | `/contests` | 创建竞赛 | admin |
| GET    | `/contests/{id}` | 竞赛详情 | 公开 |
| PUT    | `/contests/{id}` | 更新竞赛 | admin |
| DELETE | `/contests/{id}` | 删除竞赛 | admin |
| GET    | `/contests/{id}/problems` | 竞赛题目列表 | 公开 |
| POST   | `/contests/{id}/problems` | 添加题目到竞赛 | admin |
| DELETE | `/contests/{id}/problems/{problem_id}` | 移除竞赛题目 | admin |
| POST   | `/contests/{id}/register` | 报名竞赛 | 已登录 |
| GET    | `/contests/{id}/rank` | 竞赛排行榜 | 公开 |

### GET /contests 查询参数
| 参数 | 说明 |
|------|------|
| page / page_size | 分页 |
| status | not_started / running / ended |
| keyword | 关键词搜索 |

### GET /contests/{id}/rank 查询参数
| 参数 | 说明 |
|------|------|
| page / page_size | 分页 |

---

## 6. 语言枚举

| 值 | 说明 |
|----|------|
| python | Python 3.11 |
| cpp | C++ (GCC 13) |
| java | Java 17 |
| go | Go 1.21 |
| javascript | Node.js 20 |
| c | C (GCC 13) |

---

## 7. HTTP 状态码说明

| 状态码 | 场景 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 204 | 删除成功（无响应体） |
| 400 | 请求参数错误 |
| 401 | 未认证（Token 缺失或过期） |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 422 | 请求体验证失败（Pydantic） |
| 500 | 服务器内部错误 |

---

## 8. 自动文档

开发环境下可通过以下地址查看交互式 API 文档（由 FastAPI 自动生成）：

- **Swagger UI**：http://localhost:8000/docs
- **ReDoc**：http://localhost:8000/redoc

