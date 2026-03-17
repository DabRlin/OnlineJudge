"""
提交记录数据模型
"""

from datetime import datetime
from typing import Optional
from enum import Enum as PyEnum

from sqlalchemy import String, Integer, Text, Enum as SQLEnum, DateTime, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class SubmissionStatus(str, PyEnum):
    """提交状态枚举"""
    PENDING = "pending"  # 等待判题
    JUDGING = "judging"  # 判题中
    ACCEPTED = "accepted"  # 通过 (AC)
    WRONG_ANSWER = "wrong_answer"  # 答案错误 (WA)
    TIME_LIMIT_EXCEEDED = "time_limit_exceeded"  # 超时 (TLE)
    MEMORY_LIMIT_EXCEEDED = "memory_limit_exceeded"  # 内存超限 (MLE)
    RUNTIME_ERROR = "runtime_error"  # 运行错误 (RE)
    COMPILE_ERROR = "compile_error"  # 编译错误 (CE)
    SYSTEM_ERROR = "system_error"  # 系统错误 (SE)


class ProgrammingLanguage(str, PyEnum):
    """编程语言枚举"""
    PYTHON = "python"
    CPP = "cpp"
    JAVA = "java"
    C = "c"
    JAVASCRIPT = "javascript"
    GO = "go"


class Submission(Base):
    """
    提交记录模型
    
    存储用户的代码提交记录和判题结果
    """
    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        comment="提交 ID"
    )
    
    # 关联信息
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="用户 ID"
    )
    
    problem_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("problems.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="题目 ID"
    )
    
    # 代码信息
    language: Mapped[ProgrammingLanguage] = mapped_column(
        SQLEnum(ProgrammingLanguage),
        nullable=False,
        comment="编程语言"
    )
    
    code: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="提交的代码"
    )
    
    # 判题状态
    status: Mapped[SubmissionStatus] = mapped_column(
        SQLEnum(SubmissionStatus),
        nullable=False,
        default=SubmissionStatus.PENDING,
        index=True,
        comment="判题状态"
    )
    
    # 判题结果
    score: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="得分（0-100）"
    )
    
    time_used: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="运行时间（毫秒）"
    )
    
    memory_used: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="内存使用（KB）"
    )
    
    # 错误信息
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="错误信息（编译错误、运行错误等）"
    )
    
    # 测试用例通过情况（JSON 格式存储）
    test_cases_result: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="测试用例结果（JSON 格式）"
    )
    
    # 时间戳
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        comment="提交时间"
    )
    
    judged_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="判题完成时间"
    )
    
    # 关系
    user: Mapped["User"] = relationship("User", back_populates="submissions")
    problem: Mapped["Problem"] = relationship("Problem", back_populates="submissions")

    def __repr__(self) -> str:
        return f"<Submission(id={self.id}, user_id={self.user_id}, problem_id={self.problem_id}, status={self.status})>"
