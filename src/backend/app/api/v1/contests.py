"""
竞赛相关 API
"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_admin_user, get_current_user_optional
from app.models.user import User
from app.models.contest import Contest, ContestProblem, ContestParticipant, ContestStatus
from app.models.problem import Problem
from app.schemas.contest import (
    ContestCreate,
    ContestUpdate,
    Contest as ContestSchema,
    ContestList,
    ContestListResponse,
    ContestProblemCreate,
    ContestProblem as ContestProblemSchema,
    ContestParticipantCreate,
    RankItem,
    RankListResponse,
)

router = APIRouter()


@router.get("", response_model=ContestListResponse)
async def get_contests(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """获取竞赛列表"""
    
    # 构建查询
    query = select(Contest).where(Contest.is_visible.is_(True))
    
    # 状态筛选
    now = datetime.utcnow()
    if status == "not_started":
        query = query.where(Contest.start_time > now)
    elif status == "running":
        query = query.where(and_(Contest.start_time <= now, Contest.end_time > now))
    elif status == "ended":
        query = query.where(Contest.end_time <= now)
    
    # 关键词搜索
    if keyword:
        query = query.where(Contest.title.contains(keyword))
    
    # 获取总数
    count_query = select(func.count()).select_from(query.subquery())
    result = await db.execute(count_query)
    total = result.scalar_one()
    
    # 分页
    query = query.order_by(Contest.start_time.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    contests = result.scalars().all()
    
    return ContestListResponse(
        items=[ContestList.model_validate(c) for c in contests],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=ContestSchema)
async def create_contest(
    contest_in: ContestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """创建竞赛（管理员）"""
    
    # 验证时间
    if contest_in.end_time <= contest_in.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="结束时间必须晚于开始时间"
        )
    
    # 创建竞赛
    contest = Contest(
        **contest_in.model_dump(),
        created_by=current_user.id,
    )
    
    db.add(contest)
    await db.commit()
    await db.refresh(contest)
    
    return ContestSchema.model_validate(contest)


@router.get("/{contest_id}", response_model=ContestSchema)
async def get_contest(
    contest_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """获取竞赛详情"""
    
    result = await db.execute(
        select(Contest).where(Contest.id == contest_id)
    )
    contest = result.scalar_one_or_none()
    
    if not contest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="竞赛不存在"
        )
    
    if not contest.is_visible and (not current_user or current_user.role != "admin"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="竞赛不存在"
        )
    
    return ContestSchema.model_validate(contest)


@router.put("/{contest_id}", response_model=ContestSchema)
async def update_contest(
    contest_id: int,
    contest_in: ContestUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """更新竞赛（管理员）"""
    
    result = await db.execute(
        select(Contest).where(Contest.id == contest_id)
    )
    contest = result.scalar_one_or_none()
    
    if not contest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="竞赛不存在"
        )
    
    # 更新字段
    update_data = contest_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contest, field, value)
    
    await db.commit()
    await db.refresh(contest)
    
    return ContestSchema.model_validate(contest)


@router.delete("/{contest_id}")
async def delete_contest(
    contest_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """删除竞赛（管理员）"""
    
    result = await db.execute(
        select(Contest).where(Contest.id == contest_id)
    )
    contest = result.scalar_one_or_none()
    
    if not contest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="竞赛不存在"
        )
    
    await db.delete(contest)
    await db.commit()
    
    return {"message": "竞赛已删除"}


# ============ 竞赛题目管理 ============

@router.get("/{contest_id}/problems", response_model=list[ContestProblemSchema])
async def get_contest_problems(
    contest_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """获取竞赛题目列表"""
    
    # 检查竞赛是否存在
    result = await db.execute(
        select(Contest).where(Contest.id == contest_id)
    )
    contest = result.scalar_one_or_none()
    
    if not contest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="竞赛不存在"
        )
    
    # 获取题目列表
    result = await db.execute(
        select(ContestProblem)
        .where(ContestProblem.contest_id == contest_id)
        .order_by(ContestProblem.display_id)
    )
    problems = result.scalars().all()
    
    return [ContestProblemSchema.model_validate(p) for p in problems]


@router.post("/{contest_id}/problems", response_model=ContestProblemSchema)
async def add_contest_problem(
    contest_id: int,
    problem_in: ContestProblemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """添加竞赛题目（管理员）"""
    
    # 检查竞赛是否存在
    result = await db.execute(
        select(Contest).where(Contest.id == contest_id)
    )
    contest = result.scalar_one_or_none()
    
    if not contest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="竞赛不存在"
        )
    
    # 检查题目是否存在
    result = await db.execute(
        select(Problem).where(Problem.id == problem_in.problem_id)
    )
    problem = result.scalar_one_or_none()
    
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题目不存在"
        )
    
    # 检查题目是否已添加
    result = await db.execute(
        select(ContestProblem).where(
            and_(
                ContestProblem.contest_id == contest_id,
                ContestProblem.problem_id == problem_in.problem_id
            )
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="题目已存在于竞赛中"
        )
    
    # 添加题目
    contest_problem = ContestProblem(
        contest_id=contest_id,
        **problem_in.model_dump(),
    )
    
    db.add(contest_problem)
    await db.commit()
    await db.refresh(contest_problem)
    
    return ContestProblemSchema.model_validate(contest_problem)


@router.delete("/{contest_id}/problems/{problem_id}")
async def remove_contest_problem(
    contest_id: int,
    problem_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """移除竞赛题目（管理员）"""
    
    result = await db.execute(
        select(ContestProblem).where(
            and_(
                ContestProblem.contest_id == contest_id,
                ContestProblem.problem_id == problem_id
            )
        )
    )
    contest_problem = result.scalar_one_or_none()
    
    if not contest_problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="竞赛题目不存在"
        )
    
    await db.delete(contest_problem)
    await db.commit()
    
    return {"message": "题目已移除"}


# ============ 竞赛参与 ============

@router.post("/{contest_id}/register")
async def register_contest(
    contest_id: int,
    register_in: ContestParticipantCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """报名参赛"""
    
    # 检查竞赛是否存在
    result = await db.execute(
        select(Contest).where(Contest.id == contest_id)
    )
    contest = result.scalar_one_or_none()
    
    if not contest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="竞赛不存在"
        )
    
    # 检查竞赛是否已开始
    if contest.status == ContestStatus.ENDED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="竞赛已结束"
        )
    
    # 验证密码
    if contest.contest_type == "private":
        if not register_in.password or register_in.password != contest.password:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="密码错误"
            )
    
    # 检查是否已报名
    result = await db.execute(
        select(ContestParticipant).where(
            and_(
                ContestParticipant.contest_id == contest_id,
                ContestParticipant.user_id == current_user.id
            )
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        return {"message": "已报名"}
    
    # 创建参与记录
    participant = ContestParticipant(
        contest_id=contest_id,
        user_id=current_user.id,
    )
    
    db.add(participant)
    
    # 更新竞赛参与人数
    contest.participant_count += 1
    
    await db.commit()
    
    return {"message": "报名成功"}


# ============ 排行榜 ============

@router.get("/{contest_id}/rank", response_model=RankListResponse)
async def get_contest_rank(
    contest_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """获取竞赛排行榜"""
    
    # 检查竞赛是否存在
    result = await db.execute(
        select(Contest).where(Contest.id == contest_id)
    )
    contest = result.scalar_one_or_none()
    
    if not contest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="竞赛不存在"
        )
    
    # 获取参与者列表
    query = (
        select(ContestParticipant, User.username)
        .join(User, ContestParticipant.user_id == User.id)
        .where(ContestParticipant.contest_id == contest_id)
    )
    
    # 根据规则排序
    if contest.rule_type == "acm":
        # ACM 规则：通过题数降序，罚时升序
        query = query.order_by(
            ContestParticipant.solved_count.desc(),
            ContestParticipant.total_time.asc()
        )
    else:
        # OI 规则：总分降序
        query = query.order_by(ContestParticipant.total_score.desc())
    
    # 获取总数
    count_query = select(func.count()).select_from(
        select(ContestParticipant).where(ContestParticipant.contest_id == contest_id).subquery()
    )
    result = await db.execute(count_query)
    total = result.scalar_one()
    
    # 分页
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    participants = result.all()
    
    # 构建排行榜
    rank_items = []
    for idx, (participant, username) in enumerate(participants, start=(page - 1) * page_size + 1):
        rank_items.append(RankItem(
            rank=idx,
            user_id=participant.user_id,
            username=username,
            total_score=participant.total_score,
            solved_count=participant.solved_count,
            total_time=participant.total_time,
            submission_count=participant.submission_count,
            last_submission_at=participant.last_submission_at,
        ))
    
    return RankListResponse(
        items=rank_items,
        total=total,
        is_frozen=contest.is_frozen,
    )
