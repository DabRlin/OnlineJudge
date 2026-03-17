"""
多语言判题测试脚本
测试 Python / C++ / Java / Go / JavaScript
题目：两数之和（标准 IO 版）
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from judger.docker_judger import DockerJudger
from judger.languages import Language

# 测试用例：两数之和
TEST_CASES = [
    {"input": "4\n2 7 11 15\n9",  "output": "0 1"},
    {"input": "3\n3 2 4\n6",       "output": "1 2"},
    {"input": "2\n3 3\n6",         "output": "0 1"},
]

CODES = {
    Language.PYTHON: """\
n = int(input())
nums = list(map(int, input().split()))
target = int(input())
hashmap = {}
for i, num in enumerate(nums):
    comp = target - num
    if comp in hashmap:
        print(hashmap[comp], i)
        break
    hashmap[num] = i
""",

    Language.CPP: """\
#include <bits/stdc++.h>
using namespace std;
int main() {
    int n; cin >> n;
    vector<int> nums(n);
    for (int i = 0; i < n; i++) cin >> nums[i];
    int target; cin >> target;
    unordered_map<int,int> mp;
    for (int i = 0; i < n; i++) {
        int comp = target - nums[i];
        if (mp.count(comp)) {
            cout << mp[comp] << " " << i << endl;
            return 0;
        }
        mp[nums[i]] = i;
    }
    return 0;
}
""",

    Language.JAVA: """\
import java.util.*;
public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int[] nums = new int[n];
        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();
        int target = sc.nextInt();
        Map<Integer,Integer> map = new HashMap<>();
        for (int i = 0; i < n; i++) {
            int comp = target - nums[i];
            if (map.containsKey(comp)) {
                System.out.println(map.get(comp) + " " + i);
                return;
            }
            map.put(nums[i], i);
        }
    }
}
""",

    Language.GO: """\
package main
import "fmt"
func main() {
    var n int
    fmt.Scan(&n)
    nums := make([]int, n)
    for i := 0; i < n; i++ { fmt.Scan(&nums[i]) }
    var target int
    fmt.Scan(&target)
    mp := make(map[int]int)
    for i, num := range nums {
        comp := target - num
        if j, ok := mp[comp]; ok {
            fmt.Println(j, i)
            return
        }
        mp[num] = i
    }
}
""",

    Language.JAVASCRIPT: """\
const lines = require('fs').readFileSync('/dev/stdin','utf8').trim().split('\\n');
const n = parseInt(lines[0]);
const nums = lines[1].split(' ').map(Number);
const target = parseInt(lines[2]);
const map = new Map();
for (let i = 0; i < n; i++) {
    const comp = target - nums[i];
    if (map.has(comp)) {
        console.log(map.get(comp) + ' ' + i);
        process.exit(0);
    }
    map.set(nums[i], i);
}
""",
}

LANG_NAMES = {
    Language.PYTHON: "Python",
    Language.CPP: "C++",
    Language.JAVA: "Java",
    Language.GO: "Go",
    Language.JAVASCRIPT: "JavaScript",
}


def run_test(judger, lang):
    name = LANG_NAMES[lang]
    print(f"\n{'='*50}")
    print(f"🧪 测试 {name}")
    print('='*50)
    try:
        result = judger.judge(
            code=CODES[lang],
            language=lang,
            test_cases=TEST_CASES,
            time_limit=5000,
            memory_limit=256,
        )
        status_icon = "✅" if result.status == "accepted" else "❌"
        print(f"{status_icon} 状态: {result.status}")
        print(f"   得分: {result.score}")
        print(f"   时间: {result.time_used}ms")
        if result.error_message:
            print(f"   错误: {result.error_message[:200]}")
        for i, tc in enumerate(result.test_cases_result):
            icon = "✓" if tc['status'] == 'accepted' else "✗"
            print(f"   {icon} 测试用例 {tc['case_id']}: {tc['status']}", end="")
            if tc.get('output'):
                print(f" | 输出: {repr(tc['output'])}", end="")
            print()
        return result.status == "accepted"
    except Exception as e:
        print(f"❌ 异常: {e}")
        return False


def main():
    print("🚀 多语言判题引擎测试")
    print("题目：两数之和（标准 IO）\n")

    judger = DockerJudger()
    print("✅ Docker 客户端初始化成功")

    results = {}
    for lang in [Language.PYTHON, Language.CPP, Language.JAVA, Language.GO, Language.JAVASCRIPT]:
        results[lang] = run_test(judger, lang)

    print(f"\n{'='*50}")
    print("📊 测试结果汇总")
    print('='*50)
    passed = 0
    for lang, ok in results.items():
        icon = "✅" if ok else "❌"
        print(f"  {icon} {LANG_NAMES[lang]}")
        if ok:
            passed += 1
    print(f"\n通过: {passed}/{len(results)}")


if __name__ == "__main__":
    main()
