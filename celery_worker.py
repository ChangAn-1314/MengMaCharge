"""
充电桩监控系统 - Celery工作进程启动脚本

这个脚本用于启动Celery工作进程，处理异步任务。
"""

import os
from dotenv import load_dotenv
from app.tasks import celery

# 加载环境变量
load_dotenv()

if __name__ == '__main__':
    # 启动Celery工作进程
    celery.worker_main(['worker', '--loglevel=info']) 