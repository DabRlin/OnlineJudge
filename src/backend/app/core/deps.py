"""FastAPI dependencies for dependency injection"""

from typing import Any, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_access_token

# HTTP Bearer token security
security = HTTPBearer()
# Optional: 无 token 时返回 None 而非 401
optional_security = HTTPBearer(auto_error=False)


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> int:
    """
    Get current user ID from JWT token
    
    Args:
        credentials: HTTP Bearer credentials
        
    Returns:
        User ID
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: Optional[int] = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return int(user_id)


async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get current user from database
    
    Args:
        user_id: Current user ID
        db: Database session
        
    Returns:
        User model instance
        
    Raises:
        HTTPException: If user not found
    """
    from app.models.user import User
    from sqlalchemy import select
    
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security),
    db: AsyncSession = Depends(get_db),
) -> Optional[Any]:
    """
    Get current user if authenticated, otherwise return None
    """
    if not credentials:
        return None
    
    from app.models.user import User
    from sqlalchemy import select
    
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        return None
    
    user_id = payload.get("sub")
    if user_id is None:
        return None
    
    stmt = select(User).where(User.id == int(user_id))
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_current_active_user(
    current_user: Any = Depends(get_current_user),
) -> Any:
    """
    Get current active user
    
    Args:
        current_user: Current user
        
    Returns:
        Active user
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="账号已被禁用")
    return current_user


async def get_current_admin_user(
    current_user: Any = Depends(get_current_user),
) -> Any:
    """
    Get current admin user
    
    Args:
        current_user: Current user
        
    Returns:
        Admin user
        
    Raises:
        HTTPException: If user is not admin
    """
    from app.models.user import UserRole
    
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return current_user
