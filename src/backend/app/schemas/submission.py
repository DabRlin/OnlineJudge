"""
提交记录相关的 Pydantic Schema
"""

from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, ConfigDict

from app.models.submission import SubmissionStatus, ProgrammingLanguage


# ==================== 基础 Schema ====================

class SubmissionBase(BaseModel):
    """提交基础 Schema"""
    problem_id: int = Field(..., description="题目 ID")
    language: ProgrammingLanguage = Field(..., description="编程语言")
    code: str = Field(..., min_length=1, description="提交的代码")


class SubmissionCreate(SubmissionBase):
    """创建提交 Schema"""
    pass


class SubmissionUpdate(BaseModel):
    """更新提交 Schema（用于判题结果更新）"""
    status: Optional[SubmissionStatus] = None
    score: Optional[int] = Field(None, ge=0, le=100, description="得分")
    time_used: Optional[int] = Field(None, ge=0, description="运行时间（毫秒）")
    memory_used: Optional[int] = Field(None, ge=0, description="内存使用（KB）")
    error_message: Optional[str] = None
    test_cases_result: Optional[str] = None


# ==================== 响应 Schema ====================

class SubmissionResponse(SubmissionBase):
    """提交响应 Schema"""
    id: int
    user_id: int
    status: SubmissionStatus
    score: Optional[int] = None
    time_used: Optional[int] = None
    memory_used: Optional[int] = None
    error_message: Optional[str] = None
    submitted_at: datetime
    judged_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class SubmissionDetail(SubmissionResponse):
    """提交详情 Schema（包含测试用例结果）"""
    test_cases_result: Optional[str] = None
    
    # 关联信息
    user_username: Optional[str] = Field(None, description="用户名")
    problem_title: Optional[str] = Field(None, description="题目标题")
    
    model_config = ConfigDict(from_attributes=True)


class SubmissionListItem(BaseModel):
    """提交列表项 Schema"""
    id: int
    user_id: int
    user_username: str
    problem_id: int
    problem_title: str
    language: ProgrammingLanguage
    status: SubmissionStatus
    score: Optional[int] = None
    time_used: Optional[int] = None
    memory_used: Optional[int] = None
    submitted_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ==================== 查询参数 Schema ====================

class SubmissionListParams(BaseModel):
    """提交列表查询参数"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")
    user_id: Optional[int] = Field(None, description="用户 ID 筛选")
    problem_id: Optional[int] = Field(None, description="题目 ID 筛选")
    language: Optional[ProgrammingLanguage] = Field(None, description="语言筛选")
    status: Optional[SubmissionStatus] = Field(None, description="状态筛选")


# ==================== 判题结果 Schema ====================

class TestCaseResult(BaseModel):
    """单个测试用例结果"""
    test_case_id: int
    status: SubmissionStatus
    time_used: Optional[int] = None  # 毫秒
    memory_used: Optional[int] = None  # KB
    error_message: Optional[str] = None


class JudgeResult(BaseModel):
    """判题结果 Schema"""
    submission_id: int
    status: SubmissionStatus
    score: int = Field(ge=0, le=100)
    time_used: int = Field(ge=0, description="总运行时间（毫秒）")
    memory_used: int = Field(ge=0, description="总内存使用（KB）")
    error_message: Optional[str] = None
    test_cases_results: List[TestCaseResult] = Field(default_factory=list)


# ==================== 统计 Schema ====================

class SubmissionStatistics(BaseModel):
    """提交统计 Schema"""
    total_submissions: int
    accepted_submissions: int
    acceptance_rate: float
    language_distribution: Dict[str, int]
    status_distribution: Dict[str, int]
