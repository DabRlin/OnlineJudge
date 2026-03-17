"""
测试 Docker 判题引擎
"""

import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from judger.docker_judger import DockerJudger, JudgeResult
from judger.languages import Language


def test_python_simple():
    """测试 Python 简单程序"""
    print("🧪 测试 Python 判题...")
    
    code = """
n = int(input())
print(n * 2)
"""
    
    test_cases = [
        {"input": "5", "output": "10"},
        {"input": "10", "output": "20"},
        {"input": "0", "output": "0"},
    ]
    
    judger = DockerJudger()
    result = judger.judge(code, Language.PYTHON, test_cases)
    
    print(f"  状态: {result.status}")
    print(f"  分数: {result.score}")
    print(f"  时间: {result.time_used}ms")
    print(f"  内存: {result.memory_used}KB")
    
    if result.status == JudgeResult.ACCEPTED:
        print("  ✅ 测试通过！")
    else:
        print(f"  ❌ 测试失败: {result.error_message}")
    
    return result.status == JudgeResult.ACCEPTED


def test_cpp_simple():
    """测试 C++ 简单程序"""
    print("\n🧪 测试 C++ 判题...")
    
    code = """
#include <iostream>
using namespace std;

int main() {
    int n;
    cin >> n;
    cout << n * 2 << endl;
    return 0;
}
"""
    
    test_cases = [
        {"input": "5", "output": "10"},
        {"input": "10", "output": "20"},
    ]
    
    judger = DockerJudger()
    result = judger.judge(code, Language.CPP, test_cases)
    
    print(f"  状态: {result.status}")
    print(f"  分数: {result.score}")
    
    if result.status == JudgeResult.ACCEPTED:
        print("  ✅ 测试通过！")
    else:
        print(f"  ❌ 测试失败: {result.error_message}")
    
    return result.status == JudgeResult.ACCEPTED


def test_wrong_answer():
    """测试错误答案"""
    print("\n🧪 测试错误答案...")
    
    code = """
n = int(input())
print(n + 1)  # 故意错误
"""
    
    test_cases = [
        {"input": "5", "output": "10"},
    ]
    
    judger = DockerJudger()
    result = judger.judge(code, Language.PYTHON, test_cases)
    
    print(f"  状态: {result.status}")
    print(f"  分数: {result.score}")
    
    if result.status == JudgeResult.WRONG_ANSWER:
        print("  ✅ 正确识别错误答案！")
        return True
    else:
        print("  ❌ 未能识别错误答案")
        return False


def test_compile_error():
    """测试编译错误"""
    print("\n🧪 测试编译错误...")
    
    code = """
#include <iostream>

int main() {
    int n
    return 0;  // 缺少分号
}
"""
    
    test_cases = [
        {"input": "5", "output": "10"},
    ]
    
    judger = DockerJudger()
    result = judger.judge(code, Language.CPP, test_cases)
    
    print(f"  状态: {result.status}")
    
    if result.status == JudgeResult.COMPILE_ERROR:
        print("  ✅ 正确识别编译错误！")
        return True
    else:
        print("  ❌ 未能识别编译错误")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("Docker 判题引擎测试")
    print("=" * 50)
    
    results = []
    
    try:
        results.append(("Python 简单程序", test_python_simple()))
        results.append(("C++ 简单程序", test_cpp_simple()))
        results.append(("错误答案检测", test_wrong_answer()))
        results.append(("编译错误检测", test_compile_error()))
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\n总计: {passed}/{total} 通过")
