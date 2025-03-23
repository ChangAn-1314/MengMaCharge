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
    
    # API配置
    API_SECRET_KEY = os.environ.get('API_SECRET_KEY')
    API_APPID = os.environ.get('API_APPID', 'mengma')
    API_APPCOMMID = os.environ.get('API_APPCOMMID', 'MCB_INSTANCE_WECHAT_APP')
    API_TOKEN = os.environ.get('API_TOKEN')
    
    # 缓存配置
    CACHE_TIMEOUT = int(os.environ.get('CACHE_TIMEOUT', 5))

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    
class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    # 使用内存SQLite数据库进行测试
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    
    # 在生产环境中使用更安全的配置
    @classmethod
    def init_app(cls, app):
        """生产环境特定初始化"""
        # 在这里可以添加生产环境特定的配置
        pass

# 配置字典，用于选择不同环境的配置
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    
    # 默认配置
    'default': DevelopmentConfig
} 