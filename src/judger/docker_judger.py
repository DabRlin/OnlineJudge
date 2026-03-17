"""
Docker 判题引擎
"""

import os
import tempfile
import shutil
from typing import Dict, List, Tuple, Optional
from pathlib import Path

import docker
from docker.models.containers import Container

from .languages import Language, get_language_config


class JudgeResult:
    """判题结果"""
    
    # 判题状态
    PENDING = "pending"
    JUDGING = "judging"
    ACCEPTED = "accepted"
    WRONG_ANSWER = "wrong_answer"
    TIME_LIMIT_EXCEEDED = "time_limit_exceeded"
    MEMORY_LIMIT_EXCEEDED = "memory_limit_exceeded"
    RUNTIME_ERROR = "runtime_error"
    COMPILE_ERROR = "compile_error"
    SYSTEM_ERROR = "system_error"
    
    def __init__(self):
        self.status = self.PENDING
        self.score = 0
        self.time_used = 0  # 毫秒
        self.memory_used = 0  # KB
        self.error_message = ""
        self.test_cases_result = []


class DockerJudger:
    """Docker 判题器"""
    
    def __init__(self):
        """初始化 Docker 客户端"""
        try:
            # OrbStack 的 Docker socket 路径
            orbstack_socket = os.path.expanduser('~/.orbstack/run/docker.sock')
            if os.path.exists(orbstack_socket):
                self.client = docker.DockerClient(
                    base_url=f'unix://{orbstack_socket}'
                )
            else:
                self.client = docker.from_env()
        except Exception as e:
            raise RuntimeError(f"无法连接到 Docker: {e}")
    
    def judge(
        self,
        code: str,
        language: Language,
        test_cases: List[Dict[str, str]],
        time_limit: int = 1000,  # 毫秒
        memory_limit: int = 256,  # MB
    ) -> JudgeResult:
        """
        执行判题
        
        Args:
            code: 用户代码
            language: 编程语言
            test_cases: 测试用例列表 [{"input": "...", "output": "..."}, ...]
            time_limit: 时间限制（毫秒）
            memory_limit: 内存限制（MB）
            
        Returns:
            JudgeResult: 判题结果
        """
        result = JudgeResult()
        result.status = JudgeResult.JUDGING
        
        # 获取语言配置
        config = get_language_config(language)
        
        # 创建临时工作目录
        work_dir = tempfile.mkdtemp(prefix="oj_judge_")
        
        try:
            # 1. 保存代码到文件
            source_path = os.path.join(work_dir, config.source_file)
            with open(source_path, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # 2. 编译（如果需要）
            if config.compile_command:
                compile_result = self._compile(work_dir, config)
                if not compile_result[0]:
                    result.status = JudgeResult.COMPILE_ERROR
                    result.error_message = compile_result[1]
                    return result
            
            # 3. 运行测试用例
            passed = 0
            total = len(test_cases)
            
            for idx, test_case in enumerate(test_cases):
                test_result = self._run_test_case(
                    work_dir,
                    config,
                    test_case,
                    time_limit,
                    memory_limit
                )
                
                result.test_cases_result.append({
                    "case_id": idx + 1,
                    "status": test_result["status"],
                    "time_used": test_result["time_used"],
                    "memory_used": test_result["memory_used"],
                    "output": test_result.get("output", ""),
                })
                
                # 更新统计
                result.time_used = max(result.time_used, test_result["time_used"])
                result.memory_used = max(result.memory_used, test_result["memory_used"])
                
                # 检查结果
                if test_result["status"] == JudgeResult.ACCEPTED:
                    passed += 1
                elif test_result["status"] == JudgeResult.TIME_LIMIT_EXCEEDED:
                    result.status = JudgeResult.TIME_LIMIT_EXCEEDED
                    break
                elif test_result["status"] == JudgeResult.MEMORY_LIMIT_EXCEEDED:
                    result.status = JudgeResult.MEMORY_LIMIT_EXCEEDED
                    break
                elif test_result["status"] == JudgeResult.RUNTIME_ERROR:
                    result.status = JudgeResult.RUNTIME_ERROR
                    result.error_message = test_result.get("error", "")
                    break
                else:  # WRONG_ANSWER
                    result.status = JudgeResult.WRONG_ANSWER
            
            # 4. 计算分数
            if result.status == JudgeResult.JUDGING:
                if passed == total:
                    result.status = JudgeResult.ACCEPTED
                    result.score = 100
                else:
                    result.status = JudgeResult.WRONG_ANSWER
                    result.score = int(passed / total * 100)
            
        except Exception as e:
            result.status = JudgeResult.SYSTEM_ERROR
            result.error_message = str(e)
        
        finally:
            # 清理临时目录
            shutil.rmtree(work_dir, ignore_errors=True)
        
        return result
    
    def _compile(self, work_dir: str, config) -> Tuple[bool, str]:
        """
        编译代码
        
        Returns:
            (success, error_message)
        """
        try:
            compile_cmd = config.compile_command.format(
                source_file=config.source_file,
                compiled_file=config.compiled_file or "a.out"
            )
            
            container = self.client.containers.run(
                image=config.image,
                command=f"sh -c '{compile_cmd}'",
                volumes={work_dir: {'bind': '/workspace', 'mode': 'rw'}},
                working_dir='/workspace',
                network_mode='none',
                mem_limit=config.max_memory,
                cpu_quota=int(float(config.max_cpu) * 100000),
                detach=False,
                remove=True,
                stderr=True,
            )
            
            return (True, "")
            
        except docker.errors.ContainerError as e:
            return (False, e.stderr.decode('utf-8'))
        except Exception as e:
            return (False, str(e))
    
    def _run_test_case(
        self,
        work_dir: str,
        config,
        test_case: Dict[str, str],
        time_limit: int,
        memory_limit: int
    ) -> Dict:
        """
        运行单个测试用例
        
        Returns:
            {
                "status": str,
                "time_used": int (ms),
                "memory_used": int (KB),
                "output": str,
                "error": str
            }
        """
        result = {
            "status": JudgeResult.ACCEPTED,
            "time_used": 0,
            "memory_used": 0,
            "output": "",
            "error": ""
        }
        
        try:
            # 准备输入文件
            input_path = os.path.join(work_dir, "input.txt")
            with open(input_path, 'w', encoding='utf-8') as f:
                f.write(test_case["input"])
            
            # 运行命令
            run_cmd = config.run_command.format(
                source_file=config.source_file,
                compiled_file=config.compiled_file or "a.out"
            )
            
            # 运行容器
            container = self.client.containers.run(
                image=config.image,
                command=f"sh -c '{run_cmd} < input.txt'",
                volumes={work_dir: {'bind': '/workspace', 'mode': 'rw'}},
                working_dir='/workspace',
                network_mode='none',
                mem_limit=f"{memory_limit}m",
                cpu_quota=int(float(config.max_cpu) * 100000),
                detach=True,
            )
            
            # 等待执行完成（带超时）：time_limit 毫秒 + 5 秒容器启动缓冲
            timeout_seconds = time_limit / 1000.0 + 5
            try:
                exit_code = container.wait(timeout=timeout_seconds)
                
                # 获取输出
                output = container.logs(stdout=True, stderr=False).decode('utf-8').strip()
                error = container.logs(stdout=False, stderr=True).decode('utf-8').strip()
                
                # 检查运行时错误（优先于输出比较）
                if exit_code['StatusCode'] != 0:
                    result["status"] = JudgeResult.RUNTIME_ERROR
                    result["error"] = error
                else:
                    # 比较输出
                    expected_output = test_case["output"].strip()
                    actual_output = output.strip()
                    if actual_output == expected_output:
                        result["status"] = JudgeResult.ACCEPTED
                    else:
                        result["status"] = JudgeResult.WRONG_ANSWER
                        result["output"] = actual_output
                
            except Exception as e:
                result["status"] = JudgeResult.TIME_LIMIT_EXCEEDED
            
            finally:
                # 清理容器
                try:
                    container.remove(force=True)
                except:
                    pass
                    
        except docker.errors.ContainerError as e:
            result["status"] = JudgeResult.RUNTIME_ERROR
            result["error"] = e.stderr.decode('utf-8')
        except Exception as e:
            result["status"] = JudgeResult.SYSTEM_ERROR
            result["error"] = str(e)
        
        return result
