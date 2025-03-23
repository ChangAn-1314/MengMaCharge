"""
充电桩监控系统 - 配置模块

这个模块负责管理不同环境下的应用配置。
"""

import os
from dotenv import load_dotenv

# 加载环境变量（确保从正确路径加载）
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

class Config:
    """基础配置类"""
    # 应用配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')
    JSON_AS_ASCII = False
    
    # 数据库配置
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_NAME = os.environ.get('DB_NAME', 'port_status_db')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 数据库连接池配置
    SQLALCHEMY_POOL_SIZE = int(os.environ.get('DB_POOL_SIZE', 10))
    SQLALCHEMY_POOL_TIMEOUT = int(os.environ.get('DB_POOL_TIMEOUT', 30))
    SQLALCHEMY_POOL_RECYCLE = int(os.environ.get('DB_POOL_RECYCLE', 3600))
    SQLALCHEMY_MAX_OVERFLOW = int(os.environ.get('DB_MAX_OVERFLOW', 20))
    
    # API配置
    API_SECRET_KEY = os.environ.get('API_SECRET_KEY')
    API_APPID = os.environ.get('API_APPID', 'mengma')
    API_APPCOMMID = os.environ.get('API_APPCOMMID', 'MCB_INSTANCE_WECHAT_APP')
    API_TOKEN = os.environ.get('API_TOKEN')
    API_TIMEOUT = int(os.environ.get('API_TIMEOUT', 5))  # API请求超时时间（秒）
    
    # 缓存配置
    CACHE_TIMEOUT = int(os.environ.get('CACHE_TIMEOUT', 30))  # 缓存过期时间（秒）
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'RedisCache')  # 缓存类型
    
    # Redis配置
    REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', '')
    REDIS_DB = int(os.environ.get('REDIS_DB', 0))
    
    # Celery配置
    ENABLE_ASYNC = os.environ.get('ENABLE_ASYNC', 'false').lower() == 'true'
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', f'redis://{REDIS_HOST}:{REDIS_PORT}/1')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', f'redis://{REDIS_HOST}:{REDIS_PORT}/1')
    CELERY_WORKER_CONCURRENCY = int(os.environ.get('CELERY_WORKER_CONCURRENCY', 4))
    CELERY_TASK_TIMEOUT = int(os.environ.get('CELERY_TASK_TIMEOUT', 300))
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', None)
    
    # 性能优化配置
    BATCH_UPDATE_SIZE = int(os.environ.get('BATCH_UPDATE_SIZE', 10))  # 批量更新大小
    CONNECTION_POOL_SIZE = int(os.environ.get('CONNECTION_POOL_SIZE', 20))  # HTTP连接池大小
    BULK_DB_OPERATION = os.environ.get('BULK_DB_OPERATION', 'true').lower() == 'true'  # 是否启用批量数据库操作

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    SQLALCHEMY_ECHO = True
    
class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    CACHE_TYPE = 'SimpleCache'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    ENABLE_ASYNC = False
    
class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    TESTING = False
    # 实际生产环境应该有更严格的配置
    LOG_LEVEL = 'WARNING'
    SQLALCHEMY_ECHO = False

# 配置映射
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 