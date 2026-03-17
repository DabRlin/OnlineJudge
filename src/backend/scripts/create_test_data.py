"""创建测试数据脚本"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.models.user import User, UserRole
from app.models.problem import Problem, TestCase, Difficulty
from app.core.config import settings


async def create_admin_and_problems():
    """创建管理员账号和测试题目"""
    
    # 创建数据库引擎
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # 1. 创建管理员用户
        from app.core.security import get_password_hash
        
        stmt = select(User).where(User.username == "admin")
        result = await session.execute(stmt)
        admin_user = result.scalar_one_or_none()
        
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@oj.com",
                hashed_password=get_password_hash("admin123456"),
                role=UserRole.SUPER_ADMIN,
                is_active=True
            )
            session.add(admin_user)
            await session.commit()
            print(f"✅ 创建管理员账号: admin / admin123456")
        else:
            admin_user.role = UserRole.SUPER_ADMIN
            await session.commit()
            print(f"✅ 用户 {admin_user.username} 已设置为超级管理员")
        
        # 2. 创建测试题目
        problems_data = [
            {
                "title": "两数之和",
                "description": """给定一个整数数组 `nums` 和一个整数目标值 `target`，请你在该数组中找出**和为目标值** `target` 的那两个整数，并返回它们的数组下标。

你可以假设每种输入只会对应一个答案。但是，数组中同一个元素在答案里不能重复出现。

你可以按任意顺序返回答案。

## 示例

**示例 1：**
```
输入：nums = [2,7,11,15], target = 9
输出：[0,1]
解释：因为 nums[0] + nums[1] == 9，返回 [0, 1]。
```

**示例 2：**
```
输入：nums = [3,2,4], target = 6
输出：[1,2]
```

**示例 3：**
```
输入：nums = [3,3], target = 6
输出：[0,1]
```""",
                "difficulty": Difficulty.EASY,
                "input_format": """第一行包含一个整数 `n`，表示数组长度。

第二行包含 `n` 个整数，表示数组 `nums`。

第三行包含一个整数 `target`。""",
                "output_format": "输出两个整数，表示两个数的下标（从 0 开始），用空格分隔。",
                "constraints": """- `2 <= n <= 10^4`
- `-10^9 <= nums[i] <= 10^9`
- `-10^9 <= target <= 10^9`
- **只会存在一个有效答案**""",
                "time_limit": 1000,
                "memory_limit": 256,
                "tags": ["数组", "哈希表"],
                "source": "LeetCode",
                "test_cases": [
                    {"input": "4\n2 7 11 15\n9", "output": "0 1", "is_sample": True},
                    {"input": "3\n3 2 4\n6", "output": "1 2", "is_sample": True},
                    {"input": "2\n3 3\n6", "output": "0 1", "is_sample": False},
                ]
            },
            {
                "title": "回文数",
                "description": """给你一个整数 `x`，如果 `x` 是一个**回文整数**，返回 `true`；否则，返回 `false`。

回文数是指正序（从左向右）和倒序（从右向左）读都是一样的整数。

## 示例

**示例 1：**
```
输入：x = 121
输出：true
```

**示例 2：**
```
输入：x = -121
输出：false
解释：从左向右读为 -121，从右向左读为 121-，因此它不是一个回文数。
```

**示例 3：**
```
输入：x = 10
输出：false
解释：从右向左读为 01，因此它不是一个回文数。
```

## 进阶

你能不将整数转为字符串来解决这个问题吗？""",
                "difficulty": Difficulty.EASY,
                "input_format": "一个整数 `x`。",
                "output_format": "如果是回文数输出 `true`，否则输出 `false`。",
                "constraints": "- `-2^31 <= x <= 2^31 - 1`",
                "time_limit": 1000,
                "memory_limit": 256,
                "tags": ["数学"],
                "source": "LeetCode",
                "test_cases": [
                    {"input": "121", "output": "true", "is_sample": True},
                    {"input": "-121", "output": "false", "is_sample": True},
                    {"input": "10", "output": "false", "is_sample": True},
                    {"input": "12321", "output": "true", "is_sample": False},
                ]
            },
            {
                "title": "最长公共前缀",
                "description": """编写一个函数来查找字符串数组中的**最长公共前缀**。

如果不存在公共前缀，返回空字符串 `""`。

## 示例

**示例 1：**
```
输入：strs = ["flower","flow","flight"]
输出："fl"
```

**示例 2：**
```
输入：strs = ["dog","racecar","car"]
输出：""
解释：输入不存在公共前缀。
```

## 提示

- 所有输入只包含小写字母 `a-z`""",
                "difficulty": Difficulty.EASY,
                "input_format": """第一行包含一个整数 `n`，表示字符串数组的长度。

接下来 `n` 行，每行一个字符串。""",
                "output_format": "输出最长公共前缀，如果不存在则输出空字符串。",
                "constraints": """- `1 <= n <= 200`
- `0 <= strs[i].length <= 200`
- `strs[i]` 仅由小写英文字母组成""",
                "time_limit": 1000,
                "memory_limit": 256,
                "tags": ["字符串"],
                "source": "LeetCode",
                "test_cases": [
                    {"input": "3\nflower\nflow\nflight", "output": "fl", "is_sample": True},
                    {"input": "3\ndog\nracecar\ncar", "output": "", "is_sample": True},
                    {"input": "1\nabc", "output": "abc", "is_sample": False},
                ]
            },
        ]
        
        for prob_data in problems_data:
            # 创建题目
            test_cases_data = prob_data.pop("test_cases")
            problem = Problem(**prob_data)
            session.add(problem)
            await session.flush()
            
            # 创建测试用例
            for tc_data in test_cases_data:
                test_case = TestCase(
                    problem_id=problem.id,
                    **tc_data
                )
                session.add(test_case)
            
            print(f"✅ 创建题目: {problem.title}")
        
        await session.commit()
        print("\n🎉 测试数据创建完成！")
        print(f"- 管理员账号: admin / admin123456")
        print(f"- 创建了 {len(problems_data)} 道测试题目")


if __name__ == "__main__":
    asyncio.run(create_admin_and_problems())
