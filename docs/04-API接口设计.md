# Online Judge 系统 - API 接口设计

## 1. API 设计原则

- **RESTful 风格**: 使用标准 HTTP 方法
- **版本控制**: `/api/v1/...`
- **统一响应格式**: JSON
- **认证方式**: JWT Token
- **错误处理**: 标准错误码

## 2. 通用响应格式

### 2.1 成功响应

```json
{
  "code": 0,
  "message": "success",
  "data": {
    // 具体数据
  }
}
```

### 2.2 错误响应

```json
{
  "code": 40001,
  "message": "用户名或密码错误",
  "data": null
}
```

### 2.3 分页响应

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  }
}
```

## 3. 错误码定义

```
0       - 成功
10001   - 参数错误
10002   - 请求方法错误
10003   - 请求频率过高

20001   - 未登录
20002   - Token 过期
20003   - Token 无效
20004   - 权限不足

30001   - 用户不存在
30002   - 用户名已存在
30003   - 邮箱已存在
30004   - 密码错误

40001   - 题目不存在
40002   - 题目未公开

50001   - 提交失败
50002   - 提交不存在
50003   - 语言不支持

60001   - 竞赛不存在
60002   - 竞赛未开始
60003   - 竞赛已结束
60004   - 竞赛密码错误

99999   - 系统错误
```

## 4. 用户相关接口

### 4.1 用户注册

**接口**: `POST /api/v1/user/register`

**请求体**:
```json
{
  "username": "alice",
  "email": "alice@example.com",
  "password": "password123",
  "nickname": "Alice"
}
```

**响应**:
```json
{
  "code": 0,
  "message": "注册成功",
  "data": {
    "user_id": 1,
    "username": "alice",
    "email": "alice@example.com"
  }
}
```

### 4.2 用户登录

**接口**: `POST /api/v1/user/login`

**请求体**:
```json
{
  "username": "alice",
  "password": "password123"
}
```

**响应**:
```json
{
  "code": 0,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "username": "alice",
      "email": "alice@example.com",
      "nickname": "Alice",
      "role": "user"
    }
  }
}
```

### 4.3 获取用户信息

**接口**: `GET /api/v1/user/profile`

**请求头**: `Authorization: Bearer {token}`

**响应**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "username": "alice",
    "email": "alice@example.com",
    "nickname": "Alice",
    "avatar_url": "https://...",
    "solved_count": 50,
    "submission_count": 120,
    "rating": 1650,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### 4.4 更新用户信息

**接口**: `PUT /api/v1/user/profile`

**请求头**: `Authorization: Bearer {token}`

**请求体**:
```json
{
  "nickname": "Alice Wang",
  "school": "MIT",
  "bio": "Love coding!"
}
```

### 4.5 修改密码

**接口**: `PUT /api/v1/user/password`

**请求头**: `Authorization: Bearer {token}`

**请求体**:
```json
{
  "old_password": "old123",
  "new_password": "new456"
}
```

### 4.6 用户登出

**接口**: `POST /api/v1/user/logout`

**请求头**: `Authorization: Bearer {token}`

## 5. 题目相关接口

### 5.1 获取题目列表

**接口**: `GET /api/v1/problems`

**查询参数**:
- `page`: 页码（默认1）
- `page_size`: 每页数量（默认20）
- `difficulty`: 难度过滤（easy/medium/hard）
- `tag`: 标签过滤
- `keyword`: 关键词搜索
- `status`: 用户状态过滤（accepted/attempted）

**示例**: `GET /api/v1/problems?page=1&page_size=20&difficulty=medium`

**响应**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "title": "两数之和",
        "difficulty": "easy",
        "acceptance_rate": 45.6,
        "submission_count": 1000,
        "accepted_count": 456,
        "tags": ["数组", "哈希表"],
        "user_status": "accepted"
      }
    ],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

### 5.2 获取题目详情

**接口**: `GET /api/v1/problems/:id`

**响应**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "title": "两数之和",
    "description": "给定一个整数数组...",
    "input_description": "第一行...",
    "output_description": "输出...",
    "sample_input": "4\n2 7 11 15\n9",
    "sample_output": "0 1",
    "hint": "可以使用哈希表...",
    "time_limit": 1000,
    "memory_limit": 256,
    "difficulty": "easy",
    "tags": ["数组", "哈希表"],
    "submission_count": 1000,
    "accepted_count": 456,
    "acceptance_rate": 45.6,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### 5.3 创建题目（管理员）

**接口**: `POST /api/v1/problems`

**请求头**: `Authorization: Bearer {token}`

**请求体**:
```json
{
  "title": "两数之和",
  "description": "给定一个整数数组...",
  "input_description": "第一行...",
  "output_description": "输出...",
  "sample_input": "4\n2 7 11 15\n9",
  "sample_output": "0 1",
  "time_limit": 1000,
  "memory_limit": 256,
  "difficulty": "easy",
  "tags": [1, 2],
  "is_public": false
}
```

### 5.4 更新题目（管理员）

**接口**: `PUT /api/v1/problems/:id`

### 5.5 删除题目（管理员）

**接口**: `DELETE /api/v1/problems/:id`

### 5.6 上传测试数据（管理员）

**接口**: `POST /api/v1/problems/:id/testcases`

**请求体**: `multipart/form-data`
- `input`: 输入文件
- `output`: 输出文件
- `score`: 分数（OI模式）
- `is_sample`: 是否为样例

## 6. 提交相关接口

### 6.1 提交代码

**接口**: `POST /api/v1/submissions`

**请求头**: `Authorization: Bearer {token}`

**请求体**:
```json
{
  "problem_id": 1,
  "language": "cpp",
  "code": "#include <iostream>\nusing namespace std;\n...",
  "contest_id": null
}
```

**响应**:
```json
{
  "code": 0,
  "message": "提交成功",
  "data": {
    "submission_id": 12345
  }
}
```

### 6.2 获取提交详情

**接口**: `GET /api/v1/submissions/:id`

**响应**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 12345,
    "problem_id": 1,
    "problem_title": "两数之和",
    "user_id": 1,
    "username": "alice",
    "language": "cpp",
    "code": "#include <iostream>...",
    "status": "accepted",
    "score": 100,
    "time_used": 15,
    "memory_used": 1024,
    "test_cases_passed": 10,
    "test_cases_total": 10,
    "created_at": "2024-01-01T12:00:00Z",
    "judged_at": "2024-01-01T12:00:05Z",
    "judge_results": [
      {
        "test_case_order": 1,
        "status": "accepted",
        "time_used": 10,
        "memory_used": 1024,
        "score": 10
      }
    ]
  }
}
```

