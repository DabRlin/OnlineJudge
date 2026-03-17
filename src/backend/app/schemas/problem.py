"""Problem schemas"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

from app.models.problem import Difficulty


class TestCaseBase(BaseModel):
    """测试用例基础 Schema"""
    input: str = Field(..., description="测试输入")
    output: str = Field(..., description="预期输出")
    is_sample: bool = Field(default=False, description="是否为样例")
    score: int = Field(default=10, ge=0, le=100, description="分数权重")


class TestCaseCreate(TestCaseBase):
    """创建测试用例 Schema"""
    pass


class TestCaseUpdate(BaseModel):
    """更新测试用例 Schema"""
    input: Optional[str] = None
    output: Optional[str] = None
    is_sample: Optional[bool] = None
    score: Optional[int] = Field(None, ge=0, le=100)


class TestCaseResponse(TestCaseBase):
    """测试用例响应 Schema"""
    id: int
    problem_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ProblemBase(BaseModel):
    """题目基础 Schema"""
    title: str = Field(..., min_length=1, max_length=200, description="题目标题")
    description: str = Field(..., min_length=1, description="题目描述")
    difficulty: Difficulty = Field(default=Difficulty.EASY, description="难度")
    input_format: Optional[str] = Field(None, description="输入格式说明")
    output_format: Optional[str] = Field(None, description="输出格式说明")
    constraints: Optional[str] = Field(None, description="数据范围和约束")
    time_limit: int = Field(default=1000, ge=100, le=10000, description="时间限制（毫秒）")
    memory_limit: int = Field(default=256, ge=16, le=1024, description="内存限制（MB）")
    tags: List[str] = Field(default_factory=list, description="标签列表")
    source: Optional[str] = Field(None, max_length=100, description="题目来源")
    is_public: bool = Field(default=True, description="是否公开")


class ProblemCreate(ProblemBase):
    """创建题目 Schema"""
    test_cases: List[TestCaseCreate] = Field(
        default_factory=list,
        description="测试用例列表"
    )

    @field_validator('test_cases')
    @classmethod
    def validate_test_cases(cls, v: List[TestCaseCreate]) -> List[TestCaseCreate]:
        """验证至少有一个样例"""
        if not v:
            raise ValueError("至少需要一个测试用例")
        
        # 检查是否至少有一个样例
        has_sample = any(tc.is_sample for tc in v)
        if not has_sample:
            raise ValueError("至少需要一个样例测试用例")
        
        return v


class ProblemUpdate(BaseModel):
    """更新题目 Schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    difficulty: Optional[Difficulty] = None
    input_format: Optional[str] = None
    output_format: Optional[str] = None
    constraints: Optional[str] = None
    time_limit: Optional[int] = Field(None, ge=100, le=10000)
    memory_limit: Optional[int] = Field(None, ge=16, le=1024)
    tags: Optional[List[str]] = None
    source: Optional[str] = Field(None, max_length=100)
    is_public: Optional[bool] = None


class ProblemResponse(ProblemBase):
    """题目响应 Schema"""
    id: int
    submission_count: int
    accepted_count: int
    acceptance_rate: float
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ProblemDetailResponse(ProblemResponse):
    """题目详情响应 Schema（包含测试用例）"""
    test_cases: List[TestCaseResponse]

    class Config:
        from_attributes = True


class ProblemListQuery(BaseModel):
    """题目列表查询参数"""
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")
    difficulty: Optional[Difficulty] = Field(None, description="难度筛选")
    tags: Optional[List[str]] = Field(None, description="标签筛选")
    search: Optional[str] = Field(None, description="搜索关键词")
    sort_by: str = Field(default="id", description="排序字段")
    order: str = Field(default="desc", description="排序方向 (asc/desc)")

    @field_validator('sort_by')
    @classmethod
    def validate_sort_by(cls, v: str) -> str:
        """验证排序字段"""
        allowed_fields = ['id', 'title', 'difficulty', 'acceptance_rate', 'created_at']
        if v not in allowed_fields:
            raise ValueError(f"排序字段必须是以下之一: {', '.join(allowed_fields)}")
        return v

    @field_validator('order')
    @classmethod
    def validate_order(cls, v: str) -> str:
        """验证排序方向"""
        if v.lower() not in ['asc', 'desc']:
            raise ValueError("排序方向必须是 'asc' 或 'desc'")
        return v.lower()
