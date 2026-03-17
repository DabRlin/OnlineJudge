"""
提交记录 API 路由
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user
from app.models.user import User, UserRole
from app.models.problem import Problem
from app.services.submission_service import SubmissionService
from app.services.docker_judge_service import DockerJudgeService
from app.schemas.submission import (
    SubmissionCreate,
    SubmissionResponse,
    SubmissionListParams,
)
from app.schemas.response import Response

router = APIRouter()


@router.post("", response_model=Response[SubmissionResponse], status_code=status.HTTP_201_CREATED)
async def submit_code(
    submission_data: SubmissionCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    提交代码
    
    用户提交代码后，系统会在后台进行判题
    """
    service = SubmissionService(db)
    
    # 创建提交记录
    submission = await service.create_submission(
        user_id=current_user.id,
        submission_data=submission_data
    )
    
    # 提交到 Celery 判题队列
    judge_service = DockerJudgeService(db)
    await judge_service.submit_judge_task(submission.id)
    
    return Response(
        data=submission,
        message="代码提交成功，正在判题中..."
    )


@router.get("", response_model=Response[dict])
async def get_submissions(
    page: int = 1,
    page_size: int = 20,
    user_id: int = None,
    problem_id: int = None,
    language: str = None,
    status: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取提交列表
    
    支持分页和筛选
    """
    service = SubmissionService(db)
    
    params = SubmissionListParams(
        page=page,
        page_size=page_size,
        user_id=user_id,
        problem_id=problem_id,
        language=language,
        status=status,
    )
    
    submissions, total = await service.get_submissions(params)
    
    items = []
    for submission in submissions:
        user_stmt = select(User).where(User.id == submission.user_id)
        user_result = await db.execute(user_stmt)
        user = user_result.scalar_one_or_none()
        
        problem_stmt = select(Problem).where(Problem.id == submission.problem_id)
        problem_result = await db.execute(problem_stmt)
        problem = problem_result.scalar_one_or_none()
        
        items.append({
            "id": submission.id,
            "user_id": submission.user_id,
            "user_username": user.username if user else "Unknown",
            "problem_id": submission.problem_id,
            "problem_title": problem.title if problem else "Unknown",
            "language": submission.language,
            "status": submission.status,
            "score": submission.score,
            "time_used": submission.time_used,
            "memory_used": submission.memory_used,
            "submitted_at": submission.submitted_at,
        })
    
    return Response(
        data={
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size
        }
    )


@router.get("/{submission_id}", response_model=Response[dict])
async def get_submission(
    submission_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取提交详情
    
    用户只能查看自己的提交，管理员可以查看所有提交
    """
    service = SubmissionService(db)
    submission = await service.get_submission_by_id(submission_id)
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="提交记录不存在"
        )
    
    # 权限检查
    if submission.user_id != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此提交"
        )
    
    user_stmt = select(User).where(User.id == submission.user_id)
    user_result = await db.execute(user_stmt)
    user = user_result.scalar_one_or_none()
    
    problem_stmt = select(Problem).where(Problem.id == submission.problem_id)
    problem_result = await db.execute(problem_stmt)
    problem = problem_result.scalar_one_or_none()
    
    return Response(
        data={
            "id": submission.id,
            "user_id": submission.user_id,
            "user_username": user.username if user else "Unknown",
            "problem_id": submission.problem_id,
            "problem_title": problem.title if problem else "Unknown",
            "language": submission.language,
            "code": submission.code,
            "status": submission.status,
            "score": submission.score,
            "time_used": submission.time_used,
            "memory_used": submission.memory_used,
            "error_message": submission.error_message,
            "test_cases_result": submission.test_cases_result,
            "submitted_at": submission.submitted_at,
            "judged_at": submission.judged_at,
        }
    )


@router.post("/{submission_id}/rejudge", response_model=Response[SubmissionResponse])
async def rejudge_submission(
    submission_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    重新判题（仅管理员）
    """
    # 检查权限
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以重新判题"
        )
    
    service = SubmissionService(db)
    submission = await service.get_submission_by_id(submission_id)
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="提交记录不存在"
        )
    
    # 重新提交到 Celery 判题队列
    judge_service = DockerJudgeService(db)
    await judge_service.submit_judge_task(submission.id)
    
    return Response(
        data=submission,
        message="重新判题任务已提交"
    )


@router.get("/user/{user_id}", response_model=Response[List[SubmissionResponse]])
async def get_user_submissions(
    user_id: int,
    problem_id: int = None,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取用户的提交记录
    """
    service = SubmissionService(db)
    submissions = await service.get_user_submissions(
        user_id=user_id,
        problem_id=problem_id,
        limit=limit
    )
    
    return Response(data=submissions)
