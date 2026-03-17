"""
竞赛数据模型
"""

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, Text, DateTime, Integer, Boolean, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.problem import Problem


class ContestType(str, enum.Enum):
    """竞赛类型"""
    PUBLIC = "public"      # 公开竞赛
    PRIVATE = "private"    # 私有竞赛（需要密码）


class ContestStatus(str, enum.Enum):
    """竞赛状态"""
    NOT_STARTED = "not_started"  # 未开始
    RUNNING = "running"          # 进行中
    ENDED = "ended"              # 已结束


class RuleType(str, enum.Enum):
    """计分规则"""
    ACM = "acm"    # ACM 规则：通过题数 + 罚时
    OI = "oi"      # OI 规则：总分


class Contest(Base):
    """竞赛模型"""
    __tablename__ = "contests"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 时间相关
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)  # 持续时间（分钟）
    
    # 竞赛类型和规则
    contest_type: Mapped[ContestType] = mapped_column(
        SQLEnum(ContestType),
        default=ContestType.PUBLIC,
        nullable=False
    )
    rule_type: Mapped[RuleType] = mapped_column(
        SQLEnum(RuleType),
        default=RuleType.ACM,
        nullable=False
    )
    
    # 访问控制
    password: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # 排行榜设置
    real_time_rank: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)  # 实时排名
    freeze_time: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 封榜时间（分钟，从结束倒数）
    
    # 统计信息
    participant_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    submission_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # 创建者
    created_by: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # 关系
    problems: Mapped[list["ContestProblem"]] = relationship(
        "ContestProblem",
        back_populates="contest",
        cascade="all, delete-orphan"
    )
    participants: Mapped[list["ContestParticipant"]] = relationship(
        "ContestParticipant",
        back_populates="contest",
        cascade="all, delete-orphan"
    )

    @property
    def status(self) -> ContestStatus:
        """获取竞赛状态"""
        now = datetime.utcnow()
        if now < self.start_time:
            return ContestStatus.NOT_STARTED
        elif now > self.end_time:
            return ContestStatus.ENDED
        else:
            return ContestStatus.RUNNING

    @property
    def is_frozen(self) -> bool:
        """是否处于封榜状态"""
        if not self.freeze_time or self.status != ContestStatus.RUNNING:
            return False
        
        now = datetime.utcnow()
        freeze_start = self.end_time - timedelta(minutes=self.freeze_time)
        return now >= freeze_start

    def __repr__(self) -> str:
        return f"<Contest {self.id}: {self.title}>"


class ContestProblem(Base):
    """竞赛题目关联表"""
    __tablename__ = "contest_problems"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    contest_id: Mapped[int] = mapped_column(Integer, ForeignKey("contests.id"), nullable=False, index=True)
    problem_id: Mapped[int] = mapped_column(Integer, ForeignKey("problems.id"), nullable=False, index=True)
    
    # 题目在竞赛中的序号（A, B, C...）
    display_id: Mapped[str] = mapped_column(String(10), nullable=False)
    
    # 题目分数（OI 规则使用）
    score: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    
    # 统计信息
    submission_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    accepted_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    contest: Mapped["Contest"] = relationship("Contest", back_populates="problems")
    problem: Mapped["Problem"] = relationship("Problem")

    def __repr__(self) -> str:
        return f"<ContestProblem contest={self.contest_id} problem={self.problem_id}>"


class ContestParticipant(Base):
    """竞赛参与者"""
    __tablename__ = "contest_participants"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    contest_id: Mapped[int] = mapped_column(Integer, ForeignKey("contests.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 参赛状态
    is_registered: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # 统计信息（缓存，用于排行榜）
    total_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 总分（OI）
    solved_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 通过题数（ACM）
    total_time: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 总用时/罚时（分钟）
    submission_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # 时间戳
    registered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_submission_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # 关系
    contest: Mapped["Contest"] = relationship("Contest", back_populates="participants")
    user: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:
        return f"<ContestParticipant contest={self.contest_id} user={self.user_id}>"
