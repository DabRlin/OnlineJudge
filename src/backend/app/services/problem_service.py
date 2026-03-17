"""Problem service layer"""

from typing import Optional, List, Tuple
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.problem import Problem, TestCase
from app.schemas.problem import (
    ProblemCreate,
    ProblemUpdate,
    TestCaseCreate,
    ProblemListQuery,
)


class ProblemService:
    """题目服务层"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_problem(self, problem_data: ProblemCreate) -> Problem:
        """
        创建题目
        
        Args:
            problem_data: 题目创建数据
            
        Returns:
            创建的题目对象
        """
        # 创建题目
        problem = Problem(
            title=problem_data.title,
            description=problem_data.description,
            difficulty=problem_data.difficulty,
            input_format=problem_data.input_format,
            output_format=problem_data.output_format,
            constraints=problem_data.constraints,
            time_limit=problem_data.time_limit,
            memory_limit=problem_data.memory_limit,
            tags=problem_data.tags,
            source=problem_data.source,
            is_public=problem_data.is_public,
        )
        
        self.db.add(problem)
        await self.db.flush()
        
        # 创建测试用例
        for tc_data in problem_data.test_cases:
            test_case = TestCase(
                problem_id=problem.id,
                input=tc_data.input,
                output=tc_data.output,
                is_sample=tc_data.is_sample,
                score=tc_data.score,
            )
            self.db.add(test_case)
        
        await self.db.commit()
        await self.db.refresh(problem)
        
        return problem

    async def get_problem_by_id(
        self,
        problem_id: int,
        include_test_cases: bool = False
    ) -> Optional[Problem]:
        """
        根据 ID 获取题目
        
        Args:
            problem_id: 题目 ID
            include_test_cases: 是否包含测试用例
            
        Returns:
            题目对象或 None
        """
        query = select(Problem).where(Problem.id == problem_id)
        
        if include_test_cases:
            query = query.options(selectinload(Problem.test_cases))
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_problems(
        self,
        query_params: ProblemListQuery,
        only_public: bool = True
    ) -> Tuple[List[Problem], int]:
        """
        获取题目列表（分页）
        
        Args:
            query_params: 查询参数
            only_public: 是否只返回公开题目
            
        Returns:
            (题目列表, 总数)
        """
        # 构建基础查询
        query = select(Problem)
        count_query = select(func.count(Problem.id))
        
        # 只显示公开题目
        if only_public:
            query = query.where(Problem.is_public.is_(True))
            count_query = count_query.where(Problem.is_public.is_(True))
        
        # 难度筛选
        if query_params.difficulty:
            query = query.where(Problem.difficulty == query_params.difficulty)
            count_query = count_query.where(Problem.difficulty == query_params.difficulty)
        
        # 标签筛选
        if query_params.tags:
            for tag in query_params.tags:
                query = query.where(Problem.tags.contains([tag]))
                count_query = count_query.where(Problem.tags.contains([tag]))
        
        # 搜索
        if query_params.search:
            search_pattern = f"%{query_params.search}%"
            query = query.where(
                or_(
                    Problem.title.ilike(search_pattern),
                    Problem.description.ilike(search_pattern)
                )
            )
            count_query = count_query.where(
                or_(
                    Problem.title.ilike(search_pattern),
                    Problem.description.ilike(search_pattern)
                )
            )
        
        # 获取总数
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # 排序
        sort_column = getattr(Problem, query_params.sort_by, Problem.id)
        if query_params.order == 'desc':
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # 分页
        offset = (query_params.page - 1) * query_params.page_size
        query = query.offset(offset).limit(query_params.page_size)
        
        # 执行查询
        result = await self.db.execute(query)
        problems = list(result.scalars().all())
        
        return problems, total

    async def update_problem(
        self,
        problem_id: int,
        problem_data: ProblemUpdate
    ) -> Optional[Problem]:
        """
        更新题目
        
        Args:
            problem_id: 题目 ID
            problem_data: 更新数据
            
        Returns:
            更新后的题目对象或 None
        """
        problem = await self.get_problem_by_id(problem_id)
        if not problem:
            return None
        
        # 更新字段
        update_data = problem_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(problem, field, value)
        
        await self.db.commit()
        await self.db.refresh(problem)
        
        return problem

    async def delete_problem(self, problem_id: int) -> bool:
        """
        删除题目
        
        Args:
            problem_id: 题目 ID
            
        Returns:
            是否删除成功
        """
        problem = await self.get_problem_by_id(problem_id)
        if not problem:
            return False
        
        await self.db.delete(problem)
        await self.db.commit()
        
        return True

    async def add_test_case(
        self,
        problem_id: int,
        test_case_data: TestCaseCreate
    ) -> Optional[TestCase]:
        """
        添加测试用例
        
        Args:
            problem_id: 题目 ID
            test_case_data: 测试用例数据
            
        Returns:
            创建的测试用例或 None
        """
        # 检查题目是否存在
        problem = await self.get_problem_by_id(problem_id)
        if not problem:
            return None
        
        test_case = TestCase(
            problem_id=problem_id,
            **test_case_data.model_dump()
        )
        self.db.add(test_case)
        await self.db.commit()
        await self.db.refresh(test_case)
        
        return test_case

    async def get_sample_test_cases(self, problem_id: int) -> List[TestCase]:
        """
        获取样例测试用例
        
        Args:
            problem_id: 题目 ID
            
        Returns:
            样例测试用例列表
        """
        query = select(TestCase).where(
            TestCase.problem_id == problem_id,
            TestCase.is_sample.is_(True)
        )
        
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def increment_submission_count(self, problem_id: int) -> None:
        """
        增加提交次数
        
        Args:
            problem_id: 题目 ID
        """
        problem = await self.get_problem_by_id(problem_id)
        if problem:
            problem.submission_count += 1
            await self.db.commit()

    async def increment_accepted_count(self, problem_id: int) -> None:
        """
        增加通过次数
        
        Args:
            problem_id: 题目 ID
        """
        problem = await self.get_problem_by_id(problem_id)
        if problem:
            problem.accepted_count += 1
            await self.db.commit()
    
    async def update_test_case(
        self,
        test_case_id: int,
        test_case_data: TestCaseCreate
    ) -> Optional[TestCase]:
        """
        更新测试用例
        
        Args:
            test_case_id: 测试用例 ID
            test_case_data: 测试用例数据
            
        Returns:
            更新后的测试用例或 None
        """
        stmt = select(TestCase).where(TestCase.id == test_case_id)
        result = await self.db.execute(stmt)
        test_case = result.scalar_one_or_none()
        
        if not test_case:
            return None
        
        # 更新字段
        for key, value in test_case_data.model_dump().items():
            setattr(test_case, key, value)
        
        await self.db.commit()
        await self.db.refresh(test_case)
        
        return test_case
    
    async def delete_test_case(self, test_case_id: int) -> bool:
        """
        删除测试用例
        
        Args:
            test_case_id: 测试用例 ID
            
        Returns:
            是否删除成功
        """
        stmt = select(TestCase).where(TestCase.id == test_case_id)
        result = await self.db.execute(stmt)
        test_case = result.scalar_one_or_none()
        
        if not test_case:
            return False
        
        await self.db.delete(test_case)
        await self.db.commit()
        
        return True
