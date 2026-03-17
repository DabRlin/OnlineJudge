"""
Docker 判题服务 - 使用 Celery 异步判题
"""

import sys
import os
import json
from typing import Optional

# 添加 judger 路径
judger_path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
sys.path.insert(0, judger_path)

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.submission import SubmissionStatus, ProgrammingLanguage
from app.models.problem import Problem, TestCase
from app.services.submission_service import SubmissionService
from app.schemas.submission import SubmissionUpdate

# 导入 Celery 任务
try:
    from judger.tasks import judge_submission
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    print("Warning: Celery not available, falling back to sync judging")


class DockerJudgeService:
    """Docker 判题服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.submission_service = SubmissionService(db)
    
    async def submit_judge_task(self, submission_id: int) -> Optional[str]:
        """
        提交判题任务到 Celery 队列
        
        Args:
            submission_id: 提交 ID
            
        Returns:
            Celery task ID，如果失败返回 None
        """
        # 获取提交记录
        submission = await self.submission_service.get_submission_by_id(submission_id)
        if not submission:
            return None
        
        # 获取题目和测试用例
        stmt = select(Problem).where(Problem.id == submission.problem_id)
        result = await self.db.execute(stmt)
        problem = result.scalar_one_or_none()
        
        if not problem:
            await self._update_error(submission_id, "题目不存在")
            return None
        
        # 获取测试用例
        test_cases_stmt = select(TestCase).where(TestCase.problem_id == problem.id)
        test_cases_result = await self.db.execute(test_cases_stmt)
        test_cases = list(test_cases_result.scalars().all())
        
        if not test_cases:
            await self._update_error(submission_id, "没有测试用例")
            return None
        
        # 准备测试用例数据
        test_cases_data = [
            {
                "input": tc.input,
                "output": tc.output
            }
            for tc in test_cases
        ]
        
        # 转换语言枚举
        language_map = {
            ProgrammingLanguage.PYTHON: "python",
            ProgrammingLanguage.CPP: "cpp",
            ProgrammingLanguage.JAVA: "java",
            ProgrammingLanguage.GO: "go",
            ProgrammingLanguage.JAVASCRIPT: "javascript",
        }
        language_str = language_map.get(submission.language, "python")
        
        # 更新状态为等待判题
        await self.submission_service.update_submission(
            submission_id,
            SubmissionUpdate(status=SubmissionStatus.PENDING)
        )
        
        if not CELERY_AVAILABLE:
            # Celery 不可用，使用同步判题
            await self._judge_sync(
                submission_id,
                submission.code,
                language_str,
                test_cases_data,
                problem.time_limit,
                problem.memory_limit
            )
            return None
        
        # 提交到 Celery 队列
        try:
            task = judge_submission.delay(
                submission_id=submission_id,
                code=submission.code,
                language=language_str,
                test_cases=test_cases_data,
                time_limit=problem.time_limit,
                memory_limit=problem.memory_limit,
            )
            
            # 保存 task ID（可选，用于查询任务状态）
            await self.submission_service.update_submission(
                submission_id,
                SubmissionUpdate(
                    status=SubmissionStatus.JUDGING,
                    error_message=f"Task ID: {task.id}"
                )
            )
            
            return task.id
            
        except Exception as e:
            await self._update_error(submission_id, f"提交判题任务失败: {str(e)}")
            return None
    
    async def _judge_sync(
        self,
        submission_id: int,
        code: str,
        language: str,
        test_cases: list,
        time_limit: int,
        memory_limit: int
    ):
        """
        同步判题（Celery 不可用时的后备方案）
        """
        try:
            from judger.docker_judger import DockerJudger
            from judger.languages import Language
            
            # 更新状态为判题中
            await self.submission_service.update_submission(
                submission_id,
                SubmissionUpdate(status=SubmissionStatus.JUDGING)
            )
            
            # 创建判题器
            judger = DockerJudger()
            lang = Language(language.lower())
            
            # 执行判题
            result = judger.judge(
                code=code,
                language=lang,
                test_cases=test_cases,
                time_limit=time_limit,
                memory_limit=memory_limit,
            )
            
            # 更新结果
            await self._update_result(submission_id, result)
            
        except Exception as e:
            await self._update_error(submission_id, f"同步判题失败: {str(e)}")
    
    async def update_judge_result(self, submission_id: int, result_dict: dict):
        """
        更新判题结果（由 Celery 回调调用）
        
        Args:
            submission_id: 提交 ID
            result_dict: 判题结果字典
        """
        # 转换状态字符串为枚举
        status_map = {
            "accepted": SubmissionStatus.ACCEPTED,
            "wrong_answer": SubmissionStatus.WRONG_ANSWER,
            "time_limit_exceeded": SubmissionStatus.TIME_LIMIT_EXCEEDED,
            "memory_limit_exceeded": SubmissionStatus.MEMORY_LIMIT_EXCEEDED,
            "runtime_error": SubmissionStatus.RUNTIME_ERROR,
            "compile_error": SubmissionStatus.COMPILE_ERROR,
            "system_error": SubmissionStatus.SYSTEM_ERROR,
        }
        
        status = status_map.get(result_dict["status"], SubmissionStatus.SYSTEM_ERROR)
        
        # 更新提交结果
        await self.submission_service.update_submission(
            submission_id,
            SubmissionUpdate(
                status=status,
                score=result_dict.get("score", 0),
                time_used=result_dict.get("time_used", 0),
                memory_used=result_dict.get("memory_used", 0),
                error_message=result_dict.get("error_message"),
                test_cases_result=json.dumps(result_dict.get("test_cases_result", []))
            )
        )
        
        # 更新题目统计
        submission = await self.submission_service.get_submission_by_id(submission_id)
        if submission:
            await self.submission_service.update_problem_statistics(submission.problem_id)
    
    async def _update_result(self, submission_id: int, result):
        """更新判题结果"""
        from judger.docker_judger import JudgeResult
        
        status_map = {
            JudgeResult.ACCEPTED: SubmissionStatus.ACCEPTED,
            JudgeResult.WRONG_ANSWER: SubmissionStatus.WRONG_ANSWER,
            JudgeResult.TIME_LIMIT_EXCEEDED: SubmissionStatus.TIME_LIMIT_EXCEEDED,
            JudgeResult.MEMORY_LIMIT_EXCEEDED: SubmissionStatus.MEMORY_LIMIT_EXCEEDED,
            JudgeResult.RUNTIME_ERROR: SubmissionStatus.RUNTIME_ERROR,
            JudgeResult.COMPILE_ERROR: SubmissionStatus.COMPILE_ERROR,
            JudgeResult.SYSTEM_ERROR: SubmissionStatus.SYSTEM_ERROR,
        }
        
        status = status_map.get(result.status, SubmissionStatus.SYSTEM_ERROR)
        
        await self.submission_service.update_submission(
            submission_id,
            SubmissionUpdate(
                status=status,
                score=result.score,
                time_used=result.time_used,
                memory_used=result.memory_used,
                error_message=result.error_message,
                test_cases_result=json.dumps(result.test_cases_result)
            )
        )
        
        # 更新题目统计
        submission = await self.submission_service.get_submission_by_id(submission_id)
        if submission:
            await self.submission_service.update_problem_statistics(submission.problem_id)
    
    async def _update_error(self, submission_id: int, error_message: str):
        """更新错误状态"""
        await self.submission_service.update_submission(
            submission_id,
            SubmissionUpdate(
                status=SubmissionStatus.SYSTEM_ERROR,
                error_message=error_message
            )
        )
