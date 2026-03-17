"""
Celery 判题任务
"""

import sys
import os
import json
import sqlite3
from typing import Dict, List
from datetime import datetime

# 添加后端路径到 sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

from celery import Task
from judger.celery_app import celery_app
from judger.docker_judger import DockerJudger, JudgeResult
from judger.languages import Language


def _update_submission_in_db(submission_id: int, result_dict: dict):
    """直接用 sqlite3 写回判题结果（避免 asyncio 复杂性）"""
    db_path = os.path.join(backend_path, 'oj.db')
    
    status_map = {
        JudgeResult.ACCEPTED: 'ACCEPTED',
        JudgeResult.WRONG_ANSWER: 'WRONG_ANSWER',
        JudgeResult.TIME_LIMIT_EXCEEDED: 'TIME_LIMIT_EXCEEDED',
        JudgeResult.MEMORY_LIMIT_EXCEEDED: 'MEMORY_LIMIT_EXCEEDED',
        JudgeResult.RUNTIME_ERROR: 'RUNTIME_ERROR',
        JudgeResult.COMPILE_ERROR: 'COMPILE_ERROR',
        JudgeResult.SYSTEM_ERROR: 'SYSTEM_ERROR',
    }
    
    status = status_map.get(result_dict.get('status'), 'SYSTEM_ERROR')
    score = result_dict.get('score', 0)
    time_used = result_dict.get('time_used', 0)
    memory_used = result_dict.get('memory_used', 0)
    error_message = result_dict.get('error_message', '')
    test_cases_result = json.dumps(result_dict.get('test_cases_result', []))
    judged_at = datetime.utcnow().isoformat()
    
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """UPDATE submissions 
               SET status=?, score=?, time_used=?, memory_used=?,
                   error_message=?, test_cases_result=?, judged_at=?
               WHERE id=?""",
            (status, score, time_used, memory_used,
             error_message, test_cases_result, judged_at, submission_id)
        )
        # 如果 accepted，更新题目统计
        if status == 'ACCEPTED':
            conn.execute(
                """UPDATE problems SET 
                   accepted_count = accepted_count + 1,
                   submission_count = submission_count + 1
                   WHERE id = (SELECT problem_id FROM submissions WHERE id=?)""",
                (submission_id,)
            )
        else:
            conn.execute(
                """UPDATE problems SET 
                   submission_count = submission_count + 1
                   WHERE id = (SELECT problem_id FROM submissions WHERE id=?)""",
                (submission_id,)
            )
        conn.commit()
        print(f"✅ Submission {submission_id} updated: {status}")
    except Exception as e:
        print(f"❌ Failed to update submission {submission_id}: {e}")
        conn.rollback()
    finally:
        conn.close()


class CallbackTask(Task):
    """带回调的任务基类"""
    
    def on_success(self, retval, task_id, args, kwargs):
        """任务成功时的回调"""
        print(f"Task {task_id} succeeded: {retval}")
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """任务失败时的回调"""
        print(f"Task {task_id} failed: {exc}")


@celery_app.task(base=CallbackTask, bind=True, name='judger.tasks.judge_submission')
def judge_submission(
    self,
    submission_id: int,
    code: str,
    language: str,
    test_cases: List[Dict[str, str]],
    time_limit: int = 1000,
    memory_limit: int = 256,
) -> Dict:
    """
    异步判题任务
    
    Args:
        self: Celery task 实例
        submission_id: 提交 ID
        code: 用户代码
        language: 编程语言
        test_cases: 测试用例列表
        time_limit: 时间限制（毫秒）
        memory_limit: 内存限制（MB）
    
    Returns:
        判题结果字典
    """
    try:
        # 更新任务状态为判题中
        self.update_state(
            state='JUDGING',
            meta={
                'submission_id': submission_id,
                'status': 'judging',
                'progress': 0,
            }
        )
        
        # 创建判题器
        judger = DockerJudger()
        
        # 转换语言字符串为枚举
        lang = Language(language.lower())
        
        # 执行判题
        result = judger.judge(
            code=code,
            language=lang,
            test_cases=test_cases,
            time_limit=time_limit,
            memory_limit=memory_limit,
        )
        
        # 构造返回结果
        result_dict = {
            'submission_id': submission_id,
            'status': result.status,
            'score': result.score,
            'time_used': result.time_used,
            'memory_used': result.memory_used,
            'error_message': result.error_message,
            'test_cases_result': result.test_cases_result,
        }
        
        # 更新任务状态为完成
        self.update_state(
            state='SUCCESS',
            meta={
                'submission_id': submission_id,
                'status': 'completed',
                'result': result_dict,
            }
        )
        
        # 写回数据库
        _update_submission_in_db(submission_id, result_dict)
        
        return result_dict
        
    except Exception as e:
        # 任务失败
        error_msg = str(e)
        print(f"Judge task failed for submission {submission_id}: {error_msg}")
        
        error_result = {
            'submission_id': submission_id,
            'status': JudgeResult.SYSTEM_ERROR,
            'score': 0,
            'time_used': 0,
            'memory_used': 0,
            'error_message': error_msg,
            'test_cases_result': [],
        }
        
        # 写回数据库
        _update_submission_in_db(submission_id, error_result)
        
        return error_result


@celery_app.task(name='judger.tasks.batch_rejudge')
def batch_rejudge(submission_ids: List[int]) -> Dict:
    """
    批量重新判题
    
    Args:
        submission_ids: 提交 ID 列表
    
    Returns:
        批量判题结果
    """
    results = []
    
    for submission_id in submission_ids:
        # 这里需要从数据库获取提交信息
        # 暂时返回占位符
        results.append({
            'submission_id': submission_id,
            'status': 'queued',
        })
    
    return {
        'total': len(submission_ids),
        'results': results,
    }
