"""Problem model"""

from datetime import datetime
from enum import Enum
from typing import Optional, List

from sqlalchemy import String, Integer, Text, Enum as SQLEnum, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Difficulty(str, Enum):
    """题目难度枚举"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Problem(Base):
    """
    题目模型
    
    存储题目的基本信息、描述、限制条件等
    """
    __tablename__ = "problems"

    # 基础字段
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[Difficulty] = mapped_column(
        SQLEnum(Difficulty),
        nullable=False,
        default=Difficulty.EASY,
        index=True
    )
    
    # 输入输出格式
    input_format: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    output_format: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    constraints: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 限制条件
    time_limit: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1000,
        comment="时间限制（毫秒）"
    )
    memory_limit: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=256,
        comment="内存限制（MB）"
    )
    
    # 标签和分类
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True, default=list)
    source: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="题目来源，如 LeetCode, Codeforces 等"
    )
    
    # 统计信息
    submission_count: Mapped[int] = mapped_column(Integer, default=0)
    accepted_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # 状态
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        onupdate=datetime.utcnow,
        nullable=True
    )
    
    # 关联关系
    test_cases: Mapped[List["TestCase"]] = relationship(
        "TestCase",
        back_populates="problem",
        cascade="all, delete-orphan"
    )
    
    submissions: Mapped[List["Submission"]] = relationship(
        "Submission",
        back_populates="problem",
        cascade="all, delete-orphan"
    )
    
    @property
    def acceptance_rate(self) -> float:
        """计算通过率"""
        if self.submission_count == 0:
            return 0.0
        return round((self.accepted_count / self.submission_count) * 100, 2)
    
    def __repr__(self) -> str:
        return f"<Problem(id={self.id}, title='{self.title}', difficulty='{self.difficulty}')>"


class TestCase(Base):
    """
    测试用例模型
    
    存储题目的测试用例输入输出
    """
    __tablename__ = "test_cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    problem_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("problems.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="关联的题目 ID"
    )
    
    # 测试数据
    input: Mapped[str] = mapped_column(Text, nullable=False)
    output: Mapped[str] = mapped_column(Text, nullable=False)
    
    # 是否为样例（样例会显示给用户）
    is_sample: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # 分数权重（用于部分分）
    score: Mapped[int] = mapped_column(Integer, default=10)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    
    # 关联关系
    problem: Mapped["Problem"] = relationship("Problem", back_populates="test_cases")
    
    def __repr__(self) -> str:
        return f"<TestCase(id={self.id}, problem_id={self.problem_id}, is_sample={self.is_sample})>"
