"""
Celery 应用配置
"""

from celery import Celery
import os

# 从环境变量获取配置，如果没有则使用默认值
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# 创建 Celery 应用
celery_app = Celery(
    'judger',
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=['judger.tasks']
)

# Celery 配置
celery_app.conf.update(
    # 任务结果过期时间（秒）
    result_expires=3600,
    
    # 任务序列化方式
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # 时区
    timezone='Asia/Shanghai',
    enable_utc=True,
    
    # 任务路由
    task_routes={
        'judger.tasks.judge_submission': {'queue': 'judge'},
    },
    
    # 任务优先级
    task_default_priority=5,
    
    # Worker 配置
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
)

if __name__ == '__main__':
    celery_app.start()
