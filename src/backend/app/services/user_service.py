"""用户服务层"""

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


class UserService:
    """用户服务类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_user(self, user_data: UserCreate) -> User:
        """
        创建新用户
        
        Args:
            user_data: 用户创建数据
            
        Returns:
            创建的用户对象
            
        Raises:
            HTTPException: 用户名或邮箱已存在
        """
        # 检查用户名是否存在
        stmt = select(User).where(User.username == user_data.username)
        result = await self.db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        # 检查邮箱是否存在
        stmt = select(User).where(User.email == user_data.email)
        result = await self.db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        
        # 创建用户
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        根据 ID 获取用户
        
        Args:
            user_id: 用户 ID
            
        Returns:
            用户对象或 None
        """
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_user_by_username(self, username: str) -> User | None:
        """
        根据用户名获取用户
        
        Args:
            username: 用户名
            
        Returns:
            用户对象或 None
        """
        stmt = select(User).where(User.username == username)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> User | None:
        """
        根据邮箱获取用户
        
        Args:
            email: 邮箱地址
            
        Returns:
            用户对象或 None
        """
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_user_by_username_or_email(self, identifier: str) -> User | None:
        """
        根据用户名或邮箱获取用户
        
        Args:
            identifier: 用户名或邮箱
            
        Returns:
            用户对象或 None
        """
        stmt = select(User).where(
            or_(User.username == identifier, User.email == identifier)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def authenticate_user(self, username: str, password: str) -> User | None:
        """
        验证用户凭证
        
        Args:
            username: 用户名或邮箱
            password: 密码
            
        Returns:
            验证成功返回用户对象，否则返回 None
        """
        user = await self.get_user_by_username_or_email(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user
    
    async def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """
        更新用户信息
        
        Args:
            user_id: 用户 ID
            user_data: 用户更新数据
            
        Returns:
            更新后的用户对象
            
        Raises:
            HTTPException: 用户不存在或用户名/邮箱已被占用
        """
        # 获取用户
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # 检查用户名是否被占用
        if user_data.username and user_data.username != user.username:
            stmt = select(User).where(User.username == user_data.username)
            result = await self.db.execute(stmt)
            if result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already exists"
                )
            user.username = user_data.username
        
        # 检查邮箱是否被占用
        if user_data.email and user_data.email != user.email:
            stmt = select(User).where(User.email == user_data.email)
            result = await self.db.execute(stmt)
            if result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists"
                )
            user.email = user_data.email
        
        # 更新头像
        if user_data.avatar is not None:
            user.avatar = user_data.avatar
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def update_password(
        self, 
        user_id: int, 
        old_password: str, 
        new_password: str
    ) -> User:
        """
        更新用户密码
        
        Args:
            user_id: 用户 ID
            old_password: 旧密码
            new_password: 新密码
            
        Returns:
            更新后的用户对象
            
        Raises:
            HTTPException: 用户不存在或旧密码错误
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # 验证旧密码
        if not verify_password(old_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect password"
            )
        
        # 更新密码
        user.hashed_password = get_password_hash(new_password)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
