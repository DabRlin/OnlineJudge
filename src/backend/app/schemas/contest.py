"""
竞赛相关的 Pydantic schemas
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.models.contest import ContestType, ContestStatus, RuleType


# ============ Contest Schemas ============

class ContestBase(BaseModel):
    """竞赛基础 Schema"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    duration: int = Field(..., gt=0, description="持续时间（分钟）")
    contest_type: ContestType = ContestType.PUBLIC
    rule_type: RuleType = RuleType.ACM
    password: Optional[str] = Field(None, max_length=100)
    is_visible: bool = True
    real_time_rank: bool = True
    freeze_time: Optional[int] = Field(None, ge=0, description="封榜时间（分钟）")


class ContestCreate(ContestBase):
    """创建竞赛"""
    pass


class ContestUpdate(BaseModel):
    """更新竞赛"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[int] = Field(None, gt=0)
    contest_type: Optional[ContestType] = None
    rule_type: Optional[RuleType] = None
    password: Optional[str] = Field(None, max_length=100)
    is_visible: Optional[bool] = None
    real_time_rank: Optional[bool] = None
    freeze_time: Optional[int] = Field(None, ge=0)


class Contest(ContestBase):
    """竞赛详情"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_by: int
    participant_count: int
    submission_count: int
    status: ContestStatus
    is_frozen: bool
    created_at: datetime
    updated_at: datetime


class ContestList(BaseModel):
    """竞赛列表项"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    start_time: datetime
    end_time: datetime
    duration: int
    contest_type: ContestType
    rule_type: RuleType
    participant_count: int
    status: ContestStatus
    created_at: datetime


class ContestListResponse(BaseModel):
    """竞赛列表响应"""
    items: list[ContestList]
    total: int
    page: int
    page_size: int


# ============ ContestProblem Schemas ============

class ContestProblemBase(BaseModel):
    """竞赛题目基础 Schema"""
    problem_id: int
    display_id: str = Field(..., max_length=10, description="题目序号（A, B, C...）")
    score: int = Field(100, ge=0, description="题目分数")


class ContestProblemCreate(ContestProblemBase):
    """添加竞赛题目"""
    pass


class ContestProblem(ContestProblemBase):
    """竞赛题目详情"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    contest_id: int
    submission_count: int
    accepted_count: int
    created_at: datetime


class ContestProblemWithDetail(ContestProblem):
    """带题目详情的竞赛题目"""
    problem_title: str
    problem_difficulty: str


# ============ ContestParticipant Schemas ============

class ContestParticipantBase(BaseModel):
    """竞赛参与者基础 Schema"""
    pass


class ContestParticipantCreate(BaseModel):
    """报名参赛"""
    password: Optional[str] = None


class ContestParticipant(ContestParticipantBase):
    """竞赛参与者详情"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    contest_id: int
    user_id: int
    is_registered: bool
    total_score: int
    solved_count: int
    total_time: int
    submission_count: int
    registered_at: datetime
    last_submission_at: Optional[datetime]


class RankItem(BaseModel):
    """排行榜项"""
    rank: int
    user_id: int
    username: str
    total_score: int = 0  # OI 规则
    solved_count: int = 0  # ACM 规则
    total_time: int = 0  # 总用时/罚时（分钟）
    submission_count: int = 0
    last_submission_at: Optional[datetime] = None


class RankListResponse(BaseModel):
    """排行榜响应"""
    items: list[RankItem]
    total: int
    is_frozen: bool
