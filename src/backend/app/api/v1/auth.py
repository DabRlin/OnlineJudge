"""认证相关 API 路由"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user
from app.core.security import create_access_token
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserUpdate,
    UserPasswordUpdate,
    Token,
)
from app.services.user_service import UserService

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="用户注册",
    description="创建一个新用户账号"
)
async def register(
    user_data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    """
    用户注册
    
    Args:
        user_data: 用户注册数据（用户名、邮箱、密码）
        db: 数据库会话
        
    Returns:
        创建的用户信息
        
    Raises:
        HTTPException: 用户名或邮箱已存在
    """
    service = UserService(db)
    user = await service.create_user(user_data)
    return user


@router.post(
    "/login",
    response_model=Token,
    summary="用户登录",
    description="使用用户名/邮箱和密码登录"
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
    """
    用户登录
    
    Args:
        form_data: OAuth2 密码表单（username 可以是用户名或邮箱）
        db: 数据库会话
        
    Returns:
        访问令牌
        
    Raises:
        HTTPException: 用户名/邮箱或密码错误
    """
    service = UserService(db)
    user = await service.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建访问令牌
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return Token(access_token=access_token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="获取当前用户信息",
    description="获取当前登录用户的详细信息"
)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    """
    获取当前用户信息
    
    Args:
        current_user: 当前登录用户
        
    Returns:
        用户详细信息
    """
    return current_user


@router.put(
    "/me",
    response_model=UserResponse,
    summary="更新当前用户信息",
    description="更新当前登录用户的个人信息"
)
async def update_current_user(
    user_data: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    """
    更新当前用户信息
    
    Args:
        user_data: 用户更新数据
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        更新后的用户信息
        
    Raises:
        HTTPException: 用户名或邮箱已被占用
    """
    service = UserService(db)
    user = await service.update_user(current_user.id, user_data)
    return user


@router.post(
    "/me/password",
    response_model=UserResponse,
    summary="修改密码",
    description="修改当前登录用户的密码"
)
async def change_password(
    password_data: UserPasswordUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    """
    修改密码
    
    Args:
        password_data: 密码更新数据（旧密码、新密码）
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        更新后的用户信息
        
    Raises:
        HTTPException: 旧密码错误
    """
    service = UserService(db)
    user = await service.update_password(
        current_user.id,
        password_data.old_password,
        password_data.new_password
    )
    return user
