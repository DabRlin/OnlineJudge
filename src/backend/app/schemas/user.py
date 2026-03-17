"""用户相关的 Pydantic Schema"""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.models.user import UserRole


class UserBase(BaseModel):
    """用户基础模式"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")


class UserCreate(UserBase):
    """用户创建模式"""
    password: str = Field(..., min_length=8, max_length=100, description="密码")


class UserUpdate(BaseModel):
    """用户更新模式"""
    username: str | None = Field(None, min_length=3, max_length=50, description="用户名")
    email: EmailStr | None = Field(None, description="邮箱地址")
    avatar: str | None = Field(None, max_length=255, description="头像 URL")


class UserPasswordUpdate(BaseModel):
    """用户密码更新模式"""
    old_password: str = Field(..., min_length=8, max_length=100, description="旧密码")
    new_password: str = Field(..., min_length=8, max_length=100, description="新密码")


class UserResponse(UserBase):
    """用户响应模式"""
    id: int
    role: UserRole
    is_active: bool
    avatar: str | None = None
    created_at: datetime
    updated_at: datetime | None = None
    
    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """用户登录模式"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")


class Token(BaseModel):
    """Token 响应模式"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token 数据模式"""
    user_id: int | None = None
