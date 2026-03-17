"""SQLAlchemy models"""

from app.core.database import Base

# Import all models here for Alembic to detect them
# 数据模型包

from app.models.user import User, UserRole
from app.models.problem import Problem, TestCase
from app.models.submission import Submission, SubmissionStatus, ProgrammingLanguage
from app.models.contest import Contest, ContestProblem, ContestParticipant
# from app.models.discussion import Discussion

__all__ = [
    "Base",
    "User",
    "UserRole",
    "Problem",
    "TestCase",
    "Submission",
    "SubmissionStatus",
    "ProgrammingLanguage",
]