### 6.3 获取提交列表

**接口**: `GET /api/v1/submissions`

**查询参数**:
- `page`: 页码
- `page_size`: 每页数量
- `problem_id`: 题目ID
- `user_id`: 用户ID
- `language`: 语言
- `status`: 状态

**示例**: `GET /api/v1/submissions?problem_id=1&status=accepted`

### 6.4 获取我的提交

**接口**: `GET /api/v1/user/submissions`

**请求头**: `Authorization: Bearer {token}`

## 7. 竞赛相关接口

### 7.1 获取竞赛列表

**接口**: `GET /api/v1/contests`

**查询参数**:
- `status`: upcoming/running/ended
- `page`: 页码
- `page_size`: 每页数量

**响应**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "title": "周赛 #1",
        "description": "本周竞赛...",
        "start_time": "2024-01-01T14:00:00Z",
        "end_time": "2024-01-01T16:00:00Z",
        "duration": 120,
        "type": "acm",
        "is_public": true,
        "participant_count": 100,
        "status": "upcoming"
      }
    ],
    "total": 10,
    "page": 1,
    "page_size": 20
  }
}
```

### 7.2 获取竞赛详情

**接口**: `GET /api/v1/contests/:id`

**响应**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "title": "周赛 #1",
    "description": "本周竞赛...",
    "start_time": "2024-01-01T14:00:00Z",
    "end_time": "2024-01-01T16:00:00Z",
    "duration": 120,
    "type": "acm",
    "rule_type": "acm",
    "is_public": true,
    "has_password": false,
    "participant_count": 100,
    "status": "running",
    "problems": [
      {
        "problem_index": "A",
        "problem_id": 1,
        "title": "两数之和",
        "submission_count": 50,
        "accepted_count": 30
      }
    ]
  }
}
```

