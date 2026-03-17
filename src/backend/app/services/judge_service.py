"""
判题服务（简化版）

这是一个基础的判题服务，直接执行代码并比对结果
后续可以升级为 Docker 沙箱版本
"""

import asyncio
import subprocess
import tempfile
import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.submission import Submission, SubmissionStatus, ProgrammingLanguage
from app.models.problem import Problem, TestCase
from app.services.submission_service import SubmissionService
from app.schemas.submission import SubmissionUpdate


class JudgeService:
    """判题服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.submission_service = SubmissionService(db)
    
    async def judge_submission(self, submission_id: int) -> None:
        """
        判题主流程
        
        Args:
            submission_id: 提交 ID
        """
        # 获取提交记录
        submission = await self.submission_service.get_submission_by_id(submission_id)
        if not submission:
            return
        
        # 更新状态为判题中
        await self.submission_service.update_submission(
            submission_id,
            SubmissionUpdate(status=SubmissionStatus.JUDGING)
        )
        
        try:
            # 获取题目和测试用例
            from sqlalchemy import select
            stmt = select(Problem).where(Problem.id == submission.problem_id)
            result = await self.db.execute(stmt)
            problem = result.scalar_one_or_none()
            
            if not problem:
                await self._update_error(submission_id, "题目不存在")
                return
            
            # 获取测试用例
            test_cases_stmt = select(TestCase).where(TestCase.problem_id == problem.id)
            test_cases_result = await self.db.execute(test_cases_stmt)
            test_cases = list(test_cases_result.scalars().all())
            
            if not test_cases:
                await self._update_error(submission_id, "没有测试用例")
                return
            
            # 执行判题
            judge_result = await self._run_code(
                submission.code,
                submission.language,
                test_cases,
                problem.time_limit,
                problem.memory_limit
            )
            
            # 更新提交结果
            await self.submission_service.update_submission(
                submission_id,
                SubmissionUpdate(
                    status=judge_result["status"],
                    score=judge_result["score"],
                    time_used=judge_result["time_used"],
                    memory_used=judge_result["memory_used"],
                    error_message=judge_result.get("error_message"),
                    test_cases_result=json.dumps(judge_result["test_cases_result"])
                )
            )
            
            # 更新题目统计
            await self.submission_service.update_problem_statistics(problem.id)
            
        except Exception as e:
            await self._update_error(submission_id, f"判题系统错误: {str(e)}")
    
    async def _run_code(
        self,
        code: str,
        language: ProgrammingLanguage,
        test_cases: List[TestCase],
        time_limit: int,
        memory_limit: int
    ) -> Dict[str, Any]:
        """
        运行代码并测试
        
        Args:
            code: 代码
            language: 语言
            test_cases: 测试用例
            time_limit: 时间限制（毫秒）
            memory_limit: 内存限制（MB）
            
        Returns:
            判题结果
        """
        # 编译代码（如果需要）
        compile_result = await self._compile_code(code, language)
        if not compile_result["success"]:
            return {
                "status": SubmissionStatus.COMPILE_ERROR,
                "score": 0,
                "time_used": 0,
                "memory_used": 0,
                "error_message": compile_result["error"],
                "test_cases_result": []
            }
        
        # 运行测试用例
        test_results = []
        total_time = 0
        total_memory = 0
        passed_count = 0
        
        for test_case in test_cases:
            result = await self._run_test_case(
                compile_result["executable"],
                language,
                test_case.input,
                test_case.output,
                time_limit,
                memory_limit
            )
            
            test_results.append({
                "test_case_id": test_case.id,
                "status": result["status"],
                "time_used": result["time_used"],
                "memory_used": result["memory_used"],
                "error_message": result.get("error_message")
            })
            
            total_time += result["time_used"]
            total_memory = max(total_memory, result["memory_used"])
            
            if result["status"] == SubmissionStatus.ACCEPTED:
                passed_count += 1
            elif result["status"] != SubmissionStatus.ACCEPTED:
                # 如果有一个测试用例失败，整体状态就是失败
                break
        
        # 计算得分和最终状态
        score = int((passed_count / len(test_cases)) * 100)
        
        if passed_count == len(test_cases):
            final_status = SubmissionStatus.ACCEPTED
        elif test_results and test_results[-1]["status"] != SubmissionStatus.ACCEPTED:
            final_status = test_results[-1]["status"]
        else:
            final_status = SubmissionStatus.WRONG_ANSWER
        
        # 清理临时文件
        if compile_result.get("temp_file"):
            try:
                os.remove(compile_result["temp_file"])
            except:
                pass
        
        return {
            "status": final_status,
            "score": score,
            "time_used": total_time,
            "memory_used": total_memory,
            "test_cases_result": test_results
        }
    
    async def _compile_code(
        self,
        code: str,
        language: ProgrammingLanguage
    ) -> Dict[str, Any]:
        """
        编译代码
        
        Returns:
            {"success": bool, "executable": str, "error": str, "temp_file": str}
        """
        if language == ProgrammingLanguage.PYTHON:
            # Python 不需要编译
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                return {
                    "success": True,
                    "executable": f.name,
                    "temp_file": f.name
                }
        
        elif language == ProgrammingLanguage.CPP:
            # C++ 编译
            with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False) as f:
                f.write(code)
                source_file = f.name
            
            executable = source_file.replace('.cpp', '')
            
            try:
                result = subprocess.run(
                    ['g++', source_file, '-o', executable, '-std=c++17'],
                    capture_output=True,
                    timeout=10,
                    text=True
                )
                
                if result.returncode != 0:
                    return {
                        "success": False,
                        "error": result.stderr,
                        "temp_file": source_file
                    }
                
                return {
                    "success": True,
                    "executable": executable,
                    "temp_file": source_file
                }
            except subprocess.TimeoutExpired:
                return {
                    "success": False,
                    "error": "编译超时",
                    "temp_file": source_file
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "temp_file": source_file
                }
        
        else:
            return {
                "success": False,
                "error": f"不支持的语言: {language}"
            }
    
    async def _run_test_case(
        self,
        executable: str,
        language: ProgrammingLanguage,
        input_data: str,
        expected_output: str,
        time_limit: int,
        memory_limit: int
    ) -> Dict[str, Any]:
        """
        运行单个测试用例
        
        Returns:
            {"status": SubmissionStatus, "time_used": int, "memory_used": int, "error_message": str}
        """
        try:
            # 准备运行命令
            if language == ProgrammingLanguage.PYTHON:
                cmd = ['python3', executable]
            elif language == ProgrammingLanguage.CPP:
                cmd = [executable]
            else:
                return {
                    "status": SubmissionStatus.SYSTEM_ERROR,
                    "time_used": 0,
                    "memory_used": 0,
                    "error_message": f"不支持的语言: {language}"
                }
            
            # 运行代码
            start_time = datetime.now()
            
            result = subprocess.run(
                cmd,
                input=input_data,
                capture_output=True,
                timeout=time_limit / 1000,  # 转换为秒
                text=True
            )
            
            end_time = datetime.now()
            time_used = int((end_time - start_time).total_seconds() * 1000)
            
            # 检查运行时错误
            if result.returncode != 0:
                return {
                    "status": SubmissionStatus.RUNTIME_ERROR,
                    "time_used": time_used,
                    "memory_used": 0,
                    "error_message": result.stderr[:500]  # 限制错误信息长度
                }
            
            # 比对输出
            actual_output = result.stdout.strip()
            expected_output = expected_output.strip()
            
            if actual_output == expected_output:
                return {
                    "status": SubmissionStatus.ACCEPTED,
                    "time_used": time_used,
                    "memory_used": 0  # 简化版暂不统计内存
                }
            else:
                return {
                    "status": SubmissionStatus.WRONG_ANSWER,
                    "time_used": time_used,
                    "memory_used": 0,
                    "error_message": f"期望输出: {expected_output[:100]}\n实际输出: {actual_output[:100]}"
                }
        
        except subprocess.TimeoutExpired:
            return {
                "status": SubmissionStatus.TIME_LIMIT_EXCEEDED,
                "time_used": time_limit,
                "memory_used": 0,
                "error_message": "运行超时"
            }
        except Exception as e:
            return {
                "status": SubmissionStatus.SYSTEM_ERROR,
                "time_used": 0,
                "memory_used": 0,
                "error_message": str(e)
            }
    
    async def _update_error(self, submission_id: int, error_message: str) -> None:
        """更新提交为系统错误"""
        await self.submission_service.update_submission(
            submission_id,
            SubmissionUpdate(
                status=SubmissionStatus.SYSTEM_ERROR,
                score=0,
                error_message=error_message
            )
        )
