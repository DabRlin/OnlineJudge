"""
提交记录服务层
"""

from typing import Optional, List, Tuple
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.submission import Submission, SubmissionStatus, ProgrammingLanguage
from app.models.problem import Problem
from app.schemas.submission import (
    SubmissionCreate,
    SubmissionUpdate,
    SubmissionListParams,
)


class SubmissionService:
    """提交记录服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_submission(
        self,
        user_id: int,
        submission_data: SubmissionCreate
    ) -> Submission:
        """
        创建提交记录
        
        Args:
            user_id: 用户 ID
            submission_data: 提交数据
            
        Returns:
            创建的提交记录
        """
        submission = Submission(
            user_id=user_id,
            problem_id=submission_data.problem_id,
            language=submission_data.language,
            code=submission_data.code,
            status=SubmissionStatus.PENDING,
            submitted_at=datetime.utcnow()
        )
        
        self.db.add(submission)
        await self.db.commit()
        await self.db.refresh(submission)
        
        return submission
    
    async def get_submission_by_id(self, submission_id: int) -> Optional[Submission]:
        """
        根据 ID 获取提交记录
        
        Args:
            submission_id: 提交 ID
            
        Returns:
            提交记录或 None
        """
        stmt = select(Submission).where(Submission.id == submission_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_submissions(
        self,
        params: SubmissionListParams
    ) -> Tuple[List[Submission], int]:
        """
        获取提交列表（分页）
        
        Args:
            params: 查询参数
            
        Returns:
            (提交列表, 总数)
        """
        # 构建查询条件
        conditions = []
        
        if params.user_id:
            conditions.append(Submission.user_id == params.user_id)
        
        if params.problem_id:
            conditions.append(Submission.problem_id == params.problem_id)
        
        if params.language:
            conditions.append(Submission.language == params.language)
        
        if params.status:
            conditions.append(Submission.status == params.status)
        
        # 查询总数
        count_stmt = select(func.count(Submission.id))
        if conditions:
            count_stmt = count_stmt.where(and_(*conditions))
        
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar_one()
        
        # 查询列表
        stmt = select(Submission)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        
        stmt = stmt.order_by(Submission.submitted_at.desc())
        stmt = stmt.offset((params.page - 1) * params.page_size)
        stmt = stmt.limit(params.page_size)
        
        result = await self.db.execute(stmt)
        submissions = list(result.scalars().all())
        
        return submissions, total
    
    async def update_submission(
        self,
        submission_id: int,
        update_data: SubmissionUpdate
    ) -> Optional[Submission]:
        """
        更新提交记录（判题结果）
        
        Args:
            submission_id: 提交 ID
            update_data: 更新数据
            
        Returns:
            更新后的提交记录或 None
        """
        submission = await self.get_submission_by_id(submission_id)
        if not submission:
            return None
        
        # 更新字段
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(submission, field, value)
        
        # 如果状态不是 PENDING 或 JUDGING，设置判题完成时间
        if submission.status not in [SubmissionStatus.PENDING, SubmissionStatus.JUDGING]:
            submission.judged_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(submission)
        
        return submission
    
    async def get_user_submissions(
        self,
        user_id: int,
        problem_id: Optional[int] = None,
        limit: int = 10
    ) -> List[Submission]:
        """
        获取用户的提交记录
        
        Args:
            user_id: 用户 ID
            problem_id: 题目 ID（可选）
            limit: 限制数量
            
        Returns:
            提交列表
        """
        stmt = select(Submission).where(Submission.user_id == user_id)
        
        if problem_id:
            stmt = stmt.where(Submission.problem_id == problem_id)
        
        stmt = stmt.order_by(Submission.submitted_at.desc()).limit(limit)
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_problem_submissions(
        self,
        problem_id: int,
        limit: int = 10
    ) -> List[Submission]:
        """
        获取题目的提交记录
        
        Args:
            problem_id: 题目 ID
            limit: 限制数量
            
        Returns:
            提交列表
        """
        stmt = (
            select(Submission)
            .where(Submission.problem_id == problem_id)
            .order_by(Submission.submitted_at.desc())
            .limit(limit)
        )
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_user_accepted_problems(self, user_id: int) -> List[int]:
        """
        获取用户通过的题目 ID 列表
        
        Args:
            user_id: 用户 ID
            
        Returns:
            题目 ID 列表
        """
        stmt = (
            select(Submission.problem_id)
            .where(
                and_(
                    Submission.user_id == user_id,
                    Submission.status == SubmissionStatus.ACCEPTED
                )
            )
            .distinct()
        )
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def update_problem_statistics(self, problem_id: int) -> None:
        """
        更新题目的提交统计
        
        Args:
            problem_id: 题目 ID
        """
        # 获取题目
        stmt = select(Problem).where(Problem.id == problem_id)
        result = await self.db.execute(stmt)
        problem = result.scalar_one_or_none()
        
        if not problem:
            return
        
        # 统计提交总数
        count_stmt = select(func.count(Submission.id)).where(
            Submission.problem_id == problem_id
        )
        count_result = await self.db.execute(count_stmt)
        problem.submission_count = count_result.scalar_one()
        
        # 统计通过数
        accepted_stmt = select(func.count(Submission.id)).where(
            and_(
                Submission.problem_id == problem_id,
                Submission.status == SubmissionStatus.ACCEPTED
            )
        )
        accepted_result = await self.db.execute(accepted_stmt)
        problem.accepted_count = accepted_result.scalar_one()
        
        await self.db.commit()
