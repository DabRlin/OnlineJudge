"""Main API v1 router"""

from fastapi import APIRouter

from app.api.v1 import auth, problems, submissions, contests
from app.schemas.response import StandardResponse

api_router = APIRouter()

# Include sub-routers
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(problems.router, prefix="/problems", tags=["题目"])
api_router.include_router(submissions.router, prefix="/submissions", tags=["提交"])
api_router.include_router(contests.router, prefix="/contests", tags=["竞赛"])


@api_router.get("/health", response_model=StandardResponse)
async def health_check() -> StandardResponse:
    """
    健康检查接口
    
    Returns:
        系统状态信息
    """
    return StandardResponse(
        code=0,
        message="success",
        data={"status": "healthy", "version": "0.1.0"}
    )
