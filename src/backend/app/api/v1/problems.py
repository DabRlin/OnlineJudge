"""Problem API routes"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User, UserRole
from app.services.problem_service import ProblemService
from app.schemas.problem import (
    ProblemCreate,
    ProblemUpdate,
    ProblemResponse,
    ProblemDetailResponse,
    ProblemListQuery,
    TestCaseCreate,
    TestCaseResponse,
)
from app.schemas.response import Response, PaginatedResponse

router = APIRouter()


@router.post("", response_model=ProblemResponse, status_code=status.HTTP_201_CREATED)
async def create_problem(
    problem_data: ProblemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    创建题目（仅管理员）
    
    需要管理员权限
    """
    # 检查权限
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以创建题目"
        )
    
    service = ProblemService(db)
    problem = await service.create_problem(problem_data)
    
    return problem


@router.get("", response_model=Response[PaginatedResponse[ProblemResponse]])
async def get_problems(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    difficulty: str = Query(None, description="难度筛选"),
    tags: List[str] = Query(None, description="标签筛选"),
    search: str = Query(None, description="搜索关键词"),
    sort_by: str = Query("id", description="排序字段"),
    order: str = Query("desc", description="排序方向"),
    db: AsyncSession = Depends(get_db),
):
    """
    获取题目列表
    
    支持分页、筛选、搜索和排序
    """
    query_params = ProblemListQuery(
        page=page,
        page_size=page_size,
        difficulty=difficulty,
        tags=tags,
        search=search,
        sort_by=sort_by,
        order=order,
    )
    
    service = ProblemService(db)
    problems, total = await service.get_problems(query_params, only_public=True)
    
    total_pages = (total + page_size - 1) // page_size
    
    return Response(
        code=0,
        message="success",
        data=PaginatedResponse(
            items=problems,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
    )


@router.get("/{problem_id}", response_model=ProblemDetailResponse)
async def get_problem(
    problem_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    获取题目详情
    
    包含样例测试用例
    """
    service = ProblemService(db)
    problem = await service.get_problem_by_id(problem_id, include_test_cases=False)
    
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题目不存在"
        )
    
    if not problem.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="该题目未公开"
        )
    
    # 只返回样例测试用例
    sample_test_cases = await service.get_sample_test_cases(problem_id)
    
    # 手动构建响应
    problem_dict = {
        "id": problem.id,
        "title": problem.title,
        "description": problem.description,
        "difficulty": problem.difficulty,
        "input_format": problem.input_format,
        "output_format": problem.output_format,
        "constraints": problem.constraints,
        "time_limit": problem.time_limit,
        "memory_limit": problem.memory_limit,
        "tags": problem.tags or [],
        "source": problem.source,
        "is_public": problem.is_public,
        "submission_count": problem.submission_count,
        "accepted_count": problem.accepted_count,
        "acceptance_rate": problem.acceptance_rate,
        "created_at": problem.created_at,
        "updated_at": problem.updated_at,
        "test_cases": sample_test_cases,
    }
    
    return problem_dict


@router.put("/{problem_id}", response_model=ProblemResponse)
async def update_problem(
    problem_id: int,
    problem_data: ProblemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    更新题目（仅管理员）
    
    需要管理员权限
    """
    # 检查权限
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以更新题目"
        )
    
    service = ProblemService(db)
    problem = await service.update_problem(problem_id, problem_data)
    
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题目不存在"
        )
    
    return problem


@router.delete("/{problem_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_problem(
    problem_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    删除题目（仅管理员）
    
    需要管理员权限
    """
    # 检查权限
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以删除题目"
        )
    
    service = ProblemService(db)
    success = await service.delete_problem(problem_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题目不存在"
        )


@router.post("/{problem_id}/test-cases", response_model=TestCaseResponse)
async def add_test_case(
    problem_id: int,
    test_case_data: TestCaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    添加测试用例（仅管理员）
    
    需要管理员权限
    """
    # 检查权限
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以添加测试用例"
        )
    
    service = ProblemService(db)
    test_case = await service.add_test_case(problem_id, test_case_data)
    
    if not test_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题目不存在"
        )
    
    return test_case


@router.put("/{problem_id}/test-cases/{test_case_id}", response_model=TestCaseResponse)
async def update_test_case(
    problem_id: int,
    test_case_id: int,
    test_case_data: TestCaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    更新测试用例（仅管理员）
    
    需要管理员权限
    """
    # 检查权限
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以更新测试用例"
        )
    
    service = ProblemService(db)
    test_case = await service.update_test_case(test_case_id, test_case_data)
    
    if not test_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="测试用例不存在"
        )
    
    return test_case


@router.delete("/{problem_id}/test-cases/{test_case_id}")
async def delete_test_case(
    problem_id: int,
    test_case_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    删除测试用例（仅管理员）
    
    需要管理员权限
    """
    # 检查权限
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以删除测试用例"
        )
    
    service = ProblemService(db)
    success = await service.delete_test_case(test_case_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="测试用例不存在"
        )
    
    return {"message": "测试用例删除成功"}


# ============ 批量导入 ============

class ImportProblemTestCase(BaseModel):
    input: str
    output: str
    is_sample: bool = False
    score: int = 10


class ImportProblemItem(BaseModel):
    title: str
    description: str
    difficulty: str = "easy"
    input_format: str = ""
    output_format: str = ""
    constraints: str = ""
    time_limit: int = 1000
    memory_limit: int = 256
    tags: List[str] = []
    source: str = ""
    is_public: bool = True
    test_cases: List[ImportProblemTestCase] = []


class ImportProblemsRequest(BaseModel):
    problems: List[ImportProblemItem]
    skip_existing: bool = True  # 遇到同名题目时跳过


@router.post("/import", response_model=Dict[str, Any])
async def import_problems(
    data: ImportProblemsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    批量导入题目（仅管理员）
    
    支持 JSON 格式批量导入，返回导入统计信息
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以导入题目"
        )

    from app.models.problem import Difficulty as DifficultyEnum
    from sqlalchemy import select
    from app.models.problem import Problem, TestCase

    created = []
    skipped = []
    failed = []

    for item in data.problems:
        try:
            # 检查同名题目
            if data.skip_existing:
                stmt = select(Problem).where(Problem.title == item.title)
                result = await db.execute(stmt)
                existing = result.scalar_one_or_none()
                if existing:
                    skipped.append(item.title)
                    continue

            # 映射难度
            diff_map = {"easy": DifficultyEnum.EASY, "medium": DifficultyEnum.MEDIUM, "hard": DifficultyEnum.HARD}
            difficulty = diff_map.get(item.difficulty.lower(), DifficultyEnum.EASY)

            problem = Problem(
                title=item.title,
                description=item.description,
                difficulty=difficulty,
                input_format=item.input_format or None,
                output_format=item.output_format or None,
                constraints=item.constraints or None,
                time_limit=item.time_limit,
                memory_limit=item.memory_limit,
                tags=item.tags,
                source=item.source or None,
                is_public=item.is_public,
            )
            db.add(problem)
            await db.flush()

            for tc in item.test_cases:
                test_case = TestCase(
                    problem_id=problem.id,
                    input=tc.input,
                    output=tc.output,
                    is_sample=tc.is_sample,
                    score=tc.score,
                )
                db.add(test_case)

            created.append(item.title)
        except Exception as e:
            failed.append({"title": item.title, "error": str(e)})

    await db.commit()

    return {
        "total": len(data.problems),
        "created": len(created),
        "skipped": len(skipped),
        "failed": len(failed),
        "created_titles": created,
        "skipped_titles": skipped,
        "failed_details": failed,
    }
