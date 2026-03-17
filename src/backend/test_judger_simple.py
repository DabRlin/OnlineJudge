"""
简单测试判题引擎
运行: source .venv/bin/activate && python test_judger_simple.py
"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from judger.docker_judger import DockerJudger, JudgeResult
    from judger.languages import Language
    
    print("=" * 60)
    print("Docker 判题引擎简单测试")
    print("=" * 60)
    
    # 测试 Python
    print("\n🧪 测试 Python 判题...")
    
    code = """
n = int(input())
print(n * 2)
"""
    
    test_cases = [
        {"input": "5", "output": "10"},
        {"input": "10", "output": "20"},
    ]
    
    judger = DockerJudger()
    print("  ✓ Docker 客户端连接成功")
    
    result = judger.judge(code, Language.PYTHON, test_cases)
    
    print(f"\n  结果:")
    print(f"    状态: {result.status}")
    print(f"    分数: {result.score}")
    print(f"    时间: {result.time_used}ms")
    print(f"    内存: {result.memory_used}KB")
    
    if result.status == JudgeResult.ACCEPTED:
        print("\n  ✅ 判题引擎测试通过！")
    else:
        print(f"\n  ❌ 判题失败: {result.error_message}")
        for idx, tc_result in enumerate(result.test_cases_result):
            print(f"    测试用例 {idx + 1}: {tc_result}")
    
    print("\n" + "=" * 60)
    
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("\n请确保:")
    print("  1. 已安装 docker 包: pip install docker")
    print("  2. 判题引擎代码在 ../judger/ 目录")
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
