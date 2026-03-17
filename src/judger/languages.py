"""
编程语言配置
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class Language(str, Enum):
    """支持的编程语言"""
    PYTHON = "python"
    CPP = "cpp"
    JAVA = "java"
    GO = "go"
    JAVASCRIPT = "javascript"


@dataclass
class LanguageConfig:
    """语言配置"""
    name: str
    image: str
    compile_command: Optional[str]
    run_command: str
    source_file: str
    compiled_file: Optional[str]
    max_memory: str  # Docker 内存限制
    max_cpu: str     # Docker CPU 限制


# 语言配置映射
LANGUAGE_CONFIGS = {
    Language.PYTHON: LanguageConfig(
        name="Python 3.11",
        image="oj-judger-python:latest",
        compile_command=None,
        run_command="python3 {source_file}",
        source_file="solution.py",
        compiled_file=None,
        max_memory="256m",
        max_cpu="1.0",
    ),
    
    Language.CPP: LanguageConfig(
        name="C++ 17",
        image="oj-judger-cpp:latest",
        compile_command="g++ -std=c++17 -O2 -Wall -o {compiled_file} {source_file}",
        run_command="./{compiled_file}",
        source_file="solution.cpp",
        compiled_file="solution",
        max_memory="256m",
        max_cpu="1.0",
    ),
    
    Language.JAVA: LanguageConfig(
        name="Java 17",
        image="oj-judger-java:latest",
        compile_command="javac {source_file}",
        run_command="java Solution",
        source_file="Solution.java",
        compiled_file=None,
        max_memory="512m",  # Java 需要更多内存
        max_cpu="1.0",
    ),
    
    Language.GO: LanguageConfig(
        name="Go 1.21",
        image="oj-judger-go:latest",
        compile_command="go build -o {compiled_file} {source_file}",
        run_command="./{compiled_file}",
        source_file="solution.go",
        compiled_file="solution",
        max_memory="256m",
        max_cpu="1.0",
    ),
    
    Language.JAVASCRIPT: LanguageConfig(
        name="Node.js 20",
        image="oj-judger-javascript:latest",
        compile_command=None,
        run_command="node {source_file}",
        source_file="solution.js",
        compiled_file=None,
        max_memory="256m",
        max_cpu="1.0",
    ),
}


def get_language_config(language: Language) -> LanguageConfig:
    """获取语言配置"""
    return LANGUAGE_CONFIGS[language]