### 7.3 注册竞赛

**接口**: `POST /api/v1/contests/:id/register`

**请求头**: `Authorization: Bearer {token}`

**请求体**:
```json
{
  "password": "contest_password"
}
```

### 7.4 获取竞赛排行榜

**接口**: `GET /api/v1/contests/:id/ranklist`

**查询参数**:
- `page`: 页码
- `page_size`: 每页数量

**响应**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "rank": 1,
        "user_id": 1,
        "username": "alice",
        "nickname": "Alice",
        "score": 300,
        "total_time": 180,
        "problems": {
          "A": {
            "is_accepted": true,
            "submission_count": 1,
            "accepted_time": 15,
            "penalty": 0
          },
          "B": {
            "is_accepted": true,
            "submission_count": 2,
            "accepted_time": 45,
            "penalty": 20
          }
        }
      }
    ],
    "total": 100,
    "page": 1,
    "page_size": 50
  }
}
```

### 7.5 创建竞赛（管理员）

**接口**: `POST /api/v1/contests`

**请求头**: `Authorization: Bearer {token}`

**请求体**:
```json
{
  "title": "周赛 #1",
  "description": "本周竞赛...",
  "start_time": "2024-01-01T14:00:00Z",
  "end_time": "2024-01-01T16:00:00Z",
  "type": "acm",
  "is_public": true,
  "password": "optional_password",
  "problem_ids": [1, 2, 3]
}
```

## 8. 标签相关接口

### 8.1 获取所有标签

**接口**: `GET /api/v1/tags`

**响应**:
```json
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "id": 1,
      "name": "数组",
      "description": "数组相关题目",
      "color": "#1890ff",
      "problem_count": 50
    }
  ]
}
```

## 9. 讨论相关接口

### 9.1 获取讨论列表

**接口**: `GET /api/v1/discussions`

**查询参数**:
- `problem_id`: 题目ID
- `type`: general/solution/question
- `page`: 页码
- `page_size`: 每页数量

### 9.2 创建讨论

**接口**: `POST /api/v1/discussions`

**请求头**: `Authorization: Bearer {token}`

**请求体**:
```json
{
  "problem_id": 1,
  "title": "这道题的最优解法",
  "content": "我发现可以用...",
  "type": "solution"
}
```

### 9.3 获取讨论详情

**接口**: `GET /api/v1/discussions/:id`

### 9.4 评论讨论

**接口**: `POST /api/v1/discussions/:id/comments`

**请求体**:
```json
{
  "content": "很好的解法！",
  "parent_id": null
}
```

## 10. 统计相关接口

### 10.1 获取用户统计

**接口**: `GET /api/v1/user/:id/statistics`

**响应**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "solved_count": 50,
    "submission_count": 120,
    "acceptance_rate": 41.7,
    "difficulty_distribution": {
      "easy": 20,
      "medium": 25,
      "hard": 5
    },
    "language_distribution": {
      "cpp": 60,
      "python": 40,
      "java": 20
    },
    "submission_calendar": {
      "2024-01-01": 5,
      "2024-01-02": 3
    }
  }
}
```

### 10.2 获取系统统计

**接口**: `GET /api/v1/statistics`

**响应**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "user_count": 10000,
    "problem_count": 500,
    "submission_count": 100000,
    "contest_count": 50
  }
}
```

## 11. 限流策略

- 未登录用户: 100 请求/分钟
- 普通用户: 300 请求/分钟
- 提交接口: 10 次/分钟
- 管理员: 1000 请求/分钟

## 12. WebSocket 接口

### 12.1 实时判题结果

**连接**: `ws://domain/api/v1/ws/submission/:id`

**消息格式**:
```json
{
  "type": "judge_update",
  "data": {
    "submission_id": 12345,
    "status": "judging",
    "test_case_order": 3,
    "test_cases_total": 10
  }
}
```

### 12.2 竞赛排行榜实时更新

**连接**: `ws://domain/api/v1/ws/contest/:id/ranklist`
