"""用户模型"""

from datetime import datetime
from sqlalchemy import String, Boolean, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class UserRole(str, enum.Enum):
    """用户角色枚举"""
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class User(Base):
    """用户模型
    
    Attributes:
        id: 用户唯一标识
        username: 用户名
        email: 邮箱地址
        hashed_password: 哈希后的密码
        role: 用户角色
        is_active: 是否激活
        avatar: 头像 URL
        created_at: 创建时间
        updated_at: 更新时间
    """
    __tablename__ = "users"
    
    # 主键
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # 基础字段
    username: Mapped[str] = mapped_column(
        String(50), 
        unique=True, 
        nullable=False, 
        index=True,
        comment="用户名"
    )
    email: Mapped[str] = mapped_column(
        String(100), 
        unique=True, 
        nullable=False, 
        index=True,
        comment="邮箱地址"
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255), 
        nullable=False,
        comment="哈希后的密码"
    )
    
    # 角色和状态
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole),
        default=UserRole.USER,
        nullable=False,
        comment="用户角色"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否激活"
    )
    
    # 可选字段
    avatar: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="头像 URL"
    )
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False,
        comment="创建时间"
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        onupdate=func.now(),
        nullable=True,
        comment="更新时间"
    )
    
    # 关系
    submissions: Mapped[list["Submission"]] = relationship(
        "Submission",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
