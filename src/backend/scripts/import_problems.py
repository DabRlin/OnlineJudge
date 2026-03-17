"""
题库批量导入脚本

用法：
  python scripts/import_problems.py                          # 导入默认题库
  python scripts/import_problems.py path/to/problems.json   # 导入指定文件
  python scripts/import_problems.py --force                  # 强制覆盖同名题目
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# 确保能导入 app 模块
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.core.config import settings
from app.models.problem import Problem, TestCase, Difficulty


async def import_problems(json_file: str, force: bool = False):
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    problems_data = data.get("problems", [])
    print(f"📂 读取到 {len(problems_data)} 道题目\n")

    diff_map = {
        "easy": Difficulty.EASY,
        "medium": Difficulty.MEDIUM,
        "hard": Difficulty.HARD,
    }

    created, skipped, failed = [], [], []

    async with async_session() as session:
        for item in problems_data:
            title = item.get("title", "")
            try:
                # 检查同名题目
                stmt = select(Problem).where(Problem.title == title)
                result = await session.execute(stmt)
                existing = result.scalar_one_or_none()

                if existing and not force:
                    skipped.append(title)
                    print(f"  ⏭  跳过（已存在）: {title}")
                    continue

                if existing and force:
                    # 删除旧的测试用例和题目
                    await session.delete(existing)
                    await session.flush()

                difficulty = diff_map.get(item.get("difficulty", "easy").lower(), Difficulty.EASY)

                problem = Problem(
                    title=title,
                    description=item.get("description", ""),
                    difficulty=difficulty,
                    input_format=item.get("input_format") or None,
                    output_format=item.get("output_format") or None,
                    constraints=item.get("constraints") or None,
                    time_limit=item.get("time_limit", 1000),
                    memory_limit=item.get("memory_limit", 256),
                    tags=item.get("tags", []),
                    source=item.get("source") or None,
                    is_public=item.get("is_public", True),
                )
                session.add(problem)
                await session.flush()

                test_cases = item.get("test_cases", [])
                for tc in test_cases:
                    test_case = TestCase(
                        problem_id=problem.id,
                        input=tc.get("input", ""),
                        output=tc.get("output", ""),
                        is_sample=tc.get("is_sample", False),
                        score=tc.get("score", 10),
                    )
                    session.add(test_case)

                created.append(title)
                tag_str = ", ".join(item.get("tags", [])[:3])
                print(f"  ✅ 导入: [{difficulty.value.upper()}] {title}  ({tag_str})")

            except Exception as e:
                failed.append({"title": title, "error": str(e)})
                print(f"  ❌ 失败: {title}  错误: {e}")

        await session.commit()

    print(f"\n{'='*50}")
    print(f"📊 导入完成")
    print(f"   ✅ 成功: {len(created)} 道")
    print(f"   ⏭  跳过: {len(skipped)} 道")
    print(f"   ❌ 失败: {len(failed)} 道")

    if failed:
        print("\n失败详情:")
        for f in failed:
            print(f"  - {f['title']}: {f['error']}")

    await engine.dispose()


def main():
    args = sys.argv[1:]
    force = "--force" in args
    args = [a for a in args if not a.startswith("--")]

    if args:
        json_file = args[0]
    else:
        json_file = Path(__file__).parent / "classic_problems.json"

    if not os.path.exists(json_file):
        print(f"❌ 文件不存在: {json_file}")
        sys.exit(1)

    print(f"🚀 开始导入题库: {json_file}")
    if force:
        print("⚠️  强制模式：同名题目将被覆盖\n")
    else:
        print("ℹ️  默认模式：同名题目将跳过（使用 --force 强制覆盖）\n")

    asyncio.run(import_problems(str(json_file), force=force))


if __name__ == "__main__":
    main()
